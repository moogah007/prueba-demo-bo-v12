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

import ast
import pytz
from datetime import datetime, date
import zeep
from dateutil.relativedelta import relativedelta
from l10n_ar_api import documents
from l10n_ar_api.afip_webservices import wsfe, wsfex
from odoo import models, fields, registry, api
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_service_from = fields.Date('Fecha servicio inicial', help='Fecha inicial del servicio brindado', copy=False)
    date_service_to = fields.Date('Fecha servicio final', help='Fecha final del servicio brindado', copy=False)
    cae = fields.Char('CAE', readonly=True, copy=False)
    cae_due_date = fields.Date('Vencimiento CAE', readonly=True, copy=False)
    wsfe_request_detail_ids = fields.Many2many(
        'wsfe.request.detail',
        'invoice_request_details',
        'invoice_id',
        'request_detail_id',
        string='Detalles Wsfe',
        copy=False,
    )
    currency_rate = fields.Float(
        string='Cotización a utilizar',
        copy=False
    )
    current_currency_rate = fields.Float(
        string='Cotización actual',
        compute='compute_current_currency_rate'
    )
    need_rate = fields.Boolean(
        string='Necesita cotización',
        related='currency_id.need_rate'
    )
    company_partner_id = fields.Many2one(related='company_id.partner_id', string='Partner compania')
    cbu_partner_bank_id = fields.Many2one('res.partner.bank', 'Cuenta bancaria')
    cbu_transmitter = fields.Char('CBU Emisor')
    fce_associated_document_ids = fields.One2many('fce.associated.document', 'invoice_id', 'Documentos asociados')
    fce_rejected = fields.Boolean('Rechazada por el comprador?')

    @api.onchange('cbu_partner_bank_id')
    def onchange_partner_bank_id(self):
        self.cbu_transmitter = self.cbu_partner_bank_id.cbu

    @api.depends('currency_id', 'company_currency_id', 'date_invoice')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for invoice in self:
            if invoice.currency_id and invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.date_invoice or fields.Date.today()
                rate = invoice.currency_id.with_context(date=date).compute(1, invoice.company_id.currency_id)
                invoice.current_currency_rate = rate
            else:
                invoice.current_currency_rate = 0

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'currency_rate')
    def _compute_amount(self):
        """ Se modifica funcion para que el total_company_signed se tenga en
        cuenta la cotizacion cargada en la factura"""
        res = super(AccountInvoice, self)._compute_amount()
        if self.currency_rate:
            amount_total_company_signed = self.amount_total
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                amount_total_company_signed = self.amount_total * self.currency_rate
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
        return res

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        """ Heredo la funcion para cargar por contexto la cotizacion si esta cargada sino sigo la logica estandar"""
        for inv in self:
            if not inv.currency_rate and inv.need_rate:
                inv.currency_rate = inv.current_currency_rate
        return super(AccountInvoice, self.with_context(currency_rate=self.currency_rate or 0)).compute_invoice_totals(company_currency, invoice_move_lines)

    def action_electronic(self, document_book):
        """
        Realiza el envio a AFIP de la factura y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        electronic_invoices = []
        pos = document_book.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        sent_invoices = invoices.filtered(lambda x: any(request.result == 'A' for request in x.wsfe_request_detail_ids))
        invoices -= sent_invoices

        # Si hubo un problema despues de escribir una respuesta y no se llegaron a escribir los detalles en las facturas
        for invoice in sent_invoices:
            invoice._write_wsfe_details_on_invoice(
                document_book,
                ast.literal_eval(invoice.wsfe_request_detail_ids.filtered(lambda x: x.result == 'A')[0].request_received)
            )

        if invoices:
            afip_wsfe = invoices[0]._get_wsfe()

        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(document_book, invoice)
            new_cr = registry(self.env.cr.dbname).cursor()
            # Validamos que la factura se encuentre en la base de datos
            try:
                self.with_env(self.env(cr=new_cr))._is_invoice_in_db(invoice)
            except Exception as e:
                new_cr.close()
                raise ValidationError(e.args)
            # Validamos la numeracion
            document_book.with_env(self.env(cr=new_cr)).action_wsfe_number(afip_wsfe, document_afip_code)
            new_cr.close()
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_invoice_details(document_afip_code))

        if electronic_invoices:
            response = None

            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfe.check_webservice_status()
                response, invoice_detail = afip_wsfe.get_cae(electronic_invoices, pos.name)
                afip_wsfe.show_error(response)
            except Exception as e:
                raise ValidationError(e.args)
            finally:
                # Commiteamos para que no haya inconsistencia con la AFIP.
                if response and response.FeDetResp:
                    new_cr = registry(self.env.cr.dbname).cursor()
                    invoices.with_env(self.env(cr=new_cr)).write_wsfe_response(invoice_detail, response)
                    self._commit_and_close(new_cr)

            if response and response.FeCabResp and response.FeCabResp.Resultado != 'R':
                for invoice in invoices:
                    new_cr = registry(self.env.cr.dbname).cursor()
                    document_book.with_env(self.env(cr=new_cr)).next_number()
                    self._commit_and_close(new_cr)
                    invoice._write_wsfe_details_on_invoice(document_book, zeep.helpers.serialize_object(response))

            if response and response.FeCabResp and response.FeCabResp.Resultado == 'R':
                # Traemos el conjunto de errores
                errores = '\n'.join(obs.Msg for obs in response.FeDetResp.FECAEDetResponse[0].Observaciones.Obs) \
                    if hasattr(response.FeDetResp.FECAEDetResponse[0], 'Observaciones') else ''
                raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))

    def _is_invoice_in_db(self, invoice):
        """
        Chequea la existencia del ID de la factura en la Base de Datos.
        :param invoice: Record de la factura.
        :raise: Exception si no la encuentra.
        """
        if not self.search([('id', '=', invoice.id)]):
            raise Exception("Error: el ID del registro no se encuentra en la base de datos")

    def write_wsfe_response(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        if response.FeCabResp:
            # Nos traemos el offset de la zona horaria para dejar en la base en UTC como corresponde
            offset = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).utcoffset().total_seconds() / 3600
            fch_proceso = datetime.strptime(response.FeCabResp.FchProceso, '%Y%m%d%H%M%S') - relativedelta(hours=offset)
            result = response.FeCabResp.Resultado
            date = fch_proceso
        else:
            result = "Error"
            date = fields.Datetime.now()

        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, invoice.id) for invoice in self],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': date,
        })

    def _commit_and_close(self, new_cr):
        new_cr.commit()
        new_cr.close()

    def _write_wsfe_details_on_invoice(self, document_book, response):
        self.ensure_one()
        # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
        cab = response.get('FeCabResp', {})
        det = response.get('FeDetResp', {}).get('FECAEDetResponse', [])[0]
        if cab.get('Resultado') == 'A':
            self.write({
                'cae': det.get('CAE'),
                'cae_due_date': datetime.strptime(det.get('CAEFchVto'), '%Y%m%d')
                if det.get('CAEFchVto') else None,
                'name': document_book.get_number(str(det.get('CbteHasta')))
            })

    def _write_wsfex_details_on_invoice(self, document_book, response):
        self.ensure_one()
        # Busco, dentro del detalle de la respuesta, el segmento correspondiente a la factura
        auth = response.get('FEXResultAuth', {})
        if auth.get('Resultado') == 'A':
            self.write({
                'cae': auth.get('Cae'),
                'cae_due_date': datetime.strptime(
                    auth.get('Fch_venc_Cae'),
                    '%Y%m%d'
                ) if auth.get('Fch_venc_Cae') else None,
                'name': document_book.get_number(str(auth.get('Cbte_nro')))
            })

    @staticmethod
    def convert_currency(from_currency, to_currency, amount=1.0, d=None):
        """
        Convierte `amount` de `from_currency` a `to_currency` segun la cotizacion de la fecha `d`.
        :param from_currency: La moneda que queremos convertir.
        :param to_currency: La moneda a la que queremos convertir.
        :param amount: La cantidad que queremos convertir (1 para sacar el rate de la moneda).
        :param d: La fecha que se usara para tomar la cotizacion de ambas monedas.
        :return: El valor en la moneda convertida segun el rate de conversion.
        """
        if from_currency.id == to_currency.id:
            return amount
        if not d:
            d = str(date.today())
        from_currency_with_context = from_currency.with_context(date=d)
        to_currency_with_context = to_currency.with_context(date=d)
        converted_amount = from_currency_with_context.compute(
            amount, to_currency_with_context, round=False
        )
        return converted_amount

    def _set_electronic_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ElectronicInvoice"""

        self._set_empty_invoice_details()
        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfe.invoice.ElectronicInvoice(document_afip_code)
        # Para comprobantes C solo se informa el importe total conciliado que corresponde con el taxed_amount de la API
        electronic_invoice.taxed_amount = self.amount_to_tax if self.denomination_id != denomination_c else self.amount_total
        electronic_invoice.untaxed_amount = self.amount_not_taxable if self.denomination_id != denomination_c else 0
        electronic_invoice.exempt_amount = self.amount_exempt if self.denomination_id != denomination_c else 0
        electronic_invoice.document_date = self.date_invoice or fields.Date.context_today(self)
        if codes_models_proxy.get_code('afip.concept', self.afip_concept_id.id) in ['2', '3']:
            electronic_invoice.service_from = self.date_service_from or fields.Date.context_today(self)
            electronic_invoice.service_to = self.date_service_to or fields.Date.context_today(self)
        electronic_invoice.payment_due_date = self.date_due or fields.Date.context_today(self)
        electronic_invoice.customer_document_number = self.partner_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id
        )
        electronic_invoice.mon_cotiz = self.currency_rate or self.convert_currency(
            from_currency=self.currency_id,
            to_currency=self.company_id.currency_id,
            d=self._get_currency_rate_date()
        )

        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id
        ))
        # Agregamos impuestos y percepciones
        self._add_vat_to_electronic_invoice(electronic_invoice)
        self._add_other_tributes_to_electronic_invoice(electronic_invoice)
        # Agregamos lo exclusivo de facturas de crédito
        self._add_associated_documents_to_electronic_invoice_refund(electronic_invoice)
        return electronic_invoice

    def _add_associated_documents_to_electronic_invoice_refund(self, electronic_invoice):
        """ Agrega los documentos asociados para facturas de credito cuando se envíen notas de débito o crédito """
        if self.is_credit_invoice:
            if self.is_debit_note or self.type == 'out_refund':
                if not self.fce_associated_document_ids:
                    raise ValidationError(
                        "No se puede enviar una nota de débito o crédito FCE sin documentos asociados"
                    )
                associated_documents = []
                canceled = False
                for document in self.fce_associated_document_ids:
                    if document.canceled:
                        canceled = True
                    associated_documents.append(wsfe.wsfe.WsfeAssociatedDocument(
                        document.document_code,
                        document.point_of_sale,
                        document.document_number,
                        document.cuit_transmitter,
                        document.date
                    ))
                canceled = 'S' if canceled else 'N'
                # Hay que informar el opcional de si el comprobante fue o no anulado por el comprador (ID 22)
                electronic_invoice.array_optionals = [wsfe.wsfe.WsfeOptional(22, canceled)]
                electronic_invoice.associated_documents = associated_documents
            else:
                # 2101 es para CBU, como por ahora solo vamos a enviar ese opcional lo dejamos así. Si el día de mañana
                # vamos a utilizar mas opcionales habría que crear el modelo y mapeo necesario.
                electronic_invoice.array_optionals = [wsfe.wsfe.WsfeOptional(2101, self.cbu_transmitter)]

    def _add_associated_documents_to_electronic_invoice_exportation(self, electronic_invoice):
        """ Agrega los documentos asociados para facturas de exportacion cuando se envíen notas de débito o crédito """
        if self.is_debit_note or self.type == 'out_refund':
            if not self.fce_associated_document_ids and \
                    self.env['codes.models.relation'].get_code('afip.concept', self.afip_concept_id.id) == '2':
                raise ValidationError(
                    "No se puede enviar una nota de débito o crédito de servicios "
                    "de exportación sin documentos asociados"
                )
            associated_documents = []
            for document in self.fce_associated_document_ids:
                associated_documents.append(wsfe.wsfe.WsfeAssociatedDocument(
                    document.document_code,
                    document.point_of_sale,
                    document.document_number,
                    document.cuit_transmitter,
                    document.date
                ))
            electronic_invoice.associated_documents = associated_documents

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        if invoice.type == 'out_invoice' and invoice.document_book_type != 'preprint':
            invoice_name = invoice.name.split('-')
            invoice_name = invoice_name[1] if len(invoice_name) > 1 else invoice_name[0]
            point_of_sale = invoice.pos_ar_id.name.lstrip('0')
            invoice_name = invoice_name.lstrip('0')
            values['fce_associated_document_ids'] = [(0, 0, {
                'associated_invoice_id': invoice.id,
                'point_of_sale': point_of_sale,
                'document_code': invoice.get_voucher_code(),
                'document_number': invoice_name,
                'cuit_transmitter': invoice.company_id.vat,
                'date': invoice.date_invoice,
                'canceled': invoice.fce_rejected
            })]
        return values

    def _add_vat_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son iva a informar """

        group_vat = self.env.ref('l10n_ar.tax_group_vat')
        codes_models_proxy = self.env['codes.models.relation']
        for tax in self.tax_line_ids:
            if tax.tax_id.tax_group_id == group_vat and not tax.tax_id.is_exempt:
                code = int(codes_models_proxy.get_code('account.tax', tax.tax_id.id))
                electronic_invoice.add_iva(documents.tax.Iva(code, tax.amount, tax.base))

    def _add_other_tributes_to_electronic_invoice(self, electronic_invoice):
        """ Agrega los impuestos que son percepciones """

        perception_perception_proxy = self.env['perception.perception']
        tax_group_vat = self.env.ref('l10n_ar.tax_group_vat')
        tax_group_internal = self.env.ref('l10n_ar.tax_group_internal')
        tax_group_perception = self.env.ref('l10n_ar.tax_group_perception')

        # Contemplamos 2 casos de tributos que no sean IVA, internos o percepciones.
        for tax in self.tax_line_ids.filtered(lambda t: t.amount > 0 and t.tax_id.tax_group_id != tax_group_vat):
            tribute_aliquot = round(tax.amount / tax.base if tax.base else 0, 2)

            if tax.tax_id.tax_group_id == tax_group_perception:
                perception = perception_perception_proxy.search([('tax_id', '=', tax.tax_id.id)], limit=1)
                if not perception:
                    raise ValidationError("Percepcion no encontrada para el impuesto".format(tax.tax_id.name))
                code = perception.get_afip_code()
                electronic_invoice.add_tribute(documents.tax.Tribute(code, tax.amount, tax.base, tribute_aliquot))

            elif tax.tax_id.tax_group_id == tax_group_internal:
                electronic_invoice.add_tribute(documents.tax.Tribute(4, tax.amount, tax.base, tribute_aliquot))
            else:
                raise ValidationError("No se puede informar el impuesto {} a AFIP".format(tax.tax_id.name))

    def _get_wsfe(self):
        """
        Busca el objeto de wsfe para utilizar sus servicios
        :return: instancia de Wsfe
        """
        return self.env['wsfe.configuration'].get_wsfe(self.company_id)

    def _set_empty_invoice_details(self):
        """ Completa los campos de la invoice no establecidos a un default """

        vals = {}

        if not self.afip_concept_id:
            vals['afip_concept_id'] = self._get_afip_concept_based_on_products().id
        if self.env['codes.models.relation'].get_code(
                'afip.concept', self.afip_concept_id.id or vals.get('afip_concept_id')
        ) in ['2', '3']:
            if not self.date_service_from:
                vals['date_service_from'] = self.date_invoice or fields.Date.context_today(self)
            if not self.date_service_to:
                vals['date_service_to'] = self.date_invoice or fields.Date.context_today(self)

        self.write(vals)

    def _validate_required_electronic_fields(self):
        if not (self.partner_id.vat and self.partner_id.partner_document_type_id):
            raise ValidationError('Por favor, configurar tipo y numero de documento en el cliente')

    def _validate_required_electronic_exportation_fields(self):
        if not self.partner_id.partner_document_type_id:
            raise ValidationError('Por favor, configurar tipo de documento en el cliente')

    def _get_afip_concept_based_on_products(self):
        """
        Devuelve el concepto de la factura en base a los tipos de productos
        :return: afip.concept, tipo de concepto
        """
        product_types = self.invoice_line_ids.mapped('product_id.type')

        # Estaria bueno pensar una forma para no hardcodearlo, ponerle el concepto en el producto
        # me parecio mucha configuracion a la hora de importar datos o para el cliente, quizas hacer un
        # compute?

        if len(product_types) > 1 and 'service' in product_types:
            # Productos y servicios
            code = '3'
        else:
            if 'service' in product_types:
                # Servicio
                code = '2'
            else:
                # Producto
                code = '1'

        return self.env['codes.models.relation'].get_record_from_code('afip.concept', code)

    # EXPORTACION
    def _get_wsfex(self):
        """
        Busca el objeto de wsfex para utilizar sus servicios
        :return: instancia de Wsfex
        """
        wsfex_config = self.env['wsfe.configuration'].search([
            ('wsaa_token_id.name', '=', 'wsfex'),
            ('company_id', '=', self.company_id.id),
        ])

        foreign_fiscal_positions = [
            self.env.ref('l10n_ar_afip_tables.account_fiscal_position_cliente_ext'),
            self.env.ref('l10n_ar_afip_tables.account_fiscal_position_prov_ext'),
        ]

        is_foreign = self.partner_id.property_account_position_id in foreign_fiscal_positions
        country_ar = self.env.ref('base.ar')
        if self.partner_id.country_id == country_ar and self.partner_id.state_id != self.env.ref('base.state_ar_v'):
            raise ValidationError(
                'No se puede enviar una factura de exportacion a Argentina que no sea Tierra del fuego.')
        if not wsfex_config:
            raise ValidationError('No se encontro una configuracion de factura electronica exportacion')

        if not self.partner_id.vat and not is_foreign:
            raise ValidationError("El partner {} no posee numero de documento.".format(self.partner_id.name))

        if not self.partner_id.country_id.vat and is_foreign and self.partner_id.country_id != country_ar:
            raise ValidationError("El partner {} no posee pais con documento.".format(self.partner_id.name))

        access_token = wsfex_config.wsaa_token_id.get_access_token()
        homologation = False if wsfex_config.type == 'production' else True
        afip_wsfex = wsfex.wsfex.Wsfex(access_token, self.company_id.vat, homologation)

        return afip_wsfex

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountInvoice, self).refund(date_invoice, date, description, journal_id)
        for refund in res:
            refund.date_due = False
        self.env.cr.commit()
        return res

    def action_electronic_exportation(self, document_book):
        """
        Realiza el envio a AFIP de la factura de exportacion y escribe en la misma el CAE y su fecha de vencimiento.
        :raises ValidationError: Si el talonario configurado no tiene la misma numeracion que en AFIP.
                                 Si hubo algun error devuelto por afip al momento de enviar los datos.
        """
        electronic_invoices = []
        pos = document_book.pos_ar_id
        invoices = self.filtered(lambda l: not l.cae and l.amount_total and l.pos_ar_id == pos).sorted(lambda l: l.id)
        sent_invoices = invoices.filtered(lambda x: any(request.result == 'A' for request in x.wsfe_request_detail_ids))
        invoices -= sent_invoices

        # Si hubo un problema despues de escribir una respuesta y no se llegaron a escribir los detalles en las facturas
        for invoice in sent_invoices:
            invoice._write_wsfex_details_on_invoice(
                document_book,
                ast.literal_eval(invoice.wsfe_request_detail_ids[0].request_received)
            )

        if invoices:
            afip_wsfex = invoices[0]._get_wsfex()
        for invoice in invoices:
            # Validamos los campos
            invoice._validate_required_electronic_exportation_fields()
            # Obtenemos el codigo de comprobante
            document_afip_code = invoice.get_document_afip_code(document_book, invoice)
            # Validamos la numeracion
            document_book.action_wsfe_number(afip_wsfex, document_afip_code)
            # Armamos la factura
            electronic_invoices.append(invoice._set_electronic_exportation_invoice_details(document_afip_code))

        if electronic_invoices:
            responses = None
            # Chequeamos la conexion y enviamos las facturas a AFIP, guardando el JSON enviado, el response y mostrando
            # los errores (en caso de que los haya)
            try:
                afip_wsfex.check_webservice_status()
                responses, invoice_details = afip_wsfex.get_cae(electronic_invoices, pos.name)
                for r in responses:
                    afip_wsfex.show_error(r)
                if len(responses) != len(invoice_details):
                    raise ValidationError('Las longitudes son distintas')
            except Exception as e:
                raise ValidationError(e.args)
            finally:
                # Commiteamos para que no haya inconsistencia con la AFIP. Como ya tenemos el CAE escrito en la factura,
                # al validarla nuevamente no se vuelve a enviar y se va a mantener la numeracion correctamente
                if responses:
                    for idx, response in enumerate(responses):
                        if response and response.FEXResultAuth:
                            new_cr = registry(self.env.cr.dbname).cursor()
                            invoices.with_env(self.env(cr=new_cr)).write_wsfex_response(invoice_details[idx], response)
                            self._commit_and_close(new_cr)
            if responses:
                for idx, response in enumerate(responses):
                    if response and response.FEXResultAuth and response.FEXResultAuth.Resultado != 'R':
                        for invoice in invoices:
                            document_book.next_number()
                            invoice._write_wsfex_details_on_invoice(
                                document_book,
                                zeep.helpers.serialize_object(response)
                            )

                    if response and response.FEXResultAuth and response.FEXResultAuth.Resultado == 'R':
                        # Traemos el conjunto de errores
                        errores = '\n'.join(response.FEXResultAuth.Motivos_Obs) \
                            if hasattr(response.FEXResultAuth.Motivos_Obs, 'Observaciones') else ''
                        raise ValidationError('Hubo un error al intentar validar el documento\n{0}'.format(errores))

    def _set_electronic_exportation_invoice_details(self, document_afip_code):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoice"""

        self._set_empty_invoice_details()
        codes_models_proxy = self.env['codes.models.relation']

        # Seteamos los campos generales de la factura
        electronic_invoice = wsfex.invoice.ExportationElectronicInvoice(document_afip_code)
        electronic_invoice.document_date = self.date_invoice or fields.Date.context_today(self)
        electronic_invoice.payment_due_date = self.date_due or fields.Date.context_today(self)
        electronic_invoice.destiny_country = int(codes_models_proxy.get_code(
            'res.country',
            self.partner_id.country_id.id
        ))
        electronic_invoice.customer_name = self.partner_id.name
        electronic_invoice.customer_street = self.partner_id.street

        electronic_invoice.destiny_country_cuit = self.partner_id.country_id.vat if self.partner_id.state_id != self.env.ref('base.state_ar_v') else self.partner_id.vat
        electronic_invoice.customer_document_type = codes_models_proxy.get_code(
            'partner.document.type',
            self.partner_id.partner_document_type_id.id
        )
        electronic_invoice.mon_id = self.env['codes.models.relation'].get_code(
            'res.currency',
            self.currency_id.id
        )
        electronic_invoice.mon_cotiz = self.currency_rate or self.convert_currency(
            from_currency=self.currency_id,
            to_currency=self.company_id.currency_id,
            d=self._get_currency_rate_date()
        )
        electronic_invoice.concept = int(codes_models_proxy.get_code(
            'afip.concept',
            self.afip_concept_id.id
        ))
        electronic_invoice.total_amount = self.amount_total
        # 1 = Exportación definitiva de bienes, 2 = Servicios, 4 = Otros
        electronic_invoice.exportation_type = electronic_invoice.concept
        if electronic_invoice.concept == 3:
            electronic_invoice.exportation_type = 4
        # 1: Español, 2: Inglés, 3: Portugués
        electronic_invoice.document_language = 1
        ndc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_020').id))
        ncc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_021').id))
        fcc_document_code = int(self.env['codes.models.relation'].get_code(
            'afip.voucher.type',
            self.env.ref('l10n_ar_afip_tables.afip_voucher_type_019').id))
        document_codes = [ndc_document_code, ncc_document_code]
        electronic_invoice.existent_permission = '' \
            if (electronic_invoice.exportation_type in [2, 4] and electronic_invoice.document_code == fcc_document_code)\
            or electronic_invoice.document_code in document_codes else 'N'
        electronic_invoice.incoterms = 'CIF'
        # Agregamos items
        electronic_invoice.array_items = self.add_item_exportation()
        self._add_associated_documents_to_electronic_invoice_exportation(electronic_invoice)
        return electronic_invoice

    def add_item_exportation(self):
        """ Mapea los valores de ODOO al objeto ExportationElectronicInvoiceItem """
        array_items = []
        for line in self.invoice_line_ids:
            item = wsfex.invoice.ExportationElectronicInvoiceItem(line.product_id.name)
            item.quantity = line.quantity
            try:
                item.measurement_unit = self.env['codes.models.relation'].get_code(
                    'product.uom',
                    line.uom_id.id
                )
            except:
                item.measurement_unit = 98
            item.unit_price = line.price_unit
            item.bonification = ((line.price_unit * line.quantity) * (line.discount / 100)) if line.discount else 0.0
            array_items.append(item)
        return array_items

    def get_document_afip_code(self, document_book, invoice):
        """ Busco el codigo del documento de AFIP"""
        document_type_id = document_book.document_type_id.id
        voucher_type = self.env['afip.voucher.type'].search([
            ('document_type_id', '=', document_type_id),
            ('denomination_id', '=', invoice.denomination_id.id)],
            limit=1
        )
        return int(self.env['codes.models.relation'].get_code('afip.voucher.type', voucher_type.id))

    def write_wsfex_response(self, invoice_detail, response):
        """ Escribe el envio y respuesta de un envio a AFIP """
        result = response.FEXResultAuth.Resultado if response.FEXResultAuth else "Error"
        self.env['wsfe.request.detail'].sudo().create({
            'invoice_ids': [(4, invoice.id) for invoice in self],
            'request_sent': invoice_detail,
            'request_received': response,
            'result': result,
            'date': fields.Datetime.now(),
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
