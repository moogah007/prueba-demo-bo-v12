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


class DocumentBook(models.Model):
    _inherit = 'document.book'

    cai = fields.Char('CAI')
    cai_due_date = fields.Date('Vencimiento CAI')
    cai_max_number = fields.Integer('Número máximo CAI')
    requires_cai = fields.Boolean(string="Requiere CAI", compute='get_requires_cai')

    @api.constrains('cai_max_number')
    def check_cai_max_number(self):
        if any(r.cai_max_number < 0 for r in self):
            raise ValidationError("El número máximo no puede ser negativo")

    @api.onchange('category', 'book_type_id')
    def clear_cai_fields(self):
        self.update({'cai': False, 'cai_due_date': False, 'cai_max_number': False})

    @api.depends('category', 'book_type_id')
    def get_requires_cai(self):
        for r in self:
            r.requires_cai = r.category == 'picking' and r.book_type_id.type == 'selfprint'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
