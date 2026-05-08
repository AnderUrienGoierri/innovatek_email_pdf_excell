#!/usr/bin/env python3
"""
Post-consume script para Paperless-ngx.
Extrae campos de factura via Ollama y los añade a tabla_excell_facturas.xls
en formato XML Spreadsheet 2003.

Paperless lo invoca automáticamente tras consumir cada documento,
inyectando las variables de entorno DOCUMENT_ID, DOCUMENT_FILE_NAME, etc.
"""

import os
import sys
import json
import re
import html
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [post_consume] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

# ── Variables que Paperless inyecta ─────────────────────────────────────────
DOCUMENT_ID        = os.environ.get("DOCUMENT_ID", "")
DOCUMENT_FILE_NAME = os.environ.get("DOCUMENT_FILE_NAME", "")
DOCUMENT_ORIG_NAME = os.environ.get("DOCUMENT_ORIGINAL_FILENAME", DOCUMENT_FILE_NAME)

# ── Configuración desde docker-compose ──────────────────────────────────────
OLLAMA_URL   = os.environ.get("OLLAMA_URL",   "http://host.docker.internal:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
EXCEL_PATH   = os.environ.get("EXCEL_PATH",   "/data/tabla_excell_facturas.xls")

# ── 1. Obtener el texto OCR via Django ORM ───────────────────────────────────
def get_document_content(doc_id: int) -> str:
    """
    El script se ejecuta dentro del contenedor de Paperless, que tiene
    el entorno Django completo disponible. Accedemos al ORM directamente
    para leer el campo 'content' (resultado del OCR) sin necesidad de
    tokens de API ni configuración adicional.
    """
    try:
        paperless_src = "/usr/src/paperless/src"
        if paperless_src not in sys.path:
            sys.path.insert(0, paperless_src)

        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "paperless.settings.production"
        )

        import django
        django.setup()

        from documents.models import Document
        doc = Document.objects.get(pk=doc_id)
        return doc.content or ""
    except Exception as exc:
        log.error("Error al leer el contenido OCR vía ORM: %s", exc)
        return ""


# ── 2. Extraer campos de factura con Ollama ──────────────────────────────────
PROMPT = """\
Eres un extractor de datos de facturas españolas. Analiza el texto OCR que \
te proporciono y extrae exactamente los campos indicados.
Devuelve ÚNICAMENTE un objeto JSON válido, sin texto adicional ni bloques \
de código markdown.

Campos requeridos (usa null si no aparece en el texto):
{
  "emisor_nombre":   "razón social del emisor",
  "emisor_cif":      "CIF/NIF del emisor",
  "cliente_nombre":  "razón social del cliente/destinatario",
  "cliente_cif":     "CIF/NIF del cliente",
  "numero_factura":  "número de factura",
  "fecha_factura":   "fecha en formato DD/MM/YYYY",
  "concepto":        "descripción breve del servicio o producto",
  "base_imponible":  "base imponible en euros, número decimal",
  "porcentaje_iva":  "tipo de IVA aplicado, número (ej: 21)",
  "cuota_iva":       "importe del IVA en euros, número decimal",
  "total_factura":   "total con IVA en euros, número decimal",
  "forma_pago":      "forma de pago (transferencia, domiciliación…)",
  "iban":            "IBAN o cuenta bancaria si aparece"
}

TEXTO OCR:
"""

