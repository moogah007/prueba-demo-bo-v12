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

from odoo import models, api


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        if self.env.context.get('fixed_payment_currency_rate'):
            rate = self.env.context['fixed_payment_currency_rate']
            curr = self.env.context['fixed_rate_currency']
            user_curr = company.currency_id
            if from_currency == curr and to_currency == user_curr:
                return rate
            if from_currency == user_curr and to_currency == curr:
                return 1.0 / rate
        return super(ResCurrency, self)._get_conversion_rate(from_currency, to_currency, company, date)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
