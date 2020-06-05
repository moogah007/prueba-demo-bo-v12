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

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    secondary_currency_stock_value = fields.Float(string="Valor en moneda secundaria", compute='_compute_stock_value')
    secondary_currency_cost = fields.Float(string="Costo en moneda secundaria", company_dependent=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.remaining_value', 'product_tmpl_id.cost_method', 'product_tmpl_id.standard_price', 'product_tmpl_id.property_valuation', 'product_tmpl_id.categ_id.property_valuation')
    def _compute_stock_value(self):
        """ Piso la función para poder agregar los datos de moneda secundaria. """
        StockMove = self.env['stock.move']
        to_date = self.env.context.get('to_date')
        # Agrego esta declaración para reutilizar el campo más adelante
        company = self.env.user.company_id

        real_time_product_ids = [product.id for product in self if product.product_tmpl_id.valuation == 'real_time']
        if real_time_product_ids:
            self.env['account.move.line'].check_access_rights('read')
            fifo_automated_values = {}
            # Cambio la query para traer las fechas de los apuntes, así más adelante la uso para la conversión
            query = """SELECT aml.product_id, aml.account_id, aml.date, sum(aml.balance), sum(quantity), array_agg(aml.id)
                         FROM account_move_line AS aml
                        WHERE aml.product_id IN %%s AND aml.company_id=%%s %s
                     GROUP BY aml.product_id, aml.account_id, aml.date"""
            params = (tuple(real_time_product_ids), company.id)
            if to_date:
                query = query % ('AND aml.date <= %s',)
                params = params + (to_date,)
            else:
                query = query % ('',)
            self.env.cr.execute(query, params=params)

            res = self.env.cr.fetchall()
            for row in res:
                # La agrupación es por producto y cuenta, pero tengo que sumar los montos convertidos a la moneda
                # secundaria según la fecha de los apuntes
                if not fifo_automated_values.get(row[0], row[1]):
                    fifo_automated_values[(row[0], row[1])] = (0, 0, 0, [])
                fifo_automated_values[(row[0], row[1])][0] += row[3]
                fifo_automated_values[(row[0], row[1])][1] += company.currency_id._convert(
                    row[3], company.secondary_currency_id, company, row[2])
                fifo_automated_values[(row[0], row[1])][2] += row[4]
                fifo_automated_values[(row[0], row[1])][3].extend(list(row[5]))
                fifo_automated_values[(row[0], row[1])] = (row[2], row[3], list(row[4]))

        product_values = {product.id: 0 for product in self}
        # Declaro el diccionario donde se guardarán los valores en moneda secundaria
        product_secondary_currency_values = {product.id: 0 for product in self}
        product_move_ids = {product.id: [] for product in self}

        if to_date:
            domain = [('product_id', 'in', self.ids), ('date', '<=', to_date)] + StockMove._get_all_base_domain()
            value_field_name = 'value'
        else:
            domain = [('product_id', 'in', self.ids)] + StockMove._get_all_base_domain()
            value_field_name = 'remaining_value'

        StockMove.check_access_rights('read')
        query = StockMove._where_calc(domain)
        StockMove._apply_ir_rules(query, 'read')
        from_clause, where_clause, params = query.get_sql()
        # Agrego la fecha del movimiento de stock a la query, así más adelante la uso para la conversión
        query_str = """
            SELECT stock_move.product_id, SUM(COALESCE(stock_move.{}, 0.0)), stock_move.date, ARRAY_AGG(stock_move.id)
            FROM {}
            WHERE {}
            GROUP BY stock_move.product_id, stock_move.date
        """.format(value_field_name, from_clause, where_clause)
        self.env.cr.execute(query_str, params)
        for product_id, value, date, move_ids in self.env.cr.fetchall():
            product_values[product_id] = value
            # Convierto el valor a la moneda secundaria y lo guardo en el diccionario correspondiente
            product_secondary_currency_values[product_id] = company.currency_id._convert(
                value, company.secondary_currency_id, company, date)
            product_move_ids[product_id] = move_ids

        for product in self:
            if product.cost_method in ['standard', 'average']:
                qty_available = product.with_context(company_owned=True, owner_id=False).qty_available
                price_used = product.standard_price
                if to_date:
                    price_used = product.get_history_price(
                        company.id,
                        date=to_date,
                    )
                product.stock_value = price_used * qty_available
                # Convierto el valor a la moneda secundaria según la fecha correspondiente (la fecha para la cual se
                # está calculando la valoración de inventario o la actual)
                product.secondary_currency_stock_value = company.currency_id._convert(
                    product.stock_value, company.secondary_currency_id, company, to_date or fields.Date.today())
                product.qty_at_date = qty_available
            elif product.cost_method == 'fifo':
                if to_date:
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        product.stock_value = product_values[product.id]
                        # Seteo el valor en moneda secundaria según el valor del diccionario
                        product.secondary_currency_stock_value = product_secondary_currency_values[product.id]
                        product.qty_at_date = product.with_context(company_owned=True, owner_id=False).qty_available
                        product.stock_fifo_manual_move_ids = StockMove.browse(product_move_ids[product.id])
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        # Tomo los 4 valores que obtuve a partir de los apuntes
                        value, secondary_currency_value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, 0, [])
                        product.stock_value = value
                        # Seteo el valor en moneda secundaria según el valor recuperado
                        product.secondary_currency_stock_value = secondary_currency_value
                        product.qty_at_date = quantity
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)
                else:
                    product.stock_value = product_values[product.id]
                    # Seteo el valor en moneda secundaria según el valor del diccionario
                    product.secondary_currency_stock_value = product_secondary_currency_values[product.id]
                    product.qty_at_date = product.with_context(company_owned=True, owner_id=False).qty_available
                    if product.product_tmpl_id.valuation == 'manual_periodic':
                        product.stock_fifo_manual_move_ids = StockMove.browse(product_move_ids[product.id])
                    elif product.product_tmpl_id.valuation == 'real_time':
                        valuation_account_id = product.categ_id.property_stock_valuation_account_id.id
                        value, quantity, aml_ids = fifo_automated_values.get((product.id, valuation_account_id)) or (0, 0, [])
                        product.stock_fifo_real_time_aml_ids = self.env['account.move.line'].browse(aml_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
