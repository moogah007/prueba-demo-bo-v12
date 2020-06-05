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

from odoo import models


class MrpCostStructure(models.AbstractModel):
    _inherit = 'report.mrp_account.mrp_cost_structure'

    def get_lines(self, productions):
        """ Piso la función para poder agregar los datos de moneda secundaria. """
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        res = []
        # Agrego esta declaración para reutilizar el campo más adelante
        company = self.env.user.company_id
        for product in productions.mapped('product_id'):
            mos = productions.filtered(lambda m: m.product_id == product)
            total_cost = 0.0
            # Defino lo que será el total en moneda secundaria
            total_secondary_currency_cost = 0.0

            operations = []
            Workorders = self.env['mrp.workorder'].search([('production_id', 'in', mos.ids)])
            if Workorders:
                query_str = """SELECT w.operation_id, op.name, partner.name, sum(t.duration), wc.costs_hour
                                FROM mrp_workcenter_productivity t
                                LEFT JOIN mrp_workorder w ON (w.id = t.workorder_id)
                                LEFT JOIN mrp_workcenter wc ON (wc.id = t.workcenter_id )
                                LEFT JOIN res_users u ON (t.user_id = u.id)
                                LEFT JOIN res_partner partner ON (u.partner_id = partner.id)
                                LEFT JOIN mrp_routing_workcenter op ON (w.operation_id = op.id)
                                WHERE t.workorder_id IS NOT NULL AND t.workorder_id IN %s
                                GROUP BY w.operation_id, op.name, partner.name, t.user_id, wc.costs_hour
                                ORDER BY op.name, partner.name
                            """
                self.env.cr.execute(query_str, (tuple(Workorders.ids), ))
                for op_id, op_name, user, duration, cost_hour in self.env.cr.fetchall():
                    operations.append([user, op_id, op_name, duration / 60.0, cost_hour])

            raw_material_moves = []
            # Incluyo la fecha en la query para poder hacer luego la conversión entre monedas
            query_str = """SELECT product_id, bom_line_id, date, SUM(product_qty), abs(SUM(value))
                            FROM stock_move WHERE raw_material_production_id in %s AND state != 'cancel' AND product_qty != 0 AND scrapped != 't'
                            GROUP BY bom_line_id, product_id, date"""
            self.env.cr.execute(query_str, (tuple(mos.ids), ))
            for product_id, bom_line_id, date, qty, cost in self.env.cr.fetchall():
                # Agrego el monto en moneda secundaria
                secondary_currency_cost = company.currency_id._convert(cost, company.secondary_currency_id, company, date)
                raw_material_moves.append({
                    'qty': qty,
                    'cost': cost,
                    'product_id': ProductProduct.browse(product_id),
                    'bom_line_id': bom_line_id,
                    'secondary_currency_cost': secondary_currency_cost, # Agrego el costo en moneda secundaria al diccionario
                })
                total_cost += cost
                # Sumo el costo en moneda secundaria al total correspondiente
                total_secondary_currency_cost += secondary_currency_cost

            scraps = StockMove.search([('production_id', 'in', mos.ids), ('scrapped', '=', True), ('state', '=', 'done')])
            uom = mos and mos[0].product_uom_id
            mo_qty = 0
            if not all(m.product_uom_id.id == uom.id for m in mos):
                uom = product.uom_id
                for m in mos:
                    qty = sum(m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id == product).mapped('product_qty'))
                    if m.product_uom_id.id == uom.id:
                        mo_qty += qty
                    else:
                        mo_qty += m.product_uom_id._compute_quantity(qty, uom)
            else:
                for m in mos:
                    mo_qty += sum(m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id == product).mapped('product_qty'))
            for m in mos:
                sub_product_moves = m.move_finished_ids.filtered(lambda mo: mo.state != 'cancel' and mo.product_id != product)
            res.append({
                'product': product,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'operations': operations,
                'currency': company.currency_id,
                'secondary_currency': company.secondary_currency_id, # Le paso la moneda secundaria al reporte para darle el formato adecuado al monto
                'raw_material_moves': raw_material_moves,
                'total_cost': total_cost,
                'total_secondary_currency_cost': total_secondary_currency_cost, # Le paso el total en moneda secundaria al reporte para mostrarlo
                'scraps': scraps,
                'mocount': len(mos),
                'sub_product_moves': sub_product_moves
            })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
