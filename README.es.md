# Conciliaci?n financiera de facturaci?n con ACL Analytics y Oracle SQL

[English](README.md) | [Espa?ol](README.es.md)

Caso profesional de control de datos basado en la automatizaci?n de conciliaciones de facturaci?n. La soluci?n combina Oracle SQL para extraer y preparar informaci?n operativa, ACL Analytics para ejecutar reglas de control repetibles y Excel para la revisi?n de resultados y gesti?n de excepciones.

Todo el c?digo, los datos, los identificadores y las capturas p?blicas son sint?ticos o fueron sanitizados. Se excluyen deliberadamente scripts productivos, conexiones, informaci?n de estudiantes y objetos internos de base de datos.

## Problema de negocio

La facturaci?n masiva combina inscripciones, aranceles, becas, descuentos, bajas y ajustes especiales. La informaci?n puede diferir entre reportes operativos y fuentes de base de datos. Una comparaci?n manual es lenta, dif?cil de repetir y puede omitir excepciones de baja frecuencia.

El esquema de control fue dise?ado para:

- comparar facturaci?n esperada y real;
- conciliar inscripciones y movimientos financieros;
- aplicar reglas de negocio de forma consistente;
- clasificar diferencias justificables;
- aislar excepciones antes de la gesti?n de cobranzas;
- medir cu?nto valor econ?mico est? protegido por controles fuertes.

## Flujo implementado

```mermaid
flowchart LR
    A["Fuentes operativas Oracle"] --> B["Extracci?n con Oracle SQL"]
    B --> C["Normalizaci?n y joins en ACL"]
    C --> D["Reglas de validaci?n"]
    D --> E["Conciliaci?n esperado vs. real"]
    E --> F["Diferencias clasificadas"]
    F --> G["Reporte de control en Excel"]
    G --> H["Revisi?n manual de excepciones"]
```

Oracle SQL y ACL cumplen responsabilidades diferentes: SQL construye el universo de datos cerca de la fuente; ACL estandariza campos, combina extracciones, eval?a reglas, resume resultados y exporta el reporte de control.

## KPI principal: cobertura financiera mensual del control

El resultado aproximado del **98%** es una m?trica mensual de cobertura financiera. No es precisi?n de un pron?stico ni significa que el 98% de las facturas est?n libres de errores.

```text
cobertura financiera del control =
    monto facturado cubierto por controles fuertes
    ------------------------------------------------  x 100
                  monto total facturado
```

El ejemplo mensual sint?tico del repositorio utiliza un monto total de 100.000 unidades. Los conceptos alcanzados por controles automatizados fuertes representan 98.000 unidades, lo que produce una cobertura financiera del 98% para ese per?odo de facturaci?n. El 2% restante corresponde a conceptos de menor volumen o situaciones excepcionales enviadas a revisi?n manual.

![Ejemplo sint?tico de cobertura financiera del 98 por ciento](docs/images/financial-control-coverage.png)

## Capas de control

### 1. Extracci?n con Oracle SQL

Las consultas Oracle SQL embebidas seleccionan el per?odo requerido y combinan informaci?n de inscripciones, l?neas de facturaci?n, conceptos y resultados del control. Las consultas p?blicas representativas demuestran:

- `INNER JOIN` y `LEFT JOIN` entre m?ltiples tablas;
- expresiones comunes de tabla;
- filtrado y normalizaci?n de fechas;
- tratamiento de nulos con `NVL`;
- agregaciones por concepto y estado;
- conciliaci?n entre importes esperados y facturados.

```sql
SELECT
    l.account_ref,
    l.concept_code,
    l.expected_amount,
    l.billed_amount,
    NVL(r.control_status, 'PENDING') AS control_status
FROM portfolio_billing_line l
JOIN portfolio_billing_concept c
  ON c.concept_code = l.concept_code
LEFT JOIN portfolio_control_result r
  ON r.line_id = l.line_id;
```

![Ejemplo sint?tico de conciliaci?n SQL con m?ltiples tablas](pictures/sql2.PNG)

### 2. L?gica de control en ACL Analytics

Los controles operativos utilizan scripts ACL para:

