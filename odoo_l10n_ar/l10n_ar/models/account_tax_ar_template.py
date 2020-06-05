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


class AccountTaxArTemplate(models.AbstractModel):

    _name = 'account.tax.ar.template'
    _description = 'Template de impuesto de Argentina'

    name = fields.Char('Nombre', required=True)
    tax_template_id = fields.Many2one('account.tax.template', string='Impuesto', required=True)
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
    jurisdiction = fields.Selection(
        [
            ('nacional', 'Nacional'),
            ('provincial', 'Provincial'),
            ('municipal', 'Municipal')
        ],
        string='Jurisdiccion',
        default='nacional',
        required=True
    )
    state_id = fields.Many2one('res.country.state', string="Provincia")
    chart_template_id = fields.Many2one('account.chart.template', 'Template', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
