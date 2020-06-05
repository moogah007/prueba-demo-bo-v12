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

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """ Agrego este hook para que se seteen globalmente las posiciones al instalar el módulo """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['res.partner'].search([]).set_fiscal_position_globally()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
