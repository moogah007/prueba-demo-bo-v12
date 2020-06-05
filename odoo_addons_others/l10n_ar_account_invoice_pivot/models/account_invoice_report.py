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


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    original_amount_total = fields.Float('Total en moneda original', readonly=True)
    original_amount_subtotal = fields.Float('Total libre de impuestos en moneda original', readonly=True)
    secondary_currency_amount_total = fields.Float('Total en moneda secundaria', readonly=True)
    secondary_currency_subtotal = fields.Float('Total libre de impuestos en moneda secundaria', readonly=True)

    def _from(self):
        return super(AccountInvoiceReport, self)._from() + " JOIN res_company rc on (ai.company_id=rc.id)"

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.invoice_amount_untaxed as original_amount_subtotal" \
                                                             ", sub.amount_total as original_amount_total " \
                                                             ", sub.secondary_currency_amount_untaxed / COALESCE(cr.rate, 1) as secondary_currency_subtotal" \
                                                             ", sub.secondary_currency_amount_total / COALESCE(cr.rate, 1) as secondary_currency_amount_total"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ai.amount_untaxed as invoice_amount_untaxed " \
                                                                 ", CASE WHEN rc.secondary_currency_id is not null THEN ai.amount_untaxed * COALESCE(" \
                                                                 "(SELECT rate FROM res_currency_rate WHERE company_id = rc.id AND currency_id = rc.secondary_currency_id AND name <= ai.date_invoice ORDER BY name desc LIMIT 1), 1.0) ELSE 0 END as secondary_currency_amount_untaxed " \
                                                                 ", CASE WHEN rc.secondary_currency_id is not null THEN ai.amount_total * COALESCE(" \
                                                                 "(SELECT rate FROM res_currency_rate WHERE company_id = rc.id AND currency_id = rc.secondary_currency_id AND name <= ai.date_invoice ORDER BY name desc LIMIT 1), 1.0) ELSE 0 END as secondary_currency_amount_total " \

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", rc.id"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
