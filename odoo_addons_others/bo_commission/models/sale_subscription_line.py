# -*- encoding: utf-8 -*-
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


class SaleSubscriptionLine(models.Model):
    _inherit = [
        "sale.subscription.line",
        "sale.commission.mixin",
    ]
    _name = "sale.subscription.line"

    agents = fields.One2many(
        comodel_name="sale.subscription.line.agent",
    )

    @api.model
    def create(self, vals):
        """Agrego, las líneas de agente, al vals de las líneas de suscripción
        para que se autocompleten siempre que se ejecute un create"""
        agents_vals = vals.get('agents', [(6, 0, [])])
        if agents_vals and agents_vals[0][0] == 6 and not agents_vals[0][2]:
            # La relación a la suscripción es mediante el campo analytic_account_id
            aa_id = self.env['sale.subscription'].browse(vals['analytic_account_id'])
            # Tomo el partner de la suscripción
            vals['agents'] = self._prepare_agents_vals_partner(
                aa_id.partner_id,
            )
        return super(SaleSubscriptionLine, self).create(vals)

    def _prepare_agents_vals(self):
        self.ensure_one()
        res = super(SaleSubscriptionLine, self)._prepare_agents_vals()
        return res + self._prepare_agents_vals_partner(
            self.analytic_account_id.partner_id,
        )


class SaleSubscriptionLineAgent(models.Model):
    _inherit = "sale.commission.line.mixin"
    _name = "sale.subscription.line.agent"

    object_id = fields.Many2one(
        comodel_name="sale.subscription.line",
    )

    @api.depends('object_id.price_subtotal')
    def _compute_amount(self):
        for line in self:
            subscription_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission, subscription_line.price_subtotal,
                subscription_line.product_id, subscription_line.quantity,
            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
