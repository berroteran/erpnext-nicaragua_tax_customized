## Nicaragua Tax Receipt

Aplicacion Frappe / ERPNext 15 para Nicaragua.

Este repositorio es una app de ERPNext. No es un script suelto, no es un
parche manual y no modifica directamente el core de Frappe ni de ERPNext.

Todas las decisiones tecnicas de esta app deben seguir las reglas y practicas
propias de Frappe Framework 15 y ERPNext 15:

- instalacion por sitio con `bench --site <sitio> install-app`
- migracion por sitio con `bench --site <sitio> migrate`
- metadata versionada por patches, hooks y archivos de la app
- validaciones criticas en servidor
- uso de `Custom Field` y `Property Setter` para extender DocTypes estandar
- consultas SQL parametrizadas cuando el framework no provee una API adecuada
- compatibilidad con Python soportado por Frappe / ERPNext 15
- idempotencia en patches y rutinas de mantenimiento
- comportamiento seguro en benches multisitio

App reusable para Frappe / ERPNext 15 que agrega control de comprobantes
oficiales sobre retenciones aplicadas en `Payment Entry` a partir de
`Purchase Taxes and Charges Template`, y que ademas versiona campos utiles para
impresion y operacion como `concepto` en `Payment Entry` e `impresion_cheque`
en `Supplier`.

## Reglas del proyecto

Estas reglas son parte del contrato tecnico del proyecto:

- La app debe funcionar como una app normal de Frappe / ERPNext 15.
- La app debe poder instalarse en un sitio sin depender de pasos manuales en la
  interfaz.
- La app debe poder migrarse varias veces sin duplicar campos, reportes,
  workspaces, cards, shortcuts ni property setters.
- La app debe estar preparada para benches multisitio o multitenant.
- Cada instalacion, migracion o desinstalacion debe afectar solo al sitio sobre
  el que corre el comando `bench --site`.
- La app no debe asumir que todos los sitios tienen la misma metadata manual.
- La app debe validar y crear defensivamente los campos que necesita antes de
  usarlos.
- La app no debe borrar datos de negocio al desinstalarse.
- La desinstalacion no debe eliminar columnas ni valores guardados en DocTypes
  estandar como `Payment Entry`, `Advance Taxes and Charges`,
  `Payment Entry Deduction` o `Supplier`.
- Si en el futuro se propone una limpieza destructiva, debe tener backup,
  justificacion tecnica y aprobacion explicita antes de implementarse.
- Las etiquetas visibles para usuarios deben estar en espanol cuando el flujo
  funcional sea para operaciones en Nicaragua.
- Los nombres internos de campos pueden estar en ingles cuando sea conveniente,
  pero deben ser estables, claros y compatibles con Frappe.

## Lenguaje y claridad

El proyecto debe mantenerse escrito de forma simple y sin ambiguedad.

Para evitar confusion en humanos y LLM:

- usar `app` o `aplicacion` para referirse a este repositorio
- usar `sitio` para cada tenant de Frappe / ERPNext
- usar `bench` para la instalacion fisica compartida
- usar `migrate` para aplicar patches y reconciliar metadata del sitio
- usar `Custom Field` para campos agregados sobre DocTypes estandar
- usar `Property Setter` para ajustes de layout o propiedades de campos
- evitar llamar "manual" a un cambio que debe quedar versionado en la app
- evitar instrucciones que dependan de recordar pasos no documentados

Antes de cambiar comportamiento del framework, primero se debe validar contra:

- documentacion oficial de Frappe / ERPNext 15
- codigo fuente real del core instalado
- metadata real del sitio de prueba
- patrones existentes dentro de esta app
- pruebas en `testing15.inversionesbel.com`

## Objetivo de negocio

En muchos flujos contables y fiscales de Nicaragua, cuando un pago aplica
retenciones de impuestos, no basta con calcular el monto retenido. Tambien se
necesita registrar el numero de comprobante oficial asociado a esa retencion
para fines de:

- control interno
- auditoria
- conciliacion documental
- trazabilidad por pago
- reportes fiscales y administrativos

ERPNext maneja bien la aplicacion de plantillas de impuestos y la generacion de
las filas de retencion en `Payment Entry`, pero no trae de base un mecanismo
especifico para exigir y persistir ese numero de comprobante oficial como parte
del flujo.

Esta app existe para cerrar esa brecha sin modificar el core de ERPNext.

## Razon de existencia

