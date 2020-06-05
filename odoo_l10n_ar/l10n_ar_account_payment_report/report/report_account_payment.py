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

from odoo import models, api
from odoo.exceptions import ValidationError


class ReportAccountPayment(models.AbstractModel):

    _name = 'report.l10n_ar_account_payment_report.report_account_payment'
    _table = 'report_account_payment'
    _description = 'Reporte de pago'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        for doc in docs:
            self._validate_state(doc)

        return {
            'doc_ids': docids,
            'doc_model': self.env['account.payment'],
            'docs': docs,
        }

    @staticmethod
    def _validate_state(doc):
        """
        Valida que esten el estado correcto para la impresión del reporte del pago
        :param doc: Model account.payment, documento a validar sus campos
        """
        if doc.state == 'draft':
            raise ValidationError("No se puede imprimir un documento en estado borrador")
        if doc.payment_type == 'transfer':
            raise ValidationError("No hay impresion para este tipo de documento.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
