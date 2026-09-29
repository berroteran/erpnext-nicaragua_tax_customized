# Nicaragua Tax Receipt

Aplicación para Frappe Framework 15 y ERPNext 15 que incorpora trazabilidad de
comprobantes de retención en las Entradas de pago de Nicaragua.

No modifica el core de Frappe ni ERPNext. Extiende sus DocTypes estándar con
metadata versionada, validaciones de servidor, patches y reportes.

## Qué resuelve

Cuando un pago aplica una retención, el número de comprobante oficial debe
quedar guardado por cada impuesto o deducción, no como una nota externa ni como
un dato único en el encabezado del pago.

La aplicación permite definir la regla en la plantilla de impuestos, capturar
el comprobante en cada fila aplicada y consultarlo desde Contabilidad.

## Características principales

- Comprobantes oficiales obligatorios por fila de retención cuando la plantilla
  lo exige.
- Cálculo de retenciones a proveedores sobre la base neta proporcional de las
  referencias aplicadas.
- Campo `No Comprobante` en `Deducciones o Pérdida`.
- Campo `Concepto` para pagos y `Impresión en cheque` para proveedores.
- Información de cheque siempre visible y obligatoria solo para pagos con modo
  de pago `Cheque`.
- Roles `Bank User` y `Bank Manager` con permisos sobre `Bank`.
- Versión declarada, rama y commit desplegados visibles para administradores en
  `Installed Applications`, sin almacenar metadata Git en la base de datos.
- Reporte `Comprobantes de retencion en la fuente` dentro de la tarjeta
  `Informes Nicaragua` del workspace estándar `Accounting`.
- Instalación por sitio, reconciliación idempotente y desinstalación que
  preserva datos históricos de negocio.

## Requisitos

- Frappe Framework 15.
- ERPNext 15.
- Python compatible con el bench. El desarrollo se validó con Python 3.12.3,
  Frappe 15.102.1 y ERPNext 15.101.0.

## Instalación rápida

```bash
cd /ruta/a/frappe-bench
bench get-app https://github.com/berroteran/erpnext-nicaragua_tax_customized.git
bench --site <sitio> install-app nicaragua_tax_receipt
bench --site <sitio> migrate
bench build --app nicaragua_tax_receipt
bench --site <sitio> clear-cache
```

Pruebe primero en un sitio de pruebas. En este entorno, el sitio de validación
es `testing15.inversionesbel.com` dentro de
`/home/frappe/frappe-bench-staging`.

## Documentación

- [Alcance funcional por módulo](docs/functional-scope.md)
- [Arquitectura técnica](docs/architecture.md)
- [Instalación y operación](docs/operations.md)
- [Compatibilidad y sitios validados](docs/compatibility.md)
- [Instrucciones para agentes y mantenedores](AGENTS.md)

## Licencia

MIT