La necesidad funcional que resuelve es esta:

- una `Purchase Taxes and Charges Template` define la estructura de retencion
- al aplicarla en `Payment Entry`, ERPNext copia las filas a
  `Advance Taxes and Charges`
- cada fila de retencion puede necesitar su propio numero de comprobante oficial
- ese numero debe quedar visible, buscable y reportable dentro del sistema

La app separa correctamente:

- la regla reusable por fila de plantilla
- el dato transaccional propio de cada fila aplicada en el pago
- la trazabilidad detallada de cada fila de retencion

## Características por módulo

La aplicación está organizada por módulos funcionales de ERPNext. El detalle
técnico para mantenimiento y evolución se encuentra en [AGENTS.md](AGENTS.md).

### Contabilidad: retenciones de impuestos

Este es el módulo principal de la aplicación. Extiende las plantillas de
impuestos de compra y las retenciones aplicadas en `Payment Entry`.

- Agrega `Requiere comprobante oficial` por fila de
  `Purchase Taxes and Charges`.
- Copia esa regla a cada fila de `Advance Taxes and Charges` al aplicar la
  plantilla en una Entrada de pago.
- Agrega `Número de comprobante oficial` por cada fila de retención aplicada.
- Exige el número únicamente en las filas cuya regla está activada.
- Valida esa obligatoriedad en servidor para impedir omisiones por API, import
  o modificaciones del navegador.
- Mantiene trazabilidad independiente para cada retención; dos impuestos en un
  mismo pago pueden tener comprobantes distintos.
- Corrige el cálculo de retenciones de pagos a proveedores para usar el valor
  neto proporcional de la referencia, no el total con impuestos.
- Soporta el patrón `Deduct` con tasa positiva y el patrón `Add` con tasa
  negativa que ERPNext puede generar al traer una plantilla.

La regla vive por fila porque la plantilla define una condición reutilizable,
mientras que el número de comprobante es un dato real e histórico de cada pago.

### Contabilidad: deducciones o pérdida

Extiende las filas de `Payment Entry Deduction`.

- Agrega el campo opcional `No Comprobante`.
- Lo muestra por defecto en la tabla, sin que el usuario tenga que activarlo.
- Lo deja disponible para filtros estándar, búsqueda global e informes.
- Conserva el dato en la fila específica de deducción, no en el encabezado del
  pago.

### Contabilidad: informes Nicaragua

Integra reportes propios de la app dentro del workspace estándar `Accounting`.

- Crea la tarjeta `Informes Nicaragua`.
- Publica el reporte `Comprobantes de retencion en la fuente`.
- El reporte exige un rango de fechas.
- Consolida comprobantes capturados en `Impuestos` y en
  `Deducciones o Pérdida`.
- Permite filtrar por cuentas utilizadas realmente en esas dos tablas, sin
  repetirlas y sin mostrar un catálogo genérico de cuentas.
- El selector limita las opciones a cuentas de pasivo, de balance, asociadas a
  impuestos o retenciones.
- Respeta permisos de lectura de `Payment Entry` y los roles contables del
  reporte.

### Operación de pagos y cheques

Extiende el formulario estándar `Payment Entry` para documentar el pago y la
emisión de cheques.

- Agrega `Concepto`, obligatorio, para el detalle operativo del pago.
- `Concepto` queda disponible para filtros, reportes, impresiones y formatos
  de cheque.
- Ubica la sección `Concepto` antes de la información de cheque.
- Renombra `ID de transacción` como `Información de Cheque`.
- Mantiene siempre visible el bloque `Información de Cheque`, incluso antes de
  seleccionar proveedor, cliente o cuentas.
- Cuando `Modo de pago` es exactamente `Cheque`, exige `Cheque / No. de
  Referencia` y `Cheque / Fecha de referencia` en interfaz y servidor.

### Proveedores e impresión de cheques

Extiende el maestro `Supplier`.

- Agrega `Impresión en cheque` para textos usados por formatos de impresión.
- Si un sitio ya posee ese campo, la aplicación lo conserva y no reemplaza ni
  elimina sus datos.

### Plataforma, instalación y compatibilidad

- Es una app independiente y versionable por Git; no modifica el core de
  ERPNext ni Frappe.
- Crea y reconcilia su metadata por `after_install` y `after_migrate`.
- La reconciliación es idempotente y corrige campos, etiquetas, layout y
  publicación del reporte sin requerir pasos manuales normales.
