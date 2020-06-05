# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class WsfeRequestDetail(models.Model):

    _name = 'wsfe.request.detail'
    _description = 'Detalle de wsfe request'

    request_sent = fields.Text('Request enviado', required=True)
    request_received = fields.Text('Request recibido', required=True)
    invoice_ids = fields.Many2many(
        'account.invoice',
        'invoice_request_details',
        'request_detail_id',
        'invoice_id',
        string='Documento'
    )
    result = fields.Char('Resultado')
    date = fields.Datetime('Fecha')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
