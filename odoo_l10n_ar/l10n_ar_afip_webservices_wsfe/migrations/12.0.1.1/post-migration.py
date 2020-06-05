#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for inv in env['account.invoice'].search([('currency_rate', '!=', False)]):
        inv._compute_amount()
