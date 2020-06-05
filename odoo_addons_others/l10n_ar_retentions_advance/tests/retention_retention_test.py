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


class RetentionRetentionTest(TransactionCase):
    # ---
    # AUX
    # ---
    def find_retention(self):
        self.retention = self.env['retention.retention'].search(
            [('type', '=', 'gross_income'), ('type_tax_use', '=', 'purchase')], limit=1)

    # -----
    # SETUP
    # -----
    def setUp(self):
        super(RetentionRetentionTest, self).setUp()
        self.find_retention()

    # -----
    # TESTS
    # -----
    def test_gross_income_purchase_many_lines(self):
        self.retention.retention_rule_ids.unlink()
        self.env['retention.retention.rule'].create({
            'retention_id': self.retention.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        with self.assertRaises(ValidationError):
            self.env['retention.retention.rule'].create({
                'retention_id': self.retention.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_delete_lines_onchange_type_tax_use(self):
        self.env['retention.retention.rule'].create({
            'retention_id': self.retention.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        self.retention.onchange_type_tax_use()
        assert not self.retention.retention_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
