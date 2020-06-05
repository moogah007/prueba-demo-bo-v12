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

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def set_fiscal_position_globally(self):
        current_company_id = self.env.user.company_id.id
        self = self.sudo()
        proxy = self.env['ir.property']
        source_property = proxy.with_context(force_company=current_company_id)
        values = source_property.get_multi('property_account_position_id', 'res.partner', self.ids)
        for company in self.env['res.company'].search([('id', '!=', current_company_id)]):
            target_property = proxy.with_context(force_company=company.id)
            target_property.set_multi('property_account_position_id', 'res.partner', values)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if res.property_account_position_id:
            res.set_fiscal_position_globally()
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'property_account_position_id' in vals:
            self.set_fiscal_position_globally()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
