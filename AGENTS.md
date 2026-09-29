# Instrucciones para Agentes y Mantenedores

## Identidad

`nicaragua_tax_receipt` es una aplicación instalable para Frappe Framework 15
y ERPNext 15. No es un script ni una personalización manual de un sitio.

- No modificar el core de Frappe ni ERPNext.
- Usar hooks, patches, `Custom Field`, `Property Setter`, reportes estándar y
  controladores para extender el sistema.
- Mantener nombres internos de campos estables y etiquetas de usuario en
  español claro.
- La app se validó con Frappe 15.102.1, ERPNext 15.101.0 y Python 3.12.3.

## Documentación obligatoria

Antes de cambiar una funcionalidad, leer el documento que corresponde:

- [Alcance funcional por módulo](docs/functional-scope.md)
- [Arquitectura técnica](docs/architecture.md)
- [Instalación y operación](docs/operations.md)
- [Compatibilidad y validación](docs/compatibility.md)

El alcance funcional se divide en estos módulos:

- Contabilidad: retenciones de impuestos.
- Contabilidad: deducciones o pérdida.
- Contabilidad: informes Nicaragua.
- Operación de pagos y cheques.
- Proveedores e impresión de cheques.
- Administración técnica: versión desplegada de la aplicación.

No asumir comportamiento, campos, permisos, layout ni fórmulas. Validarlos en
la documentación oficial de Frappe/ERPNext 15, código core, código de la app y
metadata real del sitio objetivo.

## Reglas no negociables

- Las reglas financieras, de obligatoriedad y permisos viven en servidor. El
  JavaScript solo mejora la interfaz.
- Patches, bootstrap y reconciliación de metadata deben ser idempotentes.
- No depender de cambios manuales en Customize Form para una instalación normal.
- Consultas SQL deben ser parametrizadas y justificadas.
- Al renombrar o retirar reportes, workspaces, enlaces o shortcuts, crear un
  patch idempotente que sanee referencias antiguas por sitio.
- No introducir dependencias externas sin revisar su compatibilidad con Frappe
  y ERPNext 15.

## Multisitio, datos y desinstalación

- El código se comparte dentro de un bench; metadata y datos son por sitio.
- Ejecutar instalación, migración, pruebas y desinstalación con
  `bench --site <sitio>`.
- Un cambio aplicado en un sitio no significa que esté aplicado en otro.
- La desinstalación debe preservar columnas y valores de negocio guardados en
  DocTypes estándar. No borrar datos o metadata directamente como parte de una
  actualización normal.
- Todo cambio destructivo exige preflight, respaldo, justificación y aprobación
  explícita.

## Validación y despliegue

- Probar primero en `testing15.inversionesbel.com` con
  `/home/frappe/frappe-bench-staging`, usando el usuario `frappe`.
- Validar el código con el Python del bench, no con Python del sistema.
- Según el cambio, validar migración repetida, permisos, reporte en
  `Accounting`, cálculo de retenciones e instalación/desinstalación por sitio.
- Solicitar confirmación explícita antes de aplicar cambios en otros sitios.
