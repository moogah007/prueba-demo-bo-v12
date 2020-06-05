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

from odoo.tests import common


class TestAccountChartTemplate(common.TransactionCase):

    def setUp(self):
        super(TestAccountChartTemplate, self).setUp()
        self.company = self.env['res.company'].create({
            'name': 'Test',
        })

        self.currency = self.env['res.currency'].new({
            'name': 'ARS'
        })

        self.chart_template = self.env['account.chart.template'].new({})

    def test_journals_creation(self):
        rec_set = self.chart_template._create_bank_journals(self.company, None)

        cash_journal = rec_set.filtered(lambda x: x.type == 'cash')
        assert cash_journal.default_debit_account_id == self.env.ref('l10n_ar.1_caja_en_pesos')
        assert cash_journal.default_credit_account_id == self.env.ref('l10n_ar.1_caja_en_pesos')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
