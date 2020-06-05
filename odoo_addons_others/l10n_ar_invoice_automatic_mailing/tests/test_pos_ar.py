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


class TestPosAr(TransactionCase):

    def setUp(self):
        super(TestPosAr, self).setUp()
        template = self.env['mail.template'].new({})
        self.pos_with_template = self.env['pos.ar'].new({'name': "0001", 'invoice_mailing_template_id': template})
        self.pos_without_template_one = self.env['pos.ar'].new({'name': '0003'})
        self.pos_without_template_two = self.env['pos.ar'].new({'name': '0002'})

    def test_one_with_mail(self):
        res = self.pos_with_template.get_pos_with_mailing_template()
        assert res

    def test_one_with_mail_one_without(self):
        pos_to_test = self.pos_with_template | self.pos_without_template_one
        res = pos_to_test.get_pos_with_mailing_template()
        assert len(res) == 1
        assert self.pos_with_template in res

    def test_two_without_mail(self):
        pos_to_test = self.pos_without_template_one | self.pos_without_template_two
        res = pos_to_test.get_pos_with_mailing_template()
        assert len(res) == 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
