# Conciliación financiera de facturación con ACL Analytics y Oracle SQL

[English](README.md) | [Español](README.es.md)

Caso profesional de control de datos basado en la automatización de conciliaciones de facturación. La solución combina Oracle SQL para extraer y preparar información operativa, ACL Analytics para ejecutar reglas de control repetibles y Excel para la revisión de resultados y gestión de excepciones.

Todo el código, los datos, los identificadores y las capturas públicas son sintéticos o fueron sanitizados. Se excluyen deliberadamente scripts productivos, conexiones, información de estudiantes y objetos internos de base de datos.

## Problema de negocio

La facturación masiva combina inscripciones, aranceles, becas, descuentos, bajas y ajustes especiales. La información puede diferir entre reportes operativos y fuentes de base de datos. Una comparación manual es lenta, difícil de repetir y puede omitir excepciones de baja frecuencia.

El esquema de control fue diseñado para:

- comparar facturación esperada y real;
- conciliar inscripciones y movimientos financieros;
- aplicar reglas de negocio de forma consistente;
- clasificar diferencias justificables;
- aislar excepciones antes de la gestión de cobranzas;
- medir cuánto valor económico está protegido por controles fuertes.

## Flujo implementado

```mermaid
flowchart LR
    A["Fuentes operativas Oracle"] --> B["Extracción con Oracle SQL"]
    B --> C["Normalización y joins en ACL"]
    C --> D["Reglas de validación"]
    D --> E["Conciliación esperado vs. real"]
    E --> F["Diferencias clasificadas"]
    F --> G["Reporte de control en Excel"]
    G --> H["Revisión manual de excepciones"]
```

Oracle SQL y ACL cumplen responsabilidades diferentes: SQL construye el universo de datos cerca de la fuente; ACL estandariza campos, combina extracciones, evalúa reglas, resume resultados y exporta el reporte de control.

## KPI principal: cobertura financiera mensual del control

El resultado aproximado del **98%** es una métrica mensual de cobertura financiera. No es precisión de un pronóstico ni significa que el 98% de las facturas estén libres de errores.

```text
cobertura financiera del control =
    monto facturado cubierto por controles fuertes
    ------------------------------------------------  x 100
                  monto total facturado
```

El ejemplo mensual sintético del repositorio utiliza un monto total de 100.000 unidades. Los conceptos alcanzados por controles automatizados fuertes representan 98.000 unidades, lo que produce una cobertura financiera del 98% para ese período de facturación. El 2% restante corresponde a conceptos de menor volumen o situaciones excepcionales enviadas a revisión manual.

![Ejemplo sintético de cobertura financiera del 98 por ciento](docs/images/financial-control-coverage.png)

## Capas de control

### 1. Extracción con Oracle SQL

Las consultas Oracle SQL embebidas seleccionan el período requerido y combinan información de inscripciones, líneas de facturación, conceptos y resultados del control. Las consultas públicas representativas demuestran:

- `INNER JOIN` y `LEFT JOIN` entre múltiples tablas;
- expresiones comunes de tabla;
- filtrado y normalización de fechas;
- tratamiento de nulos con `NVL`;
- agregaciones por concepto y estado;
- conciliación entre importes esperados y facturados.

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

![Ejemplo sintético de conciliación SQL con múltiples tablas](pictures/sql2.PNG)

### 2. Lógica de control en ACL Analytics

Los controles operativos utilizan scripts ACL para:

- estandarizar cuentas, fechas e importes;
- crear diferencias y campos de clasificación calculados;
- generar índices y tablas intermedias;
- combinar resultados pre y post facturación;
- resumir montos controlados y excepciones;
- eliminar temporales antes de nuevas ejecuciones;
- exportar los libros finales de control.

El archivo público [`acl/financial_control_coverage.acl`](acl/financial_control_coverage.acl) es un ejemplo representativo reducido. Conserva el patrón del control sin exponer código productivo ni conexiones.

### 3. Conciliación y clasificación de excepciones

Las reglas típicas clasifican casos como:

- inscripto sin facturación;
- facturado sin inscripción relacionada;
- facturación anterior o posterior al período esperado;
- pagos de contado o ajustes manuales;
- becas o descuentos fuera de vigencia;
- diferencia entre descuento teórico y aplicado;
- situaciones de bajo volumen que requieren revisión manual.

![Control sintético de facturación esperada versus real](pictures/check_masiva.PNG)

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

- Aproximadamente **98% del valor económico facturado mensualmente** cubierto por controles fuertes dentro del alcance definido.
- Los controles con mayor intensidad de datos procesaban datasets que alcanzaban aproximadamente **5 GB** mediante ACL y fuentes Oracle; era una escala máxima demostrada, no el tamaño habitual de todos los controles.
- Clasificación repetible de diferencias antes de la gestión de cobranzas.
- Análisis manual concentrado en una población menor de excepciones.
- Controles reutilizables por mes y período académico con mantenimiento reducido.

## Cómo reproducir el ejemplo sintético

1. Ejecutar los scripts de `sql/` en orden numérico dentro de un ambiente Oracle de desarrollo.
2. Confirmar que `03_financial_control_coverage.sql` devuelve 98%.
3. Revisar el mismo universo en `data/synthetic_billing_control.csv`.
4. Si se dispone de ACL Analytics, adaptar el script representativo a una tabla importada con los mismos campos.

El ejemplo SQL es autocontenido y utiliza únicamente tablas ficticias del portfolio. ACL Analytics es software comercial; por eso el script se ofrece como patrón legible y no como una prueba automatizada de CI.

## Confidencialidad y seguridad

- No se incluye información real de estudiantes, clientes ni empleados.
- No se incluyen tablas productivas, servidores, DSN, correos, contraseñas ni cadenas de conexión.
- Los valores monetarios e identificadores son sintéticos.
- Los scripts públicos reproducen el patrón técnico, no la implementación productiva.
- Las capturas se conservan únicamente cuando contienen información ficticia o sanitizada.

## Resumen profesional

> Desarrollé controles automatizados de facturación utilizando ACL Analytics y Oracle SQL. SQL extraía y combinaba información de inscripciones, facturación, becas, descuentos y ajustes; ACL estandarizaba campos, aplicaba reglas de negocio, conciliaba importes esperados contra reales y clasificaba excepciones. Cada mes, los controles alcanzaban aproximadamente el 98% del valor total facturado dentro del alcance definido, permitiendo concentrar la revisión manual en los conceptos excepcionales restantes. Los controles con mayor intensidad de datos procesaban datasets que alcanzaban aproximadamente 5 GB y generaban reportes de control repetibles en Excel antes de la gestión de cobranzas.
