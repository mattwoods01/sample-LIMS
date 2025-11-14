import json
import requests
import pandas as pd
import markdown
from django.shortcuts import render
import helper

def index(request):
    initial_headers = pd.read_csv('lentipool_analysis_tool/lentipool_headers.csv', header=0).columns.tolist()
    sto_df = pd.read_csv('lentipool_analysis_tool/sto_headers.csv', header=0)
    initial_data = [['' for x in range(len(initial_headers))] for x in range(30)]
    # replicate_ls = [1, 2, 3]
    project_range = range(1)


    sto_head = sto_df.columns.tolist()
    print(sto_head)
    sto_data = [['' for x in range(len(sto_head))] for x in project_range]

    # columns_config = [
    #     {'type': 'dropdown', 'source': ['', 'ARRAY', 'POOL']},
    #     {'type': 'dropdown', 'source': ['', 'Human']},
    #     {},
    #     {'type': 'dropdown', 'source': [''] + [str(i+1) for i in project_range]},
    #     {'type': 'dropdown', 'source': [''] + [str(i+1) for i in project_range]},
    # ]

    html = helper.open_README('lentipool_analysis_tool/README.md')

    context = {
        'initial_headers': initial_headers,
        'initial_data': initial_data,
        'sto_headers': sto_head,
        'sto_data': sto_data,
        'readme': html,
    }

    return render(request, 'lentipool_analysis_tool.html', context)
