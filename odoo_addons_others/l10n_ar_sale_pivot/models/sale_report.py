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


class SaleReport(models.Model):
    _inherit = 'sale.report'

    original_price_total = fields.Float('Total en moneda original', readonly=True)
    original_price_subtotal = fields.Float('Total libre de impuestos en moneda original', readonly=True)
    secondary_currency_price_total = fields.Float('Total en moneda secundaria', readonly=True)
    secondary_currency_price_subtotal = fields.Float('Total libre de impuestos en moneda secundaria', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """
        Se agregan totales originales en reporte de ventas
        """

        fields['original_price_total'] = ", sum(l.price_total) as original_price_total"
        fields['original_price_subtotal'] = ", sum(l.price_subtotal) as original_price_subtotal"
        fields['secondary_currency_price_total'] = ", CASE WHEN c.secondary_currency_id is not null " \
                                                "THEN sum(l.price_total * COALESCE(" \
                                                "(SELECT rate " \
                                                "FROM res_currency_rate " \
                                                "WHERE company_id = c.id " \
                                                "AND currency_id = c.secondary_currency_id " \
                                                "AND name <= s.date_order " \
                                                "ORDER BY name desc " \
                                                "LIMIT 1), 1.0) / COALESCE(s.currency_rate, 1)) ELSE 0 END as secondary_currency_price_total"
        fields['secondary_currency_price_subtotal'] = ", CASE WHEN c.secondary_currency_id is not null " \
                                                   "THEN sum(l.price_subtotal * COALESCE(" \
                                                   "(SELECT rate " \
                                                   "FROM res_currency_rate " \
                                                   "WHERE company_id = s.company_id " \
                                                   "AND currency_id = c.secondary_currency_id " \
                                                   "AND name <= s.date_order " \
                                                   "ORDER BY name desc " \
                                                   "LIMIT 1), 1.0) / COALESCE(s.currency_rate, 1)) ELSE 0 END as secondary_currency_price_subtotal"
        from_clause += """left join res_company c on (s.company_id = c.id)"""
        groupby += """, c.id"""
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
