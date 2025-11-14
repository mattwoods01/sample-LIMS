import pandas as pd
from django.shortcuts import render
import helper

def index(request):

    html = helper.open_README('pluritest_form_generator/README.md')

    form_headers = pd.read_csv('pluritest_form_generator/form_headers.csv', header=0).columns.tolist()
    data_headers = pd.read_csv('pluritest_form_generator/sample_headers.csv', header=0).columns.tolist()
    
    form_initial = [['' for _ in range(len(form_headers))]]
    data_initial = [['' for _ in range(len(data_headers))] for _ in range(20)]

    context = {
        'form_headers': form_headers,
        'form_initial': form_initial,
        'data_headers': data_headers,
        'data_initial': data_initial,
        'readme': html,
    }

    return render(request, 'pluritest_form_generator/pluritest_form_generator.html', context)