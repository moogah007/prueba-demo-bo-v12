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
import mock
from openerp.exceptions import ValidationError

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    perception_ids = fields.One2many(
        'account.invoice.perception',
        'invoice_id',
        string='Percepciones',
        copy=True
    )

    @api.onchange('perception_ids')
    def onchange_perception_ids(self):
        self._onchange_invoice_line_ids()

    @api.multi
    def get_taxes_values(self):
        """
        Agregamos a las lineas de impuestos las percepciones cargadas
        :return dict: Impuestos agrupados con importe y base {'tax': {'amount': '0.0', 'base': 0.0}}
        """
        res = super(AccountInvoice, self).get_taxes_values()

        for perception in self.perception_ids:
            tax = self.env['account.tax'].browse(perception.perception_id.tax_id.id)
            tax_vals = self._get_perception_tax_vals(perception)

            # El mock deberia ser una invoice.tax.line. Como no la necesitamos la mockeamos
            vals = self._prepare_tax_line_vals(mock.Mock(), tax_vals)
            key = self.env['account.tax'].browse(tax.id).get_grouping_key(vals)

            if key not in res:
                res[key] = vals
            else:
                res[key]['amount'] += vals['amount']
                res[key]['base'] += vals['base']

        return res

    @staticmethod
    def _get_perception_tax_vals(perception):
        """
        Obtiene los valores para crear impuestos desde la percepcion
        :param perception: account.perception.tax con los datos a obtener para setear los impuestos
        :return dict: Datos para crear account.invoice.tax
        """

        tax = perception.perception_id.tax_id
        vals = {
            'analytic': False,
            'amount': perception.amount,
            'base': perception.base,
            'name': tax.name,
            'account_id': tax.account_id.id,
            'refund_account_id': tax.refund_account_id.id,
            'id': tax.id,
            'sequence': 1
        }

        return vals

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Agregamos las percepciones a las facturas que se cancelan con nota de credito """

        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        values['perception_ids'] = self._refund_cleanup_lines(invoice.perception_ids)

        return values

    @api.multi
    def action_invoice_open(self):
        """
        Validacion de facturas C con percepciones
        :return: finalmente llama al super
        """
        all_invoices = self.browse(self.ids or self.env.context.get('active_ids'))
        denomination_c = self.env.ref('l10n_ar_afip_tables.account_denomination_c')

        for invoice in all_invoices:
            if invoice.perception_ids and invoice.denomination_id == denomination_c:
                raise ValidationError("No puede validar una factura con denominacion C con percepciones.")
        return super(AccountInvoice, self).action_invoice_open()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
