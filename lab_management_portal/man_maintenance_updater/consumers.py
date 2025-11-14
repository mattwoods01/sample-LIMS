import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import random
import pandas as pd
import base64
import numpy as np
from .maintenance import MaintenanceEventCreator
from .return_maintenance import MaintenanceOutputCreator
import requests
import helper
import asyncio
from datetime import datetime
import pytz

# from .upload_attachments import *

# make list of all equipment with different IDs?
# add in filter for skip for excel paging
# automatically update/reader the maintenance (Type) column after uploading scans
# seperate dropbox for all documents
# make a seperate tool
# remove 
# add in asset labguru assset ID
# add in automatic render for Name and labguru ID
# automatically save documents that are successful
# reflect update status
# after clicking run do a popup for 
# automatically update and open scanned output window before scan has started.
# add attachment to labguru if update status is True, if false, do nothing for attachment

# Scan and upload -> save changes -> run - make updates, if true upload attachment, if false do nothing
# move attachment uploader to new tool.

# keep in order of process. 

# How to avoid the step of using the dropdown - will have to see if item can be automatically rendered - ????

# General document upload tool.  

class MyConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))
        self.headers = {'Content-type': 'application/json'}
        self.payload = {'token': "5223e9371b618b588382bfa4daab92af1f8fcf32"}
        self.base_url = 'https://thermofisher.labguru.com'
        self.instrument_df = None
        
        # print(self.folder_name)

    async def connect(self):
        """
        Connect to client
        """
        await self.accept()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Connected"}))

        # instrument_catalogue_response = requests.get('https://thermofisher.labguru.com/api/v1/instruments', json=self.payload, headers=self.headers)

        # try:
        #     instrument_catalogue = instrument_catalogue_response.json()  # Use .json() method to parse JSON response directly

        # except json.JSONDecodeError:
        #     print("Error decoding JSON")
        #     instrument_catalogue = {}


        # data = [{'id': item['id'], 'Asset ID': item['name'], 'Serial Number': item['serial_number'], 'uuid': item['uuid']} for item in instrument_catalogue]
        # self.instrument_df = pd.DataFrame(data, columns=['id', 'Asset ID', 'Serial Number', 'uuid', ])

        await self.send(text_data=json.dumps({"folder_name": self.folder_name, "event": "folder_name"}))
        os.mkdir(self.folder_name)

        # print(self.instrument_df)

        print("Connected")

    async def disconnect(self, close_code):
        """
        Disconnect from client and remove folder
        """
        helper.remove_folder(self.folder_name)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Disconnected"}))
        print("Disconnected")

    async def receive(self, text_data):
        """
        receive events from client
        """
        print(text_data)
        data = json.loads(text_data)
        event = data.get("event")
        print(event)

        if event == "file_upload":
            await self.handle_file_upload(data)
        elif event == "run_program":
            await self.run_program(data)
        elif event == "return_maintenance":
            await self.return_maintenance()
 
    async def handle_file_upload(self, data):
        """
        send file to client
        """

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Initiating"}))
        file_data = base64.b64decode(data['file_data'])
        file_name = data['filename']

        self.folder_name = str(random.randint(1, 1000000))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Creating Folder for uploaded file"}))
        os.mkdir(self.folder_name)
        directory_name = f'{self.folder_name}/{file_name}'

        try:
            with open(directory_name, "wb") as file:
                file.write(file_data)
            await self.send(text_data=json.dumps({"event": "return_output", "message": f"File saved to {directory_name}"}))
            
        except Exception as e:
            await self.send(text_data=json.dumps({"event": "return_output", "message": f"Error saving file: {str(e)}"}))

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Reading excel..."}))

        input_dataframe = pd.read_excel(directory_name)
        input_dataframe = input_dataframe.astype(str)

        print(input_dataframe)

        uploaded_data = input_dataframe.iloc[:, 0:].values.tolist()
        # uploaded_headers = input_dataframe.columns.tolist()

        print(uploaded_data)

        await self.send(text_data=json.dumps({"up_data": uploaded_data, "event": "return_data"}))
        await self.send(text_data=json.dumps({"folder_name": self.folder_name, "event": "folder_name"}))

        # os.remove(directory_name)
        # os.rmdir(self.folder_name)

    async def run_program(self, data):

        """
        run program by sending api requests to labguru server
        """

        data_df = pd.DataFrame(data['data']['data'], columns=data['data']['headers'])
        data_df['Name'].replace(['', 'nan'], np.nan, inplace=True)
        data_df = data_df.dropna()

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Initiating maintenance updater..."}))
        main_instance = MaintenanceEventCreator(data_df)
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Finished initiating maintenance updater..."}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Formatting dataframe..."}))
        instrument_with_input_df = main_instance.format_dataframes()
        instrument_with_input_df = instrument_with_input_df[['equipment_id', 'Name', 'Maintenance (Date)', 'Maintenance (Type)', 'Maintenance Int', 'Maintenance Freq', 'Maintenance Type', 'Update Status']]
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Finished formatting dataframe..."}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Updating maintenances..."}))

        for i, row in instrument_with_input_df.iterrows():
            updated_instrument_df = requests.get(self.base_url + f'/api/v1/instruments/{row["equipment_id"]}', json=self.payload, headers=self.headers).json()
            instruments_df = pd.DataFrame([updated_instrument_df])

            instruments_df.rename(columns={'id' : 'equipment_id'}, inplace=True)
            instruments_df.rename(columns={'name' : 'Name'}, inplace=True)
            row_df = pd.DataFrame(row).T

            matched_df = pd.merge(row_df, instruments_df, on='Name', how='inner')

            updated_status = main_instance.update_maintenances(matched_df)
            instrument_with_input_df['Update Status'].iloc[i] = updated_status

            instrument_with_input_df = instrument_with_input_df[['Name', "Maintenance (Type)", "Maintenance (Date)", "Update Status"]]
            instrument_with_input_df.replace(['nan', np.nan], '', inplace=True)

            uploaded_data = instrument_with_input_df.values.tolist()
            uploaded_headers = instrument_with_input_df.columns.tolist()

            await self.send(text_data=json.dumps({"up_data": uploaded_data, "up_headers": uploaded_headers, "event": "return_data"}))
            await asyncio.sleep(0.5)

        await self.send(text_data=json.dumps({"up_data": uploaded_data, "event": "return_data"}))

        directory_name = f"{self.folder_name}/supporting documents.xlsx"

        Succ_data = instrument_with_input_df[instrument_with_input_df['Update Status'] == "Success"]
        fail_data = instrument_with_input_df[instrument_with_input_df['Update Status'] != "Success"]

        with pd.ExcelWriter(directory_name, engine='xlsxwriter') as writer:
            Succ_data.to_excel(writer, sheet_name='Succesful Update', index=False)
            fail_data.to_excel(writer, sheet_name='Failed Update', index=False)

        with open(directory_name, 'rb') as file:
            excel_data = file.read()
            encoded_excel_data = base64.b64encode(excel_data).decode('utf-8')

        utc_now = datetime.now(pytz.utc)
        pst_now = utc_now.astimezone(pytz.timezone('US/Pacific'))

        excel_file_name = f"Scanned items {pst_now.strftime('%Y-%m-%d %H:%M:%S')} PST.xlsx"

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Finished updating maintenances"}))
        await self.send(text_data=json.dumps({"event": "return_supporting_excel", "file_data": encoded_excel_data, "file_name": excel_file_name}))


    async def return_maintenance(self):
        """
        return maintennace of instruments from labguru
        """

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Creating Folder for file"}))
        folder_name = str(random.randint(1, 1000000))
        os.mkdir(folder_name)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Initiating maintenance file creation..."}))
        maintenance_output_instance = MaintenanceOutputCreator(folder_name)
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Completed maintenance file creation..."}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Generating maintenance excel.."}))
        maintenance_output_instance.generate_maintenance_sheet()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Completed maintenance excel creation..."}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Formatting maintenance excel..."}))
        maintenance_output_instance.format_maintenance_excel()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Maintenance excel formatted"}))

        utc_now = datetime.now(pytz.utc)
        pst_now = utc_now.astimezone(pytz.timezone('US/Pacific'))

        excel_file_name = f"Maintenance {pst_now.strftime('%Y-%m-%d %H:%M:%S')} PST.xlsx"

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Encoding excel..."}))
        with open(f"{maintenance_output_instance.directory}", 'rb') as file:
            excel_data = file.read()
            encoded_zip_data = base64.b64encode(excel_data).decode('utf-8')

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Finished encoding excel"}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Sending File data..."}))
        await self.send(text_data=json.dumps({"event": "return_file", "file_data": encoded_zip_data, "file_name": excel_file_name}))

        helper.remove_folder(folder_name)
