# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
#
from odoo import models, fields, api, _

class stock_rule(models.Model):
    _inherit = 'stock.rule'
    
    # Pass the sale line delivery date to stock.move delivery date
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        res = super(stock_rule,self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        del_date=False
        if values.get('sale_line_id'):
            line = self.env['sale.order.line'].browse(values.get('sale_line_id'))
            del_date = line.delivery_date
        if del_date:
            res.update({'delivery_date':del_date})
        return res
        
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
