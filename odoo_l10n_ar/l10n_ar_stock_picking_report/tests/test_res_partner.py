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


class TestResPartner(TransactionCase):
    def create_partner(self):
        self.partner = self.env['res.partner'].new({})

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.create_partner()

    def test_get_formatted_vat_cuit(self):
        self.partner.partner_document_type_id = self.env.ref('l10n_ar_afip_tables.partner_document_type_80')
        self.partner.vat = "20123456789"
        assert self.partner.get_formatted_vat() == "20-12345678-9"

    def test_get_formatted_vat_cuil(self):
        self.partner.partner_document_type_id = self.env.ref('l10n_ar_afip_tables.partner_document_type_86')
        self.partner.vat = "20123456789"
        assert self.partner.get_formatted_vat() == "20-12345678-9"

    def test_get_formatted_vat_dni(self):
        self.partner.partner_document_type_id = self.env.ref('l10n_ar_afip_tables.partner_document_type_96')
        self.partner.vat = "12345678"
        assert self.partner.get_formatted_vat() == "12345678"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
