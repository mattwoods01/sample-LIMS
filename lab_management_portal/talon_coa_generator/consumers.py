import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import random
import pandas as pd
import base64
import shutil as sh
from .talon import generate_pdf
import helper


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        connect to client and mae folder
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
        receive event from client
        """
        data = json.loads(text_data)
        event = data.get("event")
        print(event)

        if event == "run_program":
            await self.run_program(data)

    async def run_program(self, data):

        """
        run program and generate pdf
        """
        input_headers = data['input_headers']
        input_data = data['input_data']
        form_headers = data['form_headers']
        form_data = data['form_data'][0]
        kit_string = data['selected_kit']

        input_df = pd.DataFrame(input_data, columns=input_headers)
        form_dict = {form_headers[i]: form_data[i] for i in range(len(form_headers))}
        file_name = generate_pdf(self.folder_name, form_dict, input_df, kit_string)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Encoding PDF..."}))
        with open(file_name, 'rb') as file:
            pdf_data = file.read()
            encoded_zip_data = base64.b64encode(pdf_data).decode('utf-8')
            
        await self.send(text_data=json.dumps({"event": "return_file", "data": [file_name, encoded_zip_data]}))