- estandarizar cuentas, fechas e importes;
- crear diferencias y campos de clasificaci?n calculados;
- generar ?ndices y tablas intermedias;
- combinar resultados pre y post facturaci?n;
- resumir montos controlados y excepciones;
- eliminar temporales antes de nuevas ejecuciones;
- exportar los libros finales de control.

El archivo p?blico [`acl/financial_control_coverage.acl`](acl/financial_control_coverage.acl) es un ejemplo representativo reducido. Conserva el patr?n del control sin exponer c?digo productivo ni conexiones.

### 3. Conciliaci?n y clasificaci?n de excepciones

Las reglas t?picas clasifican casos como:

- inscripto sin facturaci?n;
- facturado sin inscripci?n relacionada;
- facturaci?n anterior o posterior al per?odo esperado;
- pagos de contado o ajustes manuales;
- becas o descuentos fuera de vigencia;
- diferencia entre descuento te?rico y aplicado;
- situaciones de bajo volumen que requieren revisi?n manual.

![Control sint?tico de facturaci?n esperada versus real](pictures/check_masiva.PNG)

## Contenido representativo

```text
.
|-- acl/
|   `-- financial_control_coverage.acl
|-- data/
|   `-- synthetic_billing_control.csv
|-- docs/
|   |-- DATA_DICTIONARY.md
|   `-- images/
|       |-- financial-control-coverage.png
|       `-- financial-control-coverage.svg
|-- pictures/
|   `-- capturas sanitizadas
|-- sql/
|   |-- 00_create_synthetic_tables.sql
|   |-- 01_extract_control_scope.sql
|   |-- 02_reconcile_expected_actual.sql
|   |-- 03_financial_control_coverage.sql
|   `-- 04_data_quality_checks.sql
|-- README.md
`-- README.es.md
```

## Resultados demostrados

- Aproximadamente **98% del valor econ?mico facturado mensualmente** cubierto por controles fuertes dentro del alcance definido.
- Los controles con mayor intensidad de datos procesaban datasets que alcanzaban aproximadamente **5 GB** mediante ACL y fuentes Oracle; era una escala m?xima demostrada, no el tama?o habitual de todos los controles.
- Clasificaci?n repetible de diferencias antes de la gesti?n de cobranzas.
- An?lisis manual concentrado en una poblaci?n menor de excepciones.
- Controles reutilizables por mes y per?odo acad?mico con mantenimiento reducido.

## C?mo reproducir el ejemplo sint?tico

1. Ejecutar los scripts de `sql/` en orden num?rico dentro de un ambiente Oracle de desarrollo.
2. Confirmar que `03_financial_control_coverage.sql` devuelve 98%.
3. Revisar el mismo universo en `data/synthetic_billing_control.csv`.
4. Si se dispone de ACL Analytics, adaptar el script representativo a una tabla importada con los mismos campos.

El ejemplo SQL es autocontenido y utiliza ?nicamente tablas ficticias del portfolio. ACL Analytics es software comercial; por eso el script se ofrece como patr?n legible y no como una prueba automatizada de CI.

## Confidencialidad y seguridad

- No se incluye informaci?n real de estudiantes, clientes ni empleados.
- No se incluyen tablas productivas, servidores, DSN, correos, contrase?as ni cadenas de conexi?n.
- Los valores monetarios e identificadores son sint?ticos.
- Los scripts p?blicos reproducen el patr?n t?cnico, no la implementaci?n productiva.
- Las capturas se conservan ?nicamente cuando contienen informaci?n ficticia o sanitizada.

## Resumen profesional

> Desarroll? controles automatizados de facturaci?n utilizando ACL Analytics y Oracle SQL. SQL extra?a y combinaba informaci?n de inscripciones, facturaci?n, becas, descuentos y ajustes; ACL estandarizaba campos, aplicaba reglas de negocio, conciliaba importes esperados contra reales y clasificaba excepciones. Cada mes, los controles alcanzaban aproximadamente el 98% del valor total facturado dentro del alcance definido, permitiendo concentrar la revisi?n manual en los conceptos excepcionales restantes. Los controles con mayor intensidad de datos procesaban datasets que alcanzaban aproximadamente 5 GB y generaban reportes de control repetibles en Excel antes de la gesti?n de cobranzas.
