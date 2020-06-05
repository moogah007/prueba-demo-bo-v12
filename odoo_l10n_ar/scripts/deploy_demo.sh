#!/usr/bin/env bash
cd /opt/odoo_addons_l10n_ar
echo "Descargando ultimos cambios"
git pull origin develop_12.0
export OPENERP_SERVER=/etc/odoo/odoo.conf
export PYTHONPATH=/opt/odoo
echo "Reiniciando ODOO"
sudo /etc/init.d/odoo restart
echo "Actualizando ODOO"
/opt/odoo/odoo-bin -u base_vat_ar -d ${1?Error: Falta especificar la base de datos} --xmlrpc-port=${2?Error: Falta especificar el puerto} --stop-after-init