import shutil
import os
import re
from markdown import markdown
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db import connection

class sql_connector:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_timeout = 300
        self.sql_cache_key = 'sql_cache'

    # @sync_to_async
    def sql_connect_and_query(self, query):
        """
        make a query.  Will need to have active connection to database first
        """
        # Generate a cache key based on the query
        cache_key = f"{self.sql_cache_key}_{hash(query)}"
   
        # Try to get the data from the cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
   
        # If not cached, execute the query
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Store the results in the cache
        cache.set(cache_key, (results, columns), self.cache_timeout)
        # print(cache.get(cache_key))

        return results, columns

def remove_folder(folder_path):
    """
    remove folder from ec2 server
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Use shutil.rmtree to remove the folder and all its contents
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' has been removed successfully.")
    else:
        print(f"Folder '{folder_path}' does not exist.")

def has_special_characters(my_string):
    """
    Check for any special characters in string
    """
    special_characters = set("!@#$%&*?=<>/")
    return any(c in special_characters for c in my_string)

def make_bold(text):
    """
    embolden string
    """
    return f"<b>{text}</b>"

def format_exponent(text):
    """
    Format exponent string value
    """
    """ Convert number expressions with exponents from '10^8' to '10<sup>8</sup>' for ReportLab. """
    return re.sub(r'(\d+)\^(\d+)', r'\1<sup>\2</sup>', text)

def open_README(readme):
    """
    open readme and save html code.
    """
    try:
        with open(readme, 'r') as r:
            readme_file = r.read()
            html = markdown(readme_file)

    except FileNotFoundError:
        with open(readme.upper(), 'r') as r:
            readme_file = r.read()
            html = markdown(readme_file)

    return html

def detect_language(text):
    """
    detect language from string
    """

    korean_pattern = re.compile(r'[\uAC00-\uD7AF]')
    chinese_pattern = re.compile(r'[\u4E00-\u9FFF]')
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF\uFF66-\uFF9D]')
    
    if korean_pattern.search(text):
        return 'Korean'
    elif chinese_pattern.search(text):
        return 'Chinese'
    elif japanese_pattern.search(text):
        return 'Japanese'
    else:
        return 'Other'
    
def convert_date_flexible(input_date):
    """
    convert date from specified formats to another
    """
    formats = ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]  # Example list of formats you might encounter
    for fmt in formats:
        try:
            date_object = datetime.strptime(input_date, fmt)  # 'strptime' is correctly accessed here
            return date_object.strftime("%d%B%Y").lower()
        except ValueError:
            continue
    return "Invalid date format"

def initialize_font(notosans_ttf):
    """
    initialize font
    """
    pdfmetrics.registerFont(TTFont('NotoSansCJK-Regular', notosans_ttf, subfontIndex=0))


