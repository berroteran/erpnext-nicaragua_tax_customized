# Nicaragua Tax Receipt: Instrucciones del Proyecto

## Identidad y compatibilidad

`nicaragua_tax_receipt` es una aplicación instalable de Frappe / ERPNext. No
es un script ni una personalización manual de un sitio.

- Objetivo técnico: Frappe Framework 15 y ERPNext 15.
- Stack de desarrollo validado: Frappe 15.102.1, ERPNext 15.101.0 y Python
  3.12.3.
- La app debe extender ERPNext mediante hooks, patches, `Custom Field`,
  `Property Setter`, reportes estándar y controladores. No modificar el core
  de Frappe ni de ERPNext.
- Los nombres internos de campos son estables y pueden estar en inglés. Las
  etiquetas visibles para la operación nicaragüense deben estar en español.

## Propósito funcional

La aplicación registra y consulta comprobantes asociados a retenciones en
pagos de proveedores. La regla reusable vive en cada fila de una plantilla de
impuestos y el número real del comprobante se guarda en cada fila aplicada al
`Payment Entry`.

No confundir los conceptos:

- `Purchase Taxes and Charges`: fila de una plantilla de impuestos.
- `Advance Taxes and Charges`: fila de impuestos aplicada en un pago.
- `Payment Entry Deduction`: fila de deducción o pérdida aplicada en un pago.
- La plantilla define la regla; el pago guarda el dato transaccional.

## Módulos funcionales

### 1. Contabilidad: retenciones de impuestos

Extiende el flujo estándar de `Purchase Taxes and Charges Template` y
`Payment Entry`.

- `Purchase Taxes and Charges.custom_require_official_receipt_no`:
  `Requiere comprobante oficial`. Define por fila si la retención exige el
  comprobante.
- `Advance Taxes and Charges.custom_require_official_receipt_no`: copia la
  regla de la fila aplicada al pago y permanece editable.
- `Advance Taxes and Charges.custom_official_receipt_no`: `Número de
  comprobante oficial`, guardado por cada retención aplicada.
- El número debe ser obligatorio únicamente cuando la fila tiene la regla
  activada. La validación debe ejecutarse en servidor mediante
  `validate_payment_entry`; la interfaz no sustituye esa validación.
- Para `Payment Entry` de tipo `Pay` a un `Supplier`, las retenciones de
  reducción se calculan sobre la parte neta proporcional de las referencias
  aplicadas, no sobre el total con impuestos.
- La lógica cubre referencias estándar `Purchase Invoice`, `Purchase Order` y
  `Purchase Receipt`, y retenciones configuradas como `Deduct` con tasa
  positiva o `Add` con tasa negativa.
- Cualquier cambio al cálculo debe incluir pruebas que cubran importe parcial,
  total, tasa positiva, tasa negativa y ausencia de referencias válidas.

### 2. Operación de pagos y cheques

Extiende `Payment Entry` sin duplicar su lógica estándar.

- `Payment Entry.concepto`: campo obligatorio `Concepto`, tipo `Small Text`.
  Sirve para filtros, reportes, impresiones y formatos de cheque.
- El bloque `Información de Cheque` debe quedar después de `Concepto` y debe
  estar siempre visible.
- Cuando `mode_of_payment` es exactamente `Cheque`, `reference_no` y
  `reference_date` son obligatorios. Esta regla debe validarse en cliente y
  servidor.
- No se debe cambiar el comportamiento de otros modos de pago.

### 3. Proveedores e impresión de cheques

Extiende `Supplier`.

- `Supplier.impresion_cheque`: `Impresión en cheque`, campo de texto para
  formatos de impresión.
- Si ese campo ya existe en un sitio, conservar su campo y sus datos; no
  renombrarlo ni reemplazarlo.

### 4. Contabilidad: deducciones o pérdida

Extiende la tabla `Payment Entry Deduction`.

- `Payment Entry Deduction.custom_receipt_no`: `No Comprobante`, opcional.
- Debe estar visible por defecto en la tabla y habilitado para filtros,
  búsqueda global e informes.
- El valor pertenece a la fila de deducción, no al encabezado del pago.

### 5. Contabilidad: informes Nicaragua

Publica el reporte estándar `Comprobantes de retencion en la fuente` dentro
del workspace estándar `Accounting`.

- La tarjeta visible se llama `Informes Nicaragua`.
- El reporte exige `Desde` y `Hasta`.
- Consolida filas con comprobante de `Advance Taxes and Charges` y de
  `Payment Entry Deduction`.
- El selector de cuentas debe ofrecer únicamente cuentas utilizadas en esas dos
  tablas que correspondan a pasivo, balance y retención o impuesto; no debe
  ser un selector genérico de todas las cuentas.
- El reporte y el selector requieren permiso de lectura en `Payment Entry` y
  uno de los roles: `Accounts User`, `Accounts Manager`, `Auditor` o
  `System Manager`.

## Datos y desinstalación

- La app es multi-sitio: cada instalación, migración y desinstalación se
  ejecuta con `bench --site <sitio>` y debe afectar solamente ese sitio.
- Los patches y la reconciliación de metadata deben ser idempotentes.
- `after_install` y `after_migrate` deben crear o reconciliar campos, layout,
  etiquetas y reporte de forma defensiva.
- La desinstalación no debe borrar columnas ni valores guardados en DocTypes
  estándar. En particular, debe preservar `concepto`, los comprobantes de
  impuestos y deducciones, e `impresion_cheque`.
- No usar eliminación directa de datos o metadata como mecanismo normal de
  actualización. Un cambio destructivo exige preflight, respaldo, justificación
  y aprobación explícita.

## Reglas de implementación

- Antes de cambiar Frappe, ERPNext, un hook, metadata, cálculo o permiso,
  validar el comportamiento real en documentación oficial de v15, código core,
  código de esta app y metadata del sitio objetivo.
- No suponer nombres de campos, estructura de tablas, orden del formulario,
  permisos, ni comportamiento de plantillas. Verificarlos.
- Usar APIs y helpers de Frappe cuando existan; las consultas SQL deben ser
  parametrizadas y limitarse a casos donde aporten una necesidad real.
- Las reglas financieras, de obligatoriedad y permisos deben vivir en servidor.
- No depender de cambios manuales en Customize Form para que la app funcione.
- Mantener las etiquetas en español claro y los mensajes sin ambigüedad.
- Al renombrar o eliminar un artefacto versionado, agregar un patch idempotente
  que sanee por sitio las referencias antiguas de `Report`, `Workspace`, links
  y shortcuts.

## Flujo de validación y despliegue

- Probar primero en `testing15.inversionesbel.com` con
  `/home/frappe/frappe-bench-staging` y como usuario `frappe`.
- Antes de proponer otros sitios, ejecutar como mínimo revisión de diff,
  compilación con el Python del bench, importación de módulos Frappe y pruebas
  específicas de la lógica modificada.
- Validar instalación, migración repetida, visibilidad del reporte en
  `Accounting`, permisos y desinstalación no destructiva cuando el cambio
  afecte esos ámbitos.
- Solo aplicar en otros sitios tras una confirmación explícita del usuario.