- Está preparada para benches multisitio: cada acción se ejecuta por sitio.
- Su desinstalación preserva los valores históricos capturados en DocTypes
  estándar, incluidos comprobantes, concepto e impresión de cheque.

## Arquitectura tecnica

### Hooks

- `after_install`
- `doctype_js["Payment Entry"]`
- `doc_events["Payment Entry"]["validate"]`
- `after_migrate`
- `after_uninstall`

### Componentes

- `nicaragua_tax_receipt/hooks.py`
  registra hooks de frontend y backend
- `nicaragua_tax_receipt/bootstrap.py`
  centraliza la reconciliacion de metadata en orden: campos, layout, labels y
  publicacion del reporte
- `nicaragua_tax_receipt/install.py`
  ejecuta bootstrap inicial al instalar la app en un sitio
- `nicaragua_tax_receipt/tax_receipt.py`
  valida el comprobante por fila en servidor
- `nicaragua_tax_receipt/public/js/payment_entry.js`
  expone en la grilla de impuestos los campos por fila
- `nicaragua_tax_receipt/patches/v1_0/add_tax_receipt_custom_fields.py`
  crea los campos de retencion por fila y oculta los campos viejos del enfoque
  por encabezado
- `nicaragua_tax_receipt/patches/v1_1/add_payment_entry_concept_field.py`
  adopta o crea `Payment Entry.concepto`
- `nicaragua_tax_receipt/patches/v1_1/add_payment_entry_deduction_receipt_field.py`
  crea `Payment Entry Deduction.custom_receipt_no` como campo opcional visible
  en la grilla
- `nicaragua_tax_receipt/patches/v1_1/add_supplier_check_print_field.py`
  crea `Supplier.impresion_cheque` si el sitio no lo tiene
- `nicaragua_tax_receipt/patches/v1_1/ensure_payment_entry_concept_layout.py`
  crea la seccion `Concepto` y ubica el campo debajo de esa seccion
- `nicaragua_tax_receipt/patches/v1_1/ensure_retention_receipt_report.py`
  publica el reporte de comprobantes, crea un shortcut y agrega la tarjeta
  `Informes Nicaragua` en `Accounting`
- `nicaragua_tax_receipt/patches/v1_1/move_payment_entry_transaction_section_below_concept.py`
  mueve la sección `Información de Cheque` debajo de `Concepto`
- `nicaragua_tax_receipt/patches/v1_1/reorder_payment_entry_field_order.py`
  normaliza el `field_order` del `Payment Entry` para reflejar ese layout
- `nicaragua_tax_receipt/patches/v1_1/align_cheque_section_visibility.py`
  reemplaza la visibilidad estandar del bloque de cheque para que dependa de
  `Modo de pago = Cheque` en lugar de esperar `paid_from` y `paid_to`
- `nicaragua_tax_receipt/patches/v1_1/normalize_spanish_labels.py`
  normaliza etiquetas visibles a espanol, incluyendo labels estandar del core
  cuando el modulo necesita dejar la interfaz coherente en todos los sitios
- `nicaragua_tax_receipt/maintenance.py`
  ejecuta una rutina idempotente de autoajuste en cada migracion para corregir
  metadata desviada sin depender de intervencion manual
- `nicaragua_tax_receipt/uninstall.py`
  limpia cache al desinstalar sin borrar columnas ni valores de negocio
  capturados en DocTypes estandar de ERPNext

## Operacion autonoma del modulo

La intencion del modulo es que no dependa de un agente LLM para dejar un sitio
funcionando correctamente.

Por eso, desde esta version:

- los parches siguen existiendo como historia versionada
- pero ademas el app ejecuta una rutina de reconciliacion en cada
  `bench migrate`
- esa rutina revalida campos, labels, orden del layout y visibilidad del bloque
  de cheque
- si un sitio tenia metadata vieja o parcialmente aplicada, el modulo intenta
  autocorregirla

En la practica, el flujo esperado para otro sitio es:

1. instalar el app
2. correr `bench --site <sitio> migrate`
3. dejar que `after_migrate` aplique los ajustes de metadata

Eso reduce al minimo los casos donde alguien tenga que entrar manualmente a
arreglar `Property Setter`, `Custom Field` o `field_order`.

## Desinstalacion no destructiva

La app esta disenada para que `bench --site <sitio> uninstall-app
nicaragua_tax_receipt` no borre datos de negocio capturados por los usuarios.

