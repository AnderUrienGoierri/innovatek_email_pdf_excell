# 📑 Sistema Inteligente de Extracción de Facturas (Ollama + n8n)

Este proyecto automatiza la extracción de datos de facturas PDF utilizando Inteligencia Artificial local (Ollama) y n8n, inyectando los resultados directamente en una base de datos Excel optimizada.

## 📂 Estructura del Proyecto
*   📂 **`workflows/`**: Archivos de flujo (.json) para importar en n8n.
*   📂 **`prompts/`**: Instrucciones maestras (System Prompts) para la IA.
*   📂 **`docs/`**: Guías técnicas y documentación detallada de cada versión.
*   📂 **`scripts/`**: Automatizaciones auxiliares.
*   📂 **`entrada_facturas_pdf/`**: Carpeta vigilada donde debes depositar tus facturas.
*   📂 **`facturas_procesadas/`**: Archivo histórico de facturas ya gestionadas.

---

## 🤖 Versiones del Workflow (JSON)

Actualmente el proyecto cuenta con 3 variantes según la necesidad de procesamiento:

### 1. 🌟 AI Agent (Versión Recomendada)
*   **Archivo:** `workflows/email_pdf_excell_AI_Agent.json`
*   **Tecnología:** LangChain AI Agent + Ollama Qwen2.5 14b + Simple Memory.
*   **Capacidades:** 
    *   **Razonamiento:** Entiende contextos complejos (envíos, promociones, descuentos).
    *   **Memoria:** Recuerda datos de proveedores recurrentes (IBAN, CIF).
    *   **Extracción Quirúrgica:** 17 columnas de datos financieros.
    *   **Auto-reparación:** Crea el Excel automáticamente si no existe.

### 2. 🔗 Versión Unificada
*   **Archivo:** `workflows/email_pdf_excell_unificado.json`
*   **Capacidades:** Combina la lógica de recepción por Email y detección de archivos locales en un solo flujo robusto. Utiliza llamadas HTTP directas a Ollama.

### 3. 📄 Versión Estándar (Legacy)
*   **Archivo:** `workflows/email_pdf_excell.json`
*   **Capacidades:** La versión base original para extracciones simples. Ideal si buscas un flujo ligero sin la complejidad del Agente de IA.

---

## ⚙️ Configuración del Entorno
*   **Servidor Ollama:** Local IP `192.168.5.152:11434`
*   **Modelo IA:** `qwen2.5:14b` (Asegúrate de tenerlo descargado con `ollama run qwen2.5:14b`).
*   **Receptor Fijo:** El sistema está pre-configurado para **Innovatek** (Alex Calvo García y Otra CB).

## 🔒 Seguridad
Los archivos de facturas reales y los resultados de Excel (`.pdf`, `.xls`) están protegidos por el archivo **`.gitignore`** para que nunca se suban a repositorios públicos.

---
*Mantenido por Innovatek IT Consulting.*