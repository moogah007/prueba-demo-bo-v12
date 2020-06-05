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


class AccountDenomination(models.Model):

    _name = 'account.denomination'
    _description = 'Denominación'

    name = fields.Char('Nombre', required=True, size=1)
    description = fields.Char('Descripcion')
    validate_supplier = fields.Boolean(
        'Validar numeracion?',
        help="Valida numeracion con el formato 'xxxx-xxxxxxxx' para los documentos de proveedores"
    )
    vat_discriminated = fields.Boolean(
        string='Discrimina IVA?',
        help='Discriminacion de IVA en reporte'
    )

    _sql_constraints = [('name_unique', 'unique(name)', 'El nombre debe ser unico por denominacion')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
