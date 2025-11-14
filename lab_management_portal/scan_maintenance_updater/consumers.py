import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import random
import pandas as pd
import base64
import numpy as np
from .maintenance import MaintenanceEventCreator
from .scan_pdfs import scan_pdfs
import requests
import asyncio
from .upload_attachments import *
import helper
from datetime import datetime
import pytz

# reflect update status

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))
        self.headers = {'Content-type': 'application/json'}
        self.base_url = 'https://thermofisher.labguru.com'
        self.payload = {'token': "5223e9371b618b588382bfa4daab92af1f8fcf32"}
        self.instrument_df = None

    async def connect(self):
        """
        Connect to client and connect to labguru server with api.  acquire instrument catalogue.
        """

        self.file_metadata = {}
        self.file_dict = {}
        await self.accept()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Connected"}))

        instrument_catalogue_response = requests.get('https://thermofisher.labguru.com/api/v1/instruments', json=self.payload, headers=self.headers)

        try:
            instrument_catalogue = instrument_catalogue_response.json()  # Use .json() method to parse JSON response directly

        except json.JSONDecodeError:
            print("Error decoding JSON")
            instrument_catalogue = {}


        data = [{'id': item['id'], 'Asset ID': item['name'], 'Serial Number': item['serial_number'], 'uuid': item['uuid']} for item in instrument_catalogue]
        self.instrument_df = pd.DataFrame(data, columns=['id', 'Asset ID', 'Serial Number', 'uuid'])

        await self.send(text_data=json.dumps({"folder_name": self.folder_name, "event": "folder_name"}))
        os.mkdir(self.folder_name)

        print(self.instrument_df)

        print("Connected")

    async def disconnect(self, close_code):
        """
        disconnect from client and remove folder
        """

        helper.remove_folder(self.folder_name)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Disconnected"}))
        print("Disconnected")

    async def receive(self, text_data=None, bytes_data=None):
        """
        receive event from client
        """
        if text_data:
            data = json.loads(text_data)
            event = data.get("event")
            print(event)

            if event == "run_program":
                await self.run_program(data)
            elif event == 'scan':
                await self.scan_and_upload(data)
            elif event == "rematch":
                await self.rematch(data)
            elif event == "upload_files":
                file_name = data['file_name']
                file_type = data['file_type']
                self.file_metadata[file_name] = file_type

        elif bytes_data:
            # Save the uploaded file using the stored metadata
            for file_name, file_type in self.file_metadata.items():
                file_path = os.path.join(self.folder_name, file_name)
                with open(file_path, 'wb') as f:
                    f.write(bytes_data)
                await self.send(text_data=json.dumps({'event': 'return_output', 'message': file_path}))
                self.file_dict[file_name] = file_path
                del self.file_metadata[file_name]
                break

    async def run_program(self, data):
        """
        Run program.  Scan pdfs to acquire serial number and instrument information.
        Get instrument information from labguru and create excel for skipped and non skipped api requests.
        """

        data_df = pd.DataFrame(data['data']['data'], columns=data['data']['headers'])
        scan_df = pd.DataFrame(data['data']['scan_data'], columns=data['data']['scan_headers'])
        scan_df['Name'] = scan_df['Labguru Asset ID']

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

        folder_name = data['data']['folder']
        files_dict = categorize_files(folder_name)
        df = create_dataframe(files_dict)
        file_df = pd.merge(scan_df, df, on='Serial Number', how='left')
        filtered_df = file_df[file_df['Skip'] != True]
        merged_df = pd.merge(filtered_df, instrument_with_input_df, on='Name', how='left')
        
        for i, row in merged_df.iterrows():
            updated_instrument_df = requests.get(self.base_url + f'/api/v1/instruments/{row["id"]}', json=self.payload, headers=self.headers).json()
            instruments_df = pd.DataFrame([updated_instrument_df])
            instruments_df.rename(columns={'id' : 'equipment_id'}, inplace=True)
            instruments_df.rename(columns={'name' : 'Name'}, inplace=True)

            row_df = pd.DataFrame(row).T
            matched_df = pd.merge(row_df, instruments_df, on='Name', how='inner')

            updated_status = main_instance.update_maintenances(matched_df)
            merged_df['Update Status'].iloc[i] = updated_status

            merged_df = merged_df[['Name', "Maintenance (Type)", "Maintenance (Date)", "Update Status"]]
            merged_df.replace(['nan', np.nan], '', inplace=True)

            uploaded_data = merged_df.values.tolist()
            uploaded_headers = merged_df.columns.tolist()

            await self.send(text_data=json.dumps({"up_data": uploaded_data, "up_headers": uploaded_headers, "event": "return_data"}))
            await asyncio.sleep(0.5)

            if updated_status == "Success":
                print(matched_df)
                process_row(matched_df)       

        directory_name = f"{folder_name}/supporting documents.xlsx"

        skipped_df = scan_df[scan_df['Skip'] == True]
        not_skipped_df = scan_df[scan_df['Skip'] != True]

        Succ_data = merged_df[merged_df['Update Status'] == "Success"]
        fail_data = merged_df[merged_df['Update Status'] != "Success"]

        await self.send(text_data=json.dumps({"event": "return_scans", "message": f"Saving excel..."}))

        with pd.ExcelWriter(directory_name, engine='xlsxwriter') as writer:
            not_skipped_df.to_excel(writer, sheet_name='Not Skipped', index=False)
            skipped_df.to_excel(writer, sheet_name='Skipped', index=False)

            Succ_data.to_excel(writer, sheet_name='Succesful Update', index=False)
            fail_data.to_excel(writer, sheet_name='Failed Update', index=False)

        with open(directory_name, 'rb') as file:
            excel_data = file.read()
            encoded_excel_data = base64.b64encode(excel_data).decode('utf-8')

        utc_now = datetime.now(pytz.utc)
        pst_now = utc_now.astimezone(pytz.timezone('US/Pacific'))

        excel_file_name = f"Scanned items {pst_now.strftime('%Y-%m-%d %H:%M:%S')} PST.xlsx"

        await self.send(text_data=json.dumps({"event": "return_scans", "message": f"Finished saving excel"}))
        await self.send(text_data=json.dumps({"event": "return_supporting_excel", "file_data": encoded_excel_data, "file_name": excel_file_name}))
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Finished updating maintenances"}))

    async def scan_and_upload(self, data):

        """
        run scanning of pdfs and format dataframe.
        """
        document_ls = []
        for filename in os.listdir(self.folder_name):
            if filename.lower().endswith(".pdf"):
                document_entry = scan_pdfs(f"{self.folder_name}/{filename}")
                await self.send(text_data=json.dumps({"event": "return_output", "message": f"SCANNED: {document_entry}"}))
                await asyncio.sleep(0.5)

                document_ls.append(document_entry)
                document_df = pd.DataFrame(document_ls)
                merged_df = pd.merge(document_df, self.instrument_df, on='Serial Number', how='left')
                merged_df = merged_df[['Rematch',
                                       'Serial Number',
                                       'Asset ID_x',
                                       "Asset ID_y",
                                       "Calibration Date",
                                       "Calibration Due Date",
                                       "As Found",
                                       "As Left",
                                       "Description",
                                       "id", 
                                       ]]

                merged_df['Asset ID_x'].replace('N/A', np.nan, inplace=True)
                merged_df.insert(3, 'Skip', False)
                merged_df.loc[merged_df['Asset ID_x'].isna(), 'Skip'] = True
                merged_df['Asset ID_x'].replace(np.nan, 'N/A', inplace=True)
                merged_df.loc[merged_df['As Left'] == 'Fail', 'Skip'] = True
                merged_df.rename(columns={'Asset ID_x': 'Scanned Asset ID'}, inplace=True)
                merged_df.rename(columns={'Asset ID_y': 'Labguru Asset ID'}, inplace=True)
                merged_df.replace(np.nan, 'NOT FOUND', inplace=True)
                merged_df.loc[merged_df['id'] == 'NOT FOUND', 'Skip'] = True

                print(merged_df)

                merged_data = merged_df.values.tolist()
                headers = merged_df.columns.tolist()

                await self.send(text_data=json.dumps({'event': 'scan_pdfs', 'data': merged_data, 'headers': headers}))
                await asyncio.sleep(0.5)

    async def rematch(self, data):
        """
        serial number Rematch to labguru instrument list.  Performed in cases where serial number was incorrect. will display match on modal popup window
        """
        row = data['data']
        headers = data['scan_headers']
        row_number = data['row_number']
        row_df = pd.DataFrame([row], columns=headers)
        merged_df = pd.merge(row_df, self.instrument_df, on='Serial Number', how='left')

        try:
            merged_df = merged_df.drop('id_x', axis=1)
            merged_df = merged_df.drop('uuid', axis=1)
            merged_df = merged_df.rename(columns={'id_y':'id'})
            merged_df['Labguru Asset ID'] = merged_df['Asset ID']
            merged_df = merged_df.drop('Asset ID', axis=1)

            merged_data = merged_df.values.tolist()
            headers = merged_df.columns.tolist()

            print(merged_data)

            await self.send(text_data=json.dumps({'event': 'rematch_processed', 'data': merged_data, 'headers': headers, 'row_number': row_number}))
            await asyncio.sleep(0.5)

        except KeyError:
            pass


