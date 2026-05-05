# 🚀 Automatización de Facturas a Excel (n8n + Ollama)

Este repositorio contiene un sistema de automatización profesional diseñado para procesar facturas en múltiples formatos (PDF, PNG, JPG) y consolidar la información en un archivo Excel maestro de forma acumulativa.

---

## 🏗️ 1. Arquitectura del Workflow

El flujo de trabajo (`email_pdf_excell.json`) ha sido diseñado para ser **indestructible** y **resiliente**. Utiliza inteligencia artificial local (Ollama) para la extracción de datos y una lógica de persistencia avanzada.

### 📸 Vista General
![Vista general del Workflow en n8n](media/n8n_workflow_overview.png)

### 🧩 Desglose de Nodos Principales

#### 1. Lógica de Entrada y OCR
El sistema detecta si el archivo es un PDF de texto o una imagen escaneada. Si es una imagen, se redirige automáticamente al motor de **OCR (OCR.space)** antes de pasar a la IA.

#### 2. IA: Extracción con Ollama (Llama 3.2)
Utilizamos un prompt optimizado que obliga a la IA a razonar sobre los campos para evitar errores comunes como el intercambio de fechas y números de factura.

**Configuración del Nodo AI:**
```json
{
  "model": "llama3.2",
  "prompt": "Extract invoice data... IMPORTANT: 'factura_numero' is the ID, 'factura_fecha' is the date. Do not swap them."
}
```

#### 3. El Cerebro: Nodo de Código (Persistencia XML)
Este nodo es el encargado de leer el Excel existente y añadir la nueva fila sin sobrescribir nada. Utiliza el formato **SpreadsheetML** de Microsoft para mantener estilos profesionales.

![Lógica de inyección de datos](media/n8n_code_node_logic.png)

---

## 🛡️ 2. Sistemas de Seguridad (Guardarraíles)

Para garantizar que los datos sean 100% fiables, hemos implementado una **Heurística de Validación Cruzada** en JavaScript:

```javascript
// Heurística: Si el número parece una fecha y la fecha parece un número, los intercambiamos.
const isDatePattern = (s) => {
  const parts = s.split(/[\-\/\.]/);
  return parts.length === 3 && parts.every(p => /^\d+$/.test(p));
};

if (isDatePattern(rawNum) && (isOnlyDigits(rawFec) || !rawFec)) {
  [rawNum, rawFec] = [rawFec, rawNum]; // ¡Corrección automática!
}
```

---

## 🛠️ 3. Configuración Técnica

### 📂 Estructura de Archivos
- `README.md`: Este archivo de documentación.
- `email_pdf_excell.json`: Workflow completo listo para importar en n8n.
- `tabla_excell_facturas.xls`: Archivo Excel base (formato XML).
- `media/`: Imágenes y capturas del sistema.

### 🐳 Docker & Permisos
Es vital configurar el volumen correctamente en n8n para que tenga acceso a la carpeta de facturas:
- **Ruta Host:** `c:\Users\innovatek\n8n-watch\pdf_excell`
- **Ruta Contenedor:** `/data/pdf_excell/`
- **Variable de Entorno:** `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false`

---

## ❓ 4. Resolución de Problemas (FAQ)

### 🛑 ¿Por qué Excel da error al abrir el archivo?
Si el archivo se corrompe por un cierre inesperado de n8n, se puede resetear usando el archivo base proporcionado en este repo. Hemos añadido prefijos `ss:` en todo el XML para maximizar la compatibilidad.

### 📅 ¿Qué formato tienen las fechas?
El sistema normaliza todas las fechas extraídas por la IA al formato **DD-MM-AAAA**, asegurando uniformidad total en el Excel.

### 🔒 ¿Es seguro el proceso?
Sí. Al usar **Ollama**, el procesamiento de tus facturas se realiza de forma **100% local** en tu servidor, sin enviar datos privados de tus facturas a nubes externas.

---
_Desarrollado para Medios y Transportes Goiherri SL_