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

from odoo.tools import pycompat
from odoo import models, fields


class AccountChartTemplate(models.Model):

    _inherit = 'account.chart.template'

    retention_template_ids = fields.One2many(
        'retention.retention.template',
        'chart_template_id',
        string='Templates de retenciones'
    )
    perception_template_ids = fields.One2many(
        'perception.perception.template',
        'chart_template_id',
        string='Templates de percepciones'
    )

    def generate_perceptions(self, perception_templates, account_template_ref, company):
        """
        Creamos las percepciones en base al template, manteniendo la estructura base que usan las cuentas e impuestos
        """
        template_vals = []
        perceptions_template_ref = {}
        for perception_template in perception_templates:
            vals = self._get_perception_vals(perception_template, account_template_ref, company)
            template_vals.append((perception_template, vals))

        perceptions = self._create_records_with_xmlid('perception.perception', template_vals, company)
        for template, account in pycompat.izip(perception_templates, perceptions):
            perceptions_template_ref[template.id] = account.id
        return perceptions_template_ref

    def generate_retentions(self, retention_templates, account_template_ref, company):
        """
        Creamos las retenciones en base al template, manteniendo la estructura base que usan las cuentas e impuestos
        """
        template_vals = []
        retentions_template_ref = {}
        for perception_template in retention_templates:
            vals = self._get_retention_vals(perception_template, account_template_ref, company)
            template_vals.append((perception_template, vals))

        retentions = self._create_records_with_xmlid('retention.retention', template_vals, company)
        for template, account in pycompat.izip(retention_templates, retentions):
            retentions_template_ref[template.id] = account.id
        return retentions_template_ref

    def _get_perception_vals(self, perception_template, tax_template_ref, company):
        self.ensure_one()

        vals = {
            'name': perception_template.name,
            'type': perception_template.type,
            'jurisdiction': perception_template.jurisdiction,
            'company_id': company.id,
            'tax_id': tax_template_ref[perception_template.tax_template_id.id],
            'state_id': perception_template.state_id.id,
            }
        return vals

    def _get_retention_vals(self, retention_template, tax_template_ref, company):
        self.ensure_one()

        vals = {
            'name': retention_template.name,
            'type': retention_template.type,
            'jurisdiction': retention_template.jurisdiction,
            'company_id': company.id,
            'tax_id': tax_template_ref[retention_template.tax_template_id.id],
            'state_id': retention_template.state_id.id,
        }
        return vals

    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        """ Creamos las retenciones y percepciones en base al template"""
        acc_template_ref = super(AccountChartTemplate, self).generate_account(
            tax_template_ref,
            acc_template_ref,
            code_digits,
            company
        )

        self.generate_perceptions(self.perception_template_ids, tax_template_ref, company)
        self.generate_retentions(self.retention_template_ids, tax_template_ref, company)
        return acc_template_ref

    def _create_bank_journals(self, company, acc_template_ref):
        """
        Cambia y elimina las cuentas creadas en los diarios
        por defecto al instalar la localizacion
        """
        rec_set = super(AccountChartTemplate, self)._create_bank_journals(company, acc_template_ref)
        for record in rec_set.filtered(lambda x: x.type == 'bank' or x.type == 'cash'):
            if record.type == 'bank':
                debit_account_id = self.env.ref('l10n_ar.1_banco_cuenta_en_pesos').id
                credit_account_id = self.env.ref('l10n_ar.1_banco_cuenta_en_pesos').id
            elif record.type == 'cash':
                debit_account_id = self.env.ref('l10n_ar.1_caja_en_pesos').id
                credit_account_id = self.env.ref('l10n_ar.1_caja_en_pesos').id

            record.default_debit_account_id.unlink()
            record.default_credit_account_id.unlink()

            record.write({
                'default_debit_account_id': debit_account_id,
                'default_credit_account_id': credit_account_id,
            })
        return rec_set

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
