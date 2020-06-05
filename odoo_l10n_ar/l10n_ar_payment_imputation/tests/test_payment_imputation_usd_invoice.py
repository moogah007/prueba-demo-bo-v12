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

from odoo.addons.l10n_ar_account_payment.tests import set_up
from odoo.exceptions import ValidationError


class TestPaymentImputationUsdInvoice(set_up.SetUp):

    def _create_usd_invoice(self):
        invoice_proxy = self.env['account.invoice']
        invoice_line_proxy = self.env['account.invoice.line']
        product_21_consu = self.env['product.product'].create({
            'name': '21 consu',
            'type': 'consu',
            'taxes_id': [(6, 0, [self.env.ref('l10n_ar.1_vat_21_ventas').id])]
        })
        invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': 'out_invoice',
            'currency_id': self.usd.id,
        })
        invoice.onchange_partner_id()
        invoice_line = invoice_line_proxy.create({
            'name': 'product_21_test',
            'product_id': product_21_consu.id,
            'price_unit': 0,
            'account_id': product_21_consu.categ_id.property_account_income_categ_id.id,
            'invoice_id': invoice.id
        })
        invoice_line._onchange_product_id()
        invoice_line.price_unit = 100
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def _create_imputation(self, invoice, payment):
        return self.env['payment.imputation.line'].create({
            'invoice_id': invoice.id,
            'payment_id': payment.id,
            'move_line_id': invoice.move_id.line_ids.filtered(lambda x: x.account_id == invoice.account_id).id
        })

    def _set_currency_exchange_accounts(self):
        company = self.env.user.company_id
        account_proxy = self.env['account.account']
        company.income_currency_exchange_account_id = account_proxy.search(
            [('code', '=', '504002'), ('company_id', '=', company.id)], limit=1)
        company.expense_currency_exchange_account_id = account_proxy.search(
            [('code', '=', '604002'), ('company_id', '=', company.id)], limit=1)

    def setUp(self):
        super(TestPaymentImputationUsdInvoice, self).setUp()
        self.usd = self.env.ref('base.USD')
        self.env['res.currency.rate'].create({
            'currency_id': self.usd.id,
            'rate': 0.1,
        })
        self.usd_invoice = self._create_usd_invoice()
        self.imputation = self._create_imputation(self.usd_invoice, self.customer_payment)
        self._set_currency_exchange_accounts()

    def test_multicurrency_imputation(self):
        self.usd.need_rate = True
        self.customer_payment.write({
            'pos_ar_id': self.pos_inbound.id,
            'amount': 121,
            'currency_id': self.usd.id,
            'currency_rate': 20,
        })
        self.payment_line.amount = 121
        self.imputation.amount = 121
        self.customer_payment.post_l10n_ar()

        assert self.usd_invoice.state == 'paid'

        move_lines = self.customer_payment.move_line_ids
        assert sum(move_lines.mapped('debit')) == sum(move_lines.mapped('credit')) == 2420
        assert sum(abs(l.amount_currency) for l in move_lines if l.amount_currency > 0) == 121

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
