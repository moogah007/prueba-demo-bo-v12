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
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoicing_picking_company_id = fields.Many2one('res.company', string="Compañía de factura/remito", copy=False)

    def get_fixed_invoice_values_by_invoicing_picking_company(self):
        self.ensure_one()
        company = self.invoicing_picking_company_id or self.company_id
        return {
            'company_id': company.id,
            'account_id': self.with_context(force_company=company.id).partner_invoice_id.property_account_receivable_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.with_context(force_company=company.id).partner_invoice_id.property_account_position_id.id,
        }

    def action_confirm_new(self):
        """
        Función nueva que se ejecutará con el botón de Confirmar. Valida que la compañía de factura/remito esté seteada
        y se la asigna a los remitos creados al confirmar.
        """
        if not self.invoicing_picking_company_id:
            raise ValidationError("No se puede confirmar una venta sin definir la compañía de factura/remito")
        res = self.action_confirm()
        self.picking_ids.write({'company_id': self.invoicing_picking_company_id.id})
        return res

    def _prepare_invoice(self):
        """ Si la venta tiene compañía de facturación, le asigno esa compañía a la factura """
        company = self.invoicing_picking_company_id or self.company_id
        res = super(SaleOrder, self.with_context(company_id=company.id))._prepare_invoice()
        res.update(self.get_fixed_invoice_values_by_invoicing_picking_company())
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
