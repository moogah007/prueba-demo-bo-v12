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

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def remove_move_reconcile(self):
        """ Cuando rompo la conciliacion desactivo todas las imputaciones vinculadas a ese apunte y ese pago """
        for record in self:
            line = self.env['payment.imputation.line'].search(
                [('move_line_id', '=', record.id), ('payment_id', '=', record.payment_id.id)]
            )
            line.unlink()
        return super(AccountMoveLine, self).remove_move_reconcile()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
