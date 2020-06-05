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


class AccountTaxTemplate(models.Model):

    _inherit = 'account.tax.template'

    is_exempt = fields.Boolean('Es exento?')
    
    def _get_tax_vals(self, company, tax_template):
        val = super(AccountTaxTemplate, self)._get_tax_vals(company, tax_template)
        val['is_exempt'] = self.is_exempt
    
        return val

    def set_ar_as_default_country(self):
        country_ar = self.env.ref('base.ar')
        self.env['ir.values'].sudo().set(
            'res.partner', 'country_id', country_ar.id, company_id=self.company_id.id
        )
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('PUTO')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
