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

from odoo import models, api


class SaleCommissionMixin(models.AbstractModel):
    _inherit = 'sale.commission.mixin'

    @api.model
    def _prepare_agents_vals_partner(self, partner):
        """Vuelvo a calcular los valores de las líneas de agentes
        para agregar el porcentaje de comisión"""
        rec = super(SaleCommissionMixin, self)._prepare_agents_vals_partner(partner)
        for agent in partner.agents:
            for agent_line in rec:
                # agent_line es una tupla de la forma (0,0,{}) para usar en un many2many
                # en el diccionario se encuentran los valores de las líneas
                if agent.id == agent_line[2].get('agent'):
                    commission = agent.commission
                    agent_line[2]['commission_percentage'] = commission.fix_qty if commission.commission_type == 'fixed' else 0.0
                    continue
        return rec

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
