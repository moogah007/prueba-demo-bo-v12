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


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """ Heredo la funcion para traer la cotizacion por contexto o hago el calculo"""
        return self.env.context.get('currency_rate') or \
               super(ResCurrency, self)._get_conversion_rate(from_currency, to_currency, company, date)

    def set_cotization_from_afip(self, currency, company=None):
        """
        Agrega la cotización del día de hoy si no existe.
        :param currency: res.currency de la moneda a actualizar.
        :parma company: Empresa de la cual se tomará la moneda.
        """
        company = self.env.user.company_id if not company else company
        cotization = self.get_cotization_from_afip(currency, company)
        rate = self.env['res.currency.rate'].search([
            ('currency_id', '=', currency.id),
            ('name', '=', fields.Date.today()),
            ('company_id', '=', company.id)
        ])
        if cotization and not rate:
            rate = rate.create({
                'currency_id': currency.id,
                'inverse_rate': cotization,
                'rate': 1/cotization,
                'name': fields.Date.today(),
                'company_id': company.id
            })

        return rate

    def set_cotization_action(self):
        rate = self.env['res.currency.rate']
        for currency in self.browse(self.env.context.get('active_ids')):
            rate += self.set_cotization_from_afip(currency)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cotizaciones actualizadas',
            'res_model': 'res.currency.rate',
            'views': [[False, "tree"]],
            'domain': [('id', 'in', rate.ids)]
        }

    def get_cotization_from_afip(self, currency, company):
        currency_code = self.env['codes.models.relation'].get_code(
            'res.currency',
            currency.id
        )
        wsfe = self.env['wsfe.configuration'].get_wsfe(company)
        try:
            cotiz = wsfe.get_cotization(currency_code)
        except Exception as e:
            raise ValidationError(e.args[0])

        return cotiz

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
