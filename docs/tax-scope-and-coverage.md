# Contexto tributario y cobertura

## Objetivo de negocio

La aplicación `nicaragua_tax_receipt`, para Frappe/ERPNext 15, debe permitir
configurar el tratamiento tributario de las operaciones de Nicaragua y mantener
su trazabilidad contable y documental. El alcance solicitado comprende:

- IVA configurable por producto y operación, con tratamiento de exenciones.
- Precios con IVA incluido o separado. Un precio con IVA incluido no implica
  que ese IVA forme parte del costo: puede desglosarse hacia una cuenta de IVA.
- IVA acreditable de compras, IVA por pagar de ventas e IVA no recuperable
  incorporado al costo cuando corresponda, con cuentas diferenciadas.
- Retenciones de IR para la DGI, con código, hecho generador, tasa, base,
  condiciones y vigencia propios.
- Retenciones de IMI para la alcaldía correspondiente, separadas del IR/DGI.
  El caso municipal solicitado es 1%; no se presume aplicable universalmente.
- Número de comprobante por fila de impuestos y de deducciones del pago.
  Por ejemplo, un mismo pago puede tener comprobantes distintos para IR 2%
  e IMI 1%. La obligatoriedad se configura por fila de plantilla de impuestos.

Este es un objetivo funcional, no una declaración de cumplimiento integral de
la legislación ni una confirmación de configuración en todos los sitios.

## Catálogo aportado por el propietario

Fuente: fotografía titulada «Aviso: Catálogo de códigos de retenciones»,
aportada en la conversación el 2026-11-16. El texto indica vigencia desde
marzo de 2019 y menciona la Ley 822 y su Reglamento reformados. La fotografía
termina en el código 42; no acredita que ese sea el final del catálogo.
La siguiente transcripción resume exclusivamente lo visible en la imagen.

| Código | Concepto resumido de la fotografía | Alícuota indicada |
|---|---|---|
| 11 | Renta del trabajo, retención a cuenta | Tabla IR |
| 21 | Bienes y servicios pagados mediante tarjeta de crédito/débito | 1.5% |
| 22 | Compras de bienes y servicios en general | 2% |
| 23 | Construcción | 2% |
| 24 | Alquiler y arrendamiento | 2% |
| 25 | Compraventa agropecuaria | 3% |
| 26 | Metro cúbico de madera en rollo | 5% |
| 27 | Servicios profesionales o técnicos superiores de persona natural | 10% |
| 28 | Importador, próxima importación | 10% |
| 29 | Importador no inscrito, monto mayor a US$2,000 | 10% |
| 210 | Exportador irregular no inscrito, monto mayor a US$500 | 10% |
| 211 | Otras actividades | 10% |
| 31 | Indemnización adicional a cinco meses, excedente de C$500,000 | 15% |
| 32 | Dietas a residentes | 25% |
| 33 | Dietas de concejales | 12.5% |
| 34 | Dietas a no residentes | 25% |
| 35 | Rentas del trabajo a no residentes | 20% |
| 41 | Servicios profesionales al Estado, residentes, financiación externa | 10% |
| 42 | Servicios profesionales al Estado, no residentes, financiación externa | 20% |

Los códigos 21–211 corresponden en la imagen a retenciones a cuenta de rentas
de actividades económicas; 31–35 a retenciones definitivas de renta del trabajo;
41–42 a retenciones definitivas de actividades económicas. El IMI municipal
y el IVA no están definidos en esta fotografía del catálogo DGI.

Código fiscal, porcentaje, cuenta contable y número de comprobante son datos
distintos. Los códigos 22, 23 y 24 comparten 2% y no pueden distinguirse solo
por la tasa. Tampoco debe deducirse el código exclusivamente del nombre de cuenta.

Referencias oficiales localizadas durante la revisión:

