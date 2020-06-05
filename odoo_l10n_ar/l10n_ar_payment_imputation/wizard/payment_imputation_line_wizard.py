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


class PaymentImputationLineWizardAbstract(models.AbstractModel):

    _name = 'payment.imputation.line.wizard.abstract'
    _description = 'Wizard de línea de imputación'
    _inherit = 'abstract.payment.imputation.line'

    payment_id = fields.Many2one('payment.imputation.wizard')


class PaymentImputationCreditLineWizard(models.TransientModel):

    _name = 'payment.imputation.credit.line.wizard'
    _description = 'Linea de crédito de imputación de wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'


class PaymentImputationDebitLineWizard(models.TransientModel):

    _name = 'payment.imputation.debit.line.wizard'
    _description = 'Linea de débito de imputación de wizard'
    _inherit = 'payment.imputation.line.wizard.abstract'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
