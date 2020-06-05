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
from datetime import datetime, timedelta, date

import pytest
from odoo.tests import common

from l10n_ar_api.presentations import presentation


class TestPerceptionsSifere(common.TransactionCase):
    # -------------------------------------------------------------------------
    # AUX
    # -------------------------------------------------------------------------
    def create_invoicing_data(self):
        self.document_book_proxy = self.env['document.book']
        self.pos_proxy = self.env['pos.ar']

        # Configuracion de posicion fiscal RI en la compania
        self.env.user.company_id.partner_id.property_account_position_id = self.iva_ri

        self.pos = self.pos_proxy.create({'name': 5})
        self.document_book = self.document_book_proxy.create({
            'name': 32,
            'pos_ar_id': self.pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': self.env.ref('l10n_ar_afip_tables.account_denomination_a').id,
        })
        self.partner = self.env['res.partner'].create({
            'name': "Cliente",
            'country_id': self.country.id,
            'vat': '11222222223',
            'property_account_position_id': self.iva_ri.id,
        })
        self.journal = self.env['account.journal'].create({
            'name': "Diario",
            'type': 'sale',
            'code': "DIA",
        })
        self.denomination = self.env['account.denomination'].create({
            'name': "Z",
        })
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.journal.id,
            'denomination_id': self.denomination.id,
            'name': '9999-88888888',
            'date_invoice': date.today()
        })

    def create_tax_data(self):
        self.tax = self.env['account.tax'].create({
            'name': "SIFERE",
            'amount': 1
        })
        self.perception = self.env['perception.perception'].create({
            'name': "SIFERE",
            'tax_id': self.tax.id,
            'type': 'gross_income',
            'jurisdiction': 'nacional',
            'state_id': self.env.ref('base.state_ar_b').id,
        })

    def create_country(self):
        self.country = self.env['res.country'].create({
            'name': "Pais",
            'code': "ZZ",
            'no_prefix': True,
        })

    def create_account(self):
        self.account_type = self.env['account.account.type'].create({
            'name': "Tipo de cuenta",
        })
        self.account = self.env['account.account'].create({
            'code': "Codigo",
            'name': "Cuenta",
            'user_type_id': self.account_type.id,
        })

    def create_perception(self):
        self.perception_sifere = self.env['perception.sifere'].create({
            'name': "Percepcion SIFERE",
            'date_from': datetime.now() - timedelta(days=1),
            'date_to': datetime.now() + timedelta(days=1),
        })
        self.perception_line = self.env['account.invoice.perception'].create({
            'name': "Linea Percepcion",
            'invoice_id': self.invoice.id,
            'perception_id': self.perception.id,
            'amount': 400.5,
            'jurisdiction': 'nacional',
            'create_date': date.today()
        })
        self.lines = presentation.Presentation("sifere", "percepciones")
        self.code = self.perception_sifere.get_code(self.perception_line)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------
    def setUp(self, *args, **kwargs):
        super(TestPerceptionsSifere, self).setUp(*args, **kwargs)
        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')
        self.create_country()
        self.create_tax_data()
        self.create_account()
        self.create_invoicing_data()
        self.create_perception()

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------
    def test_perception(self):
        self.perception_sifere.create_line(self.code, self.lines, self.perception_line)
        today = date.today().strftime("%d/%m/%Y")
        assert self.lines.lines[0].get_line_string() == "90211-22222222-3{}999988888888CA00000400,50".format(today)

    def test_perception_no_vat_exception(self):
        self.partner.vat = None
        with pytest.raises(Exception):
            self.perception_sifere.create_line(self.code, self.lines, self.perception_line)

    def test_perception_no_code_exception(self):
        self.code = None
        with pytest.raises(Exception):
            self.perception_sifere.create_line(self.code, self.lines, self.perception_line)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
