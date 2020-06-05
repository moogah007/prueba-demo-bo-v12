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


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        template = self.env['mail.template'].new({})
        pos_with_template = self.env['pos.ar'].new({'name': '990', 'invoice_mailing_template_id': template})
        pos_without_template = self.env['pos.ar'].new({'name': '991'})
        self.invoice_with_template = self.env['account.invoice'].new({'pos_ar_id': pos_with_template})
        self.invoice_without_template = self.env['account.invoice'].new({'pos_ar_id': pos_without_template})

    def test_get_invoices(self):
        self.invoice_with_template.type = 'out_invoice'
        invoices_to_test = self.invoice_with_template | self.invoice_without_template
        invoices_to_mail = invoices_to_test.get_invoices_with_pos()
        assert len(invoices_to_mail) == 1
        assert self.invoice_with_template in invoices_to_mail

    def test_filter_to_send_out_open(self):
        self.invoice_with_template.type = 'out_invoice'
        self.invoice_with_template.state = 'open'
        assert len(self.invoice_with_template.filter_invoices_to_validate_and_send()) == 0

    def test_filter_to_send_out_draft(self):
        self.invoice_with_template.type = 'out_invoice'
        self.invoice_with_template.state = 'draft'
        assert len(self.invoice_with_template.filter_invoices_to_validate_and_send()) == 1

    def test_filter_to_send_refund_open(self):
        self.invoice_with_template.type = 'out_refund'
        self.invoice_with_template.state = 'open'
        assert not self.invoice_with_template.filter_invoices_to_validate_and_send()

    def test_filter_to_send_refund_open(self):
        self.invoice_with_template.type = 'out_refund'
        self.invoice_with_template.state = 'draft'
        assert not self.invoice_with_template.filter_invoices_to_validate_and_send()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
