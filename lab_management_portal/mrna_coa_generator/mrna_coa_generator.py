from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib.units import inch
from PyPDF4 import PdfFileWriter, PdfFileReader
from reportlab.platypus import Table, TableStyle, Paragraph, Image
from textwrap import wrap
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import numpy as np
import os
import helper

"""
initialize font for asian languages
"""
helper.initialize_font('Fonts/NotoSansCJK-VF.ttf.ttc')

def convert_image_if_tiff(image_path):
    """
    Converts tiff to image
    """
    output_path = os.path.splitext(image_path)[0] + '.jpeg'
    with PILImage.open(image_path) as img:

        if img.mode == "I;16":
            img = img.point(lambda i: i * (1 / 255))

        dst_img = img.convert("RGB")
        dst_img.save(output_path, quality=95)

        return output_path  # Return the bytes buffer for use in ReportLab
    
def create_page_numbers(c):
    """
    add page numbers to pdf
    """
    c.setFont("Helvetica", 10)
    page_num = c.getPageNumber()
    c.setFillColor(colors.grey)
    c.drawString(750, 25, f"{page_num}")

    text = "Thermo Fisher Scientific Custom Services Confidential Report"
    c.setFillColor(colors.grey)
    c.drawString(250, 25, text)

def put_watermark(input_pdf, output_pdf, watermark):
    """
    add thermofisher watermark to page
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

def generate_pdf(folder_name, form_dict, input_df, image_path):
    """
    generate coa 
    """
    form_ecd = helper.convert_date_flexible(form_dict['ECD'])
    file_name = f"{folder_name}/CoA {form_dict['Account Name']} {form_ecd}.pdf"
    c = canvas.Canvas(file_name, pagesize=(11 * inch, 8.5 * inch))
    input_df.replace('', np.nan, inplace=True)
    input_df = input_df.dropna()
    
    input_values_ls = input_df.values.tolist()
    input_headers_ls = input_df.columns.tolist()

    input_ls = [input_headers_ls] + input_values_ls

    semicolon_position = 180  # Fixed x-coordinate for semicolons
    value_start_offset = 10  # Space between the semicolon and the start of the value
    left_text_y = 450
    left_text_line_height = 15

    customer_label = form_dict['Account Name']

    left_text = ""
    left_text += "Service Type: Design and Synthesis of mRNA\n"
    left_text += f"SKU #: {form_dict['SKU']}\n"
    left_text += f"Customer Name/Institute: {customer_label}\n"
    left_text += "Species: N/A"

    # Draw text with semicolons aligned
    for line in left_text.split('\n'):
        label, value = line.split(":", 1)
        label = label.strip()
        value = value.strip()

        # Calculate label width and adjust starting position
        label_width = c.stringWidth(label, "Helvetica-Bold", 10)
        label_start_x = semicolon_position - label_width

        # Draw label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(label_start_x, left_text_y, label)
        # Draw semicolon and value
        c.drawString(semicolon_position, left_text_y, ':')

        font_name = 'Helvetica'

        if label == "Customer Name/Institute":
            language = helper.detect_language(customer_label)
            print(language)
            for char in customer_label:
                if language in ['Korean', 'Chinese', 'Japanese']:
                    font_name = 'NotoSansCJK-Regular'
                    break
                    

        c.setFont(font_name, 10)
        c.drawString(semicolon_position + value_start_offset, left_text_y, value)

        left_text_y -= left_text_line_height

    semicolon_position = 655  # Distance to the left of right_text_x where semicolons will align
    value_start_offset = 5  # Space between the semicolon and the start of the value
    right_text_y = 450
    right_text_line_height = 15

    right_text = f"Date: {form_dict['ECD']}\n"
    right_text += f"Lot: {form_dict['E1 Lot #']}\n"
    right_text += f"Quote #: {form_dict['Quote Number']}"

    # Iterate through each line to draw it
    for line in right_text.split('\n'):
        label, value = line.split(":", 1)
        label = label.strip()
        value = value.strip()

        # Calculate label width and adjust starting position
        label_width = c.stringWidth(label, "Helvetica-Bold", 10)
        label_start_x = semicolon_position - label_width

        # Draw label
        c.setFont("Helvetica-Bold", 10)
        c.drawString(label_start_x, right_text_y, label)

        # Draw semicolon and value
        c.drawString(semicolon_position, right_text_y, ':')
        c.setFont("Helvetica", 10)
        c.drawString(semicolon_position + value_start_offset, right_text_y, value)

        right_text_y -= right_text_line_height

    so_text = str(form_dict['Sales Order #'])
    x = 630
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, right_text_y, "SO #:")

    lines = wrap(so_text, width=25)
    c.setFont("Helvetica", 10)
    for line in lines:
        c.drawString(660, right_text_y, line)
        right_text_y -= 12 

    # styles = getSampleStyleSheet()
    # header_style = ParagraphStyle('HeaderStyle', parent=getSampleStyleSheet()['Normal'])
    # header_style.fontName = 'Helvetica-Bold'
    # body_style = styles['BodyText']

    table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),  # Font size
                ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
                ])
       
    # table_data = [[Paragraph(cell, body_style) for cell in row] for row in input_ls]
    # table_data[0] = [Paragraph(cell, header_style) for cell in input_ls[0]]
    table = Table(input_ls, colWidths=[310, 210, 180], rowHeights=[30] + [15 for x in range(len(input_ls)-1)])

    table_width, table_height = table.wrap(0, 0) 

    table.setStyle(table_style)
    table.wrapOn(c, 0, 0)

    x = 50
    y_header = right_text_y - 15
    table_header = "Product Qualification"
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y_header, table_header)

    y = y_header - table_height - 7
    table.drawOn(c, x, y)
    create_page_numbers(c)
    c.showPage()

    buf_adr = '<font color="#0264c2"><u><link href="' + 'https://www.thermofisher.com/order/catalog/product/A57621?SID=srch-srp-A57621' + '">' + 'mMESSAGE mMACHINE™ T7 mRNA Kit with CleanCap™ Reagent AG (#A57621)' +  '</link></u></font>'
    pur_adr = '<font color="#0264c2"><u><link href="' + 'https://www.thermofisher.com/order/catalog/product/5400630' + '">' + 'KingFisher™ Flex Purification System (#5400630)' +  '</link></u></font>'
    bea_adr = '<font color="#0264c2"><u><link href="' + 'https://www.thermofisher.com/order/catalog/product/65011' + '">' + 'Dynabeads™ MyOne™ Carboxylic Acid (#65011)' +  '</link></u></font>'
    qua_adr = '<font color="#0264c2"><u><link href="' + 'https://www.thermofisher.com/order/catalog/product/Q33140' + '">' + 'Quant-iT™ RNA Assay Kit (#Q33140)' +  '</link></u></font>'
    use_adr = '<font color="#0264c2"><u><link href="' + 'https://www.thermofisher.com/order/catalog/product/LMRNA008?ICID=search-product' + '">' + 'Please refer to Lipofectamine® MessengerMAXTM (#LMRNA008) Product Manual(s) for mRNA Transfection.' +  '</link></u></font>'
    
    image_width = 6*inch
    image_height = 4*inch
    image_stream = convert_image_if_tiff(image_path)
    reportlab_image = Image(image_stream, width=image_width, height=image_height)  # Specify desired size

    additional_data = [
            ['Deliverables', 'CoA with in vitro transcribed mRNAs'],
            ['Number of tubes', form_dict['Quantity']],
            ['Volume/Tube', form_dict['Volume/Tube'] + ' µL'],
            ['Buffer Composition', 'The RNA Storage Solution (1 mM Sodium Citrate, #AM7000)'],
            ['mRNA synthesis kit', buf_adr],
            ['mRNA synthesis kit lot #', form_dict['mRNA synthesis kit lot #']],
            ['mRNA purification', 'LiCl Precipitation (mMESSAGE mMACHINE™ T7 mRNA Kit with CleanCap™ Reagent AG (#A57621))'],
            ['mRNA quantitation kit', qua_adr],
            ['Storage Conditions', '-80°C'],
            ['RNA TapeStation Gel Analysis of mRNA', reportlab_image],
            ['Product Usage Guidelines', use_adr]
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
    
    table_style.add('LEFTPADDING', (1, 9), (1, 9), 0)
    
    frame_width = 500  
    frame_height = image_height
        
    table_data = []
    for row in additional_data:
        new_row = []
        for cell in row:
            if isinstance(cell, str):  
                new_row.append(Paragraph(cell, getSampleStyleSheet()['BodyText']))
            else: 
                new_row.append(reportlab_image)

        table_data.append(new_row)

    row_heights = [15 for x in range(len(additional_data))]
    row_heights[9] = frame_height

    table = Table(table_data, colWidths=[200, 500], rowHeights=row_heights)
    table_width, table_height = table.wrap(0, 0) 
    table.setStyle(table_style)
    table.wrapOn(c, 0, 0)

    x = 50
    y_header = 550 
    table_header = "Additional Information"
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y_header, table_header)

    y = y_header - table_height - 7
    table.drawOn(c, x, y)
    create_page_numbers(c)
    c.showPage()

    comp_text = "This Certificate of Analysis incorporates by reference Life Technologies' Terms and Conditions for Provision of Services,\nincluding restrictions on the use of deliverables.\nThese products may be covered by one or more Limited Use Label Licenses; reference original quote for specific details."
    left_text_disclaimer_y = 550
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, left_text_disclaimer_y + 15, 'Purchaser Notificaion')
    for line in comp_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(x, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    comp_text = "This product is for internal research use only. In particular, this product or components or clones of this product,\nmay not be transferred for consideration or sold to any third party without the prior written agreement of Life Technologies Corporation.\nFor information on purchasing a license to this product for purposes other than research, contact the Director of Licensing,\n5791 Van Allen Way, Carlsbad, CA 92008. Phone: (760) 603-7200. Fax: (760) 603-7201."
    left_text_disclaimer_y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, left_text_disclaimer_y + 15, 'Licensing Information') 
    for line in comp_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(x, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    comp_text = "This product is distributed for laboratory research only.  CAUTION: Not for diagnostic use.\nThe safety and efficacy of this product in diagnostic or other clinical uses has not been established."
    left_text_disclaimer_y -= 30
    for line in comp_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(x, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    image_path = "greenlab_signature/Green-Circle.png"
    c.drawImage(image_path, x, 70, width=100, height=100, mask='auto')
    blurb_text = "The Cell Biology Custom Services Laboratory in Carlsbad, CA is Green Lab Certified.\nLearn more at www.mygreenlab.org"
    left_text_disclaimer_y = 60
    for line in blurb_text.split('\n'):
        c.setFont("Helvetica", 10)
        c.drawString(x, left_text_disclaimer_y, line)
        left_text_disclaimer_y -= left_text_line_height

    create_page_numbers(c)
    c.save()
    put_watermark(file_name, file_name, "Overlays/overlay.pdf")

    return file_name