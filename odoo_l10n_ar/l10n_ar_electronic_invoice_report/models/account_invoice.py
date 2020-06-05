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

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_print(self):
        """
        En el caso de que la factura tenga un talonario del tipo electronico
        se imprime el reporte de factura electronica.
        """
        res = super(AccountInvoice, self).invoice_print()
        self.ensure_one()

        if self.document_book_type == 'electronic':
            res = self.env.ref('l10n_ar_electronic_invoice_report.action_electronic_invoice').report_action(self)

        return res

    def get_bar_code(self):
        """
        Devuelve el numero para el codigo de barras del documento segun
        Resoluci�n General A.F.I.P. 1.702/04
        http://www.afip.gov.ar/afip/resol170204.html
        """

        if not self.cae:
            raise ValidationError("No se puede generar el codigo de barras sin CAE")

        bar_code = ''.join([
            self.company_id.partner_id.vat,
            self.get_voucher_code(),
            str(self.pos_ar_id.name).zfill(4),
            self.cae,
            self.cae_due_date.strftime('%Y-%m-%d').replace('-', ''),
        ])

        return bar_code

    @staticmethod
    def get_verification_code(bar_code):
        """
        Obtiene el codigo verificador segun el codigo de barra segun resol170204
        http://www.afip.gov.ar/afip/resol170204.html
        """
        # TODO: Pasar esta funcion a una libreria externa para reutilizar.

        try:
            barcode = int(bar_code)
        except ValueError:
            raise Warning('No se pudo generar el codigo de barras')

        barcode_numbers_list = list(map(int, str(barcode)))

        # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres ubicados en las posiciones impares.
        first = sum(odd for odd in barcode_numbers_list[0::2])

        # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el n�mero 3
        second = first * 3

        # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que est�n ubicados en las posiciones pares.
        third = sum(pair for pair in barcode_numbers_list[1::2])

        # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
        fourth = third + second

        return str(10 - (fourth % 10) if fourth % 10 is not 0 else 0)

    def get_voucher_type_string(self):
        """ String que debe aparecer en el documento segun tipo """
        return self.get_invoice_name()
        
    def validate_electronic_invoice_fields(self):
        """
        Valida que esten los campos necesarios para la impresión del reporte de factura electronica
        """
        self.ensure_one()
        company = self.company_id
        if not (company.start_date and company.iibb_number and company.street and company.city):
            raise ValidationError("Antes de imprimir, configurar la fecha de inicio de actividades"
                                  ", numero de IIBB y direccion de la empresa")

        if not self.cae:
            raise ValidationError("No se puede imprimir un documento sin CAE")

        if self.state not in ['open', 'paid']:
            raise ValidationError("No se puede imprimir un documento en estado borrador o cancelado")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
