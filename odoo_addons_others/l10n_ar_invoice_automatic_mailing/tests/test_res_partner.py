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


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.first_partner_name = "Partner sin mail 1"
        self.second_partner_name = "Partner sin mail 2"
        self.partner_with_email = self.env['res.partner'].new({'name': "Partner con mail", 'email': "a@b.com"})
        self.partner_without_email_one = self.env['res.partner'].new({'name': self.first_partner_name})
        self.partner_without_email_two = self.env['res.partner'].new({'name': self.second_partner_name})

    def test_one_with_mail(self):
        partners_to_test = self.partner_with_email
        res = partners_to_test.get_partners_without_email()
        assert not res

    def test_one_with_mail_one_without(self):
        partners_to_test = self.partner_with_email | self.partner_without_email_one
        res = partners_to_test.get_partners_without_email()
        assert len(res) == 1
        assert self.first_partner_name in res

    def test_one_without_mail(self):
        partners_to_test = self.partner_without_email_one
        res = partners_to_test.get_partners_without_email()
        assert len(res) == 1
        assert self.first_partner_name in res

    def test_two_without_mail(self):
        partners_to_test = self.partner_without_email_one | self.partner_without_email_two
        res = partners_to_test.get_partners_without_email()
        assert len(res) == 2
        assert self.first_partner_name in res
        assert self.second_partner_name in res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
