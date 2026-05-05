# 🚀 Automatización de Facturas 100% Local y Privada (n8n + AI)

Este proyecto implementa un pipeline de procesamiento de documentos **completamente local**, eliminando la dependencia de APIs externas (como OCR.space o ChatGPT). Garantiza la **soberanía total de los datos** y la privacidad de la información financiera.

![Workflow Overview](file:///C:/Users/innovatek/.gemini/antigravity/brain/6772905e-33bb-4f6f-9436-a3a9a279ab8d/n8n_workflow_overview_1777962164304.png)

## 🏗️ Arquitectura del Sistema

La solución se basa en una arquitectura de microservicios orquestada por **Docker**, compuesta por cuatro pilares fundamentales:

### 1. n8n (Orquestador)
Es el cerebro del flujo. Se encarga de:
- **Vigilar carpetas locales**: Usa el nodo `Local File Trigger` para detectar nuevos PDFs instantáneamente.
- **Lógica de Decisión**: Clasifica si un PDF tiene texto nativo o es una imagen escaneada que requiere OCR.
- **Gestión de Datos**: Conecta la salida de la IA con la persistencia en archivos Excel.

### 2. Paperless-ngx (Motor de OCR Local)
Actúa como nuestro motor de visión artificial. 
- **Tecnología**: Utiliza **Tesseract OCR** optimizado.
- **Función**: Cuando n8n detecta una factura que es una "imagen" (sin texto seleccionable), la envía a Paperless. Este extrae cada carácter localmente y devuelve el texto plano a n8n.
- **Estado**: Se ejecuta en el contenedor `paperless_webserver` (puerto 8000).

### 3. Ollama (Modelo de Lenguaje Llama 3.2)
Es la inteligencia que "entiende" la factura.
- **Modelo**: `llama3.2` (ligero y extremadamente rápido).
- **Función**: Recibe el texto extraído (ya sea por OCR o nativo) y lo transforma en un objeto JSON estructurado con campos como `empresa_nombre`, `total_factura`, `CIF`, etc.
- **Ventaja**: Al ser local, la velocidad de respuesta es constante y no tiene costes por uso.

### 4. Motor de Excel (XML Inyectado)
En lugar de usar bibliotecas pesadas, el flujo inyecta directamente filas en formato **XML Spreadsheet 2003**.
- **Robustez**: Permite añadir líneas a archivos `.xls` existentes sin corromperlos.
- **Personalización**: El código JavaScript incluye guardarraíles para corregir errores comunes de la IA (como confundir fechas con números de factura).

---

## 🛠️ Detalle del Código y Nodos Críticos

### Nodo de Inyección Excel (JavaScript)
Este es el corazón lógico del post-procesamiento. Se encarga de sanitizar los datos de la IA antes de guardarlos.

![Lógica del Código](file:///C:/Users/innovatek/.gemini/antigravity/brain/6772905e-33bb-4f6f-9436-a3a9a279ab8d/n8n_code_node_logic_1777962186497.png)

**Funciones clave del código:**
- `esc()`: Escapa caracteres especiales de XML para evitar que el Excel se rompa.
- `fD()`: Normaliza formatos de fecha (YYYY-MM-DD a DD-MM-YYYY).
- **Auto-corrección**: Si la IA detecta una fecha en el campo de "Número de Factura", el código lo detecta y los intercambia automáticamente.

---

## 🚦 Guía de Inicio Rápido

### 1. Levantar la Infraestructura
Asegúrate de que todos los contenedores están funcionando:
```bash
docker compose -f docker-compose-paperless.yml up -d
```

Verifica el estado con `docker ps`:
![Docker Status](file:///C:/Users/innovatek/.gemini/antigravity/brain/6772905e-33bb-4f6f-9436-a3a9a279ab8d/media__1777968874591.png)

### 2. Configurar el Workflow
1. Importa el archivo `email_pdf_excell.json` en n8n.
2. Asegúrate de que las rutas de las carpetas coinciden con tus volúmenes de Docker.
3. El nodo **Ollama** debe apuntar a `http://ollama:11434`.

---

## 🔒 Seguridad y Privacidad

- **0% Cloud**: Ninguna factura viaja a servidores de terceros.
- **Procesamiento Offline**: Todo ocurre en la red local (`127.0.0.1`).
- **Persistencia Segura**: Los documentos procesados se quedan en tu sistema de archivos local, bajo tu control total.

---
*Desarrollado para Medios y Transportes Goiherri SL - 2026*