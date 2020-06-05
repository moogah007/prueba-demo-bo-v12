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

from odoo.exceptions import Warning
from odoo import models
import l10n_ar_api.presentations.presentation as presentation_builder


class AccountInvoicePresentation(models.Model):
    _inherit = 'account.invoice.presentation'

    def validate_header(self):
        """
        Validamos que la compania tenga los datos necesarios.
        """
        if not self.company_id.partner_id.vat:
            raise Warning(
                "ERROR\nLa presentacion no pudo ser generada porque la compania no tiene CUIT\n"
            )

    def generate_header_file(self):
        """
        Se genera el archivo de cabecera. Utiliza la API de presentaciones y tools para poder crear los archivos
        y formatear los datos.
        :return: objeto de la api (generator), con las lineas de la presentacion creadas.
        """
        self.validate_header()

        cabecera = presentation_builder.Presentation("ventasCompras", "cabecera")
        line = cabecera.create_line()

        line.cuit = self.company_id.vat
        line.periodo = self.get_period()
        line.secuencia = self.sequence
        line.sinMovimiento = 'S'
        if self.with_prorate:
            line.prorratearCFC = 'S'
            line.cFCGlobal = '1'
        else:
            line.prorratearCFC = 'N'
            line.cFCGlobal = '2'
        line.importeCFCG = 0
        line.importeCFCAD = 0
        line.importeCFCP = 0
        line.importeCFnCG = 0
        line.cFCSSyOC = 0
        line.cFCCSSyOC = 0

        return cabecera

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