- [DGI: catálogo de códigos de retenciones](https://www.dgi.gob.ni/pdfNoticia/365).
- [DGI: catálogo versión 2.0](https://www.dgi.gob.ni/pdfNoticia/147).
- [DGI: aplicación del catálogo de códigos](https://www.dgi.gob.ni/pdfNoticia/4337).

La consulta indexada permitió localizar estas referencias, pero la apertura
directa de los documentos 365 y 4337 fue rechazada por el servidor. No se
certificó su vigencia actual ni la integridad del catálogo. Antes de implementar
reglas fiscales, verificar el documento oficial completo, reformas, fechas,
sujetos, bases, mínimos y excepciones. No cargar esta transcripción como
configuración vigente automática.

## Revisión de cobertura del código

Revisión estática del 2026-11-16 sobre el checkout de integración en `main`,
HEAD `af34e1a`. No se ejecutaron pruebas runtime ni se auditaron bases de datos
de sitios en esta revisión. Un campo o una fórmula en código no demuestra
por sí solo que cada sitio esté correctamente configurado.

| Requisito | Estado observado | Evidencia relativa al repositorio |
|---|---|---|
| Comprobante por fila y obligatoriedad configurable | Implementado; validación backend para proveedor | `patches/v1_0/add_tax_receipt_custom_fields.py`, `tax_receipt.py` dentro del paquete |
| Comprobante opcional en deducciones | Implementado | `patches/v1_1/add_payment_entry_deduction_receipt_field.py` |
| Retenciones con tasa configurable | Parcial: usa la tasa de la fila; no elige régimen fiscal | `overrides/payment_entry.py` |
| Base neta proporcional | Implementada para `Pay`/`Supplier`, referencias soportadas y filas de reducción; no es regla universal del catálogo | `retention_base.py`, `overrides/payment_entry.py` |
| Catálogo DGI: código, hecho generador, vigencia, mínimos y excepciones | No implementado como configuración fiscal propia | No se define catálogo ni asociación de código fiscal en campos/instalación/reporte |
| Diferenciación DGI e IMI por autoridad y municipio | No implementada como modelo fiscal; las filas pueden usar cuentas distintas | Campos de comprobantes y lógica de cálculo sin autoridad/municipio |
| IVA configurable, incluido en precio, acreditable, por pagar o al costo | No provisionado ni validado por esta app | Instalación y bootstrap crean metadata de comprobantes, no configuración IVA |
| Renta del trabajo por tabla y retenciones definitivas del catálogo | No hay motor específico implementado | Controlador limitado al flujo de pagos a proveedores |
| Informe de comprobantes | Implementado, con alcance limitado | Reporte `comprobantes_de_retencion_en_la_fuente` |
| Declaración DGI por código fiscal | No implementada | El informe no contiene código de catálogo ni exportación DMI |

ERPNext 15 tiene mecanismos nativos para precio con impuesto incluido y
categorías de cargos `Total`, `Valuation` y `Valuation and Total`, visibles en
`erpnext/accounts/doctype/purchase_taxes_and_charges/purchase_taxes_and_charges.json`.
Su existencia no acredita que esta app configure correctamente IVA de Nicaragua,
cuentas por compañía, productos, exenciones o asientos de inventario.

### Límites que deben resolverse antes de afirmar cumplimiento completo

- Sin referencias válidas, el controlador delega el cálculo al core; no garantiza
  por sí solo base sin IVA/ISC para todo anticipo o pago sin factura.
- La base usa campos netos del documento, no identifica ni excluye cada impuesto
  por su naturaleza fiscal. No se ha demostrado el tratamiento integral de ISC.
- El cálculo no clasifica retenciones por código DGI. Reconoce filas de reducción
  por signo/tipo y no determina si corresponde tasa plana, tabla o umbral.
- En el reporte, `monto_bruto` toma el mayor valor absoluto entre pagado y recibido;
  no representa necesariamente la base fiscal de cada fila. En deducciones, el
  porcentaje de retención se devuelve vacío. No usarlo como declaración fiscal completa.
- El selector filtra cuentas usadas en impuestos de pagos y deducciones, con
  criterios de pasivo y tipo/nombre de cuenta; no es un selector de códigos DGI.

## Pruebas disponibles y aceptación pendiente

`nicaragua_tax_receipt/tests/test_payment_entry_retention_base.py` contiene
cuatro pruebas unitarias: base neta completa y parcial (115/57.50 sobre neto 100,
esperado 100/50), cálculo de 2% sobre 100, y reconocimiento de reducción con
`Add` negativo o `Deduct` positivo. Se revisó el contenido, no se ejecutó la suite
en esta tarea. Las pruebas de permisos del reporte no validan impuestos.

Para aceptar el objetivo ampliado faltan casos con asientos contables comprobados:
IVA incluido/desglosado y recuperable/no recuperable; productos exentos y gravados;
IR e IMI simultáneos con comprobantes separados; varias facturas, pagos parciales,
anticipos, moneda extranjera, redondeo, devoluciones y cancelaciones. Cada código
del catálogo requerirá condiciones y casos de borde propios, incluida tabla IR,
residencia y umbrales. Las tasas de una fotografía no sustituyen esas pruebas.
