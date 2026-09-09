# Nicaragua Tax Receipt - Reglas Para Agentes

Este proyecto es una aplicacion de Frappe / ERPNext 15.

No tratar este repositorio como un script aislado. Todo cambio debe respetar el
ciclo normal de una app Frappe: instalar por sitio, migrar por sitio, validar
metadata por sitio y mantener compatibilidad con benches multisitio.

## Contexto tecnico obligatorio

- Framework objetivo: Frappe 15.
- Aplicacion objetivo: ERPNext 15.
- Python objetivo: la version soportada por el bench Frappe / ERPNext 15 donde
  se instala la app. En este servidor se valido con Python 3.12.3.
- Base de datos: MariaDB gestionada por Frappe/Bench.
- La app extiende DocTypes estandar mediante `Custom Field`, `Property Setter`,
  hooks, patches y reportes.
- La app no debe modificar archivos del core de Frappe ni de ERPNext.

## Multisitio y multitenant

- El codigo bajo `apps/nicaragua_tax_receipt` es compartido por todos los
  sitios del mismo bench.
- La metadata y los datos son por sitio.
- Todo comando de instalacion, migracion, prueba o desinstalacion debe usar
  `bench --site <sitio>`.
- Un cambio aplicado en un sitio no debe asumirse aplicado en otro sitio.
- Cada patch debe ser idempotente y seguro ante sitios parcialmente migrados.
- Antes de usar un DocType, campo, reporte, workspace, card o shortcut, validar
  que exista o crearlo de forma defensiva.

## Regla de prueba

Primero se prueba siempre en `testing15.inversionesbel.com` usando el bench de
staging:

```bash
sudo -u frappe bash -lc 'cd /home/frappe/frappe-bench-staging && bench --site testing15.inversionesbel.com migrate'
```

Solo despues de validar en `testing15.inversionesbel.com` se puede proponer
aplicar a otros sitios. Para pasar a otros sitios se requiere confirmacion
explicita del usuario.

## Instalacion

La instalacion debe:

- crear los campos requeridos por la app si no existen
- adoptar campos funcionales existentes cuando sea seguro
- preservar valores ya grabados
- publicar el reporte en el workspace estandar de Contabilidad
- limpiar cache del sitio despues de reconciliar metadata
- no depender de ajustes manuales en Customize Form

## Desinstalacion

La desinstalacion debe ser no destructiva.

La app no debe borrar:

- columnas agregadas a DocTypes estandar
- valores guardados en `Payment Entry`
- valores guardados en `Advance Taxes and Charges`
- valores guardados en `Payment Entry Deduction`
- valores guardados en `Supplier`
- datos historicos usados en impresiones, reportes o auditoria

Si alguna vez se necesita borrar metadata o datos, debe existir un plan escrito,
backup, prueba en `testing15.inversionesbel.com` y aprobacion explicita del
usuario.

## Programacion

- Usar APIs de Frappe cuando existan.
- Usar SQL parametrizado cuando sea necesario consultar reportes o metadata.
- No asumir que un campo existe por haber existido en otro sitio.
- No asumir que el orden de campos del core es identico entre sitios.
- No asumir que una personalizacion manual existe en todos los tenants.
- Mantener validaciones criticas del lado servidor.
- Mantener JavaScript solo como ayuda de interfaz.
- Mantener patches y hooks idempotentes.
- No introducir dependencias externas sin justificar compatibilidad con Frappe /
  ERPNext 15.

## Documentacion

El README debe explicar en lenguaje simple:

- que esta app extiende ERPNext 15
- que problema de negocio resuelve
- que campos agrega
- que reportes agrega
- como se instala
- como se migra
- que versiones fueron validadas
- que la app es multisitio
- que la desinstalacion no borra datos de negocio

