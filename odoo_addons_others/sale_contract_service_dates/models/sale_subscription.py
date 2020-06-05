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

from odoo import models
from dateutil.relativedelta import relativedelta


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    def set_service_dates(self, res):
        """ Se setean fechas de servicio en facturas generadas desde suscripciones"""
        self.ensure_one()
        relative_months = 1 if self.template_id.invoice_method == 'expired_month' else 0
        res['date_service_from'] = self.recurring_next_date + relativedelta(day=1) \
                                   - relativedelta(months=relative_months)
        res['date_service_to'] = self.recurring_next_date + relativedelta(months=1 - relative_months) \
                                 + relativedelta(day=1) - relativedelta(days=1)
        return res

    def _prepare_invoice_data(self):
        res = super(SaleSubscription, self)._prepare_invoice_data()
        res = self.set_service_dates(res)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
