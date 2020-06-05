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

from odoo import models, fields, api


class PosAr(models.Model):
    _inherit = 'pos.ar'

    invoice_mailing_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Plantilla de envío por mail",
        domain="[('model', '=', 'account.invoice')]",
    )

    @api.multi
    def get_pos_with_mailing_template(self):
        return self.filtered(lambda x: x.invoice_mailing_template_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
