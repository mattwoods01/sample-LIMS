import os
import random
import shutil as sh
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
import base64
import json
from .mrna_coa_generator import generate_pdf
import helper

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        connect to client and create folder
        """
        self.folder_name = str(random.randint(1, 1000000))
        self.image_path = None

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        await self.accept()
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Connected'}))
        print(f"Folder name set to: {self.folder_name}")

    async def disconnect(self, close_code):
        """
        disconnect from client and remove folder
        """
        helper.remove_folder(self.folder_name)
        
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Disconnected'}))

    async def receive(self, text_data):

        """
        receive events from client
        """
        data = json.loads(text_data)
        event = data.get('event')

        if event == "run_mRNA":
            await self.generate_mRNA(data)
        elif event == "upload_mRNA":
            await self.upload_mRNA(data)

    async def generate_mRNA(self, data):
        """
        run program
        """
        folder_name = self.folder_name
    
        input_headers = data['input_headers']
        input_data = data['input_data']
        form_headers = data['form_headers']
        form_data = data['form_data'][0]
    
        input_df = pd.DataFrame(input_data, columns=input_headers)
        form_dict = {form_headers[i]: form_data[i] for i in range(len(form_headers))}
        image_directory = self.image_path  # Assuming image_path is set somewhere
    
        file_name = generate_pdf(folder_name, form_dict, input_df, image_directory)
    
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Encoding PDF..."}))
        with open(file_name, 'rb') as file:
            pdf_data = file.read()
            encoded_zip_data = base64.b64encode(pdf_data).decode('utf-8')
    
        await self.send(text_data=json.dumps({"event": "return_file", "data": [file_name, encoded_zip_data]}))

    async def upload_mRNA(self, data):
        """
        uplaod mRNA picture from client to django backend
        """
        file_data = data['file_data']
        file_name = data['file_name']
    
        folder_name = self.folder_name
    
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Creating Folder for uploaded file"}))
        file_directory = f'{folder_name}/{file_name}'
    
        self.image_path = file_directory  # Store the file path in image_path
    
        try:
            # Convert list to bytes
            file_data_bytes = bytes(file_data)

            with open(file_directory, "wb") as file:
                file.write(file_data_bytes)
    
            await self.send(text_data=json.dumps({"event": "return_output", "message": f"File saved to {file_directory}"}))
    
        except Exception as e:
            await self.send(text_data=json.dumps({"event": "return_output", "message": f"Error saving file: {str(e)}"}))
