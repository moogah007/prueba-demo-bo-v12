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

from odoo import models

DOMAINS_CODES = [
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Taxes'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'fixed'),
        ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '1'),
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', True),
        ('amount_type', '=', 'fixed'),
        ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '2'),
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '3'),
    ([
        ('amount', '=', 10.50),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '4'),
    ([
        ('amount', '=', 21.00),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '5'),
    ([
        ('amount', '=', 27.00),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
         ('type_tax_use', '=', 'sale'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '6'),
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Taxes'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'fixed'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '1'),
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', True),
        ('amount_type', '=', 'fixed'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '2'),
    ([
        ('amount', '=', 0.0),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '3'),
    ([
        ('amount', '=', 10.50),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '4'),
    ([
        ('amount', '=', 21.00),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '5'),
    ([
        ('amount', '=', 27.00),
        ('tax_group_id', '=', 'Iva'),
        ('is_exempt', '=', False),
        ('amount_type', '=', 'percent'),
        ('type_tax_use', '=', 'purchase'),
        '|',
        ('active', '=', False),
        ('active', '=', True),
    ], '6')
]


class CodesModelsRelations(models.Model):
    _inherit = 'codes.models.relation'

    def get_company_values(self, company):
        res = []
        for tuple in DOMAINS_CODES:
            domain = tuple[0]
            domain.insert(0, ('company_id', '=', company.id))
            tax = self.env['account.tax'].search(domain, limit=1)
            if tax and not self.search_count([('name', '=', 'Afip'), ('name_model', '=', 'account.tax'), ('id_model', '=', tax.id)]):
                res.append({
                    'name': 'Afip',
                    'name_model': 'account.tax',
                    'id_model': tax.id,
                    'code': tuple[1],
                    'company_id': company.id,
                })
        return res

    def create_for_company(self, company):
        self.create(self.get_company_values(company))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