En Frappe, al desinstalar una app se eliminan documentos propios del modulo,
como `Module Def`, `Report`, `Workspace`, `Page` o metadata enlazada al modulo de
la app. Eso es esperado.

Esta app no elimina los `Custom Field` creados sobre DocTypes estandar de
ERPNext. Por eso se preservan las columnas y valores guardados en:

- `Payment Entry.concepto`
- `Advance Taxes and Charges.custom_official_receipt_no`
- `Advance Taxes and Charges.custom_require_official_receipt_no`
- `Payment Entry Deduction.custom_receipt_no`
- `Supplier.impresion_cheque`

El resultado esperado es que al desinstalar se retire la funcionalidad activa de
la app y sus reportes propios, pero no se pierda la historia documental ya
capturada en pagos, retenciones, deducciones o proveedores.

## Nota funcional sobre cheques

ERPNext estandar controla la visibilidad de `reference_no` y `reference_date`
con una regla orientada a cuando ya existen `paid_from` y `paid_to`.

En la practica eso provoca que:

- el usuario seleccione `Modo de pago = Cheque`
- pero el bloque de cheque todavia no aparezca
- hasta despues de escoger tercero o hasta que ERPNext derive las cuentas

Para este modulo, ese comportamiento no es ideal porque el bloque de
identificacion bancaria y de cheque debe estar disponible siempre.

Por eso la app ajusta la visibilidad del bloque `Información de Cheque` y de
sus campos para que siempre esten visibles.

También renombra esa sección a `Información de Cheque` para que el usuario vea
un encabezado mas claro y alineado al proceso de negocio.

La regla de negocio queda separada asi:

- visibilidad: siempre visible
- obligatoriedad: solo cuando `Modo de pago = Cheque`

## Flujo de usuario

1. El usuario define o edita una `Purchase Taxes and Charges Template`.
2. Marca por fila si esa retencion requiere comprobante oficial.
3. En un `Payment Entry`, selecciona la plantilla de impuestos.
4. ERPNext copia las filas al detalle `Advance Taxes and Charges`.
5. Cada fila requerida debe recibir su propio `Official Receipt No`.
6. El servidor valida que no se pueda guardar vacio en las filas obligatorias.
7. El usuario puede usar `concepto` en el pago para impresiones, reportes y
   formatos de cheque.
8. El proveedor puede usar `impresion_cheque` en formatos de impresion.
9. Si el modo de pago es `Cheque`, `Cheque / No. de Referencia` y
   `Cheque / Fecha de referencia` pasan a ser obligatorios.
10. La sección `Información de Cheque` se acomoda debajo de `Concepto`.

## Beneficios

- mejora control fiscal y documental
- evita omisiones manuales
- reduce dependencia de notas libres o archivos externos
- hace el dato consultable dentro de ERPNext
- permite transportar la solucion entre instancias por Git
- evita tocar `erpnext` core

## Version Base De Desarrollo

Esta app fue desarrollada y validada originalmente sobre este stack:

- Bench `5.29.1`
- Frappe `15.102.1`
- ERPNext `15.101.0`
- Python `3.12.3`

Sitios de validacion usados durante el desarrollo:

- `testing15.inversionesbel.com`
- `ferretex.inversionesbel.com`
- `gicosa.inversionesbel.com`
- `inversionesvesta.com`
- `erp.inversionesbel.com`

## Compatibilidad Esperada

La app esta orientada a:

- Frappe `v15`
- ERPNext `v15`

Y fue probada en una rama muy cercana a:

- Frappe `15.102.x`
- ERPNext `15.101.x`

## Advertencia De Compatibilidad

Si intentas instalar esta app en otra version de Frappe o ERPNext, puede
requerir ajustes. Eso es especialmente cierto si:

- el `Payment Entry` fue muy personalizado manualmente
- existen `Property Setter` previos sobre `field_order`
- ya existen campos custom con el mismo nombre pero con otra configuracion
- el modo de pago para cheque no se llama exactamente `Cheque`
- tu rama de Frappe o ERPNext cambió estructura, metadata o renderizado del
  `Payment Entry`

En resumen: el modulo esta pensado para ERPNext 15 y Frappe 15; fuera de ese
marco no se puede prometer compatibilidad directa sin pruebas.

## Sitios Verificados

Instalaciones verificadas sobre este servidor:

