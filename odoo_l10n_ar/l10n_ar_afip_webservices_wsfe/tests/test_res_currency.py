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

from odoo.tests import common
from mock import mock


class TestResCurrency(common.TransactionCase):

    def setUp(self):
        super(TestResCurrency, self).setUp()

    def test_set_rate(self):
        currency = self.env.ref('base.USD')
        cotiz = 'odoo.addons.l10n_ar_afip_webservices_wsfe.models.res_currency.ResCurrency.get_cotization_from_afip'
        with mock.patch(cotiz) as cotiz_mock:
            cotiz_mock.return_value = 45.00
            rate = currency.set_cotization_from_afip(currency)
            assert rate.inverse_rate == 45.00
            assert rate.currency_id == currency

    def test_set_rate_with_another_rate(self):
        currency = self.env.ref('base.USD')
        cotiz = 'odoo.addons.l10n_ar_afip_webservices_wsfe.models.res_currency.ResCurrency.get_cotization_from_afip'
        self.env['res.currency.rate'].create({'currency_id': currency.id, 'inverse_rate': 30.00})
        with mock.patch(cotiz) as cotiz_mock:
            cotiz_mock.return_value = 45.00
            rate = currency.set_cotization_from_afip(currency)
            assert rate.inverse_rate == 30.00
            assert rate.currency_id == currency

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
