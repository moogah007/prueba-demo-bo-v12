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

from odoo import models, _


class AccountTax(models.Model):

    _inherit = 'account.tax'

    def get_tax_description(self):
        # EJ: IVA 21.0%
        if self.tax_group_id == self.env.ref('l10n_ar.tax_group_vat'):
            res = _('VAT ') + str(self.amount) + '%'
        elif self.tax_group_id == self.env.ref('l10n_ar.tax_group_internal'):
            res = _('INTERNAL TAX ') + self.description or ''
        else:
            res = self.description
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
