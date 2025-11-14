import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import random
import pandas as pd
import requests
import asyncio
import helper

# function attaches pdf to 
def attach_Labguru(file_path, uuid, title):
    with open(file_path, 'rb') as file:
    # The token and other data fields, excluding the file
        data = {
            'token': '5223e9371b618b588382bfa4daab92af1f8fcf32',
            'item[attach_to_uuid]': uuid,
            'item[title]': title,
            # 'item[description]': description  # Corrected field name here
        }

        # The file to be uploaded
        files = {
            'item[attachment]': (file_path, file)
        }

        # Make the POST request
        response = requests.post('https://thermofisher.labguru.com/api/v1/attachments', data=data, files=files)
        print(response.status_code)

        # Print the response from the server
        print(response.text)

        return response.status_code

class MyConsumer(AsyncWebsocketConsumer):
    # Initialize variables
    # Will need to update token every 6 months
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))
        self.headers = {'Content-type': 'application/json'}
        self.token = "5223e9371b618b588382bfa4daab92af1f8fcf32"
        self.base_url = 'https://thermofisher.labguru.com'
        instruments = requests.get(self.base_url + '/api/v1/instruments', json={"token": self.token}, headers=self.headers).text
        self.instruments_df = pd.read_json(instruments, dtype=False)

    # Connect function
    async def connect(self):
        """
        Connects to Django backend.
        if folder does not exist then create one
        sends asynchronous json to webpage
        """
        self.folder_name = os.path.join(settings.BASE_DIR, 'attachment_uploader', 'uploads', str(random.randint(1, 1000000)))
        self.image_path = None
        self.file_metadata = {}
        self.file_dict = {}

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        await self.accept()
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Connected'}))
        print(f"Folder name set to: {self.folder_name}")

    async def disconnect(self, close_code):
        """
        removes folder and sends message to webpage
        """
        helper.remove_folder(self.folder_name)
        
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Disconnected'}))

    async def receive(self, text_data=None, bytes_data=None):
        """
        receives json response from webpage inputs.
        Depending on event, certain function will run

        text_data is string response from webpage
        bytes_data is byte response from webpage.

        If bytes are detected by django backend, then default to elif conditional.  Is only done when a file converted to bytes is sent from webpage
        """

        if text_data:
            print(text_data)
            data = json.loads(text_data)
            event = data['event']

            if event == "run_program":
                await self.run_program(data)
            elif event == "upload_files":
                file_name = data['file_name']
                file_type = data['file_type']
                self.file_metadata[file_name] = file_type
            elif event == "rematch":
                await self.rematch(data)
            elif event == "save":
                await self.save(data)
                
        elif bytes_data:
            # Save the uploaded file using the stored metadata
            for file_name, file_type in self.file_metadata.items():
                file_path = os.path.join(self.folder_name, file_name)
                with open(file_path, 'wb') as f:
                    f.write(bytes_data)
                await self.send(text_data=json.dumps({'status': 'File uploaded successfully', 'path': file_path}))
                self.file_dict[file_name] = file_path
                del self.file_metadata[file_name]
                break
        
    async def run_program(self, data):
        """
        Runs attachment uploader script.  
        Will show modal window on html page
        """

        file_df = pd.DataFrame(list(self.file_dict.items()), columns=['serial_number', 'Path'])
        file_df.insert(0, 'Rematch?', 'rematch')
        file_df.insert(3, 'Save?', False)
        file_df.insert(4, 'Status', '')
        file_df['Key'] = file_df['serial_number'].str.extract(r'(\w+)')
        merged_df = pd.merge(file_df, self.instruments_df, left_on='Key', right_on='serial_number', how='left')
        merged_df = merged_df.drop(columns=['Key'])
        merged_df = merged_df[['serial_number_x', 'serial_number_y', 'name', 'Save?', 'Status', 'Path', 'uuid']]
        merged_df.fillna('', inplace=True)
        merged_df = merged_df.rename(columns={'serial_number_x':'Filename Serial Number'})
        merged_df = merged_df.rename(columns={'serial_number_y':'Labguru Serial Number'})
        merged_df = merged_df.rename(columns={'name':'Labguru Asset ID'})
        merged_df = merged_df.rename(columns={'description':'Description'})
        merged_df['Save?'] = merged_df['Labguru Asset ID'] != ''

        merged_data = merged_df.values.tolist()
        headers = merged_df.columns.tolist()  

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Running Program..."}))
        await self.send(text_data=json.dumps({'event': 'read_pdf_names', 'data': merged_data, 'headers': headers}))
        await asyncio.sleep(0.5)

    async def rematch(self, data):
        """
        function used to rematch to labguru server in case where serial number that is found in attachment filename

        Rematch button found in handsontable (excel format) 
        Once clicked, rematch function will run and left merge with labguru dataframe on serial_number and key.
        extract captures sequences of words and stops at first non word character such as -.$,@
        """

        row = data['data']
        headers = data['scan_headers']
        row_number = data['row_number']
        row_df = pd.DataFrame([row], columns=headers)
        row_df = row_df.rename(columns={'Filename Serial Number':'serial_number'})
        row_df['Key'] = row_df['serial_number'].str.extract(r'(\w+)')
        merged_df = pd.merge(row_df, self.instruments_df, left_on='Key', right_on='serial_number', how='left')
        merged_df = merged_df.drop(columns=['Key'])

        try:
            merged_df['Labguru Asset ID'] = merged_df['name']
            merged_df['Labguru Serial Number'] = merged_df['serial_number_y']
            merged_df = merged_df.rename(columns={'serial_number_x':'Filename Serial Number'})

            merged_df = merged_df[['Filename Serial Number', 'Labguru Serial Number', 'Labguru Asset ID', 'Save?', 'Status', 'Path', 'uuid']]
            merged_df.fillna('', inplace=True)
            merged_df['Save?'] = merged_df['Labguru Asset ID'] != ''
            merged_df = merged_df.rename(columns={'description':'Description'})

            merged_data = merged_df.values.tolist()
            headers = merged_df.columns.tolist()

            await self.send(text_data=json.dumps({'event': 'rematch_processed', 'data': merged_data, 'headers': headers, 'row_number': row_number}))
            await asyncio.sleep(0.5)

        except KeyError:
            pass
    
    async def save(self, data):
        """
        Saves current selection of attachments to upload to server with file path, uuid, and serial number.  All three are needed to make api call.
        """

        modal_data = data['modal_data']
        modal_headers = data['modal_headers']
        data_df = pd.DataFrame(modal_data, columns=modal_headers)

        for i, row in data_df.iterrows():
            status_code = attach_Labguru(row['Path'], row['uuid'], row['Labguru Serial Number'])

            if status_code == 201:
                data_df['Status'].iloc[i] = "Success"
    
            elif status_code == 500:
                data_df['Status'].iloc[i] = "500 error; Contact Labguru"

            else:
                data_df['Status'].iloc[i] = status_code

        merged_data = data_df.values.tolist()
        headers = data_df.columns.tolist()

        await self.send(text_data=json.dumps({'event': 'update_status', 'data': merged_data, 'headers': headers}))

            
