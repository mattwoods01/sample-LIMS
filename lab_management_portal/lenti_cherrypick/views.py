from django.shortcuts import render
import pandas as pd
import helper
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt


def index(request):
   """
   creates homepage for cherrypick 
   """
   initial_headers = pd.read_csv('lenti_cherrypick/cherry_headers.csv', header=0).columns.tolist()
   sto_df = pd.read_csv('lenti_cherrypick/sto_headers.csv', header=0)
   initial_data = [['' for x in range(len(initial_headers))] for x in range(30)]
   replicate_ls = [1, 2, 3]
   project_range = range(100)

   pref_df = pd.read_csv('lenti_cherrypick/library_pref.csv', header=0)
   coord_ls = pd.read_csv('lenti_cherrypick/form_coordinates.csv', header=0).columns.tolist()

   pref_head = pref_df.columns.tolist()
   pref_data = pref_df.values.tolist()
   sto_head = sto_df.columns.tolist()
   sto_data = [['' for x in range(len(sto_head))] for x in project_range]

   columns_config = [
       {'type': 'dropdown', 'source': ['', 'ARRAY', 'POOL']},
       {'type': 'dropdown', 'source': ['', 'Human']},
       {},
       {'type': 'dropdown', 'source': [''] + [str(i+1) for i in project_range]},
       {'type': 'dropdown', 'source': [''] + coord_ls},
       {'type': 'dropdown', 'source': [''] + [str(i+1) for i in project_range]},
   ]

   preferences_config = [
       {'type': 'dropdown', 'source': pref_data},
   ]

   html = helper.open_README('lenti_cherrypick/README.md')

   context = {
       'initial_data': initial_data,
       'initial_headers': initial_headers,
       'pref_head': pref_head,
       'pref_data': pref_data,
       'sto_head': sto_head,
       'sto_data': sto_data,
       'options': replicate_ls,
       'columns_configuration': columns_config,
       'preferences_configuration': preferences_config,
       'readme': html
   }

   return render(request, 'index.html', context)

def database(request):
   """
   Connects to databse and renders html.  Will have to setup mysql database
   """
   sql_cache_key = 'sql_cache'  # Ensure this matches your cache key
   data = cache.get(sql_cache_key)
   
   if data is None:
       # If cache is empty, perform the query and store the results in the cache
       sql_init = helper.sql_connector()
       sql_data, sql_headers = sql_init.sql_connect_and_query("SELECT * FROM lenti_catalogue;")
       cache.set(sql_cache_key, (sql_data, sql_headers), 300)
   else:
       sql_data, sql_headers = data

   # Convert data to DataFrame for further processing
   data_df = pd.DataFrame(sql_data, columns=sql_headers)
   headers = data_df.columns.tolist()

   context = {
       'headers': headers
   }

   return render(request, 'catalogue.html', context)

def data_endpoint(request):
   """
   Filter endpoint for database catalogue route.  shows filtered results based off partial string match
   """
   sql_init = helper.sql_connector()
   sql_data, sql_headers = sql_init.sql_connect_and_query("SELECT * FROM lenti_catalogue;")
   data_df = pd.DataFrame(sql_data, columns=sql_headers)

   print(data_df)
   
   data = data_df.values.tolist()


   draw = int(request.POST.get('draw', 0))
   start = int(request.POST.get('start', 0))
   length = int(request.POST.get('length', 0))
   search_value = request.POST.get('search[value]', '')
   order_column_index = int(request.POST.get('order[0][column]', 0))
   order_direction = request.POST.get('order[0][dir]', 'asc')

   filtered_data = data
   if search_value:
       filtered_data = [row for row in filtered_data if any(str(search_value).lower() in str(value).lower() for value in row)]

   if order_direction == 'asc':
       filtered_data.sort(key=lambda row: row[order_column_index])
   else:
       filtered_data.sort(key=lambda row: row[order_column_index], reverse=True)

   records_total = len(data)
   records_filtered = len(filtered_data)
   paginated_data = filtered_data[start:start + length]

   response = {
       'draw': draw,
       'recordsTotal': records_total,
       'recordsFiltered': records_filtered,
       'data': paginated_data
   }

   return JsonResponse(response)
