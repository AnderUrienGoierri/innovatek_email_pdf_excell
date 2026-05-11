# 🧠 Guía de Entrenamiento y Mejora del Agente IA

Esta guía documenta el proceso sistemático para mejorar la precisión del Agente de IA (Ollama Qwen2.5:14b) en la extracción de datos de facturas complejas.

## 1. Metodología: Few-Shot Prompting
En lugar de simplemente darle instrucciones generales, utilizamos **ejemplos maestros**. Esto permite que la IA reconozca patrones específicos de proveedores difíciles (como operadores de telefonía) antes de procesar la factura actual.

## 2. Ciclo de Mejora Continua
Para perfeccionar el sistema, seguimos este ciclo ante cada error detectado:

1.  **Detección:** Se identifica una factura donde los datos extraídos no coinciden con la realidad (ej. Base imponible incorrecta).
2.  **Análisis de Texto:** Se extrae el fragmento de texto exacto del PDF que causó la confusión (ej. una tabla de descuentos).
3.  **Creación del Caso Maestro:** Se define cómo debería haber interpretado la IA ese texto específico.
4.  **Actualización del Prompt:** Se añade el nuevo caso al archivo `system_prompt_ollama.txt` y se actualiza el nodo en n8n.

---

## 3. Registro de Casos de Éxito (Entrenamiento)

### CASO 1: MASMOVIL / Telefonía Compleja
*   **Problema detectado:** La IA se perdía en las tablas de "Cuotas Mensuales" y sumaba descuentos de forma errónea.
*   **Solución aplicada:** Regla de prioridad absoluta para el bloque "DESGLOSE FISCAL".
*   **Ejemplo de entrenamiento inyectado:**
    ```text
    - Texto: "(21%) 29,91 Base imponible" -> Extraer base_imponible: 29.91
    - Texto: "TOTAL A PAGAR 36,19" -> Extraer total_factura: 36.19
    ```

---

## 4. Cómo añadir un Nuevo Proveedor
Si un nuevo proveedor (ej. Endesa, Amazon, etc.) empieza a dar fallos, sigue este formato para el entrenamiento:

1.  **Nombre del Caso:** CASO X: [Nombre del Proveedor]
2.  **Puntos Clave:** Identifica las palabras clave que el proveedor usa para:
    *   Nº Factura (ej. "Referencia", "ID Pedido").
    *   Base Imponible (ej. "Suma de importes", "Neto").
3.  **Inyección:** Añadirlo a la sección `EJEMPLOS MAESTROS` en el `system_prompt_ollama.txt`.

---

## 5. Mejores Prácticas para el Entrenamiento
*   **JSON Puro:** Asegúrate siempre de que el prompt termine con la instrucción `Devuelve SOLO el objeto JSON`.
*   **Validación Matemática:** Obliga a la IA a realizar el cálculo `Base + IVA = Total`.
*   **Truncado de Texto:** Para facturas de muchas páginas, envía solo los primeros 10.000 caracteres para no saturar la memoria.

---
*Documento generado para Innovatek - Mayo 2026*
