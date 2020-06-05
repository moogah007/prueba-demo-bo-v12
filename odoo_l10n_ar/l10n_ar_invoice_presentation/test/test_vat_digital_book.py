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


class UnitTest(TransactionCase):

    def setUp(self):
        super(UnitTest, self).setUp()
        self.vat_digital_book_proxy = self.env['account.invoice.vat.digital.book']

    # VAT DIGITAL BOOK
    def test_vat_digital_book_can_create_a_presentation(self):
        """Se puede crear un libro IVA digital"""
        self.vat_digital_book_proxy.create({
            'name': 'TEST',
            'date_from': '2017-08-01',
            'date_to': '2017-08-31',
            'sequence': '00',
            'with_prorate': True
        })

    def test_vat_digital_book_cannot_create_a_presentation_with_bad_dates(self):
        """No se puede generar un libro IVA digital con las fechas mal"""
        with self.assertRaises(Exception):
            self.vat_digital_book_proxy.create({
                'name': 'TEST',
                'date_from': '2017-08-31',
                'date_to': '2017-08-01',
                'sequence': '00',
                'with_prorate': True
            })

    def test_vat_digital_book_can_generate_presentations(self):
        """Se pueden generar las presentaciones"""
        self.env.user.company_id.partner_id.country_id = self.env.ref('base.ar')
        self.env.user.company_id.partner_id.vat = "20359891033"
        presentation = self.vat_digital_book_proxy.create({
            'name': 'TEST',
            'date_from': '2017-08-01',
            'date_to': '2017-08-31',
            'sequence': '00',
        })
        presentation.generate_files()

    def test_vat_digital_book_validate_invoices_raises_warning(self):
        """El metodo de validar facturas arroja Warning"""
        self.env.user.company_id.partner_id.country_id = self.env.ref('base.ar')
        self.env.user.company_id.partner_id.vat = "20359891033"
        presentation = self.vat_digital_book_proxy.create({
            'name': 'TEST',
            'date_from': '2017-08-01',
            'date_to': '2017-08-31',
            'sequence': '00',
        })
        invoices = [self.env['account.invoice'].new({'name': 0o00033333333})]
        with self.assertRaises(Exception):
            presentation.validate_invoices(invoices)

    def test_vat_digital_book_generates_period(self):
        """El metodo de generar periodo genera el periodo esperado"""
        presentation = self.vat_digital_book_proxy.create({
            'name': 'TEST',
            'date_from': '2017-08-01',
            'date_to': '2017-08-31',
            'sequence': '00',
        })
        assert presentation.get_period() == '201708'


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
