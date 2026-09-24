# Controles financieros: de ACL y Oracle SQL a Python/Jupyter

[English](README.md) | [Español](README.es.md)

Caso profesional de control de datos basado en la automatización de conciliaciones de facturación. La solución original combina Oracle SQL, ACL Analytics y Excel; su evolución actual migra controles seleccionados a **Python, Jupyter Notebook y Pandas**, manteniendo Oracle como fuente y haciendo explícitas las validaciones, justificaciones y excepciones.

Todo el código, los datos, los identificadores y las capturas públicas son sintéticos o fueron sanitizados. Se excluyen deliberadamente scripts productivos, conexiones, información de estudiantes y objetos internos de base de datos.

> **Estado real del trabajo:** la migración ACL → Python/Jupyter está en curso en un entorno profesional. El ejemplo público reproduce el enfoque técnico con datos ficticios. La persistencia histórica de resultados en Oracle se encuentra en diseño conjunto con BI y no se presenta como productiva.

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

## Evolución actual: ACL → Python/Jupyter

```mermaid
flowchart LR
    A["Fuentes autorizadas Oracle"] --> B["SQL parametrizado"]
    B --> C["DataFrames de Pandas"]
    C --> D["Normalización y agregación"]
    D --> E["Conciliación bidireccional por cuenta"]
    E --> F["Justificaciones por reglas de negocio"]
    F --> G["Pendientes + controles de líneas e importes"]
    G --> H["Dashboard HTML en Jupyter"]
    H -. "en diseño con BI" .-> I["Histórico de resultados en Oracle"]
```

El nuevo patrón conserva el conocimiento de negocio de los controles existentes y mejora su trazabilidad técnica:

- conexión autorizada a Oracle con `oracledb` y SQLAlchemy;
- extracción SQL a DataFrames sin guardar credenciales en el notebook;
- normalización de identificadores, nulos, fechas y tipos;
- agregaciones y conciliación por cuenta mediante `groupby()` y `merge(..., how="outer")`;
- detección de diferencias en ambas direcciones;
- justificaciones automáticas sin ocultar la diferencia original;
- validación conjunta de cantidad de líneas, importes y casos pendientes;
- salida resumida como dashboard HTML dentro de Jupyter.

El notebook público [`python_jupyter/notebooks/01_synthetic_billing_reconciliation.ipynb`](python_jupyter/notebooks/01_synthetic_billing_reconciliation.ipynb) ejecuta ese flujo de punta a punta con datos sintéticos. La lógica reutilizable está separada en [`python_jupyter/src/control_reconciliation.py`](python_jupyter/src/control_reconciliation.py) y cuenta con pruebas automatizadas.

### Decisión de control demostrada

El ejemplo tiene 10 líneas esperadas y 10 líneas facturadas en total. Sin embargo, existe una cuenta esperada sin facturación y otra facturada sin registro esperado. Por eso no alcanza con comparar totales generales: el `outer merge` por cuenta evita que dos diferencias opuestas se compensen y produzcan un falso resultado correcto.

Los casos justificados se conservan como `JUSTIFIED`; los que no cierran cantidad e importe permanecen como `PENDING_REVIEW`. Esta separación permite explicar qué resolvió una regla automática y qué requiere análisis humano.

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
|   |-- synthetic_billing_control.csv
|   |-- synthetic_billed_scope.csv
|   `-- synthetic_expected_scope.csv
|-- docs/
|   |-- DATA_DICTIONARY.md
|   `-- images/
|       |-- financial-control-coverage.png
|       `-- financial-control-coverage.svg
|-- pictures/
|   `-- capturas sanitizadas
|-- python_jupyter/
|   |-- notebooks/
|   |   `-- 01_synthetic_billing_reconciliation.ipynb
|   |-- src/
|   |   `-- control_reconciliation.py
|   |-- .env.example
|   |-- oracle_connection.example.py
|   `-- requirements.txt
|-- sql/
|   |-- 00_create_synthetic_tables.sql
|   |-- 01_extract_control_scope.sql
|   |-- 02_reconcile_expected_actual.sql
|   |-- 03_financial_control_coverage.sql
|   `-- 04_data_quality_checks.sql
|-- tests/
|   `-- test_python_reconciliation.py
|-- README.md
`-- README.es.md
```

## Resultados demostrados

- Aproximadamente **98% del valor económico facturado mensualmente** cubierto por controles fuertes dentro del alcance definido.
- Los controles con mayor intensidad de datos procesaban datasets que alcanzaban aproximadamente **5 GB** mediante ACL y fuentes Oracle; era una escala máxima demostrada, no el tamaño habitual de todos los controles.
- Clasificación repetible de diferencias antes de la gestión de cobranzas.
- Análisis manual concentrado en una población menor de excepciones.
- Controles reutilizables por mes y período académico con mantenimiento reducido.
- Migración progresiva de controles seleccionados desde ACL hacia Python/Jupyter, con conciliaciones en Pandas y salidas de revisión más trazables.

## Cómo reproducir el ejemplo sintético

1. Ejecutar los scripts de `sql/` en orden numérico dentro de un ambiente Oracle de desarrollo.
2. Confirmar que `03_financial_control_coverage.sql` devuelve 98%.
3. Revisar el mismo universo en `data/synthetic_billing_control.csv`.
4. Si se dispone de ACL Analytics, adaptar el script representativo a una tabla importada con los mismos campos.

Para ejecutar la demostración Python/Jupyter:

```powershell
python -m pip install -r python_jupyter/requirements.txt
python -m pytest
jupyter lab python_jupyter/notebooks/01_synthetic_billing_reconciliation.ipynb
```

El archivo `oracle_connection.example.py` es únicamente una plantilla segura: usa variables de entorno y nombres de vistas ficticios. No es una copia de la conexión productiva.

El ejemplo SQL es autocontenido y utiliza únicamente tablas ficticias del portfolio. ACL Analytics es software comercial; por eso el script se ofrece como patrón legible y no como una prueba automatizada de CI.

## Confidencialidad y seguridad

- No se incluye información real de estudiantes, clientes ni empleados.
- No se incluyen tablas productivas, servidores, DSN, correos, contraseñas ni cadenas de conexión.
- Los valores monetarios e identificadores son sintéticos.
- Los scripts públicos reproducen el patrón técnico, no la implementación productiva.
- Las capturas se conservan únicamente cuando contienen información ficticia o sanitizada.
- Los notebooks productivos no se publican: pueden contener nombres internos, consultas, resultados o referencias de configuración aun cuando la contraseña esté en otro archivo.

## Resumen profesional

> Desarrollé controles automatizados de facturación con ACL Analytics y Oracle SQL, y actualmente migro controles seleccionados a Python y Jupyter Notebook. Con Pandas extraigo y normalizo datos de Oracle, concilio universos por cuenta en ambas direcciones, aplico justificaciones de negocio y valido tanto cantidades de líneas como importes. Los controles existentes alcanzan mensualmente aproximadamente el 98% del valor facturado dentro del alcance definido; los de mayor intensidad procesaron datasets de hasta aproximadamente 5 GB. La evolución a Python busca conservar ese conocimiento de control y mejorar la trazabilidad, la reutilización y la futura persistencia histórica junto con BI.