def extract_invoice_fields(text: str) -> dict:
    import urllib.request

    prompt_full = PROMPT + text[:5000]
    payload = json.dumps({
        "model":  OLLAMA_MODEL,
        "prompt": prompt_full,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        raw = result.get("response", "{}")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            return json.loads(m.group()) if m else {}
    except Exception as exc:
        log.error("Error llamando a Ollama: %s", exc)
        return {}


# ── 3. Gestión del archivo XLS (XML Spreadsheet 2003) ───────────────────────
HEADERS = [
    "Fecha Proceso", "Nombre Archivo", "Número Factura", "Fecha Factura",
    "Emisor", "CIF Emisor", "Cliente", "CIF Cliente",
    "Concepto", "Base Imponible", "% IVA", "Cuota IVA", "Total Factura",
    "Forma Pago", "IBAN",
]

# Índices de columnas numéricas (Base, %IVA, Cuota, Total)
NUMERIC_COLS = {9, 10, 11, 12}

NS = "urn:schemas-microsoft-com:office:spreadsheet"


def _xml_cell(value, numeric: bool = False) -> str:
    if value is None or str(value).strip() == "":
        return '<Cell><Data ss:Type="String"></Data></Cell>'
    if numeric:
        try:
            float(value)
            return f'<Cell><Data ss:Type="Number">{value}</Data></Cell>'
        except (TypeError, ValueError):
            pass
    safe = html.escape(str(value))
    return f'<Cell><Data ss:Type="String">{safe}</Data></Cell>'


def _build_row_xml(values: list) -> str:
    cells = "".join(
        _xml_cell(v, numeric=(i in NUMERIC_COLS))
        for i, v in enumerate(values)
    )
    return f"   <Row>{cells}</Row>"


def _create_xml() -> str:
    header_cells = "".join(
        f'<Cell ss:StyleID="hdr"><Data ss:Type="String">{h}</Data></Cell>'
        for h in HEADERS
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?mso-application progid="Excel.Sheet"?>\n'
        '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n'
        ' xmlns:o="urn:schemas-microsoft-com:office:office"\n'
        ' xmlns:x="urn:schemas-microsoft-com:office:excel"\n'
        ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"\n'
        ' xmlns:html="http://www.w3.org/TR/REC-html40">\n'
        ' <Styles>\n'
        '  <Style ss:ID="Default" ss:Name="Normal">\n'
        '   <Font ss:FontName="Calibri" ss:Size="11"/>\n'
        '  </Style>\n'
        '  <Style ss:ID="hdr">\n'
        '   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>\n'
        '   <Interior ss:Color="#4472C4" ss:Pattern="Solid"/>\n'
        '  </Style>\n'
        '  <Style ss:ID="num">\n'
        '   <NumberFormat ss:Format="#,##0.00"/>\n'
        '  </Style>\n'
        ' </Styles>\n'
        ' <Worksheet ss:Name="Facturas">\n'
        '  <Table>\n'
        f'   <Row>{header_cells}</Row>\n'
        '  </Table>\n'
        ' </Worksheet>\n'
        '</Workbook>'
    )


def _read_xml() -> tuple:
    """Devuelve (xml_str, existing_rows_as_list_of_lists)."""
    if not os.path.exists(EXCEL_PATH):
        return None, []
    try:
        with open(EXCEL_PATH, "r", encoding="utf-8-sig") as fh:
            xml_str = fh.read()
        if NS not in xml_str:
            log.warning(
                "El archivo XLS existente no es XML Spreadsheet 2003. "
                "Se creará uno nuevo sin borrar el original (se renombrará)."
            )
            backup = EXCEL_PATH + ".bak"
            os.rename(EXCEL_PATH, backup)
            log.info("Archivo original renombrado a %s", backup)
            return None, []
        rows = _parse_rows(xml_str)
        return xml_str, rows
    except Exception as exc:
        log.warning("No se pudo leer el XLS existente: %s", exc)
        return None, []


def _parse_rows(xml_str: str) -> list:
    """Extrae filas de datos (sin cabecera) para detección de duplicados."""
    import xml.etree.ElementTree as ET

    tag_row  = f"{{{NS}}}Row"
    tag_cell = f"{{{NS}}}Cell"
    tag_data = f"{{{NS}}}Data"

    try:
        root = ET.fromstring(xml_str)
        table = root.find(f".//{{{NS}}}Table")
        if table is None:
            return []
        rows = []
        for i, row_el in enumerate(table.findall(tag_row)):
            if i == 0:      # saltar cabecera
                continue
            vals = []
            for cell in row_el.findall(tag_cell):
                data = cell.find(tag_data)
                vals.append(data.text if data is not None else "")
            rows.append(vals)
        return rows
    except Exception as exc:
        log.warning("Error al parsear filas existentes: %s", exc)
        return []


def _is_duplicate(rows: list, numero: str, cif_emisor: str) -> bool:
    if not numero:
        return False
    for row in rows:
        rnum = row[2] if len(row) > 2 else ""
        rcif = row[5] if len(row) > 5 else ""
        if rnum == str(numero) and rcif == str(cif_emisor or ""):
            return True
    return False


def _append_row(xml_str: str, new_row_xml: str) -> str:
    """Inserta una nueva fila antes de </Table>."""
    marker = "  </Table>"
    if marker not in xml_str:
        marker = "</Table>"
    return xml_str.replace(marker, f"{new_row_xml}\n  </Table>", 1)


def write_excel(xml_str, rows: list, values: list):
    if xml_str is None:
        xml_str = _create_xml()

    new_row = _build_row_xml(values)
    updated = _append_row(xml_str, new_row)

    with open(EXCEL_PATH, "w", encoding="utf-8") as fh:
        fh.write(updated)
    log.info("XLS guardado: %s", EXCEL_PATH)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not DOCUMENT_ID:
        log.error(
            "DOCUMENT_ID no está disponible. "
            "Este script debe ejecutarse desde Paperless-ngx."
        )
        sys.exit(1)

    log.info("=== Iniciando post_consume para documento ID=%s (%s) ===",
             DOCUMENT_ID, DOCUMENT_ORIG_NAME)

    # 1. Obtener texto OCR
    content = get_document_content(int(DOCUMENT_ID))
    if not content:
        log.warning("Contenido OCR vacío. Se abandona el proceso.")
        sys.exit(0)
    log.info("OCR obtenido: %d caracteres", len(content))

    # 2. Extraer campos con Ollama
    fields = extract_invoice_fields(content)
    log.info("Campos extraídos: %s", fields)

    if not fields:
        log.warning("Ollama no devolvió campos. Se abandona.")
        sys.exit(0)

    # 3. Leer XLS existente
    xml_str, existing_rows = _read_xml()

    # 4. Comprobar duplicado
    num_fac = str(fields.get("numero_factura") or "")
    cif_em  = str(fields.get("emisor_cif")     or "")
    if _is_duplicate(existing_rows, num_fac, cif_em):
        log.warning(
            "Factura duplicada (nº=%s / CIF=%s). No se añade.", num_fac, cif_em
        )
        sys.exit(0)

    # 5. Convertir campos numéricos
    def to_num(v):
        if v is None:
            return ""
        try:
            return float(str(v).replace(",", "."))
        except (TypeError, ValueError):
            return str(v)

    row_values = [
        datetime.now().strftime("%d/%m/%Y %H:%M"),      #  0 Fecha Proceso
        DOCUMENT_ORIG_NAME,                              #  1 Nombre Archivo
        num_fac,                                         #  2 Número Factura
        str(fields.get("fecha_factura")   or ""),        #  3 Fecha Factura
        str(fields.get("emisor_nombre")   or ""),        #  4 Emisor
        cif_em,                                          #  5 CIF Emisor
        str(fields.get("cliente_nombre")  or ""),        #  6 Cliente
        str(fields.get("cliente_cif")     or ""),        #  7 CIF Cliente
        str(fields.get("concepto")        or ""),        #  8 Concepto
        to_num(fields.get("base_imponible")),            #  9 Base Imponible
        to_num(fields.get("porcentaje_iva")),            # 10 % IVA
        to_num(fields.get("cuota_iva")),                 # 11 Cuota IVA
        to_num(fields.get("total_factura")),             # 12 Total Factura
        str(fields.get("forma_pago")      or ""),        # 13 Forma Pago
        str(fields.get("iban")            or ""),        # 14 IBAN
    ]

    # 6. Escribir en Excel
    write_excel(xml_str, existing_rows, row_values)
    log.info("=== Factura nº%s procesada correctamente ===", num_fac)


if __name__ == "__main__":
    main()
