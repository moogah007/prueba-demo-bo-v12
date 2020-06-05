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

from datetime import timedelta
from openerp.fields import Date
from openerp.tests.common import TransactionCase


class TestPaymentImputationMulti(TransactionCase):

    def clear_rates(self):
        self.env['res.currency.rate'].search([]).unlink()

    def get_currencies(self):
        self.ars = self.env.ref('base.ARS')
        self.usd = self.env.ref('base.USD')

    def create_company(self):
        self.company = self.env['res.company'].search([], limit=1)
        self.company.currency_id = self.ars.id
        self.company.partner_id.property_account_position_id = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')

    def create_pos(self):
        self.pos = self.env['pos.ar'].create({'name': "1", 'company_id': self.company.id})
        den_a = self.env.ref('l10n_ar_afip_tables.account_denomination_a').id
        invoice = self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id
        refund = self.env.ref('l10n_ar_point_of_sale.document_type_refund').id
        preprint_inv = self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id
        inbound = self.env.ref('l10n_ar_point_of_sale.document_type_inbound').id
        outbound = self.env.ref('l10n_ar_point_of_sale.document_type_outbound').id
        preprint_pay = self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_payment').id
        self.pos.document_book_ids = [
            (0,0,{'name':"0",'category':'invoice','denomination_id':den_a,'document_type_id':invoice,'book_type_id':preprint_inv}),
            (0,0,{'name':"0",'category':'invoice','denomination_id':den_a,'document_type_id':refund,'book_type_id':preprint_inv}),
            (0,0,{'name':"0",'category':'payment','document_type_id':inbound,'book_type_id':preprint_pay}),
            (0,0,{'name':"0",'category':'payment','document_type_id':outbound,'book_type_id':preprint_pay}),
        ]

    def get_exchange_journal(self):
        self.exchange_journal = self.company.currency_exchange_journal_id
        self.company.income_currency_exchange_account_id = self.env['account.account'].search([('code', '=', "504002")], limit=1)
        self.company.expense_currency_exchange_account_id = self.env['account.account'].search([('code', '=', "604002")], limit=1)

    def create_partner(self):
        self.partner = self.env['res.partner'].create({
            'name': "Partner",
            'customer': True,
            'supplier': True,
            'company_id': self.company.id,
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari').id,
        })

    def create_journals(self):
        self.journal = self.env['account.journal'].create({
            'name': 'Diario Invoice',
            'type': 'sale',
            'code': 'JINVJ',
            'company_id': self.company.id,
        })
        self.bank_usd = self.env['account.journal'].create({
            'name': 'Diario Bank USD',
            'type': 'bank',
            'code': 'JBUSJ',
            'currency_id': self.usd.id,
            'company_id': self.company.id,
        })
        self.bank_ars = self.env['account.journal'].create({
            'name': 'Diario Bank ARS',
            'type': 'bank',
            'code': 'JBARJ',
            'company_id': self.company.id,
        })
        self.cash_usd = self.env['account.journal'].create({
            'name': 'Diario Cash USD',
            'type': 'cash',
            'code': 'JCUSJ',
            'currency_id': self.usd.id,
            'company_id': self.company.id,
        })
        self.cash_ars = self.env['account.journal'].create({
            'name': 'Diario Cash ARS',
            'type': 'cash',
            'code': 'JCARJ',
            'company_id': self.company.id,
        })
        self.journal.update_posted = True
        self.cash_ars.update_posted = True

    def create_writeoff(self):
        self.writeoff = self.env['account.account'].create({
            'name': "Cuenta writeoff",
            'code': "456789123",
            'user_type_id': self.env.ref('account.data_account_type_other_income').id,
        })

    def create_product(self):
        self.product = self.env['product.product'].create({
            'name': 'Producto',
            'type': 'consu',
            'company_id': self.company.id,
        })

    def create_payment_type(self):
        account = self.env['account.account'].create({
            'name': 'Método de pago',
            'code': 99999,
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
        })
        self.payment_type = self.env['account.payment.type'].create({
            'name': "Método de pago",
            'account_id': account.id,
        })

    def create_invoice(self, inv_type, currency, name=False):
        invoice = self.env['account.invoice'].create({
            'name': name,
            'partner_id': self.partner.id,
            'type': inv_type,
            'currency_id': currency.id,
            'journal_id': self.journal.id,
            'company_id': self.company.id,
            'date_invoice': Date.today() - timedelta(days=7),
            'date': Date.today() - timedelta(days=7),
        })
        invoice._onchange_partner_id()
        return invoice

    def create_invoice_line(self, invoice, price):
        self.env['account.invoice.line'].create({
            'name': 'product_test',
            'price_unit': price,
            'account_id': self.product.categ_id.property_account_income_categ_id.id,
            'invoice_id': invoice.id,
            'currency_id': invoice.currency_id.id,
        })
        invoice._onchange_invoice_line_ids()

    def create_payment(self, payment_type, partner_type, currency, amount, advance_amount, destination=False):
        return self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'journal_id': self.cash_ars.id,
            'payment_type': payment_type,
            'partner_type': partner_type,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'currency_id': currency.id,
            'amount': amount,
            'advance_amount': advance_amount,
            'company_id': self.company.id,
            'payment_date': Date.today(),
            'destination_journal_id': destination.id if destination else False,
            'pos_ar_id': self.pos.id,
            'payment_type_line_ids': [(0, 0, {'account_payment_type_id': self.payment_type.id, 'amount': amount})],
            'state': 'draft',
        })

    def create_imputation(self, invoice, payment, amount, writeoff=False):
        return self.env['payment.imputation.line'].create({
            'invoice_id': invoice.id,
            'move_line_id': invoice.move_id.line_ids.filtered(lambda x: x.account_id == invoice.account_id).id,
            'payment_id': payment.id,
            'payment_currency_id': payment.currency_id.id,
            'payment_date': payment.payment_date,
            'amount': amount,
            'difference_account_id': writeoff.id if writeoff else False,
        })

    def create_currency_rate(self, day_delta, currency, rate):
        self.env['res.currency.rate'].create({
            'name': Date.today() - timedelta(days=day_delta),
            'currency_id': currency.id,
            'rate': rate,
        })

    def get_journal_moves(self, journal):
        return self.env['account.move'].search([('partner_id', '=', self.partner.id), ('journal_id', '=', journal.id)])

    def get_transfer_common_account(self, lines, src, dest):
        src_accounts = lines.filtered(lambda x: x.journal_id == src).mapped('account_id')
        dest_accounts = lines.filtered(lambda x: x.journal_id == dest).mapped('account_id')
        return src_accounts & dest_accounts

    def get_lines_by_account(self, journal, account):
        return self.get_journal_moves(journal).mapped('line_ids').filtered(lambda l: l.account_id == account)

    def get_transfer_move_lines(self, src, payment, common_account):
        return payment.move_line_ids.filtered(lambda x: x.journal_id == src and x.account_id != common_account)

    def setUp(self):
        super(TestPaymentImputationMulti, self).setUp()
        self.clear_rates()
        self.get_currencies()
        self.create_company()
        self.create_pos()
        self.get_exchange_journal()
        self.create_partner()
        self.create_journals()
        self.create_writeoff()
        self.create_product()
        self.create_payment_type()

    def test_factura_proveedor_pesos_pago_pesos(self):
        invoice = self.create_invoice('in_invoice', self.ars, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_pesos_pagos_pesos(self):
        invoice = self.create_invoice('in_invoice', self.ars, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.ars, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('outbound', 'supplier', self.ars, 700, 0)
        self.create_imputation(invoice, payment, 300)
        self.create_imputation(invoice_two, payment, 400)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1100
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_pesos_pagos_pesos_writeoff(self):
        invoice = self.create_invoice('in_invoice', self.ars, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.ars, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('outbound', 'supplier', self.ars, 600, 0)
        self.create_imputation(invoice, payment, 250, self.writeoff)
        self.create_imputation(invoice_two, payment, 350, self.writeoff)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert self.get_lines_by_account(self.cash_ars, self.writeoff).mapped('credit') == [50, 50]
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1100
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_proveedor_pesos_pago_pesos(self):
        refund = self.create_invoice('in_refund', self.ars, "0001-00000001")
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('inbound', 'supplier', self.ars, 500, 0)
        self.create_imputation(refund, payment, 500)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_proveedor_pesos_pagos_pesos(self):
        refund = self.create_invoice('in_refund', self.ars, "0001-00000001")
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('inbound', 'supplier', self.ars, 200, 0)
        self.create_imputation(refund, payment, 200)
        payment.post_l10n_ar()
        assert refund.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 200
        payment = self.create_payment('inbound', 'supplier', self.ars, 300, 0)
        self.create_imputation(refund, payment, 300)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_factura_proveedor_dolares_pago_pesos(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 1000, 0)
        self.create_imputation(invoice, payment, 1000)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert all(l.currency_id == self.usd for l in self.get_journal_moves(self.exchange_journal).mapped('line_ids'))
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 2
        assert sum(abs(l.amount_currency) for l in self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 500
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        assert not self.get_journal_moves(self.cash_ars).mapped('line_ids.currency_id')
        assert not sum(abs(i.amount_currency) for i in self.get_journal_moves(self.cash_ars).mapped('line_ids'))
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_dolares_pagos_pesos(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.usd, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 1500, 0)
        self.create_imputation(invoice, payment, 750)
        self.create_imputation(invoice_two, payment, 750)
        payment.post_l10n_ar()
        assert not self.get_journal_moves(self.exchange_journal)
        assert invoice.residual == 125
        assert invoice_two.residual == 225
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1500
        payment = self.create_payment('outbound', 'supplier', self.ars, 700, 0)
        self.create_imputation(invoice, payment, 250)
        self.create_imputation(invoice_two, payment, 450)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert all(l.currency_id == self.usd for l in self.get_journal_moves(self.exchange_journal).mapped('line_ids'))
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert sum(self.get_lines_by_account(self.exchange_journal, invoice.account_id).mapped('amount_currency')) == 175
        assert sum(self.get_lines_by_account(self.exchange_journal, invoice.account_id).mapped('debit')) == 2200
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert not self.get_journal_moves(self.cash_ars).mapped('line_ids.currency_id')
        assert not sum(abs(i.amount_currency) for i in self.get_journal_moves(self.cash_ars).mapped('line_ids'))
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_dolares_pagos_dolares_writeoff(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.usd, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.usd, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 800
        payment = self.create_payment('outbound', 'supplier', self.usd, 600, 0)
        self.create_imputation(invoice, payment, 250, self.writeoff)
        self.create_imputation(invoice_two, payment, 350, self.writeoff)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert sum(self.get_lines_by_account(self.cash_ars, self.writeoff).mapped('credit')) == 200
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_dolares_pagos_pesos_writeoff(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.usd, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 800, 0)
        self.create_imputation(invoice, payment, 400)
        self.create_imputation(invoice_two, payment, 400)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 800
        payment = self.create_payment('outbound', 'supplier', self.ars, 1200, 0)
        self.create_imputation(invoice, payment, 500, self.writeoff)
        self.create_imputation(invoice_two, payment, 700, self.writeoff)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency')) == 700
        assert sum(self.get_lines_by_account(self.cash_ars, self.writeoff).mapped('credit')) == 200
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_factura_proveedor_dolares_pago_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.usd, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 2
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.exchange_journal).mapped('line_ids.debit')) == 1000
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        assert self.get_journal_moves(self.cash_ars).mapped('line_ids.currency_id') == self.usd
        assert self.get_journal_moves(self.cash_ars).mapped('line_ids').filtered(lambda l: l.debit).mapped('amount_currency')[0] == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_dolares_pagos_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('in_invoice', self.usd, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.usd, "0001-00000002")
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.usd, 500, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 300)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        payment = self.create_payment('outbound', 'supplier', self.usd, 600, 0)
        self.create_imputation(invoice, payment, 300)
        self.create_imputation(invoice_two, payment, 300)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_proveedor_dolares_pagos_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        refund = self.create_invoice('in_refund', self.usd, "0001-00000001")
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('inbound', 'supplier', self.usd, 200, 0)
        self.create_imputation(refund, payment, 200)
        payment.post_l10n_ar()
        assert refund.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('inbound', 'supplier', self.usd, 300, 0)
        self.create_imputation(refund, payment, 300)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert all(l.currency_id == self.usd for l in self.get_journal_moves(self.exchange_journal).mapped('line_ids'))
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 2
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.exchange_journal).mapped('line_ids.debit')) == 1000
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_factura_cliente_pesos_pago_pesos(self):
        invoice = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.ars, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_pesos_pagos_pesos(self):
        invoice = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.ars, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('inbound', 'customer', self.ars, 700, 0)
        self.create_imputation(invoice, payment, 300)
        self.create_imputation(invoice_two, payment, 400)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1100
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_pesos_pagos_pesos_writeoff(self):
        invoice = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.ars, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('inbound', 'customer', self.ars, 600, 0)
        self.create_imputation(invoice, payment, 250, self.writeoff)
        self.create_imputation(invoice_two, payment, 350, self.writeoff)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert self.get_lines_by_account(self.cash_ars, self.writeoff).mapped('debit') == [50, 50]
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1100
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_cliente_pesos_pago_pesos(self):
        refund = self.create_invoice('out_refund', self.ars)
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('outbound', 'customer', self.ars, 500, 0)
        self.create_imputation(refund, payment, 500)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_cliente_pesos_pagos_pesos(self):
        refund = self.create_invoice('out_refund', self.ars)
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('outbound', 'customer', self.ars, 200, 0)
        self.create_imputation(refund, payment, 200)
        payment.post_l10n_ar()
        assert refund.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 200
        payment = self.create_payment('outbound', 'customer', self.ars, 300, 0)
        self.create_imputation(refund, payment, 300)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_dolares_pagos_dolares_writeoff(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.usd, 400, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 200)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 400
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 800
        payment = self.create_payment('inbound', 'customer', self.usd, 600, 0)
        self.create_imputation(invoice, payment, 250, self.writeoff)
        self.create_imputation(invoice_two, payment, 350, self.writeoff)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert sum(self.get_lines_by_account(self.cash_ars, self.writeoff).mapped('debit')) == 200
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_factura_cliente_dolares_pago_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.usd, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 2
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.exchange_journal).mapped('line_ids.debit')) == 1000
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        assert self.get_journal_moves(self.cash_ars).mapped('line_ids.currency_id') == self.usd
        assert self.get_journal_moves(self.cash_ars).mapped('line_ids').filtered(lambda l: l.debit).mapped('amount_currency')[0] == 500
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_dolares_pagos_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice_two, 600)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.usd, 500, 0)
        self.create_imputation(invoice, payment, 200)
        self.create_imputation(invoice_two, payment, 300)
        payment.post_l10n_ar()
        assert invoice.residual == 300
        assert invoice_two.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        payment = self.create_payment('inbound', 'customer', self.usd, 600, 0)
        self.create_imputation(invoice, payment, 300)
        self.create_imputation(invoice_two, payment, 300)
        payment.post_l10n_ar()
        assert invoice.state == 'paid'
        assert invoice_two.state == 'paid'
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 4
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 2200
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_nc_cliente_dolares_pagos_dolares(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        refund = self.create_invoice('out_refund', self.usd)
        self.create_invoice_line(refund, 500)
        refund.action_invoice_open()
        payment = self.create_payment('outbound', 'customer', self.usd, 200, 0)
        self.create_imputation(refund, payment, 200)
        payment.post_l10n_ar()
        assert refund.residual == 300
        assert not self.get_journal_moves(self.exchange_journal)
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 400
        payment = self.create_payment('outbound', 'customer', self.usd, 300, 0)
        self.create_imputation(refund, payment, 300)
        payment.post_l10n_ar()
        assert refund.state == 'paid'
        assert all(l.currency_id == self.usd for l in self.get_journal_moves(self.exchange_journal).mapped('line_ids'))
        assert len(self.get_journal_moves(self.exchange_journal).mapped('line_ids')) == 2
        assert not sum(abs(i) for i in self.get_journal_moves(self.exchange_journal).mapped('line_ids.amount_currency'))
        assert sum(self.get_journal_moves(self.exchange_journal).mapped('line_ids.debit')) == 1000
        assert sum(self.get_journal_moves(self.cash_ars).mapped('amount')) == 1000
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_pesos_pago_pesos_cancelado(self):
        invoice = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.ars)
        self.create_invoice_line(invoice_two, 500)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.ars, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        payment.cancel()
        assert invoice.residual == 500
        assert payment.payment_imputation_ids
        payment.action_draft()
        payment.payment_imputation_ids.unlink()
        self.create_imputation(invoice_two, payment, 500)
        payment.post_l10n_ar()
        assert invoice.residual == 500
        assert invoice_two.state == 'paid'
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_proveedor_pesos_pago_pesos_cancelado(self):
        invoice = self.create_invoice('in_invoice', self.ars, "0001-00000001")
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('in_invoice', self.ars, "0001-00000002")
        self.create_invoice_line(invoice_two, 500)
        invoice_two.action_invoice_open()
        payment = self.create_payment('outbound', 'supplier', self.ars, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        payment.cancel()
        assert invoice.residual == 500
        assert payment.payment_imputation_ids
        payment.action_draft()
        payment.payment_imputation_ids.unlink()
        self.create_imputation(invoice_two, payment, 500)
        payment.post_l10n_ar()
        assert invoice.residual == 500
        assert invoice_two.state == 'paid'
        assert payment.move_line_ids.mapped('full_reconcile_id')

    def test_facturas_cliente_dolares_pago_dolares_cancelado(self):
        self.create_currency_rate(8, self.usd, 0.25)
        self.create_currency_rate(1, self.usd, 0.5)
        invoice = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice, 500)
        invoice.action_invoice_open()
        invoice_two = self.create_invoice('out_invoice', self.usd)
        self.create_invoice_line(invoice_two, 500)
        invoice_two.action_invoice_open()
        payment = self.create_payment('inbound', 'customer', self.usd, 500, 0)
        self.create_imputation(invoice, payment, 500)
        payment.post_l10n_ar()
        payment.cancel()
        assert invoice.residual == 500
        assert payment.payment_imputation_ids
        payment.action_draft()
        payment.payment_imputation_ids.unlink()
        self.create_imputation(invoice_two, payment, 500)
        payment.post_l10n_ar()
        assert invoice.residual == 500
        assert invoice_two.state == 'paid'
        assert payment.move_line_ids.mapped('full_reconcile_id')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
