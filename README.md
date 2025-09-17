# Proyecto Control de Facturación Masiva y Proyección de Ingresos

Modelo de control desarrollado en ACL/SQL/Excel para validar ingresos estimados vs. reales en un proceso masivo de inscripciones y aranceles.

---

⚠️ **Confidencialidad**: Los datos del repositorio público están **anonimizados** (o reemplazados por valores ficticios/escala). El contenido tiene fines demostrativos para mi CV/portfolio.

---

## 🎯 Objetivo

Implementar un control que permita:

Comparar estimaciones de inscripciones activas con los valores reales.

Proyectar ingresos, descuentos y becas con precisión cercana al 98%.

Identificar inconsistencias o errores antes del envío a gestión de cobranzas.

---

## 📊 Flujo de Control

El control incluye:

Estimaciones basadas en inscripciones proyectadas y reales.

Cálculo de facturación de asignaturas, becas y aranceles.

Consolidación en un Total Masiva.

Cálculo automático de diferencias porcentuales entre lo estimado y lo real.

---

## 📸 Ejemplo del control aplicado:

![Control de Facturación](https://raw.githubusercontent.com/hernano88/acl-sql-uade/main/pictures/check_masiva.PNG)

---

## 🛢️ Manejo de datos

Se utilizan datos provenientes de SQL y se proyectan en plantillas de control.

El modelo permite escalarse para distintos períodos (mensuales, cuatrimestrales).

Los datos mostrados son ficticios y sirven únicamente para ilustrar la lógica del control.

---

## 📈 Resultados esperados

Proyección de ingresos con un margen de error menor al 2%.

Identificación temprana de errores y diferencias entre lo estimado y lo real.

Mayor confiabilidad en la información enviada a gestión de cobranzas.

---

## 🔧 Tecnologías utilizadas

SQL (consultas para extracción de inscripciones, aranceles y becas)

Excel (tablas dinámicas y controles de proyección)

Procesos ETL para integración de fuentes de datos en ACL


---

# Proyecto Conciliación de Inscripciones, Becas, y demas conceptos criticos.

Modelo de ETL + SQL para automatizar controles de facturación y conciliación de inscripciones, con el objetivo de detectar y justificar diferencias antes del envío a gestión de cobranzas.

---

🎯 Objetivo

Automatizar procesos de conciliación en facturación masiva.

Validar inscripciones, aranceles, descuentos y becas en tablas de Oracle.

Justificar diferencias con reportes detallados y criterios de negocio.

Reducir errores y escalar procesos críticos con mínimo mantenimiento.

---

🛠️ Desarrollo

Scripts en ACL (lenguaje similar a Python/SQL) sobre Oracle.

Consultas SQL para extracción, transformación y validación de datos.

Adaptación automática de controles según calendario mensual.

Integración con herramientas complementarias (Toad) para exploración y documentación de tablas intermedias.

---

📸 Ejemplo de consultas SQL:

![Control de Facturación](https://raw.githubusercontent.com/hernano88/acl-sql-uade/main/pictures/sql.PNG)

📸 Ejemplo de conciliación y justificación de diferencias:

![Control de Facturación](https://raw.githubusercontent.com/hernano88/acl-sql-uade/main/pictures/conciliacion_asignatura.PNG)

📸 Ejemplo de joins y reglas de validación en ETL:

![Control de Facturación](https://raw.githubusercontent.com/hernano88/acl-sql-uade/main/pictures/sql2.PNG)

---


📊 Resultados

Cobertura del 97% de la operatoria mensual (asignaturas, matrículas, maestrías, descuentos, becas, bajas).

Procesamiento de volúmenes de datos superiores a 5GB con tiempos eficientes.

Justificación de diferencias anticipada, evitando errores en la gestión de cobranzas.

Escalabilidad y mantenimiento reducido gracias a controles dinámicos.

---

🔧 Tecnologías utilizadas

ACL (Audit Command Language)

Oracle SQL

Toad

Excel para reportes de conciliación y visualización

