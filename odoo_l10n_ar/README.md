REPOSITORIO DE L10N_AR V12
===========================
# RELEASE 11.0 (18/05/2020)
* Impuesto en grilla de impuestos en factura proveedor.
* Fecha de emision requerida en cheques propios en pagos.
* Leyenda y total en moneda de compañia en reporte de FE cuando la factura esta en moneda extranjera.


# TK-4764 (18/05/2020)
* Al re-seleccionar el partner en el pago se duplicaban imputaciones ya existentes, y a veces se traían imputaciones correspondientes a facturas incorrectas.

# TK-4490 (06/04/2020)
* Se envia el total de las lineas de facturas cuando es exportacion para luego que afip valide el total de los items con el total de la factura. (Dejaba enviar facturas exportacion con impupestos)

# RELEASE 9.0 (17/02/2020)
* Se permite rechazar un cheque vendido.
* Se permite generar el libro de iva digital.
* Se permite poder elegir que hacer con la diferencia de cambio en el momento del pago.

# HOTFIX TK-3843 (16/01/2020)
* Se permite cargar más de un punto de venta en los tipos de operación, para permitir que en el contexto de una compañía matriz con varias hijas cada compañía hija remita de forma distinta (ej.: una tenga talonario autoimpresor y otra, preimpreso).

# HOTFIX TK-3690 (27/12/2019)
* No se contemplaba para citi los tipos de factura de crédito unifico toda la logica para obtener tipo de documento dentro de account_invoice.

# RELEASE 8.0 (12/12/2019)
* Se agregan datos en el cobro para poder agregar una cotizacion manualmente.

# RELEASE 7.0 (02/12/2019)
* Cheques de terceros 'no a la orden':
    * Opción de registrar que el cheque es 'no a la orden'.
    * No permite el uso de cheques 'no a la orden'.
* Se arrastra la jurisdiccion a la factura automaticamente cuando se selecciona el cliente.
* Se da la posibilidad de inactivar metodos de pagos.
* Se agrega CBU en reporte de factura electronica.
* Se agrega chequeo de importe a cuenta en cobros y pagos para que no sea negativo, y se muestra en reporte en seccion de imputaciones.
* Al agregar una nota de credito de una factura no se arrastra la fecha de vencimiento.
* Se agregan cuit de pais paises al sistema.

# HOTFIX TK-3292 (30/10/2019)
* Se agrega validacion para que solo valide cuit de pais para las facturas fuera de Argentina, y se agrega validacion de factura de exportacion para solo "Tierra del fuego" en Argentina.

# HOTFIX TK-3126 (14/10/2019)
* Se agrega validación y commit en creación de factura desde POS para que no lance error si la FC no está en la BD.

# RELEASE 6.0 (26/09/2019)
* Se agrega script para automatizar los tests y jenkinsfile
* Se agregan descripción a todos los modelos para evitar los warnings y se eliminan labels duplicados de campos.
* Skipeamos el test de wsaa token que falla si se ejecuta seguido.

# HOTFIX TK-3035 (24/09/2019)
*Al generar el pago desde gastos se estaba llamando a una funcion inexistente.

# HOTFIX TK-2836 (30/08/2019)
*Se tiene en cuenta el campo de cotizacion de factura (currency_rate) para el total de la factura en moneda de la compañia.

# RELEASE 6.0
* CBU en cuentas bancarias.
* Factura de crédito electrónica:
    * Puntos de venta ahora tienen la opción de FCE.
    * Los documentos se nomenclan FCEC, NCEC, NDEC para clientes y FCEP, NCEP, NDEP para proveedores.
    * Contemplado el envío a WSFE.
* Obtención de moneda

# HOTFIX TK-2765 (21/08/2019)
*Se elimina campo duplicado en vista (currency_rate) para cotizacion de factura.

# HOTFIX TK-2593 (08/08/2019)
*Al registrar el pago de una NC mostraba una validacion erronea de validacion de montos imputados con pagados.

# HOTFIX TK-2574, TK-2604, TK-2592 (30/07/2019)
*Si la moneda necesita cotizacion a enviar y no se modifica la cotizacion a utilizar se setea en la cotizacion actual y se muestra en el reporte.
*Se corrige remito autoimpresor para que tome los datos correctos si tiene nombre o parent id
*Se corrigen atributos de campos de cotizacion cuando una factura es validada. A su vez se corrige cuando se cancela y se vuelve a borrador.
*Se corrige al imprimir factura electronica con 100% de descuento. (Division por cero)

# RELEASE 5.0
* Obtención de cotizaciones desde AFIP. Cron para el dólar.
* Se agrega cotizacion en facturas siempre y cuando la moneda tenga configurado que necesita cotizacion. Si es electronica se envia a AFIP la cotizacion y sale en el reporte. En el momento que valida la factura genera el asiento utilizando esa cotizacion.

**Actualizar las monedas necesarias para que aparezca la cotizacion en la factura (Ejemplo USD).**

# RELEASE 4.0
* Se agregan campos en POS. (Provincia, posición fiscal, tipo de documento)

# HOTFIX TK-2382, TK-2450
* Se corrige reporte de pago cuando la linea de imputacion no tiene account move asociado.
* Se corrige registro de pago para que no se pueda modificar el monto a pagar manualmente y se carguen los metodos de pago correctamente.

# HOTFIX
* Se corrige diseño de autoimpresor. Ahora esta el punto de venta en los tipos de transferencia.

# RELEASE 3.0
* Se agrega secuencia editable en grilla de talonarios desde punto de venta.
* Remito autoimpresor.
* Validacion de cuit (Contacto y empresa).
* Contactos: Datos contables ocultos segun permiso.
* Compañia: Se pueden agregar datos de la localizacion en el formulario.
* Error en pagos se traduce para que sea mas amigable con usuario. (La cantidad a pagar deber ser igual a la suma de los totales a imputar y el importe a cuenta)
* Libro mayor partner: Sale FC en datos de factura y sale el numero del pago en vez de REC.
* Se elimina impresion "Recibo de pago".
* Se coloca Numero de documento en vez de TAX ID.
* En reporte de factura electronica se coloca "Pagina" en vez de "Page".
* Plan de cuenta/Suscripciones/Codigos y modelos MULTICOMPANY.

**Actualizar base_codes, correr script "52-delete_old_rules.py" y ejecutar traducciones.**
