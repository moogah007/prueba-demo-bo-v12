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

    # Cheques recibidos
    account_third_check_ids = fields.Many2many(
        'account.third.check',
        'third_check_wizard_payment_rel',
        'source_payment_id',
        'third_check_id',
        'Cheques de terceros recibidos'
    )
    # Cheques entregados
    account_third_check_sent_ids = fields.Many2many(
        'account.third.check',
        'sent_third_check_wizard_payment_rel',
        'destination_payment_id',
        'third_check_id',
        'Cheques de terceros entregados'
    )
    account_own_check_line_ids = fields.Many2many(
        'account.own.check.line',
        'own_check_wizard_payment_rel',
        'payment_id',
        'own_check_id',
        'Cheques propios'
    )

    def _prepare_payment_vals(self, invoices):

        res = super(AccountRegisterPaymnets, self)._prepare_payment_vals(invoices)

        res['account_third_check_ids'] = [(4, third_check) for third_check in self.account_third_check_ids.ids]
        res['account_third_check_sent_ids'] = [(4, sent_check) for sent_check in self.account_third_check_sent_ids.ids]
        res['account_own_check_line_ids'] = [(4, own_check) for own_check in self.account_own_check_line_ids.ids]

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
