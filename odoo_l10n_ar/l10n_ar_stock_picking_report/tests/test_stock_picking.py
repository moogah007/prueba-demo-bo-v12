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


class TestStockPicking(TransactionCase):
    def create_company(self):
        self.company = self.env['res.company'].new({})
        self.company.start_date = '2019-01-01'
        self.company.iibb_number = "123456"
        self.company.street = "Calle Falsa 123"
        self.company.city = "Springfield"

    def create_picking(self):
        self.picking = self.env['stock.picking'].new({})
        self.picking.cai = "12345678"
        self.picking.state = 'done'
        self.picking.company_id = self.company

    def setUp(self):
        super(TestStockPicking, self).setUp()
        self.create_company()
        self.create_picking()

    def test_validate_selfprint_ok(self):
        assert self.picking.validate_selfprint_fields()

    def test_validate_selfprint_no_start_date(self):
        self.company.start_date = False
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

    def test_validate_selfprint_no_iibb_number(self):
        self.company.iibb_number = False
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

    def test_validate_selfprint_no_street(self):
        self.company.street = False
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

    def test_validate_selfprint_no_city(self):
        self.company.city = False
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

    def test_validate_selfprint_no_cai(self):
        self.picking.cai = False
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

    def test_validate_selfprint_not_done(self):
        self.picking.state = 'draft'
        with self.assertRaises(ValidationError):
            self.picking.validate_selfprint_fields()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
