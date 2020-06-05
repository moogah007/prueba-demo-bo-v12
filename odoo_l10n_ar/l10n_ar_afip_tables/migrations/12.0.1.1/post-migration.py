#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for ext_id in ['account_denomination_multi', 'afip_concept_multi', 'product_concept_multi', 'product_concept_category_multi', 'afip_voucher_type_multi']:
        ext_id_obj = env['ir.model.data'].xmlid_to_object('l10n_ar_afip_tables.' + ext_id, raise_if_not_found=False)
        if ext_id_obj:
            ext_id_obj.unlink()
    for company in env['res.company'].search([('chart_template_id', '=', env.ref('l10n_ar.ar_chart_template').id)]):
        env['codes.models.relation'].create_for_company(company)
