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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    secondary_currency_id = fields.Many2one(related='company_id.secondary_currency_id')
    secondary_currency_cost = fields.Monetary(string="Costo en moneda secundaria",
        compute='_compute_secondary_currency_cost', inverse='_set_secondary_currency_cost',
        search='_search_secondary_currency_cost',
        help="El costo del producto (excluyendo gastos) expresado en la moneda secundaria definida.")
    update_cost = fields.Boolean(string="Actualizar costo",
        help="Si este casillero se encuentra activado, se actualizará el costo en moneda secundaria al confirmar una compra del producto.")

    @api.depends('product_variant_ids', 'product_variant_ids.secondary_currency_cost')
    def _compute_secondary_currency_cost(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.secondary_currency_cost = template.product_variant_ids.secondary_currency_cost
        for template in (self - unique_variants):
            template.secondary_currency_cost = 0.0

    @api.one
    def _set_secondary_currency_cost(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.secondary_currency_cost = self.secondary_currency_cost

    def _search_secondary_currency_cost(self, operator, value):
        products = self.env['product.product'].search([('secondary_currency_cost', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
