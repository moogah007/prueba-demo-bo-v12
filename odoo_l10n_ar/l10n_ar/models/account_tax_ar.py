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

from odoo import models, fields


class AccountTaxAr(models.AbstractModel):
    _name = 'account.tax.ar'
    _description = 'Impuesto de argentina'

    def _get_country_ar(self):
        return [('country_id', '=', self.env.ref('base.ar').id)]

    name = fields.Char(string='Nombre', required=True)
    tax_id = fields.Many2one('account.tax', string='Impuesto', required=True)
    type = fields.Selection(
        [
            ('vat', 'Iva'),
            ('gross_income', 'Ingresos brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro')
        ],
        string='Tipo',
        required=True,
        default='gross_income'
    )
    type_tax_use = fields.Selection(
        [('sale', 'Sales'),
         ('purchase', 'Purchases'),
         ('none', 'None')],
        related='tax_id.type_tax_use'
    )
    jurisdiction = fields.Selection(
        [
            ('nacional', 'Nacional'),
            ('provincial', 'Provincial'),
            ('municipal', 'Municipal')
        ],
        string='Jurisdiccion',
        required=True,
        default='nacional'
    )
    state_id = fields.Many2one('res.country.state', string="Provincia", domain=_get_country_ar)
    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
