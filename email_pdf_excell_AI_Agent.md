# Documentación del Flujo: Agente de IA para Facturación (Ollama)

Este documento detalla la evolución del sistema de extracción de facturas desde una lógica basada en reglas simples a un sistema de **Agente de IA Autónomo**.

## 🧠 Arquitectura del Sistema
El nuevo flujo (`email_pdf_excell_AI_Agent.json`) utiliza una arquitectura de agentes basada en LangChain dentro de n8n, compuesta por:

1.  **AI Agent (Cerebro):** Toma el texto extraído del PDF y razona sobre él para identificar campos complejos.
2.  **Ollama Chat Model (Motor):** Utiliza el modelo `qwen2.5:14b` alojado localmente en `192.168.5.152`.
3.  **Simple Memory (Contexto):** Mantiene una memoria de sesión (bajo la clave "facturas") para recordar datos recurrentes de proveedores.

## 🎯 Mejoras de Precisión (Surgical Precision)
Se ha implementado un **System Prompt** (`system_prompt_ollama.txt`) que garantiza:
*   **Normalización de Fechas:** Conversión automática a formato `DD/MM/YYYY`.
*   **Limpieza Numérica:** Punto decimal garantizado y eliminación de símbolos de moneda para cálculos precisos.
*   **Lógica Emisor/Receptor:** Identificación estricta de **Innovatek** como receptor, evitando que la IA lo confunda con el proveedor.
*   **Extracción Avanzada:** Ahora se capturan automáticamente datos que antes se perdían:
    *   Dirección completa del proveedor.
    *   CIF/NIF del emisor.
    *   Fecha de vencimiento.
    *   Desglose de IVA y Base Imponible.
    *   Forma de pago e IBAN.

## 📊 Sistema de Excel (SpreadsheetML)
El nodo **"Procesar"** utiliza un motor de generación XML compatible con Excel que ofrece:
*   **Multicolumna:** 15 columnas detalladas con datos de proveedor, cliente y financieros.
*   **Auto-reparación:** Si el archivo `tabla_excell_facturas.xls` es borrado o se corrompe, el flujo lo vuelve a crear desde cero con las cabeceras correctas.
*   **Gestión de Duplicados:** El sistema verifica el número de factura antes de escribir para evitar registros repetidos.

## 🔒 Seguridad y Privacidad
Se ha configurado un archivo **`.gitignore`** estricto que:
*   Bloquea la subida de cualquier archivo `.pdf` o `.xls`.
*   Mantiene la privacidad de los datos de proveedores y clientes.
*   Asegura que el flujo sea compartible sin exponer información confidencial.

## 🛠️ Especificaciones Técnicas
*   **N8N Version:** 2.18.5 (Self Hosted)
*   **Modelo IA:** qwen2.5:14b (Ollama)
*   **Formato de Salida:** SpreadsheetML (Excel 2003 XML)
*   **Localización:** 100% Local (Docker/Windows)

---
*Documentación actualizada el 11 de Mayo de 2026.*
