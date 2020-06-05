#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    report_translations = env['ir.translation'].search([('name', 'like', 'l10n_ar_electronic_invoice_report')])
    report_translations.unlink()
