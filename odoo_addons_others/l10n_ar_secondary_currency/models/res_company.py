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


class ResCompany(models.Model):
    _inherit = 'res.company'

    secondary_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda secundaria',
        copy=False
    )

    @api.constrains('currency_id', 'secondary_currency_id')
    def check_currencies(self):
        """ Chequeo de monedas """
        for company in self.filtered(lambda x: x.currency_id and x.secondary_currency_id):
            if company.currency_id == company.secondary_currency_id:
                raise ValidationError('La moneda secundaria tiene que ser distinta a la moneda principal')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
