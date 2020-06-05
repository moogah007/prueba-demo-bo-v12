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

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestStockPicking(TransactionCase):
    def create_pos_ar(self):
        self.pos_ar = self.env['pos.ar'].create({
            'name': "1",
            'prefix_quantity': 4,
        })

    def create_document_book(self):
        self.document_book = self.env['document.book'].create({
            'pos_ar_id': self.pos_ar.id,
            'category': 'picking',
            'book_type_id': self.env.ref('l10n_ar_stock.document_book_type_selfprint_picking').id,
            'name': 5,
            'cai': "12345678",
            'cai_due_date': date.today(),
            'cai_max_number': 100,
        })

    def create_picking_type(self):
        self.picking_type = self.env['stock.picking.type'].new({})
        self.picking_type.code = 'outgoing'
        self.picking_type.pos_ar_ids = [(6, 0, [self.pos_ar.id])]

    def create_picking(self):
        self.picking = self.env['stock.picking'].new({})
        self.picking.picking_type_id = self.picking_type

    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.create_pos_ar()
        self.create_document_book()
        self.create_picking_type()
        self.create_picking()

    def test_set_picking_number(self):
        self.picking.set_picking_number(self.document_book)
        assert self.picking.name == "0001-00000006"

    def test_action_done_same_company(self):
        self.picking.company_id = self.document_book.company_id
        self.picking.action_done()
        assert self.picking.cai
        assert self.picking.cai_due_date

    def test_action_done_different_company(self):
        self.picking.action_done()
        assert not self.picking.cai
        assert not self.picking.cai_due_date

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
