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
import itertools
import operator
from odoo import models, api, fields
from odoo.exceptions import ValidationError


class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    def _get_default_pos(self):
        default_type = self.default_get(['payment_type']).get('payment_type')
        pos = None
        if default_type:
            pos = self.get_pos(default_type)
        return pos

    pos_ar_id = fields.Many2one('pos.ar', 'Punto de venta', default=_get_default_pos)
    journal_id = fields.Many2one(default=lambda l: l.env.user.company_id.default_payment_journal_id.id)
    payment_type_line_ids = fields.One2many('account.payment.type.line', 'payment_id', 'Lineas de pagos')
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

    @api.depends('currency_id', 'journal_id.company_id.currency_id', 'payment_date')
    def compute_current_currency_rate(self):
        """ Calculo la cotizacion actual de la moneda siempre y cuando sea distinta a la de la compañia """
        for p in self:
            p.current_currency_rate = p.currency_id._convert(
                1, p.journal_id.company_id.currency_id, p.company_id, p._get_payment_date()) if p.currency_id else 0

    @api.onchange('payment_type_line_ids')
    def onchange_payment_type_line_ids(self):
        self.recalculate_amount()

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        self.payment_type_line_ids = None

    def recalculate_amount(self):
        self.ensure_one()
        amount = sum(payment_method.get('amount') for payment_method in self.set_payment_methods_vals())
        self.amount = amount

    def get_document_book(self):
        """
        Busca el talonario predeterminado para el tipo de pago
        :return: Talonario a utilizar
        :raise ValidationError: No hay configurado punto de venta
        :raise ValidationError: No hay configurado un talonario para ese punto de venta y tipo de comprobante
        """
        self.ensure_one()

        if not self.pos_ar_id:
            raise ValidationError("Por favor, configurar punto de venta primero")

        domain = ([
            ('pos_ar_id', '=', self.pos_ar_id.id),
            ('category', '=', 'payment'),
            ('document_type_id.type', '=', self.payment_type)
        ])

        document_book = self.env['document.book'].search(domain, limit=1)
        if not document_book:
            raise ValidationError(
                'No existe talonario configurado para el punto de venta ' + self.pos_ar_id.name_get()[0][1]
            )

        return document_book

    def get_pos(self, document_type):
        """ Devuelve el punto de venta segun el tipo de pago"""

        res = self.env['document.book'].search([
            ('category', '=', 'payment'),
            ('document_type_id.type', '=', document_type)],
            limit=1,
            order="sequence asc",
        ).pos_ar_id.id

        return res

    def set_payment_methods_vals(self):
        """
        Hook para agregar metodos de pagos y que se computen en el importe total del recibo/orden de pago
        :return: lista de diccionarios con los valores 'account_id' y 'amount', agrupados por cuenta.
        """

        vals = [
            {'amount': payment_type_line.amount, 'account_id': payment_type_line.account_payment_type_id.account_id.id}
            for payment_type_line in self.payment_type_line_ids
        ]

        return vals

    def _get_payment_date(self):
        self.ensure_one()
        return self.payment_date or fields.Date.today()


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('payment_type')
    def onchange_payment_type(self):
        if self.payment_type == 'transfer' or self.has_number:
            self.update({
                'pos_ar_id': None,
                'payment_type_line_ids': None
            })
        else:
            self.pos_ar_id = self.get_pos(self.payment_type)

    @api.depends('name')
    def _set_has_number(self):

        default_name = self.default_get(['name']).get('name')

        # Si tiene un punto de venta al momento de setear el nombre, ya no se deberia poder editar nuevamente
        for payment in self:
            payment.has_number = True if payment.name and payment.name != default_name else False

    has_number = fields.Boolean('Tiene numero pos', compute='_set_has_number')

    @api.multi
    def post(self):
        """
         El metodo post es el default para validar pagos,
         nos aseguramos que no se usen en ningun lado de la localizacion ya que no contempla
         multiples metodos de pagos.
        """

        raise ValidationError("Funcion de validacion de pago estandar deshabilitada")

        # return super(AccountPayment, self).post() - La funcion se heredo, solo que nunca va a llegar al super

    @api.multi
    def unlink(self):

        # No se puede borrar pagos en borrador si tiene move_name, como no tiene sentido para
        # la localizacion le desasignamos el move_name asi se puede borrar
        for rec in self:
            rec.move_name = None

        return super(AccountPayment, self).unlink()

    @api.multi
    def post_l10n_ar(self):
        """
        Crea los movimientos contables que genera el pago y valida el asiento creado.
        Imputa a las facturas asociadas el pago para conciliarlas.
        """

        for rec in self:
            rec._validate_states_and_fields()

            if rec.need_rate and rec.currency_rate:
                rec = rec.with_context(fixed_payment_currency_rate=rec.currency_rate,
                                       fixed_rate_currency=rec.currency_id)

            # Utilizamos las secuencias pre-definidas para los casos que no sean ordenes de pago o recibos
            sequence_code = None
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer' and rec.payment_type == 'outbound':
                    sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier' and rec.payment_type == 'inbound':
                    sequence_code = 'account.payment.supplier.refund'

            if sequence_code:
                rec.write({
                    'name': self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                        sequence_code),
                    'pos_ar_id': None
                })

            elif not rec.has_number:
                # Si es orden de pago o recibo y todavia no tiene numero
                document_book = rec.get_document_book()
                rec.name = document_book.next_number()

            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_l10n_ar_payment_entry(amount)

            # En caso de transferencia interna, se realiza otro asiento para la contrapartida
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

    def create_imputation(self, move_line):
        """ Concilia la move_line con la creada en el pago """
        self.invoice_ids.register_payment(move_line)

    def _reconcile_with_invoices(self, move, counterpart_aml):
        """
        Extraigo la parte de la función base que arma el apunte de writeoff, para poder modificar la funcionalidad en
        los casos que sea necesario
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(
                self.payment_difference, self.currency_id, self.company_id.currency_id)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id._convert(
                self.amount, self.company_id.currency_id, self.company_id, self._get_payment_date())
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            debit_wo = amount_wo > 0 and amount_wo or 0.0
            credit_wo = amount_wo < 0 and -amount_wo or 0.0
            writeoff_line['name'] = "Contrapartida"
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        return counterpart_aml

    def _create_l10n_ar_payment_entry(self, amount):
        """
        Create el asiento correspondiente al pago. Concilia las facturas que referencia.
        Tener en cuenta que es la funcion original modificada para la parte de contrapartidas, la cual es
        donde se contemplan multiples metodos de pago (se detalla en la funcion dicha parte para trazabilidad)
        :return: account.move - Asiento creado
        """

        # Analizamos si es orden de pago o recibo para el nombre de los move lines
        prefix = ''
        if (self.payment_type == 'outbound' and self.partner_type == 'supplier') \
                or (self.payment_type == 'inbound' and self.partner_type == 'customer'):
            prefix = 'REC ' if self.payment_type == 'inbound' else 'OP '

        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml_dict['name'] = prefix + self.name
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        counterpart_aml = self._reconcile_with_invoices(move, counterpart_aml)

        self.create_imputation(counterpart_aml)

        # Parte modificada para hookear las contrapartidas
        if self.payment_type == 'transfer':
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)
        else:

            sign = (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            for payment_method in self._get_payment_methods_vals():

                amount = payment_method.get('amount') * sign
                # Utilizamos la funcion de account_move base que computa multicurrency para cada metodo de pago
                debit, credit, amount_currency, currency_id = \
                    aml_obj.with_context(date=self.payment_date)._compute_amount_fields(
                        amount,
                        self.currency_id,
                        self.company_id.currency_id,
                    )
                if currency_id == self.company_id.currency_id.id:
                    amount_currency = 0

                # Creamos la move line del metodo de pago con su importe y cuenta
                liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id,
                                                                     False)
                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                liquidity_aml_dict.update({
                    'account_id': payment_method.get('account_id'),
                    'name': prefix + self.name,
                })
                if amount_currency:
                    liquidity_aml_dict.update({
                        'currency_id': currency_id,
                        'amount_currency': -amount_currency,
                    })

                aml_obj.create(liquidity_aml_dict)

        move.post()

        return move

    def _get_payment_methods_vals(self):
        """ Valida el formato y agrupa por cuenta los metodos de pago. """

        vals = self.set_payment_methods_vals()
        self._validate_payment_vals(vals)

        # Ordenamos por account_id
        keyfunc = operator.itemgetter('account_id')
        vals.sort(key=keyfunc)
        grouped_vals = []

        # Agrupamos por cuenta y sumamos los importes
        for key, index in itertools.groupby(vals, keyfunc):
            d = {'account_id': key}
            d.update({k: sum([item[k] for item in index]) for k in ['amount']})
            grouped_vals.append(d)

        return grouped_vals

    @staticmethod
    def _validate_payment_vals(vals):
        """
        Valida que todos los metodos de pago tengan los valores necesarios
        :param vals: Lista de diccionario con los valores del metodo de pago para la account.move.line
        :return: Valores originales
        """
        for value in vals:
            if 'account_id' not in value:
                raise ValidationError("Falta definir la cuenta para el metodo de pago establecido")
            if 'amount' not in value:
                raise ValidationError("Falta definir el importe del metodo de pago establecido")

        return vals

    def _validate_states_and_fields(self):
        """ Se asegura que los estados y campos de los documentos de pago y del pago sean correctos """

        if self.state != 'draft':
            raise ValidationError("Solo se pueden validar pagos en borrador")
        if any(inv.state != 'open' for inv in self.invoice_ids):
            raise ValidationError(
                "Los pagos no se pueden validar porque no todas las "
                "facturas estan en estado abierta"
            )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
