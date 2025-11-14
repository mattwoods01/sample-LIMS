import pytesseract
from pdf2image import convert_from_path
import os
import pandas as pd
import re
from PIL import Image, ImageFilter, ImageEnhance, ImageOps



# Function to preprocess image
def preprocess_image(image):
    """
    Function used to scan pdfs
    should be optimal settings, but can be adjusted for use case.
    """
    # Convert image to grayscale
    image = image.convert('L')
    # Resize image to increase text size if needed (adjust as necessary)
    image = image.resize([6 * size for size in image.size], Image.BICUBIC)
    # Apply denoising filter
    image = image.filter(ImageFilter.MedianFilter())
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(6)
    # Apply adaptive threshold to get a binary image
    image = image.point(lambda p: p > 0 and 255)

    image = ImageOps.invert(image)
    return image

def scan_pdfs(pdf_path):
    """
    Function to parse string extract from pdf.
    Look for key and acquire anything after the key.

    Will only work with some pdfs out of the box, depending on format.  Mostly if there are any other strings after the initial parsing.
    """

    # Initialize a list to hold all documents' data
    # Convert the first page of the PDF to image
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    if images:
        # Preprocess image for better OCR
        image = preprocess_image(images[0])
        # Apply OCR with enhanced settings
        custom_config = "--oem 3 --psm 6"

        text = pytesseract.image_to_string(image, config=custom_config, lang='eng')
        print(text)
        # Post-process text for common OCR errors
        text = text.replace('‘', "'").replace('N‘A', 'N/A')
        # Extract Serial Number and Asset ID using regex
        serial_number = re.search(r"Serial Number:\s*([^\s\n]+)", text, re.IGNORECASE) 
        asset_id = re.search(r"Asset ID:\s*([^\s\n]*)", text)
        cal_date = re.search(r"Calibration Date:\s*([^\s\n]*)", text)
        cal_due = re.search(r"Calibration Due Date:\s*([^\s\n]*)", text)
        as_found = re.search(r"As Found Result:\s*([^\s\n]*)", text)
        as_left = re.search(r"As Left Result:\s*([^\s\n]*)", text)
        description_field = re.search(r"Description:\s*(.*)", text)
        
        # Prepare document data
        doc_data = {
            'Rematch': 'Rematch?',
            'Serial Number': serial_number.group(1) if serial_number else 'N/A',
            'Asset ID': asset_id.group(1) if asset_id else 'N/A',
            'Calibration Date': cal_date.group(1) if cal_date else 'N/A',
            'Calibration Due Date': cal_due.group(1) if cal_due  else 'N/A',
            'As Found': as_found.group(1) if as_found else 'N/A',
            'As Left': as_left.group(1) if as_left else 'N/A',
            'Description': description_field.group(1).replace("uL", "µL").replace("ul", "µl").replace("pL", "µl").replace("|", "I") if description_field else 'N/A',
        }

    # Create a DataFrame from the list of dictionaries

    return doc_data

