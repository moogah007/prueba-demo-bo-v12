#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['codes.models.relation'].search([('name_model', '!=', 'account.tax')]).write({'company_id': False})
