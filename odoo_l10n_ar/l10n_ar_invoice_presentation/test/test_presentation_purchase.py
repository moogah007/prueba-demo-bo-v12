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
import base64
from odoo.tests.common import TransactionCase


class TestPresentationPurchase(TransactionCase):
    def create_product(self):
        return self.env['product.product'].create({
            "name": "Test Consumable Product",
            "type": "consu",
            "standard_price": 1000,
            "supplier_taxes_id": [(6, 0, [self.env.ref("l10n_ar.1_vat_21_compras").id])]
        })

    def create_partner(self):
        data = {
            "name": "Test Partner",
            "vat": "20307810795",
            "supplier": True,
            "customer": True,
            "partner_document_type_id": self.env.ref("l10n_ar_afip_tables.partner_document_type_80").id,
            "country_id": self.env.ref("base.ar").id,
        }

        data.update({"property_account_position_id": self.fiscal_position_ri.id})

        return self.env['res.partner'].create(data)

    def create_invoice_line(self, invoice, product):
        return self.env['account.invoice.line'].create({
            "name": "Test Consumable Product",
            "product_id": product.id,
            "price_unit": 1000,
            "account_id": product.categ_id.property_account_expense_categ_id.id,
            "invoice_id": invoice.id,
            "invoice_line_tax_ids": [(6, 0, [self.env.ref("l10n_ar.1_vat_21_compras").id])]
        })

    def create_invoice(self):
        partner = self.create_partner()
        product = self.create_product()
        invoice = self.env['account.invoice'].create({
            "name": '0001-00000001',
            "partner_id": partner.id,
            "type": "in_invoice",
            "date_invoice": "2017-08-01",
        })
        # Ejecuto onchange de partner
        invoice.onchange_partner_id()

        # Creo linea y ejecuto onchange de producto
        invoice_line = self.create_invoice_line(invoice, product)
        invoice_line._onchange_product_id()

        # Ejecuto onchange de lineas y valido
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def create_invoice_no_taxed(self):
        partner = self.create_partner()
        product = self.create_product()
        invoice = self.env['account.invoice'].create({
            "name": '0001-00000123',
            "partner_id": partner.id,
            "type": "in_invoice",
            "date_invoice": "2017-08-01",
        })
        # Ejecuto onchange de partner
        invoice.onchange_partner_id()

        # Creo linea y ejecuto onchange de producto
        invoice_line = self.create_invoice_line(invoice, product)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = self.env.ref("l10n_ar.1_vat_no_gravado_compras")

        # Ejecuto onchange de lineas y valido
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def create_invoice_exempt(self):
        partner = self.create_partner()
        product = self.create_product()
        invoice = self.env['account.invoice'].create({
            "name": '0001-00201123',
            "partner_id": partner.id,
            "type": "in_invoice",
            "date_invoice": "2017-08-01",
        })
        # Ejecuto onchange de partner
        invoice.onchange_partner_id()

        # Creo linea y ejecuto onchange de producto
        invoice_line = self.create_invoice_line(invoice, product)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = self.env.ref("l10n_ar.1_vat_exento_compras")

        # Ejecuto onchange de lineas y valido
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def create_importation_invoice(self):
        partner = self.create_partner()
        product = self.create_product()
        invoice = self.env['account.invoice'].create({
            "name": '17073IC04092010Z',
            "partner_id": partner.id,
            "type": "in_invoice",
            "date_invoice": "2017-08-01",
            "denomination_id": self.env.ref('l10n_ar_afip_tables.account_denomination_d').id
        })

        # Ejecuto onchange de partner
        invoice.onchange_partner_id()

        # Creo linea y ejecuto onchange de producto
        invoice_line = self.create_invoice_line(invoice, product)
        invoice_line._onchange_product_id()

        # Ejecuto onchange de lineas y valido
        invoice._onchange_invoice_line_ids()
        invoice.action_invoice_open()

        return invoice

    def create_presentation(self):
        return self.env['account.invoice.presentation'].create({
            "name": "test",
            "date_from": "2017-08-01",
            "date_to": "2017-08-31",
            "sequence": "00",
            "with_prorate": False
        })

    def get_general_data(self):
        self.fiscal_position_ri = self.env.ref("l10n_ar_afip_tables.account_fiscal_position_ivari")

    def setUp(self):
        super(TestPresentationPurchase, self).setUp()
        self.get_general_data()
        self.env.user.company_id.partner_id.property_account_position_id = self.fiscal_position_ri
        self.env.user.company_id.partner_id.country_id = self.env.ref('base.ar').id
        self.env.user.company_id.partner_id.vat = '20359891033'

        self.presentation = self.create_presentation()

    def test_purchase_invoice_presentation_with_no_taxed(self):
        """Validamos codigo de operacion No gravado."""
        self.create_invoice_no_taxed()
        self.presentation.generate_files()
        decoded = base64.decodebytes(self.presentation.purchase_file)
        assert decoded[238:239] == b"N"

    def test_purchase_invoice_presentation_with_exempt(self):
        """Validamos codigo de operacion Exento."""
        self.create_invoice_exempt()
        self.presentation.generate_files()
        decoded = base64.decodebytes(self.presentation.purchase_file)
        assert decoded[238:239] == b"E"

    def test_purchase_invoice_presentation(self):
        """Se puede generar la presentacion de una factura comun."""
        self.create_invoice()
        self.presentation.generate_files()
        decoded = base64.decodebytes(self.presentation.purchase_file)
        # Fecha de comprobante
        assert decoded[0:8] == b"20170801"
        # Tipo de comprobante
        assert decoded[8:11] == b"001"
        # Punto de venta
        assert decoded[11:16] == b"00001"
        # Numero de comprobante
        assert decoded[16:36] == b"00000000000000000001"
        # Numero de despacho de importacion
        assert decoded[36:52] == b"".ljust(16)
        # Codigo de documento del proveedor
        assert decoded[52:54] == b"80"
        # Numero de identificacion del proveedor
        assert decoded[54:74] == b"00000000020307810795"
        # Apellido y nombre del proveedor
        assert decoded[74:104] == b"Test Partner".ljust(30)
        # Importe total de la operacion
        assert decoded[104:119] == b"000000000121000"
        # Importe total de conceptos que no integran el precio neto gravado
        assert decoded[119:134] == b"000000000000000"
        # Importe operaciones exentas
        assert decoded[134:149] == b"000000000000000"
        # Percepciones IVA
        assert decoded[149:164] == b"000000000000000"
        # Percepciones impuestos nacionales
        assert decoded[164:179] == b"000000000000000"
        # Importe de percepciones de ingresos brutos
        assert decoded[179:194] == b"000000000000000"
        # Importe de percepciones impuestos municipales
        assert decoded[194:209] == b"000000000000000"
        # Importe impuestos internos
        assert decoded[209:224] == b"000000000000000"
        # Codigo de moneda
        assert decoded[224:227] == b"PES"
        # Tipo de cambio
        assert decoded[227:237] == b"0001000000"
        # Cantidad de alicuotas de IVA
        assert decoded[237:238] == b"1"
        # Codigo de operacion
        assert decoded[238:239] == b" "
        # Credito fiscal computable
        assert decoded[239:254] == b"000000000021000"
        # Otros tributos
        assert decoded[254:269] == b"000000000000000"
        # CUIT emisor
        assert decoded[269:280] == b"00000000000"
        # Denominacion emisor
        assert decoded[280:310] == b"".ljust(30)
        # IVA comision
        assert decoded[310:325] == b"000000000000000"

    def test_purchase_invoice_iva_presentation(self):
        """Se puede generar la presentacion de iva de una factura comun."""
        self.create_invoice()
        self.presentation.generate_files()
        decoded = base64.decodebytes(self.presentation.purchase_vat_file)
        # Tipo de comprobante
        assert decoded[0:3] == b"001"
        # Punto de venta
        assert decoded[3:8] == b"00001"
        # Numero de comprobante
        assert decoded[8:28] == b"00000000000000000001"
        # Codigo documento del proveedor
        assert decoded[28:30] == b"80"
        # Numero identificacion del proveedor
        assert decoded[30:50] == b"00000000020307810795"
        # Importe neto gravado
        assert decoded[50:65] == b"000000000100000"
        # Alicuota de iva
        assert decoded[65:69] == b"0005"
        # Impuesto liquidado
        assert decoded[69:84] == b"000000000021000"

    # TODO: Agregar este test cuando se hagan despachos de importacion
    # def test_importation_purchase_invoice_presentation(self):
    #     "Se puede generar la presentacion de una factura de aduana comun."
    #     self.create_importation_invoice()
    #     self.presentation.generate_files()
    #     decoded = base64.decodestring(self.presentation.purchase_file)
    #     # Fecha de comprobante
    #     assert decoded[0:8] == "20170801"
    #     # Tipo de comprobante
    #     assert decoded[8:11] == "066"
    #     # Punto de venta
    #     assert decoded[11:16] == "00000"
    #     # Numero de comprobante
    #     assert decoded[16:36] == "00000000000000000000"
    #     # Numero de despacho de importacion
    #     assert decoded[36:52] == "17073IC04092010Z"
    #     # Codigo de documento del proveedor
    #     assert decoded[52:54] == "80"
    #     # Numero de identificacion del proveedor
    #     assert decoded[54:74] == "00000000020307810795"
    #     # Apellido y nombre del proveedor
    #     assert decoded[74:104] == "Test Partner".ljust(30)
    #     # Importe total de la operacion
    #     assert decoded[104:119] == "000000000121000"
    #     # Importe total de conceptos que no integran el precio neto gravado
    #     assert decoded[119:134] == "000000000000000"
    #     # Importe operaciones exentas
    #     assert decoded[134:149] == "000000000000000"
    #     # Percepciones IVA
    #     assert decoded[149:164] == "000000000000000"
    #     # Percepciones impuestos nacionales
    #     assert decoded[164:179] == "000000000000000"
    #     # Importe de percepciones de ingresos brutos
    #     assert decoded[179:194] == "000000000000000"
    #     # Importe de percepciones impuestos municipales
    #     assert decoded[194:209] == "000000000000000"
    #     # Importe impuestos internos
    #     assert decoded[209:224] == "000000000000000"
    #     # Codigo de moneda
    #     assert decoded[224:227] == "PES"
    #     # Tipo de cambio
    #     assert decoded[227:237] == "0001000000"
    #     # Cantidad de alicuotas de IVA
    #     assert decoded[237:238] == "1"
    #     # Codigo de operacion
    #     assert decoded[238:239] == "X"
    #     # Credito fiscal computable
    #     assert decoded[239:254] == "000000000021000"
    #     # Otros tributos
    #     assert decoded[254:269] == "000000000000000"
    #     # CUIT emisor
    #     assert decoded[269:280] == "00000000000"
    #     # Denominacion emisor
    #     assert decoded[280:310] == "".ljust(30)
    #     # IVA comision
    #     assert decoded[310:325] == "000000000000000"

    # TODO: Agregar este test cuando se hagan despachos de importacion
    # def test_purchase_importation_presentation(self):
    #     "Se puede generar la presentacion de importacion de una factura de aduana comun."
    #     self.create_importation_invoice()
    #     self.presentation.generate_files()
    #     decoded = base64.decodestring(self.presentation.purchase_imports_file)
    #     # Despacho importacion
    #     assert decoded[0:16] == "17073IC04092010Z"
    #     # Neto gravado
    #     assert decoded[16:31] == "000000000100000"
    #     # Alicuota de iva
    #     assert decoded[31:35] == "0005"
    #     # Impuesto liquidado
    #     assert decoded[35:50] == "000000000021000"

    def test_cannot_create_presentation_without_partner_cuit(self):
        """No se puede crear una presentacion con un partner sin cuit"""
        invoice = self.create_invoice()
        invoice.partner_id.vat = False
        with self.assertRaises(Exception):
            self.presentation.generate_purchase_file()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
