# Documentación: Flujo de Facturación Inteligente con AI Agent

Este documento describe el funcionamiento y la estructura del flujo de n8n contenido en `email_pdf_excell_AI_Agent.json`. Este flujo utiliza agentes de IA autónomos para la extracción y procesamiento de facturas.

## 1. Descripción General
El flujo automatiza la detección de facturas en carpetas locales, extrae el texto mediante OCR (usando Paperless-ngx si es necesario) y utiliza un **Agente de IA (Ollama)** para analizar y estructurar los datos antes de guardarlos en un archivo Excel maestro.

## 2. Estructura del Workflow

El flujo se divide en 5 etapas principales:

### Etapa 1: Disparo y Detección
*   **Cada Minuto (Schedule Trigger):** Inicia el proceso automáticamente.
*   **Buscar PDFs (Execute Command):** Escanea la carpeta `/data/pdf_excell/entrada_facturas_pdf/` en busca de archivos nuevos (PDF, JPG, PNG).
*   **Hay Archivos? (If):** Filtra la ejecución si no se encuentran documentos nuevos.

### Etapa 2: Preparación de Archivos
*   **Separar Archivos (Code):** Convierte la lista de archivos en ítems individuales para n8n.
*   **Bucle (Split in Batches):** Procesa cada documento uno por uno para evitar sobrecargas.
*   **Leer PDF (Read/Write File):** Carga el contenido binario del archivo.

### Etapa 3: Extracción de Texto (OCR)
*   **Texto (Extract from File):** Intenta extraer texto nativo si el PDF es digital.
*   **¿Vacío? (If):** Si el PDF es una imagen o escaneo, lo envía al motor de OCR.
*   **OCR & Resultado (HTTP Request):** Se comunica con la API de Paperless-ngx para realizar un OCR profundo.

### Etapa 4: El Cerebro (AI Agent)
Esta es la parte central y más avanzada del flujo:
*   **AI Agent (Facturación):** Un nodo de agente que actúa como un humano. Recibe el texto del OCR y tiene la misión de generar un JSON válido.
*   **Ollama Chat Model:** Conecta con el modelo `qwen2.5:14b` alojado en `192.168.5.152`. Es el motor de razonamiento.
*   **Memoria de Sesión:** Permite al agente mantener el contexto entre diferentes pasos del análisis si fuera necesario.

### Etapa 5: Almacenamiento y Limpieza
*   **Excel (Read/Write File):** Lee la base de datos actual (`tabla_excell_facturas.xls`).
*   **Procesar (Code):** Inyecta los nuevos datos en el XML del Excel, validando duplicados.
*   **Guardar:** Sobrescribe el archivo Excel con la nueva fila añadida.
*   **Mover PDF:** Traslada la factura procesada a la carpeta `/data/pdf_excell/facturas_procesadas/`.

## 3. Configuración del Agente de IA

El agente está configurado con las siguientes **Instrucciones del Sistema**:
> "Eres un Agente de Facturación Autónomo. Tu objetivo es extraer datos de facturas con precisión quirúrgica. Si falta algún dato, indica 'No disponible'. Devuelve SIEMPRE un JSON puro."

### Ventajas de usar un Agente frente a un Prompt simple:
1.  **Razonamiento:** El agente puede "pensar" antes de responder.
2.  **Robustez:** Maneja mejor los errores y las inconsistencias en el formato del texto.
3.  **Escalabilidad:** Se le pueden añadir "Tools" (Herramientas) para que el agente consulte bases de datos o internet por su cuenta.

## 4. Requisitos del Sistema
*   **n8n:** Versión compatible con nodos de LangChain/IA.
*   **Ollama:** Modelo `qwen2.5:14b` corriendo en `192.168.5.152:11434`.
*   **Almacenamiento:** Acceso a las rutas de red configuradas en Docker.

---
*Documentación generada por Antigravity AI.*

## 5. Comparativa: Flujo Estándar vs. Flujo con Agente de IA

A continuación se detallan las mejoras clave de esta nueva versión frente al sistema de extracción tradicional (HTTP Request).

### Tabla Comparativa

| Característica | Flujo Anterior (Estándar) | Nuevo Flujo (AI Agent) |
| :--- | :--- | :--- |
| **Arquitectura** | Secuencial y rígida | Dinámica y adaptativa |
| **Lógica de IA** | Un solo intento (One-shot) | Ciclo de razonamiento (Chain-of-thought) |
| **Memoria** | No tiene (olvida cada factura) | Memoria de ventana (recuerda contexto) |
| **Herramientas** | Limitadas a nodos fijos | Puede usar "Tools" (Google, DB, Scripts) |
| **Gestión de Errores** | Falla si el JSON es imperfecto | Puede auto-corregirse antes de responder |

### Ventajas Principales del Agente de IA

#### 1. Razonamiento Autónomo
En el flujo anterior, el modelo simplemente intentaba rellenar un formulario. El **AI Agent** tiene un objetivo: *"Ser un gestor de facturación"*. Esto significa que si el texto del OCR es confuso, el agente utiliza su lógica interna para deducir qué campo es el más probable, en lugar de fallar o dejarlo vacío.

#### 2. Capacidad de Extensión (Skills)
El flujo estándar está "atrapado" en lo que n8n le envía. Al Agente de IA se le pueden añadir herramientas externas. Si mañana quieres que el sistema busque el CIF de una empresa en internet si no lo encuentra en el PDF, solo tienes que añadirle una **Tool** de búsqueda; el Agente decidirá por sí mismo cuándo usarla.

#### 3. Memoria de Sesión
Gracias al nodo **Window Buffer Memory**, el agente puede mantener un historial. Esto es crucial cuando procesas lotes de facturas del mismo proveedor, ya que el agente se vuelve más preciso a medida que "aprende" el formato específico durante la sesión de trabajo.

#### 4. Formato de Salida Garantizado
Los agentes de n8n están optimizados para interactuar con otros nodos. El nodo AI Agent gestiona internamente la limpieza de la respuesta, eliminando texto innecesario y asegurando que el JSON entregado al siguiente nodo sea lo más limpio posible.

## 6. ¿Por qué cambiar a este modelo?
La automatización tradicional se rompe ante la variabilidad. El **AI Agent** está diseñado para manejar la incertidumbre. En el mundo de las facturas, donde cada proveedor usa un diseño distinto, tener un "empleado virtual" que razone sobre los datos es mucho más eficiente que un script rígido.

## 7. Requisitos del Sistema
*   **n8n:** Versión compatible con nodos de LangChain/IA.
*   **Ollama:** Modelo `qwen2.5:14b` corriendo en `192.168.5.152:11434`.
*   **Almacenamiento:** Acceso a las rutas de red configuradas en Docker.
