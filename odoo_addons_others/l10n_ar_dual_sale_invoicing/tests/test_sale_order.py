# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime


class TestSaleOrder(TransactionCase):
    def create_partner(self):
        self.partner = self.env['res.partner'].create({'name': "Ejemplo"})

    def create_company(self):
        self.company = self.env['res.company'].create({
            'name': "Compañía A",
            'currency_id': self.env.ref('base.ARS').id,
        })
        self.env.ref('base.main_company').parent_id = self.company

    def create_tax(self):
        self.tax = self.env['account.tax'].create({
            'amount': 50,
            'amount_type': 'percent',
            'company_id': self.env.ref('base.main_company').id,
            'name': "Ejemplo IVA Ventas",
            'tax_group_id': self.env.ref('l10n_ar.tax_group_vat').id,
            'type_tax_use': 'sale',
        })

    def create_products(self):
        self.product = self.env['product.product'].create({
            'name': "Ejemplo",
            'type': 'consu',
            'taxes_id': [(6, 0, [self.tax.id])],
        })
        self.advance = self.env['product.product'].create({
            'name': "Anticipo",
            'type': 'service',
            'taxes_id': [(6, 0, [self.tax.id])],
        })

    def create_order(self):
        self.order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'date_order': datetime.today(),
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'product_uom': self.product.uom_id.id,
                'price_unit': 200,
                'qty_to_invoice': 2,
                })
            ],
            'company_id': self.company.id,
        })
        self.order.onchange_partner_id()

    def set_up_invoice(self):
        iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        denomination_a = self.env.ref('l10n_ar_afip_tables.account_denomination_a')
        self.env.user.company_id.partner_id.property_account_position_id = iva_ri
        pos = self.env['pos.ar'].create({'name': 5, 'company_id': self.env.ref('base.main_company').id})
        self.env['document.book'].create({
            'name': 32,
            'pos_ar_id': pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': denomination_a.id,
        })
        self.partner.property_account_position_id = iva_ri

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.create_partner()
        self.create_company()
        self.create_tax()
        self.create_products()
        self.create_order()

    def test_no_invoicing_company(self):
        with self.assertRaises(ValidationError):
            self.order.action_confirm_new()

    def test_invoicing_company(self):
        self.set_up_invoice()
        self.order.invoicing_picking_company_id = self.env.ref('base.main_company')
        self.order.action_confirm_new()
        self.order.action_invoice_create()
        assert self.order.invoice_ids and all(i.company_id == self.env.ref('base.main_company') for i in self.order.invoice_ids)
        assert self.order.invoice_ids.mapped('invoice_line_ids.invoice_line_tax_ids') == self.tax
        assert self.order.invoice_ids.mapped('tax_line_ids.tax_id') == self.tax

    def test_invoicing_company_advance(self):
        self.set_up_invoice()
        self.order.invoicing_picking_company_id = self.env.ref('base.main_company')
        self.order.action_confirm_new()
        wizard = self.env['sale.advance.payment.inv'].create({
            'advance_payment_method': 'fixed',
            'product_id': self.advance.id,
            'amount': 100,
        })
        wizard._create_invoice(self.order, self.order.order_line[0], wizard.amount)
        assert self.order.invoice_ids and all(i.company_id == self.env.ref('base.main_company') for i in self.order.invoice_ids)
        assert self.order.invoice_ids.mapped('invoice_line_ids.invoice_line_tax_ids') == self.tax
        assert self.order.invoice_ids.mapped('tax_line_ids.tax_id') == self.tax

    def test_picking_company(self):
        self.order.invoicing_picking_company_id = self.env.ref('base.main_company')
        self.order.action_confirm_new()
        assert self.order.picking_ids and all(p.company_id == self.env.ref('base.main_company') for p in self.order.picking_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
