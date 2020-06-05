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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleCommissionLineMixin(models.AbstractModel):
    _inherit = "sale.commission.line.mixin"

    commission_percentage = fields.Float(string="Porcentaje de comisión")

    # Campo computado para usar en dominio de vista
    commission_type = fields.Selection(related="commission.commission_type")

    @api.constrains('commission_percentage')
    def check_commission_percentage_range(self):
        if any(l.commission_percentage < 0 or l.commission_percentage > 100 for l in self):
            raise ValidationError("El porcentaje de comisión debe estar comprendido entre 0 y 100.")

    @api.onchange('commission')
    def onchange_commission_set_percentage(self):
        self.ensure_one()
        if self.commission and self.commission.commission_type == 'fixed':
            self.commission_percentage = self.commission.fix_qty

    def _get_commission_amount(self, commission, subtotal, product, quantity):
        """Redefino el cálculo de la comisión (en caso de ser de tipo fijo)
        para que tome el valor de la línea"""
        self.ensure_one()
        if product.commission_free or not commission:
            return 0.0
        if commission.amount_base_type == 'net_amount':
            # Si el subtotal (sale_price * quantity) es menor a
            # standard_price * quantity, significa que el costo del producto fue
            # mayor a lo obtenido en la venta, entonces se setea amount_base a 0
            subtotal = max([
                0, subtotal - product.standard_price * quantity,
            ])
        if commission.commission_type == 'fixed':
            # La función original hacía
            # return subtotal * (commission.fix_qty / 100.0)
            # Se modificó para que lo tome de la línea del comisionista
            # y no del tipo de comisión
            return subtotal * (self.commission_percentage / 100.0)
        elif commission.commission_type == 'section':
            return commission.calculate_section(subtotal)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
