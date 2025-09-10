# Proyecto Control de Facturación Masiva y Proyección de Ingresos

Modelo de control desarrollado en Excel/SQL para validar ingresos estimados vs. reales en un proceso masivo de inscripciones y aranceles.

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

Procesos ETL para integración de fuentes de datos
