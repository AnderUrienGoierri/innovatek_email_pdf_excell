# Configuración de Gmail en Paperless-ngx

Guía paso a paso para conectar la cuenta **anurte@gmail.com** a Paperless-ngx
mediante IMAP y descargar automáticamente facturas adjuntas.

---

## Requisitos previos

1. Paperless-ngx arrancado:
   ```
   docker compose -f docker-compose-paperless.yml up -d
   ```
2. Acceder al panel en: **http://localhost:8010**
3. Credenciales de admin: `admin` / `admin123`
   *(Cámbialas en cuanto puedas desde Settings → Users)*

---

## Paso 1 — Crear la cuenta de correo (Mail Account)

1. En el menú lateral izquierdo abre **Settings** (⚙️).
2. Haz clic en **Mail Accounts**.
3. Pulsa **Add Mail Account** (botón azul, arriba a la derecha).
4. Rellena el formulario:

| Campo | Valor |
|-------|-------|
| **Name** | Gmail Facturas |
| **IMAP server** | `imap.gmail.com` |
| **IMAP port** | `993` |
| **IMAP security** | `SSL` |
| **Username** | `anurte@gmail.com` |
| **Password** | `agsz dzcf nima npiy` |

5. Pulsa **Test** (aparecerá un tick verde si la conexión es correcta).
6. Pulsa **Save**.

> **Nota:** La contraseña es una *clave de aplicación* de Google, no la
> contraseña normal de Gmail. Si la conexión falla, regenera una nueva en
> [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

---

## Paso 2 — Crear la regla de correo (Mail Rule)

La regla le dice a Paperless qué correos procesar y qué hacer con sus adjuntos.

1. En **Settings**, haz clic en **Mail Rules**.
2. Pulsa **Add Mail Rule**.
3. Rellena el formulario:

| Campo | Valor recomendado |
|-------|-------------------|
| **Name** | Facturas adjuntas |
| **Account** | Gmail Facturas *(la cuenta que acabas de crear)* |
| **Folder** | `INBOX` |
| **Filter from** | *(dejar vacío para procesar todos los remitentes)* |
| **Filter subject** | *(dejar vacío, o poner `factura` para filtrar)* |
| **Filter body** | *(dejar vacío)* |
| **Maximum age** | `30` días |
| **Attachment type** | `Attachments only` |
| **Action** | `Mark as read` |
| **Assign title from** | `None` |
| **Assign tags** | `factura` *(opcional, créala antes en Settings → Tags)* |

4. Pulsa **Save**.

---

## Paso 3 — Verificar que Paperless descarga los correos

Paperless revisa el correo automáticamente cada pocos minutos.
Para forzar una comprobación inmediata:

```bash
docker exec paperless_webserver python manage.py mail_fetcher
```

Verás en los logs (`docker logs paperless_webserver -f`) cómo se descargan
los adjuntos y, al terminar cada uno, cómo se invoca el post-consume script.

---

## Paso 4 — Comprobar el resultado en Excel

Tras procesar una factura, abre:

```
C:\Users\innovatek\n8n-watch\pdf_excell\tabla_excell_facturas.xls
```

Debería aparecer una nueva fila con todos los campos extraídos por Ollama.

---

## Ciclo de vida completo

```
Gmail (IMAP)
    │ Paperless descarga adjunto (pdf/jpg/png)
    ▼
Paperless OCR (Tesseract · idioma español)
    │ Texto extraído almacenado en BD
    ▼
post_consume.py  ←── Django ORM lee el texto OCR
    │
    ├─► Ollama llama3.2  →  JSON con campos de factura
    │
    └─► tabla_excell_facturas.xls  (XML Spreadsheet 2003)
             · Comprueba duplicados (nº factura + CIF emisor)
             · Añade nueva fila si no existe
```

---

## Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| Test de conexión falla | Clave de app incorrecta o IMAP desactivado | Revisar [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| No se descargan adjuntos | Regla de correo mal configurada | Revisar campo *Attachment type* = `Attachments only` |
| Script no se ejecuta | Permiso de ejecución | Verificar `PAPERLESS_POST_CONSUME_SCRIPT` en los logs del contenedor |
| Ollama no responde | Ollama no está corriendo en el host | Ejecutar `ollama serve` en la máquina Windows |
| Modelo no encontrado | Modelo no descargado | `ollama pull llama3.2` |
| XLS no se actualiza | Ruta de volumen incorrecta | Comprobar que el volumen `.:/data` está montado (`docker inspect paperless_webserver`) |

---

## Verificar logs del script

```bash
docker logs paperless_webserver --tail 50 | grep post_consume
```
