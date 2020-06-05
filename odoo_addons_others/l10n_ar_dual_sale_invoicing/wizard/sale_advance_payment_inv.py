# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoice(self, order, so_line, amount):
        """ Si la venta tiene la compania de facturacion, la seteo en el adelanto y cambio los impuestos """
        company = order.invoicing_picking_company_id or order.company_id
        res = super(SaleAdvancePaymentInv, self.with_context(company_id=company.id))._create_invoice(order, so_line, amount)
        res.update(order.get_fixed_invoice_values_by_invoicing_picking_company())
        res.onchange_partner_id()
        # Siempre va a haber una sola linea
        res.invoice_line_ids[0].update(order.order_line[0].get_fixed_invoice_line_values_by_invoicing_picking_company(self.product_id))
        res.compute_taxes()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
