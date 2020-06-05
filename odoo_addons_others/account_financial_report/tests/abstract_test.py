# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import common
from odoo.tools import test_reports

_logger = logging.getLogger(__name__)


class AbstractTest(common.TransactionCase):
    """Common technical tests for all reports."""
    at_install = False
    post_install = True

    accounts = {}

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def _chart_template_create(self):
        transfer_account_id = self.env['account.account.template'].create({
            'code': '000',
            'name': 'Liquidity Transfers',
            'reconcile': True,
            'user_type_id': self.ref(
                "account.data_account_type_current_assets"),
        })
        self.chart = self.env['account.chart.template'].create({
            'name': 'Test COA',
            'code_digits': 4,
            'bank_account_code_prefix': 1014,
            'cash_account_code_prefix': 1014,
            'currency_id': self.ref('base.USD'),
            'transfer_account_code_prefix': '000',
        })
        transfer_account_id.update({
            'chart_template_id': self.chart.id,
        })
        self.env['ir.model.data'].create({
            'res_id': transfer_account_id.id,
            'model': transfer_account_id._name,
            'name': 'Liquidity Transfers',
        })
        act = self.env['account.account.template'].create({
            'code': '001',
            'name': 'Expenses',
            'user_type_id': self.ref("account.data_account_type_expenses"),
            'chart_template_id': self.chart.id,
            'reconcile': True,
        })
        self.env['ir.model.data'].create({
            'res_id': act.id,
            'model': act._name,
            'name': 'expenses',
        })
        act = self.env['account.account.template'].create({
            'code': '002',
            'name': 'Product Sales',
            'user_type_id': self.ref("account.data_account_type_other_income"),
            'chart_template_id': self.chart.id,
            'reconcile': True,
        })
        self.env['ir.model.data'].create({
            'res_id': act.id,
            'model': act._name,
            'name': 'sales',
        })
        act = self.env['account.account.template'].create({
            'code': '003',
            'name': 'Account Receivable',
            'user_type_id': self.ref("account.data_account_type_receivable"),
            'chart_template_id': self.chart.id,
            'reconcile': True,
        })
        self.env['ir.model.data'].create({
            'res_id': act.id,
            'model': act._name,
            'name': 'receivable',
        })
        act = self.env['account.account.template'].create({
            'code': '004',
            'name': 'Account Payable',
            'user_type_id': self.ref("account.data_account_type_payable"),
            'chart_template_id': self.chart.id,
            'reconcile': True,
        })
        self.env['ir.model.data'].create({
            'res_id': act.id,
            'model': act._name,
            'name': 'payable',
        })

    def _add_chart_of_accounts(self):
        self.company = self.env['res.company'].create({
            'name': 'Spanish test company',
        })
        self.env.ref('base.group_multi_company').write({
            'users': [(4, self.env.uid)],
        })
        self.env.user.write({
            'company_ids': [(4, self.company.id)],
            'company_id': self.company.id,
        })
        self.with_context(
            company_id=self.company.id, force_company=self.company.id)
        self.chart.try_loading_for_current_company()
        self.revenue = self.env['account.account'].search(
            [('user_type_id', '=', self.ref(
                "account.data_account_type_other_income"))], limit=1)
        self.expense = self.env['account.account'].search(
            [('user_type_id', '=', self.ref(
                "account.data_account_type_expenses"))], limit=1)
        self.receivable = self.env['account.account'].search(
            [('user_type_id', '=', self.ref(
                "account.data_account_type_receivable"))], limit=1)
        self.payable = self.env['account.account'].search(
            [('user_type_id', '=', self.ref(
                "account.data_account_type_payable"))], limit=1)
        return True

    def _journals_create(self):
        self.journal_sale = self.env['account.journal'].create({
            'company_id': self.company.id,
            'name': 'Test journal for sale',
            'type': 'sale',
            'code': 'TSALE',
            'default_debit_account_id': self.revenue.id,
            'default_credit_account_id': self.revenue.id,
        })
        self.journal_purchase = self.env['account.journal'].create({
            'company_id': self.company.id,
            'name': 'Test journal for purchase',
            'type': 'purchase',
            'code': 'TPUR',
            'default_debit_account_id': self.expense.id,
            'default_credit_account_id': self.expense.id,
        })
        return True

    def _invoice_create(self):
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'company_id': self.company.id,
            'property_account_receivable_id': self.receivable.id,
            'property_account_payable_id': self.payable.id,
            'property_account_position_id': self.iva_ri.id,
        })

        # customer invoice
        customer_invoice_lines = [(0, False, {
            'name': 'Test description #1',
            'account_id': self.revenue.id,
            'quantity': 1.0,
            'price_unit': 100.0,
        }), (0, False, {
            'name': 'Test description #2',
            'account_id': self.revenue.id,
            'quantity': 2.0,
            'price_unit': 25.0,
        })]
        self.invoice_out = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'type': 'out_invoice',
            'invoice_line_ids': customer_invoice_lines,
            'account_id': self.partner.property_account_receivable_id.id,
            'journal_id': self.journal_sale.id,
        })
        self.invoice_out.action_invoice_open()

        # vendor bill
        vendor_invoice_lines = [(0, False, {
            'name': 'Test description #1',
            'account_id': self.revenue.id,
            'quantity': 1.0,
            'price_unit': 100.0,
        }), (0, False, {
            'name': 'Test description #2',
            'account_id': self.revenue.id,
            'quantity': 2.0,
            'price_unit': 25.0,
        })]
        self.invoice_in = self.env['account.invoice'].create({
            'name': "1111-11111111",
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'invoice_line_ids': vendor_invoice_lines,
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.journal_purchase.id,
        })
        self.invoice_in.action_invoice_open()

    def set_up_invoice(self):
        denomination_a = self.env.ref('l10n_ar_afip_tables.account_denomination_a')
        self.company.partner_id.property_account_position_id = self.iva_ri
        pos = self.env['pos.ar'].create({'name': 5, 'company_id': self.company.id})
        self.env['document.book'].create({
            'name': 32,
            'pos_ar_id': pos.id,
            'category': 'invoice',
            'book_type_id': self.env.ref('l10n_ar_point_of_sale.document_book_type_preprint_invoice').id,
            'document_type_id': self.env.ref('l10n_ar_point_of_sale.document_type_invoice').id,
            'denomination_id': denomination_a.id,
        })

    def setUp(self):
        super(AbstractTest, self).setUp()

        self.iva_ri = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari')

        self.with_context()
        self._chart_template_create()
        self._add_chart_of_accounts()
        self.set_up_invoice()
        self._journals_create()
        self._invoice_create()

        self.model = self._getReportModel()

        self.qweb_report_name = self._getQwebReportName()
        self.xlsx_report_name = self._getXlsxReportName()
        self.xlsx_action_name = self._getXlsxReportActionName()

        self.report_title = self._getReportTitle()

        self.base_filters = self._getBaseFilters()
        self.additional_filters = self._getAdditionalFiltersToBeTested()

        self.report = self.model.create(self.base_filters)
        self.report.compute_data_for_report()
