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

from odoo import models, fields, api
from odoo.exceptions import ValidationError

ROUND_PRECISION = 2


class AccountAbstractPayment(models.AbstractModel):
    _inherit = 'account.abstract.payment'

    @api.depends('payment_imputation_ids', 'amount', 'advance_amount')
    def _compute_payment_imputation_difference(self):
        for payment in self:
            total_imputation = sum(payment.payment_imputation_ids.mapped('amount'))
            payment.payment_imputation_difference = payment.amount - payment.advance_amount - total_imputation

    payment_imputation_ids = fields.One2many(
        'payment.imputation.line',
        'payment_id',
        'Imputaciones',
        copy=False
    )
    payment_imputation_difference = fields.Monetary(
        compute='_compute_payment_imputation_difference',
        string='Diferencia',
        help='La resta del total del pago con las imputaciones y el importe a cuenta',
        readonly=True
    )
    advance_amount = fields.Monetary(
        'A pagar a cuenta',
        readonly=True
    )

    @api.onchange('partner_id')
    def onchange_partner_imputation(self):
        """ Elegimos las facturas pendientes de pago """
        invoice_proxy = self.env['account.invoice']
        context_invoices_ids = self.env.context.get('active_ids')
        lines = invoice_proxy.browse(context_invoices_ids).mapped('move_id').mapped('line_ids').filtered(
            lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')
        ) if self.env.context.get('active_model') == 'account.invoice' else self._get_imputation_move_lines()

        self.payment_imputation_ids = False

        debit_lines = [(0, 0, {
            'invoice_id': line.invoice_id.id,
            'move_line_id': line.id,
            'amount': abs(line.amount_residual),
            'concile': True,
        }) for line in lines]

        self.payment_imputation_ids = debit_lines or [(6, 0, [])]

    def reconcile_imputations(self, move_line):
        """
        Imputa los importes del pago a las move lines en base a los importes seleccionado en las imputaciones
        :param move_line: account.move.line generada del pago
        """
        # Borramos las imputaciones que no se van a realizar
        self.payment_imputation_ids.filtered(lambda x: not (x.amount or x.difference_account_id)).unlink()

        # Asignamos las facturas al pago
        self.invoice_ids = self.payment_imputation_ids.mapped('invoice_id')

        # Verificamos los montos de las imputaciones e importe a cuenta contra el del pago
        imp_total = sum(i.amount for i in self.payment_imputation_ids)
        if round(self.amount - self.advance_amount - imp_total, ROUND_PRECISION) != 0:
            raise ValidationError(
                "La cantidad a pagar debe ser igual a la suma de los totales a imputar y el importe a cuenta")

        lines_to_reconcile = move_line

        # Itero las imputaciones, ordenando por lo que quedará pendiente y el monto de la imputación, para evitar
        # problemas con la conciliación de apuntes base
        for imputation in self.payment_imputation_ids.sorted(
                key=lambda l: (l.amount_residual_in_payment_currency - l.amount, -l.amount)):

            amount_currency = False
            currency = False

            # Validamos que no haya importes o move lines erróneas
            imputation.validate(imputation.move_line_id)
            # Si se imputó el restante de factura, ajustamos el valor para ajustar las imprecisiones de usar 2 decimales
            full = round(imputation.amount_residual_in_payment_currency - imputation.amount, ROUND_PRECISION) == 0
            if full and self.currency_id != imputation.currency_id:
                imputation_amount = imputation.company_currency_id._convert(
                    imputation.amount_residual_company, self.currency_id, self.company_id, self._get_payment_date(), round=False)
            else:
                imputation_amount = min(abs(imputation.amount_residual_in_payment_currency), abs(imputation.amount))

            amount = self.currency_id._convert(
                imputation_amount, imputation.company_currency_id, self.company_id, self._get_payment_date())

            # Caso de multimoneda
            if imputation.move_line_id.currency_id:
                currency = imputation.move_line_id.currency_id
                amount_currency = self.currency_id._convert(
                    imputation_amount, imputation.move_line_id.currency_id, self.company_id, self._get_payment_date())

            new_ml = self._split_payment_ml(imputation.move_line_id, move_line, amount, amount_currency, currency)

            debit_move = new_ml or move_line if move_line.debit > 0 else imputation.move_line_id
            credit_move = new_ml or move_line if move_line.credit > 0 else imputation.move_line_id

            # Si no se imputó el total de la factura ni se definió una cuenta destino, creamos una conciliación parcial
            if not (full or imputation.difference_account_id) or self.advance_amount:
                self.env['account.partial.reconcile'].with_context(skip_full_reconcile_check=True).create({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': amount,
                    'amount_currency': amount_currency,
                    'currency_id': currency.id if currency else currency,
                })

            # Si no se imputó el total de la factura no nos interesa hacer esta conciliación,
            # con el partial reconcile alcanza
            if not new_ml and (full or imputation.difference_account_id):
                lines_to_reconcile |= imputation.move_line_id

        if not self.advance_amount:
            lines_to_reconcile.filtered(lambda l: not l.reconciled).reconcile()

    def _get_imputation_move_lines(self):
        account_type = 'receivable' if self.payment_type == 'inbound' else 'payable'
        search_domain = [
            ('account_id.user_type_id.type', '=', account_type),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False),
            ('amount_residual', '!=', 0.0)
        ]
        lines = self.env['account.move.line'].search(search_domain) if self.partner_id else \
            self.env['account.move.line']
        return lines.filtered(lambda x: x.debit > 0 if account_type == 'receivable' else x.credit > 0)

    def _split_payment_ml(self, imputation_move_line, payment_move_line, amount, amount_currency, currency):
        """
        En el caso que haya imputaciones de facturas con distintas cuentas, creamos una move line
        similar pero con la otra cuenta, y a la anterior le restamos el valor.
        """

        new_ml = None
        if imputation_move_line.account_id != payment_move_line.account_id:
            ml_vals = {
                'amount_currency': payment_move_line.amount_currency - amount_currency if amount_currency else None
            }
            new_ml_vals = {
                'amount_currency': amount_currency,
                'payment_id': self.id,
                'account_id': imputation_move_line.account_id.id,
                'currency_id': currency.id if currency else False
            }
            if payment_move_line.debit > 0:
                ml_vals['debit'] = payment_move_line.debit - amount
                new_ml_vals['debit'] = amount
            else:
                ml_vals['credit'] = payment_move_line.credit - amount
                new_ml_vals['credit'] = amount

                payment_move_line.write(ml_vals)
            new_ml = payment_move_line.copy(new_ml_vals)

            (new_ml | imputation_move_line).reconcile()

        return new_ml

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        super(AccountAbstractPayment, self).onchange_currency_id()
        for line in self.payment_imputation_ids:
            line.onchange_concile()

    @api.constrains('advance_amount')
    def check_advance_amount(self):
        if any(payment.advance_amount < 0 for payment in self):
            raise ValidationError('El importe a cuenta no puede ser negativo.')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def create_imputation(self, move_line):
        """ Sobreescribimos la funcion original de imputacion para que realice por las invoices seleccionadas """
        if self.payment_imputation_ids:
            self.reconcile_imputations(move_line)
        else:
            super(AccountPayment, self).create_imputation(move_line)

    def _create_l10n_ar_payment_entry(self, amount):
        if not self.invoice_ids:
            self.invoice_ids = self.payment_imputation_ids.mapped('invoice_id')
        return super(AccountPayment, self)._create_l10n_ar_payment_entry(amount)

    def _reconcile_with_invoices(self, move, counterpart_aml):
        """ Heredo la función de l10n_ar_account_payment para hacer un apunte por cada writeoff de las imputaciones """
        counterpart_aml = super(AccountPayment, self)._reconcile_with_invoices(move, counterpart_aml)

        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        for line in self.payment_imputation_ids.filtered(lambda l: l.difference_account_id):
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, line.invoice_id)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self._get_payment_date())._compute_amount_fields(
                line.amount_residual_in_payment_currency - line.amount, self.currency_id, self.company_id.currency_id)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency minus the
            # payment amount in company currency, and not from the payment difference in the payment currency to
            # avoid loss of precision during the currency rate computations. See revision
            # 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = line.amount_residual_company
            total_payment_company_signed = self.currency_id._convert(
                line.amount, self.company_id.currency_id, self.company_id, self._get_payment_date())
            if line.invoice_id.type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = "Contrapartida"
            writeoff_line['account_id'] = line.difference_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line['payment_id'] = self.id
            aml_obj.create(writeoff_line)
            if counterpart_aml.debit:
                counterpart_aml.debit += credit_wo - debit_wo
            if counterpart_aml.credit:
                counterpart_aml.credit += debit_wo - credit_wo
            counterpart_aml.amount_currency -= amount_currency_wo

        return counterpart_aml

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
