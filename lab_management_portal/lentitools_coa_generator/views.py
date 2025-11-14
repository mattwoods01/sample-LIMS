from django.shortcuts import render
import pandas as pd
import helper

def index(request):
    html = helper.open_README('lentitools_coa_generator/README.md')

    form_headers = pd.read_csv('lentitools_coa_generator/lentitools_form_headers.csv', header=0).columns.tolist()
    
    form_initial = [['' for _ in range(len(form_headers))] for _ in range(20)]
    
    context = {
        'form_headers': form_headers,
        'form_initial': form_initial,
        'readme': html
    }

    return render(request, 'lentitools_coa_generator/lentitools_coa_generator.html', context)