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

from odoo.tests.common import TransactionCase
import datetime
import mock


class TestPartnerRules(TransactionCase):

    def setUp(self):
        super(TestPartnerRules, self).setUp()

    def test_generar_valores_regla_iibb_tucuman(self):
        get_padron_line_mock = 'odoo.addons.l10n_ar_padron_iibb_tucuman.models.' \
                               'padron_iibb_tucuman.PadronIIBBTucuman.get_padron_line'
        get_tucuman_perception_mock = 'odoo.addons.l10n_ar_padron_iibb_tucuman.models.' \
                               'perception_perception.PerceptionPerception.get_tucuman_perception'
        get_tucuman_retention_mock = 'odoo.addons.l10n_ar_padron_iibb_tucuman.models.' \
                               'retention_retention.RetentionRetention.get_tucuman_retention'

        with mock.patch(get_padron_line_mock) as line_mock, mock.patch(get_tucuman_perception_mock) as perception_mock,\
            mock.patch(get_tucuman_retention_mock) as retention_mock:
            perception_mock.return_value = self.env['perception.perception'].new({})
            retention_mock.return_value = self.env['retention.retention'].new({})
            line_mock.return_value = self.env['padron.iibb.tucuman'].new({
                'aliquot': 5.5,
                'cuit': '111222333',
                'date_from': '20200201',
                'date_to': '20200229',
            })

            partner = self.env['res.partner'].new({'vat': '111222333'})
            rules = partner.get_rule_values()
        # Percepcion
        assert rules[0][0][2]['percentage'] == 5.50
        assert rules[0][0][2]['date_from'] == datetime.date(2020, 2, 1)
        assert rules[0][0][2]['date_to'] == datetime.date(2020, 2, 29)
        # Retencion
        assert rules[1][0][2]['percentage'] == 5.5
        assert rules[1][0][2]['date_from'] == datetime.date(2020, 2, 1)
        assert rules[1][0][2]['date_to'] == datetime.date(2020, 2, 29)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
