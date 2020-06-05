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

from odoo import models, fields


class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    payment_imputation_ids = fields.One2many(
        'register.payment.imputation.line',
        'payment_id',
        'Imputaciones',
    )

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        res['payment_imputation_ids'] = [(0, 0, {
            'invoice_id': imputation.invoice_id.id,
            'move_line_id': imputation.move_line_id.id,
            'difference_account_id': imputation.difference_account_id.id,
            'concile': imputation.concile,
            'amount': imputation.amount,
        }) for imputation in self.payment_imputation_ids]

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
