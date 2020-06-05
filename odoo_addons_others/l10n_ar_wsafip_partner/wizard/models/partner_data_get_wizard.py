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

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from l10n_ar_api.afip_webservices.ws_sr_padron import ws_sr_padron


class PartnerDataGetWizard(models.TransientModel):
    _name = 'partner.data.get.wizard'

    vat = fields.Char("CUIT", required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner")
    write_partner = fields.Boolean("¿Sobreescribir partner?")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('partner.data.get.wizard'),
    )

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.vat = self.partner_id.vat

    def get_and_write_data(self):
        """
        Obtiene y escribe los datos de AFIP en un determinado partner. Si se selecciono 'sobreescribir', se
        pisan los datos del partner seleccionado o en su defecto el que coincida con el CUIT ingresado. Sino,
        se arrojan diferentes errores. En caso de que no exista en el sistema ningún partner con el CUIT
        ingresado, se creara uno con los datos obtenidos.
        """

        if not self.write_partner:
            if self.partner_id:
                raise ValidationError("ERROR\nPara sobreescribir el partner seleccionado, "
                                      "marque la casilla 'sobreescribir partner'.")

            elif self.env['res.partner'].search([('vat', '=', self.vat)]):
                raise ValidationError("ERROR\nYa existe un partner con dicho CUIT. Para sobreescribirlo"
                                      " seleccione la casilla 'sobreescribir partner'.")

        data = self.get_data()
        # Cargamos los datos en un diccionario
        vals = self.load_vals(data)
        partner = self.write_data(vals) if self.write_partner else self.create_partner(vals)

        view = self.env.ref('base.view_partner_form')
        return {
            'type': 'ir.actions.act_window',
            'view_id': view.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'target': 'current',
            'res_id': partner.id,
        }

    def get_data(self):
        """
        Obtiene los valores para ese numero de documento desde el servicio SOAP de AFIP.
        :return: Json con los datos del contribuyente
        """
        wsfe_config = self.env['wssrpadrona5.configuration'].search([
            ('wsaa_token_id.name', '=', 'ws_sr_padron_a5')
        ])

        if not wsfe_config:
            raise ValidationError('No se encontro una configuracion del webservice de padron a5')

        access_token = wsfe_config.wsaa_token_id.get_access_token()
        homologation = False if wsfe_config.type == 'production' else True
        afip_ws_sr_padron_a5 = ws_sr_padron.WsSrPadron(access_token, self.company_id.vat, homologation)

        try:
            result = afip_ws_sr_padron_a5.get_partner_data(self.vat)
        except Exception as e:
            raise ValidationError('{}'.format(e.args))

        return result

    def write_data(self, vals):
        """
        Escribe los datos traídos de AFIP en el partner seleccionado, o si no hay ninguno seleccionado busca
        el que tenga el mismo CUIT del formulario. Si no encuentra ninguno, lo crea.
        :param vals: diccionario con datos de AFIP
        """
        partner = self.partner_id if self.partner_id else self.env['res.partner'].search([('vat', '=', self.vat)],
                                                                                         limit=1)
        if partner:
            partner.write(vals)
            return partner
        return self.create_partner(vals)

    def create_partner(self, vals):
        """
        Crea un partner en el sistema con los datos traídos desde AFIP.
        :param vals: diccionario con datos de AFIP
        """
        return self.env['res.partner'].create(vals)

    def _get_position_fiscal(self, data):
        """ Se busca el id de la posicion fiscal desde los datos de la respuesta del servicio """
        # Si la respuesta tiene datosMonotributo, es monotributista
        # Si esta el 30 en los impuestos de datosRegimenGeneral es RI
        # Si no, si esta el 32 es exento
        if data.datosMonotributo:
            id_pos_fiscal = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_mon').id
        else:
            id_pos_fiscal = ''
            if data.datosRegimenGeneral:
                taxes = data.datosRegimenGeneral.impuesto
                if any(tax.descripcionImpuesto == 'IVA' for tax in taxes):
                    id_pos_fiscal = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari').id
                elif any(tax.descripcionImpuesto == 'IVA EXENTO' for tax in taxes):
                    id_pos_fiscal = self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ex').id
        return id_pos_fiscal

    def load_vals(self, data):
        """
        Carga los datos en un diccionario para sobreescribir o crear luego el partner. 
        :param data: json con los datos del contribuyente
        :return: diccionario para escribir res.partner
        """
        persona = data.datosGenerales
        if not persona:
            return {}
        # Si la respuesta tiene datosMonotributo, es monotributista
        # Si esta el 30 en los impuestos de datosRegimenGeneral es RI
        # Si no, si esta el 32 es exento
        position_fiscal = self._get_position_fiscal(data)
        domicilio = persona.domicilioFiscal if persona.domicilioFiscal else None
        vals = {
            'vat': self.vat,
            'country_id': self.env.ref('base.ar').id,
            'name': persona.razonSocial or '{name}{spacer}{surname}'.format(
                name=persona.apellido or '',
                spacer=' ' if persona.apellido and persona.nombre else '',
                surname=persona.nombre or '',
            ),
            'property_account_position_id': position_fiscal if position_fiscal else False,
            'partner_document_type_id': self.env.ref('l10n_ar_afip_tables.partner_document_type_80').id,  # CUIT
        }

        if domicilio:
            vals['city'] = domicilio.localidad or ''
            vals['zip'] = domicilio.codPostal or ''
            vals['street'] = domicilio.direccion or ''
            vals['state_id'] = self.get_state(domicilio.idProvincia)

        # TODO: Ver si podemos obtener de alguna forma posiciones fiscales (por ej desde los ID de impuestos)

        return vals

    def get_state(self, id_provincia):
        """
        Obtiene el id de la provincia usando codes models relations.
        :param id_provincia: id de la provincia segun SUPA
        :return: id de provincia
        """
        codes_models_proxy = self.env['codes.models.relation']

        try:
            return codes_models_proxy.get_record_from_code('res.country.state', id_provincia).id
        except Exception:
            return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
