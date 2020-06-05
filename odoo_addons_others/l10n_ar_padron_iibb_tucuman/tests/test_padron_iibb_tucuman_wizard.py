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
from ..wizard import padron_iibb_tucuman_wizard as wizard
import os


class TestPadronIIBBTucumanWizard(common.TransactionCase):

    def setUp(self):
        super(TestPadronIIBBTucumanWizard, self).setUp()

    def test_process_file(self):
        path = os.path.dirname(__file__)
        lines = wizard.process_file_176(path+'/ACREDITAN_REDUCIDO.TXT')
        assert lines[0] == ('30710061196', '20200201', '20200229', 1.5)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
