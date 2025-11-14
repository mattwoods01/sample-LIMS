from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.lib.colors import Color, black
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from textwrap import wrap
from datetime import datetime

def convert_date_flexible(input_date, date_field=False, date_type=False):
    """
    Converts various date formats to select few based off field it is being placed into
    """
    formats = ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]  
    for fmt in formats:
        try:
            date_object = datetime.strptime(input_date, fmt)

            if date_field:
                return date_object.strftime("%d/%m/%Y")
            
            elif date_type:
                return date_object.strftime("%d%b%y").upper()
            
            else:
                return date_object.strftime('%d-%b-%y')
        
        except ValueError:
            continue
        
    return "Invalid date format"
 
class sto_generator:
    def __init__(self, folder_name, bio_headers, sto_headers, sto_data):
        self.folder_name = folder_name
        self.bio_headers = bio_headers
        self.sto_headers = sto_headers
        self.sto_data = sto_data

    def create_page_numbers(self, c):
        """
        adds page numbers to stos.
        """
        c.setFont("Helvetica", 12)
        page_num = c.getPageNumber()
        text = f"Page | {page_num}"
        c.drawString(530, 50, text)

    def generate_pool(self, bio_data_group):  
        """
        Generates pooled coas
        """

        sto_dict = {self.sto_headers[i]: self.sto_data[i] for i in range(len(self.sto_headers))}  
        so_text = str(sto_dict['Sales Order #'])
        sku_text = str(sto_dict['SKU'])
        ncbi_text = str(bio_data_group.iloc[0]['ncbi_gene'])
        ecd_text = str(convert_date_flexible(sto_dict['ECD'], False, True))

        file_name = f"{self.folder_name}/{so_text} {sku_text} NCBI {ncbi_text} {ecd_text}.pdf"
   
        c = canvas.Canvas(file_name, pagesize=letter)
        # Set the font size and position for the left side text
        left_text_x = 60
        left_text_y = 630
        left_text_line_height = 13

        left_text = "Service Type: LentiArray™ Custom Lentiviral Particles\n"
        left_text += f"SKU #: {sto_dict['SKU']}\n"
        left_text += f"Customer Name/Institute: {sto_dict['Account Name']}\n"
        left_text += "Lentivirus Plasmid: Target Gene gRNA Sequence - Puro\n"
        left_text += "Titer Method: Presence of live viral particles confirmed by antibiotic selection"

        for line in left_text.split('\n'):
            label, value = line.split(":", 1)
            label = label.strip()
            value = value.strip()

            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_text_x, left_text_y, label + ': ')
            c.setFont("Helvetica", 10)
            c.drawString(left_text_x + c.stringWidth(label) + 15, left_text_y, value)

            left_text_y -= left_text_line_height

        right_text_x = 420
        right_text_y = 630
        right_text_line_height = 13

        right_text = f"Date: {sto_dict['ECD']}\n"
        right_text += f"Lot: {sto_dict['Lot #']}\n"
        right_text += f"Quote: {sto_dict['Quote Number']}"
    
        for line in right_text.split('\n'):
            label, value = line.split(":", 1)
            label = label.strip()
            value = value.strip()

            c.setFont("Helvetica-Bold", 10)
            c.drawString(right_text_x, right_text_y, label + ': ')
            c.setFont("Helvetica", 10)
            c.drawString(right_text_x + c.stringWidth(label) + 15, right_text_y, value)

            right_text_y -= right_text_line_height

        x, y = 420, 590
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "SO #:")

        lines = wrap(so_text, width=25)
        c.setFont("Helvetica", 10)
        for line in lines:
            c.drawString(455, y, line)
            y -= 12 

        additional_text_y = 550
        additional_text = "Product Qualification"
        c.setFont("Helvetica-Bold", 11)  

        for line in additional_text.split('\n'):
            c.drawString(50, 550, line)
            additional_text_y -= 10

        if len(bio_data_group['sequence1'].values) == 4:
            table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
                ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
                ])

        else:
            table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
                ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
                ])
            
        product_data = [['Target Gene', 'gRNA Sequence(s)', 'Titer Result'], 
                        [str(bio_data_group.iloc[0]['gene_name']), '\n'.join(str(value) for value in bio_data_group['sequence1'].values), 'Conforms']]
        
        table_data = [[Paragraph(cell, getSampleStyleSheet()['BodyText']) for cell in row] for row in product_data]
        table = Table(product_data, colWidths=[100, 300, 100], rowHeights=[15, 50])

        table.setStyle(table_style)
        table.wrapOn(c, 0, 0)
        table_height = table._height

        x = 50 
        y = additional_text_y - table_height + 7
        table.drawOn(c, x, y)
        address = '<font color="#0264c2"><u><link href="' + 'https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0016089_LentiArray_CRISPR_gRNA_UG.pdf' + '">' + 'https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0016089_LentiArray_CRISPR_gRNA_UG.pdf' +  '</link></u></font>'

        additional_text_y = 465
        additional_text = "Additional Information"
        c.setFont("Helvetica-Bold", 11)  

        for line in additional_text.split('\n'):
            c.drawString(50, additional_text_y, line)
            additional_text_y -= 15

        add_data = [
            ['Deliverables', 'Lentivirus and CoA'],
            ['Lentivirus Stock Provided', '200 μL of each lentivirus'],
            ['Number of Tubes', f"{str(sto_dict['Quantity'])} tube(s)"],
            ['Virus Media', 'LV-MAX<sup>TM</sup> Production Medium (A3583401)'],
            ['Titer Assay', 'Puromycin Resistance Assay'],
            ['Titer Results Determined By', 'Resistant colonies at dilution'],
            ['Viral Concentration', 'Titer Units: TU/mL'],
            ['Storage Information', 'Lentivirus stock should be stored at -80° C. Multiple freeze/thaw cycles or storage at higher temperatures will result in a loss in titer.'],
            ['Product Usage Guidelines', f'Please reference {address} for usage guidelines.'],
            ['Additional Notes', 'Titers of viral stocks may vary depending upon the specific insert of interest and the original DNA used in the viral production process. Life Technologies does not guarantee the TU/mL of viral stocks. Life Technologies does not guarantee insert functionality. Functionality may vary by insert, cell line, volume of cell suspension, and duration. These variables may be optimized by the custom services department using additional services.']
            ]

        table_data = [[Paragraph(cell, getSampleStyleSheet()['BodyText']) for cell in row] for row in add_data]
        second_table = Table(table_data, colWidths=[150, 350], rowHeights=[20 for x in range(7)] + [30, 40, 90])

        second_table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
            ('BACKGROUND', (0, 0), (-1, 0), 'white'),  # Header background color
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
            ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
            ])

        second_table.setStyle(second_table_style)
        second_table.wrapOn(c, 0, 0)
        second_table.drawOn(c, 50, 160)

        c.setFont("Helvetica-Bold", 10)
        text = "Purchaser Notification"
        x = 50
        y = 140
        c.drawString(x, y, text)

        # Calculate the width of the text to draw the underline
        text_width = c.stringWidth(text, "Helvetica-Bold", 10)
        c.line(x, y - 2, x + text_width, y - 2)

        # Set the font and draw the disclaimer text
        c.setFont("Helvetica", 10)

        disclaimer_text = ("This Certificate of Analysis incorporates by reference Life Technologies` Terms and Conditions for Provision of\n"
                           "Services, including restrictions on the use of deliverables.  These products may be covered by one or more\n"
                           "Limited Use Label Licenses; reference original quote for specific details.")
        left_text_x = 50
        left_text_disclaimer_y = 125
        left_text_line_height = 12
        for line in disclaimer_text.split('\n'):
            c.drawString(left_text_x, left_text_disclaimer_y, line)
            left_text_disclaimer_y -= left_text_line_height

        c.save()

        return file_name

    def generate_single(self, bio_data):
        """
        generates single coas
        """
        def adjust_font_size_for_transcripts(transcripts, max_items=6, normal_size=10, reduced_size=8):
            """
            adjust size of string if transcripts can't fit on a single line
            """
            style_sheet = getSampleStyleSheet()
            items = transcripts.split(',')

            if len(items) > max_items:
                custom_style = ParagraphStyle(
                    'reduced',
                    parent=style_sheet['BodyText'],
                    fontSize=reduced_size,
                    alignment=1 
                )

            else:
                custom_style = ParagraphStyle(
                    'normal',
                    parent=style_sheet['BodyText'],
                    fontSize=normal_size,
                    alignment=1 
                )
            return Paragraph(transcripts, custom_style)

        
        bio_dict = {self.bio_headers[i]: bio_data[i] for i in range(len(self.bio_headers))}
        sto_dict = {self.sto_headers[i]: self.sto_data[i] for i in range(len(self.sto_headers))}

        so_text = str(sto_dict['Sales Order #'])
        sku_text = str(sto_dict['SKU'])
        crispr_text = str(bio_dict['crispr_id'])
        ecd_text = str(convert_date_flexible(sto_dict['ECD'], False, True))

        file_name = f"{self.folder_name}/{so_text} {sku_text} CRISPR {crispr_text} {ecd_text}.pdf"

        left_text_x = 25
        left_text_line_height = 13
        left_text_y = 560

        # file_name = f"{self.folder_name}/{bio_dict['gene_name']}_{bio_dict['crispr_id']}_CRISPR_ARRAY.pdf"

        product_text = f"Product: LentiArray™ CRISPR Guide RNA (Pre-defined gene target)\n"
        quant_text = "Quantity: 1 Tube\n"
        sku_text = f"SKU#: {sto_dict['SKU']}\n"
        lot_text = f"Lot#: {sto_dict['Lot #']}\n"
        amount_text = f"Amount: Minimum of 200 μl of lentiviral particles\n"
        storage_text = f"Storage: at -80°C\n"
        supp_text = f"Supplied in / Composition: Lentivirus is provided in a proprietary, chemically defined, antibiotic-free, serum-free, protein-free medium\n"
        date_text = f"Date of MFG: {convert_date_flexible(sto_dict['Lab ECD'])}"

        left_text = product_text + quant_text + sku_text + lot_text + amount_text + storage_text + supp_text + date_text

        c = canvas.Canvas(file_name, pagesize=(11 * inch, 8.5 * inch))

        for line in left_text.split('\n'):
            label, value = line.split(":", 1)
            label = label.strip()
            value = value.strip()

            c.setFont("Helvetica-Bold", 10)
            c.drawString(left_text_x, left_text_y, label + ': ')
            c.setFont("Helvetica", 10)
            c.drawString(left_text_x + 130, left_text_y, value)

            left_text_y -= left_text_line_height

        product_data = [
                ['CRISPR ID #', bio_dict['crispr_id']],
                ['Gene Name', bio_dict['gene_name']],
                ['Gene ID #', bio_dict['ncbi_gene']],
                ['gRNA Sequence', bio_dict['sequence1']],
                ['PAM Site', bio_dict['crispr_pam']],
                ['Targeted Transcripts', adjust_font_size_for_transcripts(bio_dict['transcript_id'])]
                ]

        quality_data = [
                ['Titer', 'Prescence of live viral particles confirmed by Antibiotic Selection', 'Conforms'],
                ['Sequence Verification', 'Sequencing results for the DNA template used for lentiviral package match to\nexpected target sequence', 'Conforms']
            ]

        product_data = [['Parameter', 'Description']] + product_data
        quality_data = [['Parameter', 'Method', 'Result']] + quality_data

        product_table = Table(product_data, colWidths=[120, 520], rowHeights=[20] + [23 for x in range(len(product_data)-1)])

        product_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
                ('BACKGROUND', (0, 0), (0, -1), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (0, -1), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
            ])
        product_table.setStyle(product_style)

        product_table.wrapOn(c, 0, 0)
        product_table.drawOn(c, 100, 290)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(370, 455, "Product Information")

        product_table = Table(quality_data, colWidths=[120, 400, 120], rowHeights=[20] + [25 for x in range(len(quality_data)-1)])

        product_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
                ('BACKGROUND', (0, 0), (0, -1), 'white'),  # Header background color
                ('TEXTCOLOR', (0, 0), (0, -1), '#000000'),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (-1, -1), 0.5, '#000000'),  # Grid lines
            ])
        product_table.setStyle(product_style)

        product_table.wrapOn(c, 0, 0)
        product_table.drawOn(c, 100, 185)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(380, 265, "Quality Control")
        c.setFont("Helvetica", 12)
        disclaimer_text = "For Research Use Only. Not for use in diagnostic procedures. If you have any further questions about this Certificate of Analysis,\nplease contact Technical Services at 1-800-955-6288 x4 (US and Canada) or 1-760-603-7200, x4 (all other countries)."
        left_text_disclaimer_y = 150
        for line in disclaimer_text.split('\n'):
            c.drawString(left_text_x, left_text_disclaimer_y, line)
            left_text_disclaimer_y -= left_text_line_height

        comp_text = "Thermo Fisher Scientific\nLife Sciences Solutions\n5781 Van Allen Way\nCarlsbad, CA, USA 92008\nwww.thermofisher.com\nFor inquiries, contact us at cofarequests@thermofisher.com"

        left_text_disclaimer_y = 95
        for line in comp_text.split('\n'):
            c.drawString(left_text_x, left_text_disclaimer_y, line)
            left_text_disclaimer_y -= left_text_line_height

        new_date_str = convert_date_flexible(sto_dict['ECD'])

        image_path = "greenlab_signature/Green-Circle.png"
        c.drawImage(image_path, 660, 40, width=100, height=100, mask='auto')
        blurb_text = "The Cell Biology Custom Services Laboratory in Carlsbad, CA is Green Lab Certified.\nLearn more at www.mygreenlab.org"
        left_text_disclaimer_y = 40
        for line in blurb_text.split('\n'):
            c.setFont("Helvetica", 10)
            c.drawString(375, left_text_disclaimer_y, line)
            left_text_disclaimer_y -= left_text_line_height

        navy_blue = Color(0, 0, 0.5)  
        c.setFillColor(navy_blue)

        c.drawString(690, 5, "Page 1 of 1")
        c.drawString(10, 5, new_date_str)

        c.save()

        return file_name
