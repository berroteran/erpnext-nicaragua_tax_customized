# Alcance Funcional por Módulo

## Objetivo de negocio

En una retención, la plantilla define una regla reutilizable y cada pago guarda
el comprobante real que fue emitido. El dato se conserva por fila para permitir
auditoría, conciliación documental, impresión y reportes.

No confundir:

- `Purchase Taxes and Charges`: fila de una plantilla de impuestos.
- `Advance Taxes and Charges`: fila de impuestos aplicada al pago.
- `Payment Entry Deduction`: fila de deducción o pérdida aplicada al pago.

## Contabilidad: retenciones de impuestos

La aplicación extiende el flujo entre `Purchase Taxes and Charges Template` y
`Payment Entry`.

- `Purchase Taxes and Charges.custom_require_official_receipt_no` tiene la
  etiqueta `Requiere comprobante oficial` y configura la regla por fila de
  plantilla.
- `Advance Taxes and Charges.custom_require_official_receipt_no` conserva esa
  regla por cada fila aplicada al pago.
- `Advance Taxes and Charges.custom_official_receipt_no` almacena el `Número
  de comprobante oficial` de esa retención.
- El número es obligatorio solo si la regla de la fila está activada.
- La validación corre en servidor; no es posible eludirla mediante API, import
  o un cambio de interfaz.
- Cada retención del mismo pago puede conservar un comprobante distinto.

### Base de cálculo

Para una Entrada de pago de tipo `Pay` a un proveedor, la app calcula las
retenciones de reducción sobre la porción neta proporcional de las referencias
aplicadas, no sobre el total que incluye impuestos.

La lógica cubre `Purchase Invoice`, `Purchase Order` y `Purchase Receipt`. Es
compatible con retenciones configuradas como `Deduct` con tasa positiva y como
`Add` con tasa negativa.

## Contabilidad: deducciones o pérdida

La aplicación extiende `Payment Entry Deduction` con:

- `custom_receipt_no`, etiqueta `No Comprobante`.
- Campo opcional y visible por defecto en la tabla.
- Disponible para filtros estándar, búsqueda global e informes.

El comprobante se guarda en la fila de deducción correspondiente, no en el
encabezado de `Payment Entry`.

## Contabilidad: informes Nicaragua

La aplicación publica el reporte estándar `Comprobantes de retencion en la
fuente` en el workspace estándar `Accounting`.

- La tarjeta se llama `Informes Nicaragua`.
- Requiere los filtros `Desde` y `Hasta`.
- Consolida filas con comprobante de `Advance Taxes and Charges` y
  `Payment Entry Deduction`.
- Ofrece solo cuentas distintas que ya aparecen en esas dos tablas y que son
  cuentas de pasivo, balance y retención o impuesto.
- No utiliza un selector genérico de todas las cuentas.
- Requiere permiso de lectura en `Payment Entry` y alguno de estos roles:
  `Accounts User`, `Accounts Manager`, `Auditor` o `System Manager`.

## Operación de pagos y cheques

La aplicación extiende `Payment Entry`.

- `concepto` tiene la etiqueta `Concepto`, es obligatorio y se usa en filtros,
  reportes, impresiones y formatos de cheque.
- La sección `Información de Cheque` aparece después de `Concepto` y permanece
  visible aunque el usuario todavía no haya seleccionado tercero o cuentas.
- La sección reemplaza visualmente el título estándar `ID de transacción`.
- Cuando `mode_of_payment` es exactamente `Cheque`, los campos
  `reference_no` y `reference_date` son obligatorios en interfaz y servidor.
- Los demás modos de pago no reciben esa obligatoriedad.

## Proveedores e impresión de cheques

La aplicación extiende `Supplier` con:

- `impresion_cheque`, etiqueta `Impresión en cheque`.
- Campo destinado a formatos de impresión de cheques.

Si el campo ya existía en un sitio, la aplicación no lo reemplaza, renombra ni
elimina sus valores.
