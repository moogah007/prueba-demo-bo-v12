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


class TestAccountRegisterPayments(set_up.SetUp):

    def setUp(self):
        super(TestAccountRegisterPayments, self).setUp()
        self.move_line = self.invoice.move_id.line_ids.filtered(lambda x: x.account_id == self.invoice.account_id)
        self.imputation = self.env['register.payment.imputation.line'].create({
            'invoice_id': self.invoice.id,
            'move_line_id': self.move_line.id,
        })
        self.payment_wizard = self.env['account.register.payments']. \
            with_context(active_ids=self.invoice.id, active_model='account.invoice').create({
                'partner_id': self.partner.id,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'amount': 500,
                'payment_type_line_ids': [(6, 0, [self.payment_line.id])],
                'payment_imputation_ids': [(6, 0, [self.imputation.id])]
            })

    def test_get_payment_vals(self):
        res = self.payment_wizard._prepare_payment_vals(self.env['account.invoice'].new({'type': 'out_invoice'}))
        assert res.get('payment_imputation_ids') == [(0, 0, {
            'invoice_id': self.invoice.id,
            'move_line_id': self.move_line.id,
            'difference_account_id': False,
            'concile': False,
            'amount': 0,
        })]

    def test_onchange_partner(self):
        self.payment_wizard.payment_imputation_ids = None
        self.payment_wizard.onchange_partner_imputation()
        assert len(self.payment_wizard.payment_imputation_ids) == 1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
