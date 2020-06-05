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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    cai = fields.Char("CAI", copy=False)
    cai_due_date = fields.Date("Fecha vencimiento CAI", copy=False)

    def set_picking_number(self, document_book):
        self.ensure_one()
        self.name = document_book.next_number()

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for r in self:
            document_book = r.picking_type_id.get_document_book(r.company_id)
            if document_book:
                r.set_picking_number(document_book)
                if document_book.book_type_id.type == 'selfprint':
                    r.picking_type_id.validate_cai_fields(document_book)
                    r.update({
                        'cai': document_book.cai,
                        'cai_due_date': document_book.cai_due_date,
                    })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
