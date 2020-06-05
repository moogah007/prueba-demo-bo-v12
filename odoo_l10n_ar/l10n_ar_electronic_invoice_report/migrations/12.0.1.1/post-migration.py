#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ext_id_obj = env['ir.model.data'].xmlid_to_object('l10n_ar_point_of_sale.denomination_fiscal_position_multi', raise_if_not_found=False)
    if ext_id_obj:
        ext_id_obj.unlink()
