# Profundización para entrevistas · decisiones y límites

[English](interview_deep_dive.md) · [Inicio](../README.es.md)

## 1. Empezar por el grano, no por la sintaxis del merge

Los controles nuevos filtran período y comparan alumno/carrera. Los originales de inscripciones
y facturación resumían sólo por alumno. La mejora pública evita compensaciones entre carreras,
pero no detecta materias sustituidas dentro de una misma clave. El matching exacto requiere
linaje por materia, concepto y cuota, con sus contratos.

El ID de origen detecta eventos repetidos. El join one_to_one detecta otra falla: un grano
incorrecto en un resumen. La configuración de becas tiene relación many_to_one: una regla
duplicada debe fallar antes de multiplicar la base.

Código: [contratos](../src/financial_controls/contracts.py),
[adaptadores](../src/financial_controls/controls.py),
[motor](../src/financial_controls/reconciliation.py).

## 2. El dinero necesita una política explícita

1,005 unidades se convierten a 101 centavos con half-up; luego se suman centavos firmados.
La tasa de beca se redondea una vez por alumno/carrera, no por movimiento.
Son decisiones públicas explícitas, no supuestos sobre política institucional.
La tolerancia de un centavo cambia el estado, no elimina el delta almacenado.

Código: [dinero](../src/financial_controls/money.py).
Los tests incluyen nulos/no finitos, negativos, límites de redondeo y diferencias sólo de cantidad.

## 3. Justificar no es borrar

El motor conserva delta original, justificación firmada y remanente.
Cada evidencia tiene ID único, dirección y capacidad limitada por el pendiente.
DE MÁS/DE MENOS sigue visible aunque la revisión pase a JUSTIFICADO.
Cerrar importe sin cerrar cantidad deja el caso pendiente.

Los límites independientes no prueban atribución por factura. Dos evidencias con IDs distintos
pero semánticamente superpuestas requieren linaje adicional. Las fixtures usan evidencia
independiente y el límite está documentado.

## 4. Probar conservación por separado de corrección

Facturación: 890,00 − 930,00 = −40,00. Los excesos explicados +190,00 y los faltantes pendientes
−230,00 reconstruyen esa diferencia. El puente concilia y el control sigue abierto.

Becas: 65,00 − 45,00 = 20,00. El detalle explica 17,00 y el registro no asignado 3,00.
Un left join desde teoría puede perder aplicados sin base. Distribuir el importe sin carrera
en ambas carreras puede duplicarlo. Outer y registro separado evitan ambos problemas.

## 5. Trazar etapas sin registrar datos personales

La traza muestra cantidades filtradas/excluidas, grano agregado, cardinalidad, clasificación,
asignaciones y cuadre. --verbose registra los mismos eventos.
No incluye IDs de alumnos, conexiones ni registros fuente.
Es evidencia de una ejecución, no un scheduler ni un servicio de auditoría inmutable.

Código: [trazas](../src/financial_controls/trace.py), [reportes](../src/financial_controls/reporting.py).

## 6. Límite de integración y confidencialidad

El [ejemplo Oracle](../examples/oracle_connection.py) enlaza período, externaliza credenciales,
evita interpolarlas en la URL y dispone el engine. Importarlo no conecta.
Los tests locales no prueban permisos, consistencia de snapshots, rendimiento ni mapeo de tipos
Oracle/Pandas: hace falta un ambiente aislado y autorizado.

Los datos públicos se inventaron desde cero. El escáner es una ayuda, no una certificación
de ausencia de todo secreto ni una revisión de binarios históricos.

## Propuesta de entrevista en vivo

1. Leer el [notebook de facturación](../notebooks/02_assigned_vs_billed.ipynb).
2. Mostrar por qué igual cantidad total no cierra cada clave.
3. Seguir un DE MÁS hasta su evidencia y un DE MENOS hasta su pendiente.
4. Ejecutar pruebas de configuración duplicada y justificación parcial.
5. Explicar el puente de beca no asignada y las decisiones funcionales restantes.

Ver [tests](../tests/test_financial_controls.py), [matriz](control_matrix.md) y [límites](limitations.md).
No atribuir a estos artefactos métricas de rendimiento o impacto que no miden.
