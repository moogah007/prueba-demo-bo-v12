odoo.define('l10n_ar_pos_invoicing.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    var _super_posmodel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;

            models.load_models(['partner.document.type'], {});
            models.load_models(['res.country.state'], {});
            models.load_fields('res.partner',['partner_document_type_id']);
            models.load_fields('res.partner',['state_id']);

            _super_posmodel.models.push({
                model:  'partner.document.type',
                fields: ['name'],
                loaded: function(self,doc_types){
                    self.doc_types = doc_types;
                }
            })
            _super_posmodel.models.push({
                model:  'res.country.state',
                fields: ['name'],
                domain: function(self) {return [['country_id', '=', self.company.country && self.company.country.id || false]]},
                loaded: function(self,states){
                    self.states = states;
                }
            })

            _super_posmodel.initialize.apply(this, arguments);
        }
    });
});
