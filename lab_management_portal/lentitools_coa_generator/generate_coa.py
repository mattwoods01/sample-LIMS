import helper
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from PyPDF4 import PdfFileWriter, PdfFileReader
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date
import numpy as np

def put_watermark(input_pdf, output_pdf, watermark):
    """
    add thermofisher watermark to pages
    """
    watermark_instance = PdfFileReader(watermark)
    watermark_page = watermark_instance.getPage(0)
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for i in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(i)
        
        if i == 0:      
            page.mergePage(watermark_page)  # Add watermark only to the first page
        
        pdf_writer.addPage(page)

    with open(output_pdf, 'wb') as out:
        pdf_writer.write(out)


def generate_pdf(folder_name, form_row):
    """
    generate coa
    """

    file_name2 = form_row['Quote No']
    file_name3 = form_row['GeneName'].replace("/", "-")
    date_name = str(date.today().strftime('%m-%d-%Y').lstrip('0'))
    acct_name = str(form_row['Account Name'])
    file_name_extension = 'lentivirus CoA'
    file_name = f'{file_name2} {file_name3} {date_name} {file_name_extension}.pdf'

    if helper.has_special_characters(file_name):
        return "FileNameError", file_name

    file_name = f'{folder_name}/{acct_name} {file_name2} {file_name3} {date_name} {file_name_extension}.pdf'

    c = canvas.Canvas(file_name, pagesize=(8.5 * inch, 11 * inch))
    
    left_text_x = 25 
    left_text_y = 670
    left_text_line_height = 13

    left_text = "Service Type: Lentivirus Production Concentration & Titer\n"
    left_text += f"SKU #: {form_row['SKU']}\n"
    left_text += f"Customer Name: {form_row['Customer Name']}\n"
    left_text += f"Institute: {form_row['Account Name']}\n"
    left_text += f"Lentivirus Plasmid: {form_row['VectorName']}"

    for line in left_text.split('\n'):
        label, value = line.split(":", 1)
        label = label.strip()
        value = value.strip()
        label += ' : '
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_text_x, left_text_y, label)
        label_width = stringWidth(label, "Helvetica-Bold", 10)
        c.setFont("Helvetica", 10)
        c.drawString(left_text_x + label_width + 5, left_text_y, value)
        left_text_y -= left_text_line_height

    right_text_x = 410
    right_text_y = 670
    right_text_line_height = 13

    right_text = f"Date: {form_row['Est. Lab Completion Date']}\n"
    right_text += f"Lot: {form_row['E1 Lot #']}\n"
    right_text += f"Quote #: {form_row['Quote No']}"

    for line in right_text.split('\n'):
        label, value = line.split(":", 1)
        label = label.strip()
        value = value.strip()
        label += ' : '
        c.setFont("Helvetica-Bold", 10)
        c.drawString(right_text_x, right_text_y, label)
        label_width = stringWidth(label, "Helvetica-Bold", 10)
        c.setFont("Helvetica", 10)
        c.drawString(right_text_x + label_width + 5, right_text_y, value)
        right_text_y -= right_text_line_height

    if form_row['Intercompany S6#'] == 'N/A':
        so_text = str(form_row['Sales Order #'])

    if isinstance(value, (int, float)) and np.isnan(value):
        so_text = str(form_row['Sales Order #'])

    else:
        so_text = str(form_row['Sales Order #']) + '\n' + str(form_row['Intercompany S6#'])


    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_text_x, right_text_y , "SO #/S6 #:")
    label_width = stringWidth("SO #/S6 #:", "Helvetica-Bold", 10)

    c.setFont("Helvetica", 10)
    for line in so_text.split('\n'):
        c.drawString(right_text_x + label_width + 5, right_text_y, line)
        right_text_y -= 12 

    styles = getSampleStyleSheet()

    center_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['BodyText'],
        fontSize=8,
        leading=10,
        spaceAfter=3,
        alignment=TA_CENTER  
    )

    left_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['BodyText'],
        fontSize=8,
        leading=10,
        spaceAfter=3,
        alignment=TA_LEFT  
    )

    table_data = [
        [Paragraph(helper.make_bold("Deliverables"), center_style), f"{form_row['# of vials']} x {form_row['Aliquot Size (uL)']} uL aliquots of Concentrated Lentivirus and CoA"],
        [Paragraph(helper.make_bold('Viral Suspension'), center_style), 'Lentivirus stock resuspended in 1X PBS (#14190250)'],
        [Paragraph(helper.make_bold('Number of Tubes'), center_style), f"{form_row['# of vials']} tubes per construct"],
        [Paragraph(helper.make_bold('Storage Information'), center_style), 'Lentivirus stock should be stored at -80° C. Freeze thaw cycles or storage at higher temperatures will result in a gradual loss in titer.'],
    ]

    table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
                ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
                ])
       
    table_data = [[Paragraph(str(cell), left_style) if isinstance(cell, str) else cell for cell in row] for row in table_data]
    table = Table(table_data, colWidths=[100, 410], rowHeights=[23 for x in range(len(table_data))])
    table.setStyle(table_style)
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 40, 515)

    test_method = form_row['Test Method']

    if test_method == 'p24':
        titer_thresh = '≥ 1 x 10^7'
        titer_method = f'{test_method} ELISA Assay'
        titer_deter = f'{test_method} concentration'

    elif test_method == 'Flow Cytometry':
        titer_thresh = '≥ 1 x 10^7'
        titer_method = 'Flow Cytometry'
        titer_deter = "Percent of GFP expression per dilution"

    else: 
        titer_thresh = '≥ 1 x 10^5'
        titer_method = f"{test_method} Resistance Assay" 
        titer_deter = "Number of colonies per dilution"


    titer_detect = form_row['Titer Results TU/mL']

    c.setFont("Helvetica-Bold", 10)
    c.drawString(25, 495, 'Product Qualification')

    prod_data = [
        [Paragraph(helper.make_bold('Viral Construct'), center_style), Paragraph(helper.make_bold('Test Method'), center_style), Paragraph(helper.make_bold('Titer Specification TU/mL'), center_style), Paragraph(helper.make_bold('Titer Results TU/mL'), center_style)],
        [Paragraph(f"{form_row['GeneName']}", center_style), Paragraph(titer_method, center_style), Paragraph(helper.format_exponent(titer_thresh), center_style), Paragraph(helper.format_exponent(titer_detect), center_style)]
    ]

    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
        ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
        ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines,
        ])
    
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['BodyText'],
        fontSize=10,
        leading=12,
        spaceAfter=6
    )
    
    table_data = [[Paragraph(str(cell), center_style) if isinstance(cell, str) else cell for cell in row] for row in prod_data]

    row_heights = [27 for x in range(len(prod_data))]
    table = Table(prod_data, colWidths=[140, 130, 125, 115], rowHeights=row_heights)
    table.setStyle(table_style)
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 40, 435)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(25, 415, 'Additional Information')
    add_data = [
        [Paragraph(helper.make_bold('Lenti Stock Provided'), center_style), f"{form_row['Volume / Construct']} mL of concentrated Lentivirus in {form_row['Aliquot Size (uL)']} uL aliquots"],
        [Paragraph(helper.make_bold('Titer Assay'), center_style), titer_method],
        [Paragraph(helper.make_bold('Titer Results Determined By'), center_style), titer_deter],
        [Paragraph(helper.make_bold('Viral Concentration'), center_style), 'Titer Units: TU/mL'],
        [Paragraph(helper.make_bold('Packaging Mix'), center_style), 'LV-MAX<sup>TM</sup> Lentiviral Packaging Mix (A43237)'],
        [Paragraph(helper.make_bold('Additional Notes'), center_style), 'Titers of viral stocks may vary depending upon the specific insert of interest and the original. DNA used in the viral production process. Life Technologies does not gurantee the TU/mL of viral stocks. Life Technologies does not gurantee the specific insert of interest funcntionality or levels of expression.'],
    ]

    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
        ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
        ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines,
        ])
    
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle('Custom', parent=styles['BodyText'], fontSize=8)

    table_data = [[Paragraph(str(cell), left_style) if isinstance(cell, str) else cell for cell in row] for row in add_data]
    row_heights = [30 for x in range(len(add_data))]
    row_heights[len(add_data)-1] = 60
    table = Table(table_data, colWidths=[125, 385], rowHeights=row_heights)
    table.setStyle(table_style)
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 40, 200)

    comp_text = "This Certificate of Analysis incorporates by reference Life Technologies' Terms and Conditions for Provision of Services,\nincluding restrictions on the use of deliverables. These products may be covered by one or more Limited Use Label\nLicenses; reference original quote for specific details."
    left_text_disclaimer_x = 25
    left_text_disclaimer_y = 150
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_text_disclaimer_x, left_text_disclaimer_y + 15, 'Purchaser Notificaion')

    for line in comp_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(50, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    image_path = "greenlab_signature/Green-Circle.png"
    c.drawImage(image_path, 500, 30, width=100, height=100, mask='auto')
    blurb_text = "The Cell Biology Custom Services Laboratory in Carlsbad, CA is Green Lab Certified.\nLearn more at www.mygreenlab.org"
    left_text_disclaimer_y = 60
    for line in blurb_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(left_text_disclaimer_x, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    c.save()
    put_watermark(file_name, file_name, "lentitools_coa_generator/vertical_overlay.pdf")

    return "NoError", file_name
