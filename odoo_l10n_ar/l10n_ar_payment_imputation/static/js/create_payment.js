odoo.define('l10n_ar_payment_imputation.create_payment_wizard', function(require){

    var ListController = require('web.ListController');

    ListController.include({
        /**
         * @override
         */
        renderButtons: function() {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('#payment_imputation').click(this.proxy('create_imputation'));
            }
        },

        create_imputation: function () {
            if (this.initialState.context.default_payment_type != 'transfer'){
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'payment.imputation.wizard',
                    views: [[false, 'form']],
                    target: 'new',
                    context: this.initialState.context
                });
            }else{
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'account.payment',
                    views: [[false, 'form']],
                    context: this.initialState.context
                });
            }
        }
    });
});