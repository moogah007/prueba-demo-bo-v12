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


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.depends('recurring_invoice_line_ids.agents.amount')
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.recurring_invoice_line_ids:
                record.commission_total += sum(x.amount for x in line.agents)

    commission_total = fields.Float(
        string="Total comisiones",
        compute="_compute_commission_total",
        store=True,
    )

    def recompute_lines_agents(self):
        self.mapped('recurring_invoice_line_ids').recompute_agents()

    def _prepare_invoice_line(self, line, fiscal_position):
        """ Se setean a las lineas de la factura el comisionista,
        su comisión y porcentaje de comisión"""
        vals = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)
        vals['agents'] = [
            (0, 0, {'agent': x.agent.id,
                    'commission': x.commission.id,
                    'commission_percentage': x.commission_percentage}) for x in line.agents]
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
