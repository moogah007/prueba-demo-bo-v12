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
    
class stock_move(models.Model):
    _inherit = 'stock.move'
    
    delivery_date = fields.Date('Delivery Date')
    
    
    #assign move delivery date to picking delivery date
    def _get_new_picking_values(self):
        res=super(stock_move,self)._get_new_picking_values()
        res.update({'delivery_date':self.delivery_date})
        return res
        
    # Search Picking for move and assign to picking to move 
    def _search_picking_for_assignation(self):
        res = super(stock_move,self)._search_picking_for_assignation()
        if self.delivery_date:
            picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('delivery_date','=',self.delivery_date),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
            return picking
        return res
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
