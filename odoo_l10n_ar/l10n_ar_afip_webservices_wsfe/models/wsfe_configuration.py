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
from odoo.exceptions import ValidationError
from l10n_ar_api.afip_webservices import wsfe


class WsfeConfiguration(models.Model):

    _name = 'wsfe.configuration'
    _description = 'Configuración wsfe'

    name = fields.Char('Nombre', required=True)
    type = fields.Selection([
            ('homologation', 'Homologacion'),
            ('production', 'Produccion')
        ],
        'Tipo',
        required=True
    )
    wsaa_configuration_id = fields.Many2one('wsaa.configuration', 'WSAA', required=True)
    # Me parece mal que no este filtrado el token de acceso solo para los de tipo FE. Como por el momento
    # no utilizamos otro lo dejamos asi, tener en cuenta si algun dia se utiliza el wsaa para otros servicios.
    wsaa_token_id = fields.Many2one('wsaa.token', 'Token Acceso', required=True)

    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        required=True,
        default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [('unique_name', 'unique(name, company_id)', 'Ya existe una configuracion con ese nombre')]

    @api.constrains('wsaa_token_id')
    def check_unique_ticket(self):
        for wsfe in self:
            if wsfe.search_count([('wsaa_token_id', '=', wsfe.wsaa_token_id.id)]) > 1:
                raise ValidationError('Ya existe una configuracion de factura electronica asociado a ese token')

    @api.onchange('wsaa_configuration_id')
    def onchange_wsaa_configuration(self):
        self.wsaa_token_id = None

    def get_wsfe(self, company):
        """
        Busca el objeto de wsfe para utilizar sus servicios
        :return: instancia de Wsfe
        """
        wsfe_config = self.env['wsfe.configuration'].search([
            ('wsaa_token_id.name', '=', 'wsfe'),
            ('company_id', '=', company.id),
        ])

        if not wsfe_config:
            raise ValidationError('No se encontro una configuracion de factura electronica')

        access_token = wsfe_config.wsaa_token_id.get_access_token()
        homologation = False if wsfe_config.type == 'production' else True
        afip_wsfe = wsfe.wsfe.Wsfe(access_token, company.vat, homologation)

        return afip_wsfe

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
