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
from datetime import datetime
    
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    
    @api.model
    def _get_current_date(self):
        date = datetime.now().today()
        return date.strftime("%Y-%m-%d")
    
    delivery_date = fields.Date('Delivery Date', default=_get_current_date)
        
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            if self.order_id:
                self.delivery_date = self.order_id.date_order.strftime("%Y-%m-%d %H:%M:%S")
                
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
