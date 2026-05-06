# 📑 Sistema de Extracción de Facturas con IA (Arquitectura Híbrida)

Este repositorio contiene la solución definitiva y unificada para la automatización de facturas de **Medios y Transportes Goiherri SL / Innovatek**. El sistema procesa documentos en un entorno "Air-Gapped" 100% local, garantizando privacidad total y cumplimiento RGPD.

Tras las últimas actualizaciones, el sistema cuenta con una **Arquitectura Híbrida** (Workflow Unificado) capaz de procesar facturas a través de dos vías de entrada simultáneas y sin colisiones.

---

## 🚀 Cómo Usar el Sistema (Rutas de Entrada)

El flujo de n8n (`email_pdf_excell_unificado.json`) vigila dos "buzones" distintos. Elige el que mejor se adapte al documento:

### Opción A: Vía Paperless-ngx (Recomendada)
**Carpeta:** `entrada_facturas_pdf`
* **Ideal para:** Facturas escaneadas, fotos, o PDFs complejos que requieren un OCR perfecto, así como para archivar permanentemente la factura.
* **Proceso:**
  1. Dejas el archivo en la carpeta `entrada_facturas_pdf` (o lo subes por la web de Paperless).
  2. Paperless lo consume, aplica su motor OCR profundo y lo guarda en su base de datos documental.
  3. Al terminar, dispara automáticamente un Webhook instantáneo hacia n8n.
  4. n8n recoge el texto extraído, lo envía a Ollama (IA) y lo añade al Excel.

### Opción B: Vía Directa (n8n "Cada Minuto")
**Carpeta:** `entrada_n8n_directo`
* **Ideal para:** Facturas digitales nativas (donde el texto se puede seleccionar con el ratón) que quieres procesar a máxima velocidad sin guardarlas en Paperless.
* **Proceso:**
  1. Dejas el archivo en la carpeta `entrada_n8n_directo`.
  2. n8n revisa la carpeta cada minuto.
  3. Extrae el texto digitalmente en un milisegundo (si es una imagen, tiene una ruta de emergencia para enviarla temporalmente a OCR).
  4. La IA procesa los datos, actualiza el Excel y mueve físicamente el archivo a la carpeta `facturas_procesadas`.

---

## 🧐 Análisis Profundo del Flujo de Trabajo (n8n)

Ambas rutas confluyen en un único nodo de Inteligencia Artificial para evitar duplicar código. A continuación se explican las ramas clave:

### Rama Webhook (Paperless)
1. **Webhook Paperless:** Escucha en el puerto 5678 peticiones `POST` desde Paperless-ngx.
2. **Obtener OCR Paperless Webhook:** Hace una petición `HTTP GET` a la API de Paperless para descargar el último texto OCR perfecto.

### Rama Carpeta (Cada Minuto)
3. **Cada Minuto / Buscar PDFs:** Despierta silenciosamente, busca archivos en `entrada_n8n_directo` y los encola.
4. **Bucle (Split in Batches):** Asegura que no haya colisiones liberando un archivo de cada vez.
5. **Leer PDF / Texto:** Intenta lectura rápida. Si el texto devuelto está vacío, usa la ruta de emergencia de enviar el archivo vía API a Paperless para forzar un OCR al vuelo.

### Convergencia y Procesamiento
6. **Ollama (Inferencia IA):** El "cerebro" del sistema (`Llama 3.2` local). Recibe el texto de cualquiera de las dos rutas y aplica un Prompt Engineering estricto:
   - Respetar tildes y sufijos legales.
   - Forzar "No disponible" si faltan datos.
   - Distinguir perfectamente al Cliente (Innovatek) del Proveedor.
   - Extraer campos precisos: NIFs, IBAN, importes y método de pago.
7. **Leer Excel:** Verifica si el archivo `tabla_excell_facturas.xls` existe. Si no existe o está vacío, no se detiene, pasará un archivo nulo al siguiente paso.
8. **Procesar (JavaScript Code):** El núcleo de seguridad:
   - Valida que Base Imponible + IVA = Total.
   - Verifica que el número de factura no exista ya en el archivo para evitar **duplicados**.
   - Genera dinámicamente un código **XML Spreadsheet 2003**. Si el Excel no existe, construye las cabeceras desde cero con estilos y colores.
9. **¿Nuevo? / Guardar Excel:** Si pasó los filtros, sobrescribe físicamente el archivo Excel.
10. **¿Viene de Carpeta? / Mover PDF:** Nodo inteligente que detecta el origen. Si vino de Webhook, termina silenciosamente. Si vino de la carpeta, mueve el PDF procesado a `facturas_procesadas`.

---

## 🛠️ Componentes de la Infraestructura Docker

- **n8n:** Orquestador principal (`email_pdf_excell_unificado.json`).
- **Paperless-ngx (con Tesseract):** Gestor documental y motor OCR avanzado.
- **Ollama:** Servidor de Inferencia Generativa (`Llama 3.2`).
- **Redis / PostgreSQL:** Motores de base de datos para la gestión rápida de los documentos de Paperless.

*Documentación actualizada: Mayo 2026*