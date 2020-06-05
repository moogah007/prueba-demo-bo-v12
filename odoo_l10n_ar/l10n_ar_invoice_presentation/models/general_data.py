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


class GeneralData:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.get_general_data()

    # Datos del sistema
    def get_general_data(self):
        """
        Obtiene valores predeterminados de la localizacion
        """
        self.type_b = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_b')
        self.type_c = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_c')
        self.type_d = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_d')
        self.type_i = self.proxy.env.ref('l10n_ar_afip_tables.account_denomination_i')
        self.tax_group_vat = self.proxy.env.ref('l10n_ar.tax_group_vat')
        self.tax_group_internal = self.proxy.env.ref('l10n_ar.tax_group_internal')
        self.tax_group_perception = self.proxy.env.ref('l10n_ar.tax_group_perception')
        self.tax_purchase_ng = self.proxy.env.ref('l10n_ar.{}_vat_no_gravado_compras'.format(
            self.proxy.env.user.company_id.id)
        )
        self.tax_sale_ng = self.proxy.env.ref('l10n_ar.{}_vat_no_gravado_ventas'.format(
            self.proxy.env.user.company_id.id)
        )
        self.codes_model_proxy = self.proxy.env['codes.models.relation']
        self.fiscal_position_nc = self.proxy.env.ref("l10n_ar_afip_tables.account_fiscal_position_no_categ")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
