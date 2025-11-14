import json
import requests
import pandas as pd
import markdown
from django.shortcuts import render
import helper

def index(request):
    html = helper.open_README('talon_coa_generator/README.md')

    form_headers = pd.read_csv('talon_coa_generator/talon_form_headers.csv', header=0).columns.tolist()
    data_headers = pd.read_csv('talon_coa_generator/talon_seq_headers.csv', header=0).columns.tolist()
    
    form_initial = [['' for x in range(len(form_headers))]]
    data_initial = [['' for x in range(len(data_headers))] for x in range(20)]

    options_ls = ['mMESSAGE mMACHINE™ T7 mRNA Kit with CleanCap™ Reagent AG (#A57620)',
                  'mMESSAGE mMACHINE™ T7 ULTRA Transcription Kit (#AM1345)']

    context = {
        'form_headers': form_headers,
        'form_initial': form_initial,
        'data_headers': data_headers,
        'data_initial': data_initial,
        'readme': html,
        'options': options_ls
    }

    return render(request, 'talon_coa_generator.html', context)