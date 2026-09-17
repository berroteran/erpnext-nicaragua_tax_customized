# Compatibilidad y Validación

## Versiones objetivo

La aplicación está diseñada para Frappe Framework 15 y ERPNext 15.

El desarrollo se validó originalmente con:

- Bench 5.29.1
- Frappe 15.102.1
- ERPNext 15.101.0
- Python 3.12.3

Fuera de Frappe y ERPNext 15 no se promete compatibilidad directa sin una
revisión y pruebas específicas.

## Factores que requieren revisión previa

- Un `Payment Entry` con personalizaciones extensas de layout o `field_order`.
- `Property Setter` previos sobre las secciones de pagos o cheque.
- Campos existentes con el mismo nombre y una definición incompatible.
- Un modo de pago de cheque cuyo nombre no sea exactamente `Cheque`.
- Diferencias de metadata entre tenants.

## Sitios verificados

Durante el desarrollo se verificó instalación o reconciliación de metadata en:

- `testing15.inversionesbel.com`
- `ferretex.inversionesbel.com`
- `gicosa.inversionesbel.com`
- `inversionesvesta.com`
- `erp.inversionesbel.com`

La validación inicial de cada cambio debe ocurrir en
`testing15.inversionesbel.com`. La existencia de una instalación previa no
sustituye las pruebas funcionales para un cliente, versión o metadata distintos.
