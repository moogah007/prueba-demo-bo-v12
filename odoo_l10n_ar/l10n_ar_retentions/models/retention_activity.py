# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields


class RetentionActivity(models.Model):
    _name = 'retention.activity'
    _description = 'Actividad de retencion'

    name = fields.Char(
        string="Actividad",
        required=True,
    )

    code = fields.Integer(
        string="Codigo AFIP",
        required=True,
    )

    def name_get(self):
        res = []
        for r in self:
            res.append(
                (r.id, "{}".format(r.name) if len(r.name) <= 40 else "{}...".format(r.name[:40])))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
