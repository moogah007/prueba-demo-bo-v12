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
from collections import defaultdict


class SaleCommissionSettlement(models.Model):
    _inherit = "sale.commission.settlement"

    @api.multi
    def action_view_settlement_lines(self):
        """Acción para ver las líneas de la liquidación agrupadas por factura"""
        settlement_lines_ids = self.mapped('lines')
        action = self.env.ref('bo_commission_group_by_invoice.action_settlement_commission_line').read()[0]
        action['domain'] = [('id', 'in', settlement_lines_ids.ids)]
        return action

    def lines_groupby_invoice(self):
        """ Genero un diccionario para agrupar la liquidacion por factura"""
        self.ensure_one()
        amount_by_invoice = defaultdict(float)
        # Agrupo las lineas por factura y calculo el total liquidado por factura
        for line in self.lines:
            amount_by_invoice[line.invoice] += line.settled_amount
        return amount_by_invoice

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
