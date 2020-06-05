# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    secondary_currency_id = fields.Many2one(related='company_id.secondary_currency_id')
    secondary_currency_value = fields.Float(string="Valor en moneda secundaria", compute='get_secondary_currency_value')

    def get_secondary_currency_value(self):
        for r in self:
            moves = r.env['stock.move.line'].search([('product_id', '=', r.product_id.id),
                ('location_dest_id', '=', r.location_id.id), ('lot_id', '=', r.lot_id.id), '|',
                ('package_id', '=', r.package_id.id), ('result_package_id', '=', r.package_id.id)]).mapped('move_id')
            r.secondary_currency_value = sum(m.company_id.currency_id._convert(
                m.remaining_value, m.company_id.secondary_currency_id, m.company_id, m.date) for m in moves)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
