import os

EXCEL_PATH = "tabla_excell_facturas.xls"
HEADERS = [
    "Fecha Proceso", "Nombre Archivo", "Número Factura", "Fecha Factura",
    "Emisor", "CIF Emisor", "Cliente", "CIF Cliente",
    "Concepto", "Base Imponible", "% IVA", "Cuota IVA", "Total Factura",
    "Forma Pago", "IBAN",
]

def create_empty_excel():
    header_cells = "".join(
        f'<Cell ss:StyleID="hdr"><Data ss:Type="String">{h}</Data></Cell>'
        for h in HEADERS
    )
    xml_content = (
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
    
    with open(EXCEL_PATH, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"Archivo {EXCEL_PATH} reseteado con éxito.")

if __name__ == "__main__":
    create_empty_excel()
