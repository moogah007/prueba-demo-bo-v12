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

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestPaymentImputationWizard(common.TransactionCase):

    def _create_invoice(self, invoice_type='in_invoice'):
        invoice_proxy = self.env['account.invoice']
        invoice_line_proxy = self.env['account.invoice.line']
        product_21_consu = self.env['product.product'].create({
            'name': '21 consu',
            'type': 'consu',
            'taxes_id': [(6, 0, [self.env.ref('l10n_ar.1_vat_21_compras').id])]
        })
        invoice = invoice_proxy.create({
            'partner_id': self.partner.id,
            'type': invoice_type,
            'name': '0001-00000001'
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
        invoice_line.price_unit = 1000
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def setUp(self):
        super(TestPaymentImputationWizard, self).setUp()

        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri

        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'supplier': True,
            'customer': True,
            'property_account_position_id': self.iva_ri.id,

        })
        self.payment_imputation_wizard = self.env['payment.imputation.wizard'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound'
        })

    def test_onchange_type(self):
        domain = self.payment_imputation_wizard.onchange_type()
        assert domain == {'domain': {'partner_id': [('supplier', '=', True)]}}

    def test_onchange_partner(self):
        self._create_invoice()
        self.payment_imputation_wizard.onchange_partner_id()
        assert len(self.payment_imputation_wizard.debit_imputation_line_ids) == 1
        self.payment_imputation_wizard.payment_type = 'inbound'
        self.payment_imputation_wizard.onchange_partner_id()
        assert not self.payment_imputation_wizard.debit_imputation_line_ids

    def test_onchange_journal(self):
        usd = self.env.ref('base.USD')
        assert self.payment_imputation_wizard.currency_id == self.env.user.company_id.currency_id
        self.payment_imputation_wizard.journal_id.currency_id = usd
        self.payment_imputation_wizard.onchange_journal_id()
        assert self.payment_imputation_wizard.currency_id == usd

    def test_invalid_amount(self):
        self.payment_imputation_wizard.advance_amount = -5
        with self.assertRaises(ValidationError):
            self.payment_imputation_wizard.create_payment()

    def test_credits_higher_than_debits(self):
        imputation = self.env['payment.imputation.wizard'].new({
            'debit_imputation_line_ids': self.env['payment.imputation.debit.line.wizard'].new({
                'amount': 1000,
                'move_line_id': self.env['account.move.line'].new({
                    'account_id': self.env['account.account'].new({})
                }),
            }),
            'credit_imputation_line_ids': self.env['payment.imputation.credit.line.wizard'].new({
                'amount': 1001,
                'move_line_id': self.env['account.move.line'].new({
                    'account_id': self.env['account.account'].new({})
                }),
            }),
            'total': 1
        })
        with self.assertRaises(ValidationError):
            imputation.create_payment()

    def test_not_amount(self):
        with self.assertRaises(ValidationError):
            self.payment_imputation_wizard.create_payment()

    def test_create_payment(self):
        self._create_invoice()
        self.payment_imputation_wizard.onchange_partner_id()
        self.payment_imputation_wizard.debit_imputation_line_ids.write({
            'amount': 500
        })
        self.payment_imputation_wizard.advance_amount = 50
        res = self.payment_imputation_wizard.create_payment()
        payment = self.env['account.payment'].browse(res.get('res_id'))
        assert payment.partner_type == 'supplier'
        assert payment.payment_type == 'outbound'
        assert payment.partner_id == self.partner
        assert payment.amount == 550
        assert payment.advance_amount == 50

    def test_credit_imputation_same_amount(self):
        invoice = self._create_invoice()
        self.payment_imputation_wizard.onchange_partner_id()
        self.payment_imputation_wizard.advance_amount = 1
        self.payment_imputation_wizard.debit_imputation_line_ids.write({
            'amount': 1210
        })

        move = self.env['account.move'].create({
            'journal_id': self.payment_imputation_wizard.journal_id.id,
            'line_ids': [(0, 0,
                {
                    'debit': 1210,
                    'account_id': invoice.account_id.id,
                    'name': 'move',
                    'partner_id': invoice.partner_id.id
                }),
                 (0, 0, {
                    'credit': 1210,
                    'account_id': invoice.invoice_line_ids[0].account_id.id,
                    'name': 'move'
                })
            ]
        })

        self.payment_imputation_wizard.credit_imputation_line_ids.create({
            'move_line_id': move.line_ids[1].id,
            'amount': 1210,
            'payment_id': self.payment_imputation_wizard.id
        })

        res = self.payment_imputation_wizard.create_payment()
        payment = self.env['account.payment'].browse(res.get('res_id'))
        assert not payment.payment_imputation_ids
        assert invoice.state == 'paid'

    def test_credit_imputation_with_remaining_in_invoice(self):
        invoice = self._create_invoice()
        self.payment_imputation_wizard.onchange_partner_id()
        self.payment_imputation_wizard.advance_amount = 1
        self.payment_imputation_wizard.debit_imputation_line_ids.write({
            'amount': 1210
        })

        move = self.env['account.move'].create({
            'journal_id': self.payment_imputation_wizard.journal_id.id,
            'line_ids': [(0, 0,
                {
                    'debit': 1210,
                    'account_id': invoice.account_id.id,
                    'name': 'move',
                    'partner_id': invoice.partner_id.id
                }),
                 (0, 0, {
                    'credit': 1210,
                    'account_id': invoice.invoice_line_ids[0].account_id.id,
                    'name': 'move'
                })
            ]
        })

        self.payment_imputation_wizard.credit_imputation_line_ids.create({
            'move_line_id': move.line_ids[1].id,
            'amount': 1000,
            'payment_id': self.payment_imputation_wizard.id
        })

        res = self.payment_imputation_wizard.create_payment()
        payment = self.env['account.payment'].browse(res.get('res_id'))
        assert payment.payment_imputation_ids
        assert invoice.state == 'open'
        assert invoice.residual == 210

    def test_multicurrency_imputation_rate_in_payment(self):
        company = self.env.user.company_id
        account_proxy = self.env['account.account']
        company.income_currency_exchange_account_id = account_proxy.search(
            [('code', '=', '504002'), ('company_id', '=', company.id)], limit=1)
        company.expense_currency_exchange_account_id = account_proxy.search(
            [('code', '=', '604002'), ('company_id', '=', company.id)], limit=1)

        pos = self.env['pos.ar'].create({
            'name': '1'
        })
        self.env['document.book'].with_context(default_payment_type='inbound').create({
            'name': '1',
            'category': 'payment',
            'pos_ar_id': pos.id,
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_payment').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_inbound').id
        })
        self.env['document.book'].create({
            'name': '1',
            'category': 'invoice',
            'pos_ar_id': pos.id,
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id
        })

        invoice = self._create_invoice('out_invoice')
        self.payment_imputation_wizard.payment_type = 'inbound'
        self.payment_imputation_wizard.onchange_partner_id()
        self.payment_imputation_wizard.debit_imputation_line_ids.write({
            'amount': 43.21,
        })

        usd = self.env.ref('base.USD')
        usd.need_rate = True
        self.payment_imputation_wizard.journal_id.currency_id = usd
        self.payment_imputation_wizard.onchange_journal_id()
        self.payment_imputation_wizard.write({
            'amount': 43.21,
            'currency_rate': 28,
        })
        res = self.payment_imputation_wizard.create_payment()
        payment = self.env['account.payment'].browse(res.get('res_id'))
        payment.update({
            'pos_ar_id': pos.id,
            'payment_type_line_ids': [(0, 0, {
                'amount': 43.21,
                'account_payment_type_id': self.env['account.payment.type'].create({
                    'name': 'Transferencia',
                    'account_id': self.env.ref('l10n_ar.1_banco_cuenta_en_pesos').id,
                    'currency_id': usd.id,
                }).id,
            })]
        })
        payment.post_l10n_ar()

        assert not invoice.residual

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
