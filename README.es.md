# Controles financieros con Python, Pandas, Jupyter y Oracle SQL

[English](README.md)

Tres casos reproducibles con **datos completamente sintéticos**, basados en patrones de
modernización de controles cuyo conocimiento de negocio se originó en **ACL Analytics y Oracle SQL**.
Python y Jupyter son el centro del proyecto; ACL se conserva como antecedente.

| Caso | Pregunta de control | Medidas | Clave pública |
|---|---|---|---|
| [01 — Inscripciones vs asignado](notebooks/01_enrollment_vs_assigned.ipynb) | ¿Las líneas asignadas coinciden con las inscripciones? | Cantidades | Alumno + carrera ficticia |
| [02 — Asignado vs facturado](notebooks/02_assigned_vs_billed.ipynb) | ¿Se facturaron los conceptos asignados? | Líneas e importe | Alumno + carrera ficticia |
| [03 — Beca teórica vs aplicada](notebooks/03_expected_vs_applied_scholarship.ipynb) | ¿El beneficio aplicado coincide con la elegibilidad sintética? | Importe y cantidades auxiliares | Alumno + carrera ficticia |

Los ejemplos contienen excepciones deliberadas. **Que los totales concilien no significa que
todos los casos estén resueltos.**

## Ejecución local sin Oracle

Python 3.11 o superior. Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev,notebooks]"
python -m pytest -q
python -m financial_controls.demo --period 2030-09 --output artifacts
python scripts/run_notebooks.py
python scripts/scan_public.py
```

Abrir los notebooks en JupyterLab o revisar `artifacts/<caso>/report.html`.
Cada caso genera detalle, asignaciones de justificaciones, registros sin asignar y métricas.
Las columnas monetarias terminadas en `cents` están expresadas en centavos enteros.

## Evidencia del trabajo real vs demostración pública sintética

| Evidencia observada en los notebooks profesionales | Demostración pública / mejora de ingeniería |
|---|---|
| Extracción Oracle, DataFrames, agrupaciones y merges | CSV locales y plantilla Oracle opcional |
| Comparaciones de cantidades académicas y financieras | Clave compuesta en los tres casos; los dos primeros originales agrupaban sólo por alumno |
| Conciliación de facturación por líneas e importes | Motor compartido y contratos monetarios en centavos |
| Beca teórica/aplicada y cardinalidad en merges | Mínimo y tasa **ficticios** configurables; configuración faltante produce error |
| Justificaciones, pendientes, HTML y una exportación Excel | Asignaciones explícitas, límites por evidencia y exportaciones CSV/HTML |
| Totales madre contra detalle | Puente independiente con registros sin asignar, métricas netas y absolutas |

Los originales son privados y no se copian ni importan. La revisión estática observó código
y salidas guardadas; no certificó exactitud operativa, periodicidad, escala, autoría o impacto.
No se afirma migración completa, despliegue programado, histórico productivo en Oracle,
seniority de liderazgo ni ahorro medido. Las cifras de cobertura/volumen previamente descritas
no se presentan como resultados verificados de estos tres casos.

**Los identificadores, importes, fechas, fuentes y reglas de los nuevos casos son ficticios.**
El mínimo de dos materias y la tasa del 10% son decisiones de la demo; no representan políticas
institucionales. Las excepciones también usan importes y reglas sintéticos.

## Decisiones técnicas defendibles

- Granularidad explícita y claves compuestas para evitar compensaciones entre carreras.
- Normalización como texto, conservando ceros iniciales y rechazando claves faltantes.
- Cruce bidireccional y validaciones de cardinalidad y unicidad.
- Conversión decimal con redondeo half-up y aritmética en centavos.
- Estado matemático `OK / DE MÁS / DE MENOS` separado del estado de revisión.
- Diferencia original, parte justificada y pendiente conservadas.
- Beca sin carrera visible como no asignada, sin replicación.
- Totales de origen previos al merge contra detalle más no asignados.
- Métricas netas y absolutas, con período explícito.

## Documentación y estructura

La [arquitectura](docs/architecture.md) separa contratos, dinero, motor de conciliación,
adaptadores por caso y presentación. También se incluyen [diccionario](docs/synthetic_data_dictionary.md),
[matriz de controles](docs/control_matrix.md), [reglas](docs/business_rules.md),
[límites](docs/limitations.md), [seguridad](docs/security.md) y
[textos para entrevistas/LinkedIn](docs/professional_summary.md).

`src/financial_controls/` contiene los módulos compartidos; `notebooks/` explica los casos;
`data/synthetic/` contiene las fuentes ficticias. Las pruebas incluyen el ejemplo público
anterior. CI ejecuta tests y los tres notebooks desde kernels nuevos, genera reportes y escanea
texto público. No se conecta a Oracle.

## Oracle SQL y ACL como antecedente

Se conservan los [ejemplos SQL](sql/), el [script ACL](acl/financial_control_coverage.acl),
el [notebook anterior](python_jupyter/notebooks/01_synthetic_billing_reconciliation.ipynb)
y su módulo, datos y tests. El ejemplo previo de cobertura es ilustrativo y no valida
por sí mismo una métrica productiva actual.

La [consulta Oracle de clave compuesta](sql/05_synthetic_composite_scope.sql) usa datos ficticios
autocontenidos; no fue ejecutada contra Oracle en esta validación.
La [plantilla de conexión](python_jupyter/oracle_connection.example.py) sólo consulta variables
de entorno al llamar su función y no se conecta al importarla. Sus vistas son ficticias.