- `testing15.inversionesbel.com`
- `ferretex.inversionesbel.com`
- `gicosa.inversionesbel.com`
- `inversionesvesta.com`
- `erp.inversionesbel.com`

En esos sitios se confirmo al menos:

- instalacion del app
- ejecucion de `migrate`
- creacion o adopcion de `concepto`
- creacion o adopcion de `impresion_cheque`
- campos por fila de retencion
- label `Información de Cheque`
- visibilidad permanente del bloque de cheque

Esto no reemplaza QA funcional por cada cliente, pero si confirma que la rutina
de autoajuste del modulo puede aterrizar la metadata principal sin depender de
intervencion manual posterior.

## Instalacion

### En un bench existente

```bash
cd /home/frappe/frappe-bench
bench get-app <URL_DEL_REPO>
bench --site <SITIO> install-app nicaragua_tax_receipt
bench --site <SITIO> migrate
bench build --app nicaragua_tax_receipt
bench clear-cache
```

### Ejemplo en este servidor

```bash
sudo -u frappe bash -lc '
cd /home/frappe/frappe-bench &&
bench --site testing15.inversionesbel.com install-app nicaragua_tax_receipt &&
bench --site testing15.inversionesbel.com migrate &&
bench build --app nicaragua_tax_receipt &&
bench --site testing15.inversionesbel.com clear-cache
'
```

## Versionado y despliegue

La app esta pensada para administrarse como repositorio Git independiente.

Esto permite:

- promover cambios por ramas y pull requests
- instalar la misma solucion en varios sitios ERPNext
- mantener historial de cambios funcionales y tecnicos
- desplegar fixes y mejoras sin tocar el core
- hacer que `migrate` sirva tambien como rutina de reconciliacion de metadata

## Politica de compatibilidad con sitios existentes

La app usa dos estrategias distintas:

### Campos propios de la app

Para los campos de retencion de esta app, el patch puede crearlos o ajustarlos
porque forman parte del comportamiento funcional esperado del modulo.

### Campos funcionales que algunos sitios ya tienen manualmente

Para estos campos la politica es conservadora:

- `Payment Entry.concepto`
- `Supplier.impresion_cheque`

La regla es:

- si el campo no existe, la app lo crea
- si el campo ya existe, la app lo ignora
- no se borran datos existentes
- no se renombran campos existentes

Esto permite instalar la app en sitios heterogeneos sin perder informacion ni
romper personalizaciones previas.

## Mantenimiento operativo

En la version actual, el modulo intenta ser autosuficiente para despliegue y
correccion de metadata:

- `bench --site <sitio> install-app nicaragua_tax_receipt`
- `bench --site <sitio> migrate`

Con eso, el hook `after_migrate` ejecuta una reconciliacion idempotente para:

- campos custom del flujo fiscal
- seccion `Concepto`
- posicion del bloque de cheque
- label `Información de Cheque`
- visibilidad del bloque de cheque
- labels en espanol

Adicionalmente, `after_install` aplica la misma reconciliacion en la instalacion
inicial del sitio para evitar escenarios donde el reporte o la UI queden
publicados antes de que existan todos los campos requeridos.

La meta de diseno es que el modulo no dependa de un agente LLM para completar
ajustes normales de instalacion en otros sitios con Frappe / ERPNext 15.

## Consideraciones

- La app crea `Custom Fields` por patch, no tocando DocTypes core.
- La app tambien crea o ajusta `Property Setter` para layout del `Payment Entry`
  cuando hace falta ordenar secciones.
- La validacion principal corre en servidor para evitar saltos por API o import.
- El comportamiento visual corre en cliente para mejorar la experiencia.
- El layout final del formulario puede variar si el sitio ya tiene
  personalizaciones fuertes en `field_order`.
- La regla de cheque depende hoy del valor exacto `Cheque` en
  `mode_of_payment`.
- Las etiquetas visibles del flujo principal deben mantenerse en espanol claro.
- Los nombres internos de campos deben mantenerse estables para no romper
  datos, reportes ni formatos de impresion.

## Posibles mejoras futuras

- traducciones formales `es`
- print formats que muestren el comprobante oficial
- soporte para mas tipos de documentos fiscales relacionados
- naming y labels mas orientados a normativa local

## Desarrollo

Esta app usa el flujo normal de apps Frappe.

Herramientas de calidad presentes en el scaffold:

- `pre-commit`
- `ruff`
- `eslint`
- `prettier`
- `pyupgrade`

## Licencia

`mit`
