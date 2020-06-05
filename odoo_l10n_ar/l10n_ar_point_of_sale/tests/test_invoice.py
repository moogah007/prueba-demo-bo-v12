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

from odoo.exceptions import ValidationError
from .test_document_book import TestDocumentBook
import simplejson


class TestInvoice(TestDocumentBook):

    def _create_partners(self):
        self.partner_ri = self.env['res.partner'].create({
            'name': 'Customer',
            'customer': True,
            'supplier': True,
            'property_account_position_id': self.iva_ri.id
        })

        self.partner_cf = self.env['res.partner'].create({
            'name': 'Supplier',
            'customer': True,
            'supplier': True,
            'property_account_position_id': self.iva_cf.id
        })

    def _create_invoices(self):

        account = self.partner_ri.property_account_receivable_id

        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_ri.id,
            'fiscal_position_id': self.partner_ri.property_account_position_id.id,
            'account_id': account.id,
            'type': 'out_invoice',
            'state': 'draft'
        })

        self.env['account.invoice.line'].create({
            'name': 'Producto',
            'account_id': self.env.ref('l10n_ar.1_materiales_e_insumos').id,
            'quantity': 1,
            'price_unit': 500,
            'invoice_id': self.invoice.id,
        })

        self.debit_note = self.env['account.invoice'].create({
            'partner_id': self.partner_ri.id,
            'fiscal_position_id': self.partner_ri.property_account_position_id.id,
            'account_id': account.id,
            'type': 'out_invoice',
            'state': 'draft',
            'is_debit_note': True,
        })

        self.env['account.invoice.line'].create({
            'name': 'Producto',
            'account_id': account.id,
            'quantity': 1,
            'price_unit': 500,
            'invoice_id': self.debit_note.id,
        })

        self.invoice_new = self.env['account.invoice'].new({})


    def setUp(self):
        super(TestInvoice, self).setUp()

        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.iva_cf = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_cf')
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri
        self.company_fiscal_position = self.env.user.company_id.partner_id.property_account_position_id

        # Clientes y proveedores
        self._create_partners()

        # Documentos
        self._create_invoices()

    def onchange_partner_out_invoice(self):
        self.invoice.onchange_partner_id()

        # Deberia tener el mismo punto de venta el talonario de tipo factura y denominacion A (RI-RI)
        assert self.invoice.pos_ar_id == self.document_book.pos_ar_id
        partner_fiscal_position = self.invoice.partner_id.property_account_position_id
        assert self.invoice.denomination_id == self.company_fiscal_position.get_denomination(partner_fiscal_position)

    def onchange_partner_in_invoice(self):
        # Cambiamos la factura a proveedor y le seteamos que sea consumidor final
        self.invoice.type = 'in_invoice'
        cf = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_cf')
        self.partner_ri.property_account_position_id = cf
        self.invoice.onchange_partner_id()

        # No deberia tener punto de venta al ser de proveedor y deberia tener posicion fiscal 'C'
        assert not self.invoice.pos_ar_id
        assert self.invoice.denomination_id == cf.get_denomination(self.company_fiscal_position)

    def onchange_no_partner(self):
        self.invoice_new.onchange_partner_id()
        assert not (self.invoice_new.denomination_id and self.invoice_new.pos_ar_id)

    def test_outstanding_widget_info_credit_note_customer(self):
        """ Probamos que la info del widget este bien """

        # Validamos la factura
        self.invoice.onchange_partner_id()
        self.invoice.invoice_line_ids[0]._onchange_product_id()
        self.invoice.invoice_line_ids[0].price_unit = 500
        self.invoice._onchange_invoice_line_ids()
        self.invoice.action_invoice_open()

        # Creamos una nota de credito
        self.document_book_proxy.create({
            'name': 12,
            'pos_ar_id': self.pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_refund').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
        })
        refund = self.invoice.copy()
        refund.write({
            'type': 'out_refund',
            'name': '1-1'
        })
        refund.onchange_partner_id()
        refund.invoice_line_ids[0]._onchange_product_id()
        refund.invoice_line_ids[0].price_unit = 500
        refund._onchange_invoice_line_ids()
        refund.action_invoice_open()

        # Validamos la informacion
        outstanding_credits = simplejson.loads(self.invoice.outstanding_credits_debits_widget)
        contents = outstanding_credits.get('content')
        assert contents[0].get('journal_name') == 'NCC '+refund.name[-8:]

    def test_outstanding_widget_info_credit_note_supplier(self):
        """ Probamos que la info del widget este bien """

        # Creamos una nota de credito y la validamos
        refund = self.invoice.copy()
        refund.write({
            'type': 'in_refund',
            'name': '1-1'
        })
        refund.onchange_partner_id()
        refund.invoice_line_ids[0]._onchange_product_id()
        refund.invoice_line_ids[0].price_unit = 500
        refund._onchange_invoice_line_ids()
        refund.action_invoice_open()

        # Validamos la factura
        self.invoice.write({
            'type': 'in_invoice',
            'name': '1-2'
        })
        self.invoice.onchange_partner_id()
        self.invoice.invoice_line_ids[0]._onchange_product_id()
        self.invoice.invoice_line_ids[0].price_unit = 500
        self.invoice._onchange_invoice_line_ids()
        self.invoice.action_invoice_open()

        # Validamos la informacion
        outstanding_credits = simplejson.loads(self.invoice.outstanding_credits_debits_widget)
        contents = outstanding_credits.get('content')
        assert contents[0].get('journal_name') == 'NCP '+refund.name[-8:]

    def test_get_invoice_denomination(self):
        assert self.invoice.get_invoice_denomination() == self.env.ref('l10n_ar_afip_tables.account_denomination_a')
        self.partner_ri.property_account_position_id = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ex')
        assert self.invoice.get_invoice_denomination() == self.env.ref('l10n_ar_afip_tables.account_denomination_b')
        self.onchange_partner_in_invoice()
        assert self.invoice.get_invoice_denomination() == self.env.ref('l10n_ar_afip_tables.account_denomination_c')

    def test_invalid_fiscal_positions(self):
        company_fiscal_position = self.company_fiscal_position
        self.env.user.company_id.partner_id.property_account_position_id = None
        # Probamos validar una factura si la compania no tiene posicion fiscal
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()
        self.env.user.company_id.partner_id.property_account_position_id = company_fiscal_position

        # Probamos cambiandole la posicion fiscal del partner y validar la factura
        self.partner_ri.property_account_position_id = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ex').id
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

        # Probamos sacandole la posicion fiscal al partner y validar la factura
        self.partner_ri.property_account_position_id = None
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

    def test_invalid_invoice_denomination(self):
        self.invoice.denomination_id = self.env.ref('l10n_ar_afip_tables.account_denomination_b')
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

    def test_supplier_invoice_number(self):
        self.invoice.type = 'in_invoice'
        self.invoice.onchange_partner_id()

        # Deberia tener numero...
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

        # Y el formato XXXX-XXXXXXXX Y solo enteros
        self.invoice.name = 'AAAA-AAAAAAAA'
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

        self.invoice.name = '111178797979'
        with self.assertRaises(ValidationError):
            self.invoice.action_invoice_open()

        self.invoice.name = '3333-33333333'
        self.invoice._validate_supplier_invoice_number()
        assert self.invoice.name == '3333-33333333'

        self.invoice.name = '3223-1'
        self.invoice._validate_supplier_invoice_number()
        assert self.invoice.name == '3223-00000001'

        self.invoice.name = '2-1'
        self.invoice.action_invoice_open()
        assert self.invoice.name == '0002-00000001'

        self.invoice.name = '00001-00000001'
        self.invoice._validate_supplier_invoice_number()

    def test_dupplicate_invoice(self):
        self.invoice.onchange_partner_id()
        new_invoice = self.invoice.copy()
        self.invoice.action_invoice_open()

        # Le restamos en uno la numeracion del talonario para que se vuelva a setiar
        self.document_book.name = str(int(self.document_book.name) - 1)
        with self.assertRaises(ValidationError):
            new_invoice.action_invoice_open()

    def test_document_book(self):
        # Probamos talonario no encontrado
        self.document_book.unlink()
        with self.assertRaises(ValidationError):
            self.invoice.get_document_book()

    def test_name_get(self):
        self.invoice.onchange_partner_id()
        name_get = self.invoice.name_get()[0][1]
        assert name_get == 'FCC A'
        self.invoice.action_invoice_open()
        name_get = self.invoice.name_get()[0][1]
        assert name_get == 'FCC A '+self.invoice.name

    def test_name_get_credit_invoice(self):
        self.invoice.is_credit_invoice = True
        self.invoice.onchange_partner_id()
        name_get = self.invoice.name_get()[0][1]
        assert name_get == 'FCEC A'

    def test_get_full_name(self):
        self.invoice.onchange_partner_id()
        self.invoice.action_invoice_open()
        assert self.invoice.full_name == 'FCC A '+self.invoice.name

    def test_get_document_book_type(self):
        self.invoice.onchange_partner_id()
        assert self.invoice.document_book_type == 'preprint'

    def test_refund(self):
        self.invoice.name = '0001-00000001'
        values = self.invoice._prepare_refund(self.invoice)
        assert values['pos_ar_id'] == self.invoice.pos_ar_id.id
        assert values['denomination_id'] == self.invoice.denomination_id.id
        assert values['origin'] == self.invoice.name_get()[0][1]

    def test_refund_fce(self):
        self.env['document.book'].create({
            'name': '1',
            'pos_ar_id': self.pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice_fce').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
        })
        self.invoice.is_credit_invoice = True
        self.invoice.name = '0001-00000001'
        values = self.invoice._prepare_refund(self.invoice)
        assert values['is_credit_invoice']
        assert values['pos_ar_id'] == self.invoice.pos_ar_id.id
        assert values['denomination_id'] == self.invoice.denomination_id.id
        assert values['origin'] == self.invoice.name_get()[0][1]

    def test_name_get_customer_debit_note(self):
        assert self.debit_note.name_get()[0][1] == 'NDC A'
        # Al validarla deberia darnos la numeracion del talonario
        self.debit_note.action_invoice_open()
        pos_ar_name_get = self.pos.name_get()[0][1]
        document_book_name_get = self.document_book_debit.name_get()[0][1]
        assert self.debit_note.name_get()[0][1] == 'NDC A '+pos_ar_name_get+'-'+document_book_name_get

    def test_name_get_credit_invoice_customer_debit_note(self):
        self.debit_note.is_credit_invoice = True
        assert self.debit_note.name_get()[0][1] == 'NDEC A'

    def test_name_get_supplier_debit_note(self):
        self.debit_note.type = 'in_invoice'
        self.partner_ri.property_account_position_id = self.iva_cf.id
        self.debit_note.onchange_partner_id()
        self.debit_note._onchange_partner_id()
        # El onchange nos deberia dar la denominacion
        assert self.debit_note.name_get()[0][1] == 'NDP C'
        self.debit_note.name = '5-3'
        self.debit_note.action_invoice_open()
        assert self.debit_note.name_get()[0][1] == 'NDP C 0005-00000003'

    def test_name_get_credit_invoice_supplier_debit_note(self):
        self.debit_note.type = 'in_invoice'
        self.debit_note.is_credit_invoice = True
        self.partner_ri.property_account_position_id = self.iva_cf.id
        self.debit_note.onchange_partner_id()
        self.debit_note._onchange_partner_id()
        # El onchange nos deberia dar la denominacion
        assert self.debit_note.name_get()[0][1] == 'NDEP C'
        self.debit_note.name = '5-3'
        self.debit_note.action_invoice_open()
        assert self.debit_note.name_get()[0][1] == 'NDEP C 0005-00000003'

    def test_check_invoice_duplicity(self):
        self.debit_note.onchange_partner_id()
        self.debit_note.check_invoice_duplicity()

    def test_get_document_book_debit_note(self):
        self.debit_note.onchange_partner_id()
        self.debit_note.get_document_book()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
