from django.shortcuts import render
import helper
import pandas as pd

def index(request):
    """
    initialize homepage
    """
    html = helper.open_README('mrna_coa_generator/README.md')

    form_headers = pd.read_csv('mrna_coa_generator/mRNA_form_headers.csv', header=0).columns.tolist()
    data_headers = pd.read_csv('mrna_coa_generator/mRNA_seq_headers.csv', header=0).columns.tolist()
    
    form_initial = [['' for _ in range(len(form_headers))]]
    data_initial = [['' for _ in range(len(data_headers))] for _ in range(20)]

    context = {
        'form_headers': form_headers,
        'form_initial': form_initial,
        'data_headers': data_headers,
        'data_initial': data_initial,
        'readme': html
    }

    return render(request, 'mrna_coa_generator/mrna_coa_generator.html', context)