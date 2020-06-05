#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for pick_type in env['stock.picking.type'].search([]):
        cr.execute("SELECT pos_ar_id FROM stock_picking_type WHERE id = %s" % pick_type.id)
        pos_ar_id = cr.dictfetchone().get('pos_ar_id')
        if pos_ar_id:
            pick_type.pos_ar_ids = [(6, 0, [pos_ar_id])]
