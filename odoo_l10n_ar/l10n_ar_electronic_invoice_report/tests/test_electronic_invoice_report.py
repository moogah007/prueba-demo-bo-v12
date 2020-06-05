# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pytest
from odoo.addons.l10n_ar_afip_webservices_wsfe.tests import set_up
from odoo.exceptions import ValidationError


class TestElectronicInvoiceReport(set_up.SetUp):

    def setUp(self):
        super(TestElectronicInvoiceReport, self).setUp()
        company = self.env.user.company_id
        company.write({
            'street': 'street',
            'city': 'Ciudad'
        })
        company.partner_id.write({
            'start_date': '1900-01-01',
            'iibb_number': '123151'
        })

        self.invoice.cae = '67334641922335'
        self.refund.cae = '67304121890252'
        self.debit_note.cae = '67294049531279'
        self.documents = self.invoice | self.refund | self.debit_note
        cae_due_date = '2000-01-01'
        self.documents.write({'cae_due_date': cae_due_date})

    def test_get_voucher_type_string(self):
        assert self.invoice.get_voucher_type_string() == 'FACTURA'
        assert self.refund.get_voucher_type_string() == 'NOTA DE CREDITO'
        assert self.debit_note.get_voucher_type_string() == 'NOTA DE DEBITO'

    def test_bar_code(self):
        # http://www.afip.gov.ar/afip/resol170204.html
        # CUIT EMISOR + CODIGO DE COMPROBANTE + PUNTO DE VENTA + CAE + FECHA VTO CAE (YYYYMMAA)
        vat = self.env.user.company_id.partner_id.vat

        assert self.invoice.get_bar_code() == ''.join([vat, '001', self.invoice.pos_ar_id.name.zfill(4),
                                                       self.invoice.cae,
                                                       self.invoice.cae_due_date.strftime('%Y-%m-%d').replace('-', "")])
        assert self.refund.get_bar_code() == ''.join([vat, '008', self.refund.pos_ar_id.name.zfill(4),
                                                      self.refund.cae,
                                                      self.refund.cae_due_date.strftime('%Y-%m-%d').replace('-', "")])
        assert self.debit_note.get_bar_code() == ''.join([vat, '012', self.debit_note.pos_ar_id.name.zfill(4),
                                                          self.debit_note.cae,
                                                          self.debit_note.cae_due_date.strftime('%Y-%m-%d').replace('-',
                                                                                                                    "")])

        with pytest.raises(ValidationError):
            self.invoice.cae = None
            assert self.invoice.get_bar_code()

    def test_verification_code(self):
        assert self.invoice.get_verification_code(self.invoice.get_bar_code()) == '5'
        assert self.refund.get_verification_code(self.refund.get_bar_code()) == '2'
        assert self.debit_note.get_verification_code(self.debit_note.get_bar_code()) == '5'
        with pytest.raises(Warning):
            # No tiene forma de entero el codigo de barra
            self.invoice.get_verification_code('A3')

    def test_invoice_print(self):
        assert self.invoice.invoice_print().get('report_name') == \
               'l10n_ar_electronic_invoice_report.report_electronic_invoice'

        self.document_book_fc_a.book_type_id = \
            self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id

        self.invoice.get_document_book_type()
        assert self.invoice.invoice_print().get('report_name') == \
            'account.report_invoice_with_payments'

    def test_tax_description(self):
        assert self.invoice.invoice_line_ids[0].invoice_line_tax_ids.get_tax_description() == 'IVA 21.0%'

    def test_invalid_invoice_fields(self):
        # Intentamos imprimir una factura borrador
        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)
        self.invoice.state = 'open'
        # Sin cae
        self.invoice.cae = None
        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)
        self.invoice.cae = '11231'
        self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(self.invoice.id)

    def test_invalid_company_fields(self):
        company = self.env.user.company_id
        start_date = company.start_date
        iibb_number = company.iibb_number
        street = company.street
        city = company.city
        self.invoice.state = 'open'

        company.start_date = None

        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)

        company.start_date = start_date
        company.street = None
        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)

        company.street = street
        company.iibb_number = None
        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)

        company.iibb_number = iibb_number
        company.city = None
        with pytest.raises(ValidationError):
            self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(
                self.invoice.id)

        company.city = city
        self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').render_qweb_text(self.invoice.id)

    def test_cantidad_de_copias(self):
        with pytest.raises(ValidationError):
            self.invoice.pos_ar_id.write({'copies_quantity': -1})
        with pytest.raises(ValidationError):
            self.invoice.pos_ar_id.write({'copies_quantity': 5})
        self.invoice.pos_ar_id.write({'copies_quantity': 4})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
