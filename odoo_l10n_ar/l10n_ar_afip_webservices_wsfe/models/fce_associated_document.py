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

from odoo import models, fields, api


class FceAssociatedDocument(models.Model):

    _name = 'fce.associated.document'
    _description = 'Documento de FCE asociado'

    invoice_id = fields.Many2one('account.invoice', 'Documento', ondelete='cascade')
    associated_invoice_id = fields.Many2one('account.invoice', 'Documento asociado', domain=[
        ('type', 'in', ['out_invoice', 'out_refund']),
        ('state', 'in', ['open', 'paid'])
    ])
    point_of_sale = fields.Char('Punto de venta', required=True)
    document_number = fields.Char('Numero', required=True)
    document_code = fields.Char('Código comprobante', required=True)
    cuit_transmitter = fields.Char('Cuit emisor', required=True)
    date = fields.Date('Fecha', required=True)
    canceled = fields.Boolean('Rechazado por comprador?')

    @api.onchange('associated_invoice_id')
    def onchange_invoice_id(self):
        invoice_name = self.associated_invoice_id.name.split('-') if self.associated_invoice_id.name else ['']
        invoice_name = invoice_name[1] if len(invoice_name) > 1 else invoice_name[0]
        point_of_sale = self.associated_invoice_id.pos_ar_id.name.lstrip('0') \
            if self.associated_invoice_id.pos_ar_id.name else ''
        invoice_name = invoice_name.lstrip('0')
        self.update({
            'point_of_sale': point_of_sale,
            'document_code': self.associated_invoice_id.get_voucher_code() if self.associated_invoice_id else '',
            'document_number': invoice_name,
            'cuit_transmitter': self.associated_invoice_id.company_id.vat,
            'date': self.associated_invoice_id.date_invoice,
            'canceled': self.associated_invoice_id.fce_rejected,
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
