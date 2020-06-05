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

from odoo import models, api, fields


class AccountRegisterPayments(models.TransientModel):

    _inherit = 'account.register.payments'

    payment_type_line_ids = fields.Many2many(
        'account.payment.type.line',
        'register_payment_payment_line_rel',
        'payment_id',
        'line_id',
        'Lineas de pagos'
    )

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        res.update({
            'pos_ar_id': self.pos_ar_id.id,
            'payment_type_line_ids': [(4, payment) for payment in self.payment_type_line_ids.ids],
        })
        return res

    @api.multi
    def create_payment_l10n_ar(self):
        payments = self.env['account.payment']
        for payment_vals in self.get_payments_vals():
            payments += self.env['account.payment'].create(payment_vals)
        payments.post_l10n_ar()
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
