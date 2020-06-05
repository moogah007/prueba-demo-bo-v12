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

from odoo import models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_fixed_invoice_line_values_by_invoicing_picking_company(self, product=False):
        self.ensure_one()
        company = self.order_id.invoicing_picking_company_id or self.order_id.company_id
        if not product:
            product = self.product_id
        
        # Toda esta parte fue copiada de base, pero agregando los force_company
        account = product.with_context(force_company=company.id).property_account_income_id or \
            product.with_context(force_company=company.id).categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError('Por favor defina la cuenta de ingresos para este producto: \"%s\" (id:%d) o su categoría: \"%s\".' %
                product.name, product.id, product.categ_id.name)

        fpos = self.order_id.fiscal_position_id or self.with_context(force_company=company.id).order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)
            
        return {
            'account_id': account.id,
            'invoice_line_tax_ids': [(6, 0, [t.id for t in product.taxes_id if t.company_id == company])],
        }

    def _prepare_invoice_line(self, qty):
        """
        Si la venta tiene compañía de facturación, tomo los impuestos de la línea según los del producto en la compañía
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update(self.get_fixed_invoice_line_values_by_invoicing_picking_company())
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
