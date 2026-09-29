# Arquitectura Técnica

## Principios

La aplicación extiende ERPNext sin modificar su core. Usa `Custom Field`,
`Property Setter`, hooks, patches, un override de controlador y un Script
Report estándar de Frappe.

Las reglas financieras, permisos y obligatoriedad se validan en servidor. El
JavaScript de formulario solo complementa la experiencia de usuario.

## Hooks

- `after_install`: aprovisiona la metadata inicial del sitio.
- `after_migrate`: reconcilia metadata del sitio en cada migración.
- `doctype_js["Payment Entry"]`: mejora el cálculo mostrado, la grilla de
  impuestos y los requisitos de cheque.
- `doctype_js["Installed Applications"]`: muestra la versión Git desplegada
  sin cambiar el DocType estándar ni persistir metadata de Git.
- `doc_events["Payment Entry"]["validate"]`: valida comprobantes y cheque en
  servidor.
- `override_doctype_class["Payment Entry"]`: ajusta el cálculo de la base de
  retención.
- `after_uninstall`: limpia caché sin borrar datos de negocio.

## Componentes relevantes

- `nicaragua_tax_receipt/bootstrap.py`: ordena la reconciliación defensiva de
  campos, layout, etiquetas y reporte.
- `nicaragua_tax_receipt/bank_roles.py`: garantiza los roles bancarios y sus
  permisos sobre `Bank`.
- `nicaragua_tax_receipt/api/deployed_version.py`: endpoint propio y protegido
  que consulta la rama y el SHA del checkout instalado.
- `nicaragua_tax_receipt/public/js/installed_applications.js`: agrega solo la
  fila de esta app a la tabla compartida `Commits desplegados`.
- `nicaragua_tax_receipt/tax_receipt.py`: validaciones de comprobante y cheque.
- `nicaragua_tax_receipt/retention_base.py`: obtiene la base neta proporcional
  de cada referencia.
- `nicaragua_tax_receipt/overrides/payment_entry.py`: aplica esa base al
  cálculo de retención del controlador estándar.
- `nicaragua_tax_receipt/public/js/payment_entry.js`: actualiza la interfaz y
  solicita la base de cálculo al servidor.
- `nicaragua_tax_receipt/nicaragua_tax_receipt/report/`: implementación del
  reporte estándar de comprobantes.
- `nicaragua_tax_receipt/patches/`: historia versionada de creación y
  normalización de metadata.

## Reconciliación idempotente

`after_install` y `after_migrate` ejecutan el mismo bootstrap. La rutina crea
o corrige de forma defensiva los campos requeridos, la sección `Concepto`, la
posición y visibilidad de `Información de Cheque`, las etiquetas visibles y el
reporte de Contabilidad.

La app no debe depender de ajustes manuales en Customize Form para completar
una instalación normal.

## Seguridad y permisos

La validación de comprobantes, la obligatoriedad de información de cheque y el
control de acceso del reporte se ejecutan en servidor. Las consultas SQL del
reporte están parametrizadas. El selector de cuentas comprueba permisos antes
de devolver resultados.

La consulta de versión desplegada también se controla en servidor y solo está
disponible para `Administrator` y `System Manager`. No guarda rama ni SHA en la
base de datos. El frontend usa `textContent` y un namespace compartido para no
reemplazar los aportes de otras aplicaciones instaladas.
