# 🚀 Automatización de Facturas 100% Local (n8n + Ollama Vision)

Este proyecto es una solución **Air-Gapped** (sin internet) para la extracción y consolidación de facturas. A diferencia de otras soluciones, todo el procesamiento de datos y el OCR se realizan de forma privada en tu propio servidor.

---

## 🏗️ 1. Arquitectura de Privacidad Total

El workflow (`email_pdf_excell.json`) utiliza inteligencia artificial de vanguardia para procesar tanto documentos de texto como imágenes escaneadas sin enviar datos a la nube.

### 📸 Vista General
![Vista general del Workflow en n8n](media/n8n_workflow_overview.png)

### 🧩 Lógica de Procesamiento Dual
1.  **Rama de Texto (PDF Directo)**: Si el PDF contiene capas de texto, se utiliza el modelo `llama3.2`. Es extremadamente rápido y preciso.
2.  **Rama de Visión (Escaneos/Imágenes)**: Si el archivo es una imagen o un PDF sin texto, el sistema activa automáticamente **Ollama Vision**.
    *   **Modelo:** `llama3.2-vision`.
    *   **Proceso:** Se convierte la imagen a Base64 localmente y la IA la "lee" para extraer el JSON.

---

## 🛠️ 2. Requisitos del Sistema

Para que el sistema funcione en modo local, debes tener instalados los siguientes modelos en tu instancia de Ollama:

```bash
# Para facturas de texto (rápido)
ollama pull llama3.2

# Para facturas escaneadas o imágenes (OCR local)
ollama pull llama3.2-vision
```

---

## 🛡️ 3. Sistemas de Seguridad y Validación

El sistema no solo extrae datos, sino que los valida mediante heurística en JavaScript:
*   **Corrección de Fecha/Número**: Detecta automáticamente si la IA ha intercambiado el ID de la factura con la fecha de emisión.
*   **Normalización de Fechas**: Convierte cualquier formato a `DD-MM-AAAA`.
*   **Escapado XML**: Garantiza que caracteres especiales (como el símbolo `&`) no corrompan el archivo Excel.

---

## 📂 4. Estructura del Proyecto
- `email_pdf_excell.json`: Workflow completo (Importar en n8n).
- `tabla_excell_facturas.xls`: Archivo maestro consolidado.
- `README.md`: Esta documentación.
- `media/`: Capturas y diagramas del flujo.

---

## ❓ 5. FAQ Local

### 🛑 ¿Por qué tarda más en procesar imágenes?
Al hacer el OCR localmente, tu ordenador tiene que "ver" la imagen píxel a píxel usando el modelo de visión. El tiempo depende de la potencia de tu CPU/GPU, pero ganas **privacidad total**.

### 🐳 ¿Cómo descargo los modelos en Docker?
Si usas Docker, ejecuta:
`docker exec -it ollama ollama pull llama3.2-vision`

---
_Desarrollado para Medios y Transportes Goiherri SL_