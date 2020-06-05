# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


class TestInvoice(TransactionCase):

    def setUp(self):
        super(TestInvoice, self).setUp()

    def test_domain_jurisdiction(self):
        country_ar = self.env['res.country'].search([('code', '=', 'AR')], limit=1)
        domain = self.env['account.invoice']._get_domain()
        assert domain[0][2] == country_ar.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
