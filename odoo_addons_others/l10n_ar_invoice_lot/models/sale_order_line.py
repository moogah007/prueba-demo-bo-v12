# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Heredo la funcion para modificar la descripcion de las lineas de facturas
        con los lotes utilizados en los remitos
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        # Si el producto tiene configurado que muestre lotes en facturas hago la logica
        if self.product_id.lot_invoice:
            # Busco los movimientos de stock asociados a las lineas de venta
            stock_moves = self.move_ids.filtered(lambda x: x.state not in ('cancel', 'draft'))
            # Me traigo las lineas de movimientos de stock que contienen lotes
            stock_move_lines = stock_moves.move_line_ids.filtered(lambda x: x.qty_done and x.lot_id)
            if stock_move_lines:
                # Genero una lista por lote con el nombre, vencimiento y cantidad
                name_lots = ['Lote: {} Vto: {} Cant: {}'.format(
                    lot.lot_id.name,
                    lot.lot_id.removal_date.strftime('%d/%m/%Y') if lot.lot_id.removal_date else '',
                    lot.qty_done
                ) for lot in stock_move_lines]
                # Modifico el name de la linea de factura para colocar la informacion de los lotes
                res['name'] = '{}\n{}'.format(res['name'], '\n'.join(lot for lot in name_lots))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
