odoo.define('account.invoice.info', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var QWeb = core.qweb;
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');


var ShowAmountInfoWidget = AbstractField.extend({

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);
        if (!info) {
            this.$el.html('');
            return;
        }
        _.each(info.content, function(k,v){
            k.index = v;
            k.amount = field_utils.format.float(k.amount, {digits: k.digits});
            if (k.date){
                k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
            }
        });
        this.$el.html(QWeb.render('ShowAmountInfo', {
            'title': info.title
        }));
        _.each(this.$('.js_amount_info'), function(k, v){
            var content = info.content[v];
            var options = {
                content: function() {
                    return $(QWeb.render('AmountPopOver', {
                        amount_to_tax: content.amount_to_tax,
                        'amount_not_taxable': content.amount_not_taxable,
                        'amount_exempt': content.amount_exempt,
                        'currency': content.currency,
                        'position': content.position,
                    }));
                },
                html: true,
                placement: 'left',
                title: 'Informacion de importes',
                trigger: 'focus',
                delay: { "show": 0, "hide": 100 },
            };
            $(k).popover(options);
        });
    },

});

field_registry.add('amountinfo', ShowAmountInfoWidget);

return {
    ShowAmountInfoWidget: ShowAmountInfoWidget
};

});