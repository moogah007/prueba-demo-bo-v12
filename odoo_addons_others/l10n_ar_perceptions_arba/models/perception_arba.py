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
from datetime import datetime

from l10n_ar_api.presentations import presentation
from odoo import models, fields
from odoo.exceptions import Warning


class PerceptionArba(models.Model):
    _name = 'perception.arba'

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        if invoice.move_id.line_ids:
            move = invoice.move_id.line_ids[0]
            if move.amount_currency != 0:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate

    def _get_tipo(self, p):
        if p.invoice_id.type == 'out_invoice':
            return 'D' if p.invoice_id.is_debit_note else 'F'
        else:
            return 'C'

    def _get_sign(self, p):
        return '-' if p.invoice_id.type == 'out_refund' else '0'

    def _get_state_b(self):
        return self.env.ref('base.state_ar_b').id

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80')

    def create_line(self, presentation_arba, perception):

        line = presentation_arba.create_line()

        vat = perception.invoice_id.partner_id.vat

        perception_date = perception.invoice_id.date_invoice.strftime('%d/%m/%Y')

        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fechaPercepcion = perception_date
        line.tipoComprobante = self._get_tipo(perception)
        line.letraComprobante = perception.invoice_id.denomination_id.name
        line.numeroSucursal = perception.invoice_id.name.split('-')[0]
        line.numeroEmision = perception.invoice_id.name.split('-')[1]
        line.basePercepcion = '{0:.2f}'.format(perception.base * self._get_invoice_currency_rate(perception.invoice_id)).replace('.', ',')
        line.importePercepcion = '{0:.2f}'.format(perception.amount * self._get_invoice_currency_rate(perception.invoice_id)).replace('.', ',')
        line.tipoOperacion = 'A'
        line.sign = self._get_sign(perception)

    def generate_file(self):
        presentation_arba = presentation.Presentation("arba", "percepciones")
        perceptions = self.env['account.invoice.perception'].search([
            ('invoice_id.date', '>=', self.date_from),
            ('invoice_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('perception_id.state_id', '=', self._get_state_b()),
            ('invoice_id.state', 'in', ['open', 'paid']),
            ('perception_id.type_tax_use', '=', 'sale')
        ]).sorted(key=lambda r: (r.invoice_id.date, r.id))

        missing_vats = set()
        invalid_doctypes = set()
        invalid_vats = set()

        for p in perceptions:

            vat = p.invoice_id.partner_id.vat
            if not vat:
                missing_vats.add(p.invoice_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(p.invoice_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(p.invoice_id.partner_id):
                invalid_doctypes.add(p.invoice_id.name_get()[0][1])

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats:
                continue
            self.create_line(presentation_arba, p)

        if missing_vats or invalid_doctypes or invalid_vats:
            errors = []
            if missing_vats:
                errors.append("Los partners de las siguientes facturas no poseen numero de CUIT:")
                errors.extend(missing_vats)
            if invalid_doctypes:
                errors.append("El tipo de documento de los partners de las siguientes facturas no es CUIT:")
                errors.extend(invalid_doctypes)
            if invalid_vats:
                errors.append("Los partners de las siguientes facturas poseen numero de CUIT erroneo:")
                errors.extend(invalid_vats)
            raise Warning("\n".join(errors))

        else:
            self.file = presentation_arba.get_encoded_string()
            self.filename = 'AR-{vat}-{period}{fortnight}-{activity}-LOTE{lot}.TXT'.format(
                vat=self.company_id.vat,
                period=self.date_from.strftime('%Y%m'),
                fortnight=self.fortnight,
                activity=self.activity,
                lot=self.lot,
            )

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    activity = fields.Char(string='Actividad', required=True, default='7')
    fortnight = fields.Char(string='Quincena', required=True, default='0')
    lot = fields.Char(string='Lote', required=True, default='0')
    file = fields.Binary(string='Archivo', filename="filename")
    filename = fields.Char(string='Nombre Archivo')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('perception.arba')
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
