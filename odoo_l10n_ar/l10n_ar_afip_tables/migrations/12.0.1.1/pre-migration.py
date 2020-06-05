#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    cr.execute("SELECT id, res_id FROM ir_model_data WHERE module = 'l10n_ar_point_of_sale' AND model = 'denomination.fiscal.position'")
    for ext_id, obj_id in cr.fetchall():
        cr.execute("DELETE FROM ir_model_data WHERE id = {}".format(ext_id))
        if obj_id:
            cr.execute("DELETE FROM denomination_fiscal_position WHERE id = {}".format(obj_id))
