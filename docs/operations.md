# Instalación y Operación

## Instalación por sitio

```bash
cd /ruta/a/frappe-bench
bench get-app https://github.com/berroteran/erpnext-nicaragua_tax_customized.git
bench --site <sitio> install-app nicaragua_tax_receipt
bench --site <sitio> migrate
bench build --app nicaragua_tax_receipt
bench --site <sitio> clear-cache
```

La app debe instalarse y migrarse con `bench --site <sitio>`. El código de una
app se comparte dentro de un bench, pero campos, reportes, permisos y datos son
propios de cada sitio.

## Orden de despliegue

1. Aplicar y validar primero en `testing15.inversionesbel.com` usando
   `/home/frappe/frappe-bench-staging`.
2. Ejecutar migración, limpiar caché y verificar el formulario de pagos, el
   reporte y sus permisos.
3. Confirmar cálculo de retenciones con datos de prueba representativos.
4. Solicitar confirmación explícita antes de aplicar en otros sitios.

## Mantenimiento normal

`bench --site <sitio> migrate` ejecuta la reconciliación idempotente de la
app. Esta verifica los campos requeridos, los ajustes de layout, las etiquetas
y la publicación del reporte en `Accounting`.

No se requieren pasos manuales normales en Customize Form.

## Política para campos existentes

`Payment Entry.concepto` y `Supplier.impresion_cheque` pueden existir por una
personalización anterior. Si existen, la app los conserva y no borra ni renombra
sus datos.

Los campos propios de retención y deducción se crean o ajustan de manera
idempotente para mantener el comportamiento del módulo.

## Desinstalación no destructiva

```bash
bench --site <sitio> uninstall-app nicaragua_tax_receipt
```

Al desinstalar, Frappe puede eliminar documentos propios de la app, como su
reporte o su Module Def. La aplicación no elimina columnas ni valores de
negocio en DocTypes estándar.

Se preservan, entre otros:

- `Payment Entry.concepto`
- `Advance Taxes and Charges.custom_official_receipt_no`
- `Advance Taxes and Charges.custom_require_official_receipt_no`
- `Payment Entry Deduction.custom_receipt_no`
- `Supplier.impresion_cheque`

No ejecutar borrados directos de datos o metadata como procedimiento normal. Un
cambio destructivo requiere preflight, respaldo y aprobación explícita.
