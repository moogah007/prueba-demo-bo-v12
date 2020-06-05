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

from odoo import fields
from odoo.exceptions import ValidationError
from .test_deposit_slip import TestDepositSlip


class TestAccountThirdCheck(TestDepositSlip):

    def test_invalid_third_check_state(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.third_check.deposit_slip_ids = None

    def test_multiple_deposit_slips(self):
        with self.assertRaises(ValidationError):
            self.env['account.deposit.slip'].create({
                'journal_id': self.deposit_slip.journal_id.id,
                'date': fields.Date.context_today(self.env['account.deposit.slip']),
                'check_ids': [(6, 0, [self.third_check.id])]
            })

    def test_invalid_check_state_post(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.deposit_slip.post()

    def test_invalid_check_currency_post(self):
        usd = self.env.ref('base.USD')
        self.third_check.currency_id = usd.id
        third_checks = self.third_check | self.third_check_2
        with self.assertRaises(ValidationError):
            third_checks.post_deposit_slip()

    def test_invalid_check_state_cancel(self):
        self.third_check.state = 'draft'
        with self.assertRaises(ValidationError):
            self.deposit_slip.cancel_deposit_slip()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
