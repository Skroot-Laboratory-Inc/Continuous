from datetime import datetime
from functools import partial

from reportlab.lib import colors, units
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.datetime_helpers import formatDatetime
from src.app.ui_manager.theme.colors import Colors


def createPdf(raw_data, pdfFilename, header: str, exportedBy: str, isLandscape: bool = False):
    pdf = SimpleDocTemplate(pdfFilename, pagesize=landscape(letter) if isLandscape else letter,
                            leftMargin=1 * units.inch,
                            rightMargin=1 * units.inch,
                            topMargin=1 * units.inch,
                            bottomMargin=1.25 * units.inch)
    elements = []
    data = [raw_data[0]]

    styles = getSampleStyleSheet()
    cell_style = styles["Normal"]
    cell_style.wordWrap = 'CJK'  # Enable word wrapping
    cell_style.alignment = 1     # Center alignment

    # Format data rows - convert all text cells to Paragraph objects
    for row in raw_data[1:]:
        processed_row = []
        for cell in row:
            # Convert to string and create Paragraph object for text wrapping
            p = Paragraph(str(cell), cell_style)
            processed_row.append(p)
        data.append(processed_row)

    table = Table(data)

    header_color = Colors().reportLabPrimary
    even_row_color = colors.white
    odd_row_color = Colors().reportLabLightPrimary

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    row_num = len(data)
    for i in range(1, row_num):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), even_row_color)
        else:
            style.add('BACKGROUND', (0, i), (-1, i), odd_row_color)

    table.setStyle(style)
    elements.append(table)

    header_footer_with_vars = partial(header_footer,
                                      header=header,
                                      exportedBy=exportedBy,
                                      isLandscape=isLandscape)
    # Build the PDF
    pdf.build(elements, onFirstPage=header_footer_with_vars, onLaterPages=header_footer_with_vars)


def header_footer(canvas, pdf: SimpleDocTemplate, header, exportedBy, isLandscape=False):
    canvas.saveState()
    styles = getSampleStyleSheet()

    # Get actual page width and height from the canvas
    page_width = canvas._pagesize[0]  # Width of the current page
    page_height = canvas._pagesize[1]  # Height of the current page

    leftMargin = 1 * units.inch
    rightMargin = 1 * units.inch
    topMargin = 1 * units.inch
    bottomMargin = 1 * units.inch

    # Header
    p = Paragraph(header, styles['Heading1'])
    p.wrapOn(canvas, page_width - (leftMargin + rightMargin), topMargin)
    p.drawOn(canvas, leftMargin, page_height - topMargin)

    # Footer Left
    p = Paragraph(f"Exported by {exportedBy}<br/><br/>Exported on {formatDatetime(datetime.now())}")
    p.wrapOn(canvas, page_width - (leftMargin + rightMargin), topMargin)
    p.drawOn(canvas, leftMargin, bottomMargin - 0.5 * units.inch)

    # Footer Right - Logo
    img_height = 1.5 * units.inch

    # For logo, calculate right position explicitly
    logo_x = page_width - rightMargin - 2 * units.inch  # Position from right side

    # Draw the image in the footer area - use explicit positioning
    canvas.drawImage(CommonFileManager().getSkrootLogo(),
                     x=logo_x,  # Right-aligned position
                     y=bottomMargin - 1 * units.inch,
                     height=img_height,
                     width=2 * units.inch,  # Explicitly set width
                     preserveAspectRatio=True,
                     mask='auto')

    # Release the canvas
    canvas.restoreState()
