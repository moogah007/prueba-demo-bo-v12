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


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    pos_ar_ids = fields.Many2many('pos.ar', string="Puntos de venta")

    def get_document_book(self, company):
        self.ensure_one()
        pos_ar_id = self.pos_ar_ids.filtered(lambda l: l.company_id == company)
        if not pos_ar_id:
            return False
        pos_ar_id = pos_ar_id[0]
        domain = ([
            ('pos_ar_id', '=', pos_ar_id.id),
            ('category', '=', 'picking'),
        ])
        document_book = self.env['document.book'].search(domain, limit=1)
        if not document_book:
            raise ValidationError(
                'No existe talonario configurado para el punto de venta ' + pos_ar_id.name_get()[0][1]
            )
        return document_book

    def validate_cai_fields(self, document_book):
        self.ensure_one()
        if document_book.book_type_id.type != 'selfprint':
            raise ValidationError("No se puede asignar CAI en base a talonarios no autoimpresores")

        if not document_book.cai:
            raise ValidationError("El talonario no posee CAI")

        if document_book.cai_due_date < fields.Date.today():
            raise ValidationError("El CAI del talonario se encuentra vencido")

        number = int(document_book.name)
        if number >= document_book.cai_max_number:
            raise ValidationError("El número del talonario se encuentra por fuera de los límites definidos en el mismo")

        return True

    @api.onchange('code')
    def onchange_code_clear_pos(self):
        self.pos_ar_ids = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
