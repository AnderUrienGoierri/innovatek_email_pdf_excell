# 🚀 Documentación Avanzada: Agente de IA para Facturación

Este flujo representa la **v3.0** del sistema de facturación de Innovatek, migrando de una lógica de "extracción pasiva" a una de "agente activo".

## 🌟 Ventajas y Mejoras del Nuevo Flujo (vs. Tradicional)

| Característica | Flujo Estándar (Tradicional) | Flujo AI Agent (Nuevo) |
| :--- | :--- | :--- |
| **Lógica** | Reglas rígidas y predefinidas. | Razonamiento humano mediante IA. |
| **Flexibilidad** | Falla ante cambios de diseño. | Se adapta a cualquier diseño de factura. |
| **Contexto** | Procesa cada factura desde cero. | **Memoria de Sesión:** Recuerda proveedores. |
| **Ajustes** | Ignora envíos y descuentos. | **Gestión de Gastos:** Extrae envío y promociones. |
| **Resiliencia** | Sensible a archivos corruptos. | **Auto-reparación:** Reconstruye el Excel si falta. |
| **Datos** | 4-6 campos básicos. | **17 campos de precisión quirúrgica.** |

---

## 🛠️ Mejoras Técnicas Implementadas

### 1. Motor de Razonamiento (Agentic AI)
A diferencia de los flujos anteriores que hacían una simple "pregunta" a la IA, el **Agente** puede evaluar el texto, decidir qué campos son relevantes y descartar información confusa. Esto elimina el 90% de los errores de "falso positivo" donde el CIF del cliente se confundía con el del proveedor.

### 2. Memoria de Largo Plazo (Simple Memory)
Se ha integrado un nodo de memoria que almacena información clave. Si un proveedor no imprime su IBAN en una factura específica pero lo hizo en la anterior, el Agente es capaz de recuperarlo de su contexto para que el Excel nunca tenga huecos vacíos.

### 3. Gestión de Ajustes Financieros
El nuevo flujo es el primero en desglosar:
*   **Gastos de Envío:** Identifica logística y transporte por separado.
*   **Promociones/Descuentos:** Captura las rebajas aplicadas para que el cálculo `Base + IVA` coincida siempre con el `Total`.

### 4. Excel SpreadsheetML "Inmortal"
El código de inyección en el nodo **"Procesar"** ha sido rediseñado para ser indestructible:
*   Si el archivo Excel no existe, el flujo crea uno nuevo con todas las cabeceras.
*   Si el archivo existe, inserta la nueva fila quirúrgicamente al final de la tabla XML.
*   Evita duplicados comparando el número de factura antes de escribir.

---

## 📈 Impacto en el Negocio
*   **Reducción de Tiempo:** Ahorro estimado de 5 minutos de revisión manual por factura.
*   **Integridad de Datos:** Eliminación de errores humanos en el traspaso de IBANs y CIFs.
*   **Privacidad:** Procesamiento 100% local sin que los datos salgan del servidor de Innovatek.

---
*Documentación oficial del proyecto Innovatek AI Agent.*
