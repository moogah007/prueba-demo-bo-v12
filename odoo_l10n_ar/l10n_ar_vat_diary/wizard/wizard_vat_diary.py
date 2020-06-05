# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import io
import base64
from datetime import datetime
from odoo import models, fields, http, api
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class WizardVatDiary(models.TransientModel):

    _name = 'wizard.vat.diary'
    _description = 'Wizard de subdiario de IVA'

    type = fields.Selection([
        ('sales', 'Ventas'),
        ('purchases', 'Compras')
    ], 'Tipo', required=True)
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta', required=True)
    report = fields.Binary('Reporte')

    @api.constrains('date_from', 'date_to')
    def validate_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError("Rango invalido de fechas")

    def _get_invoices(self):
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', 'not in', ('draft', 'cancel'))
        ]
        if self.type == 'sales':
            domain.append(('type', 'in', ('out_invoice', 'out_refund')))
        else:
            domain.append(('type', 'in', ('in_invoice', 'in_refund')))

        invoices = self.env['account.invoice'].search(domain)
        if not invoices:
            raise ValidationError("No se han encontrado documentos para ese rango de fechas")

        return invoices

    def _get_taxes_position(self, invoices):
        """
        Devuelve los impuestos de las facturas en un diccionario con un valor distinto para cada uno
        :param invoices: account.invoice - Del cual se obtendran todos los impuestos
        :return dict: de la forma {account.tax(): posicion}
        """

        res = {}
        position = 0

        # Ordenamos los impuestos para tener el IVA primero y removemos duplicados
        sorted_taxes = invoices.mapped('tax_line_ids').filtered(
            lambda l: l.amount or (l.tax_id.tax_group_id ==
                                   self.env.ref('l10n_ar.tax_group_vat') and not l.tax_id.is_exempt)
        ).mapped('tax_id').sorted(
            key=lambda x: (x.tax_group_id != self.env.ref('l10n_ar.tax_group_vat'), x.name),
        )

        # Para el iva vamos a utilizar no solo el valor si no la base imponible
        for tax in sorted_taxes:
            res[tax] = position
            position += 2 if tax.tax_group_id == self.env.ref('l10n_ar.tax_group_vat') else 1

        return res

    def _get_header(self):
        """ Genero un diccionario con los valores basicos de la cabecera del reporte """
        header = {
            0: 'Fecha',
            1: 'Razon Social',
            2: 'Doc. Numero',
            3: 'Condicion IVA',
            4: 'Tipo',
            5: 'Denominacion',
            6: 'Numero',
            7: 'Jurisdiccion'
        }
        return header

    def get_header_values(self, taxes_position):
        """
        Crea la estructura de datos para la cabecera del reporte
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :return header: diccionario con la posicion y valor, ej: {0: 'Fecha', 1: 'Razon Social'..}
        """
        header = self._get_header()
        last_header_position = len(header)
        for tax in taxes_position:
            if tax.tax_group_id == self.env.ref('l10n_ar.tax_group_vat'):
                header[taxes_position[tax] + last_header_position] = tax.name + ' - Base'
                header[taxes_position[tax] + last_header_position + 1] = tax.name + ' - Importe'
            else:
                header[taxes_position[tax] + last_header_position] = tax.name

        if taxes_position:
            last_tax = max(taxes_position, key=taxes_position.get)
            last_position = taxes_position[last_tax] + \
                (2 if last_tax.tax_group_id == self.env.ref('l10n_ar.tax_group_vat') else 1)
        else:
            last_position = 0

        header[last_position + last_header_position] = 'No Gravado/Exento'
        header[last_position + last_header_position + 1] = 'Total'

        return header

    def _get_invoice_values(self, invoice, last_position, size, sign, rate):
        """ Setteo los valores para cada posicion de una fila"""
        return {
            0: invoice.date_invoice.strftime('%d/%m/%Y'),
            1: invoice.partner_id.name,
            2: invoice.partner_id.vat or '',
            3: invoice.partner_id.property_account_position_id.name or '',
            4: invoice.name_get()[0][1][:3],
            5: invoice.denomination_id.name,
            6: invoice.name,
            7: invoice.jurisdiction_id.name or invoice.partner_id.state_id.name or '',
            last_position + size: (invoice.amount_not_taxable + invoice.amount_exempt) * sign * rate,
            last_position + size + 1: invoice.amount_total_company_signed
        }

    def get_details_values(self, taxes_position, invoices):
        """
         Crea la estructura de datos para los detalle del reporte, los cuales son datos de invoices.
        :param taxes_position: diccionario que contiene la posicion del impuesto y el impuesto
        :param invoices: account.invoice - De donde se tomaran los datos segun filtros del wizard
        :return: lista de diccionarios, cada uno con la posicion y valor, ej: {0: '01/01/2000'}
        """
        res = []

        # Obtenemos el ultimo impuesto para saber en que columna van los totales
        if taxes_position:
            last_tax = max(taxes_position, key=taxes_position.get)
            last_position = taxes_position[last_tax] + \
                            (2 if last_tax.tax_group_id == self.env.ref('l10n_ar.tax_group_vat') else 1)
        else:
            last_position = 0

        for invoice in invoices.sorted(key=lambda x: (x.date_invoice, x.type, x.name)):
            rate = self._get_invoice_currency_rate(invoice)
            sign = invoice.type in ['in_refund', 'out_refund'] and -1 or 1
            header = self._get_header()
            size_header = len(header)
            invoice_values = self._get_invoice_values(invoice, last_position, size_header, sign, rate)
            if any(not invoice_tax.tax_id for invoice_tax in invoice.tax_line_ids):
                raise ValidationError('Alguna linea de impuesto en {} no tiene impuesto establecido'.format(invoice.name_get()[0][1]))
            for invoice_tax in invoice.tax_line_ids.filtered(
                    lambda l: l.amount or (l.tax_id.tax_group_id == self.env.ref('l10n_ar.tax_group_vat') and not l.tax_id.is_exempt)
            ):
                if invoice_tax.tax_id.tax_group_id == self.env.ref('l10n_ar.tax_group_vat'):
                    invoice_values[taxes_position[invoice_tax.tax_id] + size_header] = invoice_tax.base * sign * rate
                    invoice_values[taxes_position[invoice_tax.tax_id] + size_header + 1] = invoice_tax.amount * sign * rate
                else:
                    invoice_values[taxes_position[invoice_tax.tax_id] + size_header] = invoice_tax.amount * sign * rate

            res.append(invoice_values)

        return res
    
    def get_report_values(self):
        """
        Devuelve los datos de cabecera y detalles del reporte a armar de las invoices obtenidas del wizard
        :return list: Lista de diccionarios con la cabecera y detalles
            [{0: 'Fecha',...}{0: '01/01/2000,...}]
        """

        invoices = self._get_invoices()
        taxes_position = self._get_taxes_position(invoices)
        header = self.get_header_values(taxes_position)
        details = self.get_details_values(taxes_position, invoices)

        return [header] + details

    def generate_xls_report(self):
        """ Crea un xls con los valores obtenidos de get_report_values"""
        values = self.get_report_values()

        # Preparamos el workbook y la hoja
        import xlwt
        wbk = xlwt.Workbook()
        style = xlwt.easyxf(
            'font: bold on,height 240,color_index 0X36;'
            'align: horiz center;'
            'borders: left thin, right thin, top thin'
        )
        name = 'Iva Ventas' if self.type == 'sales' else 'Iva Compras'
        sheet = wbk.add_sheet(name)
        # Ancho de las columnas
        sheet.col(0).width = 2500
        sheet.col(1).width = 6000
        sheet.col(2).width = 4000
        sheet.col(3).width = 6000
        sheet.col(4).width = 1500
        sheet.col(5).width = 1500
        sheet.col(6).width = 4000
        sheet.col(7).width = 4000

        row_number = 0
        total_cols = 0
        # Header
        for col in values[0]:
            # Le asignamos el ancho a las columnas de importes
            if total_cols > 7:
                sheet.col(col).width = 3500
            sheet.write(row_number, col, values[0][col], style)
            total_cols += 1

        # Detalles
        row_number += 1
        for value in values[1:]:
            for col in value:
                sheet.write(row_number, col, value[col])
            row_number += 1
        header = self._get_header()
        size_header = len(header)
        for x in range(size_header, total_cols):
            column_start = xlwt.Utils.rowcol_to_cell(1, x)
            column_end = xlwt.Utils.rowcol_to_cell(row_number - 1, x)
            sheet.write(row_number, x, xlwt.Formula('SUM(' + column_start + ':' + column_end + ')'))

        # Exportamos y guardamos
        file_data = io.BytesIO()
        wbk.save(file_data)
        out = base64.encodebytes(file_data.getvalue())
        self.report = out

        date_from = self.date_from.strftime('%d-%m-%Y')
        date_to = self.date_to.strftime('%d-%m-%Y')

        filename = 'Subdiario ' + name + ' ' + date_from + ' a ' + date_to

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_vat_diary?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }

    @staticmethod
    def _get_invoice_currency_rate(invoice):
        """ Calculo el rate de la factura """
        rate = 1
        if (invoice.company_id.currency_id != invoice.currency_id) and invoice.move_id.line_ids:
            move = invoice.move_id.line_ids[0]
            if move.amount_currency != 0:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate


class WizardVatDiaryRoute(http.Controller):
    @http.route('/web/binary/download_vat_diary', type='http', auth="public")
    @serialize_exception
    def download_vat_diary(self, debug=1, wizard_id=0, filename=''):  # pragma: no cover
        """ Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: Si esta o no en modo debug.
        :param int wizard_id: Id del modelo que contiene el documento.
        :param filename: Nombre del archivo.
        :returns: :class:`werkzeug.wrappers.Response`, descarga del archivo excel.
        """
        filecontent = base64.b64decode(request.env['wizard.vat.diary'].browse(int(wizard_id)).report or '')
        return request.make_response(filecontent, [('Content-Type', 'application/excel'),
                                                   ('Content-Disposition', content_disposition(filename))])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
