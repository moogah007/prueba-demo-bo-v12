# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class ResCompany(models.Model):

    _inherit = "res.company"

    iibb_number = fields.Char(related='partner_id.iibb_number', string="Numero IIBB", readonly=False)
    start_date = fields.Date(related='partner_id.start_date', string="Fecha Inicio Actividad", readonly=False)
    account_position_id = fields.Many2one('account.fiscal.position', related='partner_id.property_account_position_id', string="Posicion Fiscal", readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
