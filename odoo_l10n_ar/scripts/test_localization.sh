#!/usr/bin/env bash
cd /opt/odoo_addons_l10n_ar
echo "Descargando ultimos cambios"
git fetch
git checkout ${2?Error: Falta especificar el branch}
git pull
export OPENERP_SERVER=/etc/odoo/odoo.conf
export PYTHONPATH=/opt/odoo
echo "Reiniciando ODOO"
sudo /etc/init.d/odoo restart
echo "Actualizando ODOO"
/opt/odoo/odoo-bin -u base_vat_ar -d ${1?Error: Falta especificar la base de datos} --stop-after-init
cd /opt/odoo_addons_l10n_ar
echo "Ejecutando tests"
pytest -v -s --disable-pytest-warnings --junit-xml junit.xml
