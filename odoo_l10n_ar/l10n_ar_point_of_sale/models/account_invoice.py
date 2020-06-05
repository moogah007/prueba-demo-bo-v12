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

import json
import simplejson
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if not res.pos_ar_id:
            res.onchange_partner_id()
        return res

    @api.model
    def _get_domain(self):
        country_id = self.env.ref('base.ar').id
        return [('country_id', '=', country_id)]

    pos_ar_id = fields.Many2one('pos.ar', 'Punto de venta')
    denomination_id = fields.Many2one('account.denomination', 'Denominacion')
    is_debit_note = fields.Boolean('Es nota de debito?')
    is_credit_invoice = fields.Boolean('Es factura de credito?')
    jurisdiction_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Jurisdiccion',
        domain=_get_domain
    )

    # Dato que se va a utilizar desde diferentes modulos para poder aplicar
    # filtros y cambiar los datos que se visualizan en el formulario de una
    # factura. Ejemplo: En modulo de facturacion electronica solo se mostrara
    # cae y fecha vencimiento cae en caso de que el tipo de de talonario sea
    # electronico.
    document_book_type = fields.Char(
        compute='get_document_book_type',
        string='Tipo de talonario'
    )

    @api.multi
    def name_get(self):
        """ Utilizamos la idea original, pero cambiando los parametros """

        result = []

        for inv in self:

            invoice_type = inv.get_invoice_type()

            name_get = [invoice_type]
            if inv.denomination_id:
                name_get.append(inv.denomination_id.name)

            if inv.name or inv.number:
                name_get.append(inv.name or inv.number)

            # EJ FC A 0001-00000001
            result.append((inv.id, " ".join(name_get)))

        return result

    def check_invoice_duplicity(self):
        """ Valida que la factura no este duplicada. """

        domain = [
            ('is_debit_note', '=', self.is_debit_note),
            ('is_credit_invoice', '=', self.is_credit_invoice),
            ('denomination_id', '=', self.denomination_id.id),
            ('pos_ar_id', '=', self.pos_ar_id.id),
            ('name', '!=', False),
            ('name', '=', self.name),
            ('type', '=', self.type),
            ('state', 'not in', ['draft', 'cancel']),
            ('id', '!=', self.id)
        ]

        if self.type in ['in_invoice', 'in_refund']:
            domain.append(('partner_id', '=', self.partner_id.id))

        if self.search_count(domain) > 0:
            raise ValidationError("Ya existe un documento con ese número!")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        """
        Seteamos el punto de venta y la denominacion del talonario mas prioritario
        """
        if self.partner_id:

            vals = {}
            denomination = self.get_invoice_denomination()
            vals['jurisdiction_id'] = self.partner_shipping_id.state_id.id or self.partner_id.state_id.id
            vals['denomination_id'] = denomination.id
            vals['pos_ar_id'] = self.env['pos.ar'].get_pos('invoice', denomination=denomination,
                                                           company=self.company_id).id \
                if self.type in ['out_invoice', 'out_refund'] else None

            self.update(vals)

        else:
            self.update({
                'pos_ar_id': None,
                'denomination_id': None,
                'jurisdiction_id': None
            })

    def _get_invoice_type_dict(self):
        return {
            # (type, is_debit_note, is_credit_invoice)
            ('out_invoice', False, False): {'internal_type': 'invoice', 'type': 'FCC', 'name': _('INVOICE')},
            ('out_invoice', True, False): {'internal_type': 'debit_note', 'type': 'NDC', 'name': _('DEBIT NOTE')},
            ('out_refund', False, False): {'internal_type': 'refund', 'type': 'NCC', 'name': _('CREDIT NOTE')},
            ('out_invoice', False, True): {'internal_type': 'invoice_fce', 'type': 'FCEC',
                                           'name': 'FACTURA DE CRÉDITO ELECTRÓNICA MiPyMEs (FCE)'},
            ('out_invoice', True, True): {'internal_type': 'debit_note_fce', 'type': 'NDEC',
                                          'name': 'NOTA DE DÉBITO ELECTRÓNICA MiPyMEs (FCE)'},
            ('out_refund', False, True): {'internal_type': 'refund_fce', 'type': 'NCEC',
                                          'name': 'NOTA DE CRÉDITO ELECTRÓNICA MiPyMEs (FCE)'},
            ('in_invoice', False, False): {'internal_type': 'invoice', 'type': 'FCP', 'name': _('INVOICE')},
            ('in_invoice', True, False): {'internal_type': 'debit_note', 'type': 'NDP', 'name': _('DEBIT NOTE')},
            ('in_refund', False, False): {'internal_type': 'refund', 'type': 'NCP', 'name': _('CREDIT NOTE')},
            ('in_invoice', False, True): {'internal_type': 'invoice_fce', 'type': 'FCEP',
                                          'name': 'FACTURA DE CRÉDITO ELECTRÓNICA MiPyMEs (FCE)'},
            ('in_invoice', True, True): {'internal_type': 'debit_note_fce', 'type': 'NDEP',
                                         'name': 'NOTA DE DÉBITO ELECTRÓNICA MiPyMEs (FCE)'},
            ('in_refund', False, True): {'internal_type': 'refund_fce', 'type': 'NCEP',
                                         'name': 'NOTA DE CRÉDITO ELECTRÓNICA MiPyMEs (FCE)'},
        }

    def get_invoice_types(self):
        return self._get_invoice_type_dict().get(
            (self.type, self.is_debit_note, self.is_credit_invoice),
            {'internal_type': 'other', 'type': 'NF', 'name': _('NO FISCAL')}
        )

    def get_invoice_type(self):
        return self.get_invoice_types().get('type')

    def get_invoice_internal_type(self):
        return self.get_invoice_types().get('internal_type')

    def get_invoice_name(self):
        return self.get_invoice_types().get('name')

    def get_invoice_denomination(self):
        """ Busca la denominacion en base a las posiciones fiscales del partner y la empresa """

        issue_fiscal_position = self.get_issue_fiscal_position()
        receipt_fiscal_position = self.get_receipt_fiscal_position()

        denomination = self.denomination_id

        if issue_fiscal_position and receipt_fiscal_position:
            denomination = issue_fiscal_position.get_denomination(receipt_fiscal_position)

        return denomination

    def get_issue_fiscal_position(self):
        """
        :return: Posicion fiscal emisora segun tipo de factura
        """
        company_self = self.with_context(force_company=self.company_id.id)
        company_fiscal_position = company_self.company_id.partner_id.property_account_position_id
        partner_fiscal_position = company_self.partner_id.property_account_position_id

        issue_fiscal_position = company_fiscal_position if self.type in ('out_invoice', 'out_refund')\
            else partner_fiscal_position

        return issue_fiscal_position

    def get_receipt_fiscal_position(self):
        """
        :return: Posicion fiscal receptora segun tipo de factura
        """
        company_self = self.with_context(force_company=self.company_id.id)
        company_fiscal_position = company_self.company_id.partner_id.property_account_position_id
        partner_fiscal_position = company_self.partner_id.property_account_position_id

        receipt_fiscal_position = partner_fiscal_position if self.type in ('out_invoice', 'out_refund')\
            else company_fiscal_position

        return receipt_fiscal_position

    @api.multi
    def action_move_create(self):

        for invoice in self:

            # Validamos posiciones fiscales y denominacion
            invoice._validate_fiscal_position_and_denomination()

            # Obtenemos el proximo numero o validamos su estructura
            if invoice.type in ['out_invoice', 'out_refund']:

                document_book = invoice.get_document_book()

                # Llamamos a la funcion a ejecutarse desde el tipo de talonario, de esta forma, hará lo correspondiente
                # para distintos casos (preimpreso, electronica, fiscal, etc.)
                getattr(invoice, document_book.book_type_id.foo)(document_book)

            else:
                invoice._validate_supplier_invoice_number()

            invoice.check_invoice_duplicity()

        return super(AccountInvoice, self).action_move_create()

    def get_voucher_code(self):
        """ Devuelve el codigo de AFIP del documento """
        self.ensure_one()

        document_type_id = self.get_document_book().document_type_id.id
        voucher_type = self.env['afip.voucher.type'].search([
            ('document_type_id', '=', document_type_id),
            ('denomination_id', '=', self.denomination_id.id)],
            limit=1
        )
        document_afip_code = self.env['codes.models.relation'].get_code('afip.voucher.type', voucher_type.id)

        return document_afip_code

    def get_document_book(self):
        """
        Busca el talonario obtenido del punto de venta y denominacion.
        Agregamos un parametro de domains adicionales
        para considerar el caso de notas de debito u otros domains de negocio que se puedan agregar
        a futuro.
        :return: Talonario a utilizar
        :raise ValidationError: No esta seteado el punto de venta o la denominacion
        :raise ValidationError: No hay configurado un talonario para ese punto de venta y denominacion
        """

        if self.is_debit_note:
            invoice_type = 'debit_note'
        else:
            invoice_type = 'invoice' if self.type == 'out_invoice' else 'refund'

        if self.is_credit_invoice:
            invoice_type += '_fce'

        domain = [
            ('document_type_id.type', '=', invoice_type),
            ('denomination_id', '=', self.denomination_id.id),
            ('pos_ar_id', '=', self.pos_ar_id.id),
            ('category', '=', 'invoice'),
        ]

        if not (self.pos_ar_id and self.denomination_id):
            raise ValidationError('El documento debe tener punto de venta y denominacion para ser validado')

        document_book = self.env['document.book'].search(domain, limit=1)

        if not document_book:
            raise ValidationError('No existe talonario configurado para el punto de venta '
                            + self.pos_ar_id.name_get()[0][1] + ' y la denominacion ' + self.denomination_id.name)

        return document_book

    def action_preprint(self, document_book):
        """ Funcion para ejecutarse al validar una factura con talonario preimpreso """
        self.name = document_book.next_number()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Override, agregamos a las notas de credito creadas originalmente el punto de venta y la denominacion """

        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)

        values['pos_ar_id'] = invoice.pos_ar_id.id
        values['denomination_id'] = invoice.denomination_id.id
        values['name'] = None
        values['origin'] = invoice.name_get()[0][1]
        values['is_credit_invoice'] = invoice.is_credit_invoice

        return values

    def _validate_fiscal_position_and_denomination(self):
        """
        Valida si las posiciones fiscales de los partnes y la empresa
        van acorde a la denominacion de la factura
        :raises ValidationError: Si no esta configurada la posicion fiscal de la empresa, partner, o si no es igual
        la posicion fiscal del partner a la de la factura
        :raise ValidationError: Si la denominacion de la factura no es la correcta segun posiciones fiscales
        """

        # Valido posiciones fiscales
        company_self = self.with_context(force_company=self.company_id.id)
        company_fiscal_position = company_self.company_id.partner_id.property_account_position_id
        partner_fiscal_position = company_self.partner_id.property_account_position_id
        self._validate_fiscal_position(company_fiscal_position, partner_fiscal_position)

        # Valido denominacion
        issue_fiscal_position = self.get_issue_fiscal_position()
        receipt_fiscal_position = self.get_receipt_fiscal_position()
        denomination = issue_fiscal_position.get_denomination(receipt_fiscal_position)
        self._validate_denomination(denomination)

    def _validate_fiscal_position(self, company_fiscal_position, partner_fiscal_position):
        """
        Valida las posiciones fiscales de la factura
        :param company_fiscal_position: account.fiscal.position - Posicion fiscal de la empresa
        :param partner_fiscal_position: account.fiscal.position - Posicion fiscal del partner de la factura
        :raises ValidationError: Si no esta configurada la posicion fiscal de la empresa, partner, o si no es igual
        la posicion fiscal del partner a la de la factura
        """

        if not company_fiscal_position:
            raise ValidationError('Por favor, configurar la posicion fiscal de la empresa ' + self.company_id.name)
        if not partner_fiscal_position:
            raise ValidationError('Por favor, configurar la posicion fiscal del partner')

        if self.fiscal_position_id != partner_fiscal_position:
            raise ValidationError('La posicion fiscal del documento debe ser la misma que la configurada en el partner')

    def _validate_denomination(self, denomination):
        """
        Valida la denominacion de la factura
        :param denomination: account.denomination - Posicion fiscal que deberia tener la factura
        :raise ValidationError: Si la denominacion de la factura no es la correcta segun posiciones fiscales
        """

        if denomination != self.denomination_id:
            raise ValidationError('La denominacion de la factura no es la misma que la configurada en las posiciones fiscales')

    def _validate_supplier_invoice_number(self):
        """
        Validamos el numero de factura
        :raise ValidationError: Si no cumple con el formato xxxx-xxxxxxxx, y debe tener solo enteros
        """

        if not self.name:
            raise ValidationError('El documento no tiene numero!')

        if self.denomination_id.validate_supplier:
            invoice_number = self.name.split('-')
            error_msg = "Formato invalido, el documento debe tener el formato 'xxxxx-xxxxxxxx' y contener solo números!"

            # Nos aseguramos que contenga '-' para separar punto de venta de numero
            if len(invoice_number) != 2:
                raise ValidationError(error_msg)

            # Rellenamos con 0s los valores necesarios
            point_of_sale = invoice_number[0].zfill(4)
            number = invoice_number[1].zfill(8)
            invoice_number = point_of_sale+'-'+number

            # Validamos el formato y se lo ponemos a la factura
            if not re.match('^([0-9]{4}|[0-9]{5})-[0-9]{8}$', invoice_number):
                raise ValidationError(error_msg)

            self.name = invoice_number

    @api.depends('number', 'denomination_id', 'type', 'name')
    def get_full_name(self):
        for inv in self:
            inv.full_name = inv.name_get()[0][1]

    @api.depends('denomination_id', 'pos_ar_id')
    def get_document_book_type(self):
        for inv in self:
            if inv.denomination_id and inv.pos_ar_id:
                inv.document_book_type = inv.get_document_book().book_type_id.type

    full_name = fields.Char(compute='get_full_name', string="Numero")

    @api.one
    def _get_outstanding_info_JSON(self):
        """
        Por default trae el nombre del diario en los creditos pendientes de la factura, la idea es que
        muestre el tipo y numero de documento, por ejemplo, FCC A 0001-000000001 en lugar de INV/XXXX/XXXX
        """
        super(AccountInvoice, self)._get_outstanding_info_JSON()
        outstanding_credits = simplejson.loads(self.outstanding_credits_debits_widget)
        if outstanding_credits:
            contents = outstanding_credits.get('content')
            for content in contents:
                line = self.env['account.move.line'].browse(content.get('id'))
                if line and (line.payment_id or line.invoice_id):
                    invoice_name = line.invoice_id.full_name[:4] + line.invoice_id.full_name[-8:] \
                        if line.invoice_id else None
                    payment_name = line.name[:3].split(" ")[0] + ' ' + line.name[-8:] if line.payment_id else None
                    content['journal_name'] = invoice_name or payment_name or line.name
            self.outstanding_credits_debits_widget = json.dumps(outstanding_credits)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
