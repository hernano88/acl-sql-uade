# Capturas recomendadas para la migración Python/Jupyter

Las capturas son opcionales: el repositorio ya contiene un notebook reproducible, código modular y pruebas. Si se agregan evidencias visuales, conviene que refuercen el razonamiento sin exponer el entorno productivo.

## Capturas seguras

1. **Resultado del notebook sintético**: tabla final con `RECONCILED`, `JUSTIFIED` y `PENDING_REVIEW`.
2. **Dashboard HTML sintético**: tarjetas de cantidades, importes y pendientes generadas por el notebook público.
3. **Pruebas automatizadas**: terminal mostrando `python -m pytest` exitoso.
4. **Arquitectura conceptual**: Oracle → SQLAlchemy/oracledb → Pandas → conciliación → dashboard → histórico en diseño.

## No publicar

- celdas de conexión, aunque importen la contraseña desde otro archivo;
- nombres reales de servidores, DSN, esquemas, tablas o vistas;
- identificadores o información de estudiantes;
- resultados, importes o cantidades de una ejecución productiva;
- rutas locales, usuarios, correos o nombres de archivos internos;
- notebooks originales con outputs guardados.

Antes de subir cualquier captura real, recortarla y revisar visualmente cada celda, encabezado, tooltip y resultado. La alternativa más segura es ejecutar el notebook sintético incluido y capturar únicamente esa ejecución.
