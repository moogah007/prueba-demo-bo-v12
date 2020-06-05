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


class TestStockPickingType(TransactionCase):
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
        self.picking_type.pos_ar_ids = [(6, 0, [self.pos_ar.id])]

    def setUp(self):
        super(TestStockPickingType, self).setUp()
        self.create_pos_ar()
        self.create_document_book()
        self.create_picking_type()

    def test_onchange_picking_type(self):
        self.picking_type.onchange_code_clear_pos()
        assert not self.picking_type.pos_ar_ids

    def test_validate_cai_fields_ok(self):
        assert self.picking_type.validate_cai_fields(self.document_book)

    def test_validate_cai_fields_not_selfprint(self):
        self.document_book.book_type_id = self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_picking')
        with self.assertRaises(ValidationError):
            self.picking_type.validate_cai_fields(self.document_book)

    def test_validate_cai_fields_no_cai(self):
        self.document_book.cai = False
        with self.assertRaises(ValidationError):
            self.picking_type.validate_cai_fields(self.document_book)

    def test_validate_cai_fields_expired_cai(self):
        self.document_book.cai_due_date = '2019-01-01'
        with self.assertRaises(ValidationError):
            self.picking_type.validate_cai_fields(self.document_book)

    def test_validate_cai_fields_invalid_cai_max_number(self):
        self.document_book.cai_max_number = 4
        with self.assertRaises(ValidationError):
            self.picking_type.validate_cai_fields(self.document_book)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
