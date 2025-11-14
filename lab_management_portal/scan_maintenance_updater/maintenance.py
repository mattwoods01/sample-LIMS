import requests
import pandas as pd
from numpy import nan
from datetime import datetime

# attachment = variable('trigger_attachment')
# file_name = variable('uploaded_files')['trigger_attachment']

class MaintenanceEventCreator:
    def __init__(self, file_dataframe):
        self.maintenance_input = file_dataframe
        self.base_url = 'https://thermofisher.labguru.com'
        self.maintenance_events_url = '/api/v1/maintenance_events'
        self.token = "5223e9371b618b588382bfa4daab92af1f8fcf32"
        self.headers = {'Content-type': 'application/json'}
        self.instruments = requests.get(self.base_url + '/api/v1/instruments', json={"token": self.token}, headers=self.headers).text
        self.maintenance_types = requests.get(self.base_url + '/api/v1/maintenance_types', json={"token": self.token}, headers=self.headers).json()
        self.maintenance_type = 'Maintenance Type' 
        self.maintenance_date = 'Maintenance Date' 

    def format_dataframes(self):
        """
        Format dataframe to match table on client page
        """
        maintenace_types_df = pd.DataFrame(self.maintenance_types)
        maintenace_types_df.rename(columns={'name' : self.maintenance_type}, inplace=True)

        instruments_df = pd.read_json(self.instruments, dtype=False)
        instruments_df.rename(columns={'id' : 'equipment_id'}, inplace=True)
        instruments_df.rename(columns={'name' : 'Name'}, inplace=True)
        
        self.maintenance_input[['Maintenance Int', 'Maintenance Freq', self.maintenance_type]] = self.maintenance_input.apply(lambda row: pd.Series(row['Maintenance (Type)'].split('_')), axis=1)
        instruments_with_type_df = pd.merge(self.maintenance_input, maintenace_types_df, on=self.maintenance_type, how='left', sort=False)
        
        return pd.merge(instruments_with_type_df, instruments_df, on='Name', how='left')

    def update_maintenances(self, item):
        """
        update maintenances on labguru server with api request
        """
        try:
            maintenance_df = pd.DataFrame(item['maintenances'][0])
        
        except:
            pass

        try:
            pipette_id = int(item['equipment_id_x'])
            item_maintenance_type = item[self.maintenance_type].iloc[0]

            print(maintenance_df)

            filtered_maintenance_df = maintenance_df[maintenance_df['maintenance_type_name'].str.contains(f"{item_maintenance_type}", case=True)]
            timestamp_str = item['Maintenance (Date)'].iloc[0]
            timestamp = pd.to_datetime(timestamp_str)
            formatted_date_str = timestamp.strftime('%b %d, %Y %H:%M')
            filtered_id = str(filtered_maintenance_df['id'].iloc[0])
            performed_id = str(9)

            json_payload = {
                "token": self.token,
                "item": {
                "item_id": pipette_id,
                "item_type": "System::Instrument",
                "maintenance_id": filtered_id,
                "data": '[]',
                "performed_at": formatted_date_str,
                "performed_by": performed_id
                  }
            }

            create_maintenance = requests.post(self.base_url + self.maintenance_events_url, json=json_payload, headers=self.headers)
            print(create_maintenance)

            if create_maintenance.status_code == 201:
                print(create_maintenance.status_code)
                return "Success"
    
            if create_maintenance.status_code == 500:
                print(create_maintenance.status_code)
                return "500 error; Contact Labguru"

        except (IndexError, ValueError, KeyError, TypeError) as e:
            print(e)
            return "Fail"

       