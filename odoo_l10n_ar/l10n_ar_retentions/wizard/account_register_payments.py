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


class AccountRegisterPaymnets(models.TransientModel):

    _inherit = 'account.register.payments'

    retention_ids = fields.Many2many(
        'account.payment.retention',
        'register_payment_retention_rel',
        'payment_id',
        'retention_id',
        'Retenciones'
    )

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPaymnets, self)._prepare_payment_vals(invoices)
        res['retention_ids'] = [(4, retention) for retention in self.retention_ids.ids]

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
