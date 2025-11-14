import json
import requests
import pandas as pd
import markdown
from django.shortcuts import render

def index(request):
    headers = {'Content-type': 'application/json'}
    payload = {'token': "5223e9371b618b588382bfa4daab92af1f8fcf32"}
    initial_headers = [
        'Name',
        'Maintenance (Type)',
        'Maintenance (Date)',
        'Update Status'
    ]
    
    initial_data = [['' for x in range(len(initial_headers))] for x in range(100)]
    
    instrument_catalogue_response = requests.get('https://thermofisher.labguru.com/api/v1/instruments', json=payload, headers=headers)

    try:
        instrument_catalogue = instrument_catalogue_response.json()  # Use .json() method to parse JSON response directly
    except json.JSONDecodeError:
        print("Error decoding JSON")
        instrument_catalogue = {}

    def extract_equipment_data(equipment):
        name = equipment.get("name", "No Name")
        maintenances = [
            f"{maint['frequency_period']}_{maint['frequency_frame']}_{maint['maintenance_type_name']}"
            for maint in equipment.get("maintenances", [])
            if "maintenance_type_name" in maint and "None_None" not in f"{maint['frequency_period']}_{maint['frequency_frame']}_{maint['maintenance_type_name']}"
        ]
        return name, maintenances

    equipment_info = [extract_equipment_data(equip) for equip in instrument_catalogue]
    df = pd.DataFrame(equipment_info, columns=["Name", "allMaintenances"])
    maintenance_dict = df.set_index('Name')['allMaintenances'].to_dict()
    maintenance_json = json.dumps(maintenance_dict)

    try:
        with open('man_maintenance_updater/READMEbm.md', 'r') as r:
            readme_file = r.read()
            html = markdown.markdown(readme_file)
    
    except FileNotFoundError:
        with open('man_maintenance_updater/READMEbm.md', 'r') as r:
            readme_file = r.read()
            html = markdown.markdown(readme_file)

    context = {
        'initial_headers': initial_headers,
        'initial_data': initial_data,
        'maintenance_json': maintenance_json,
        'readme': html
    }

    return render(request, 'scan_maintenance_updater.html', context)
