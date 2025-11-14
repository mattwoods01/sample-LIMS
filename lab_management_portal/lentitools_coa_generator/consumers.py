import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import random
import pandas as pd
import base64
import numpy as np
import helper
import zipfile
from .generate_coa import generate_pdf

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))

    async def connect(self):
        """
        Connects to client
        """
        await self.accept()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Connected"}))
        os.mkdir(self.folder_name)
        print("Connected")

    async def disconnect(self, close_code):
        """
        disconnects from client
        """
        helper.remove_folder(self.folder_name)
        await self.send(json.dumps({"event": "return_output", "message": "Client Disconnected"}))
        print("Disconnected")

    async def receive(self, text_data):
        """
        receive events from client
        """
        data = json.loads(text_data)
        event = data.get("event")
        print(event)

        if event == "run_program":
            await self.run_program(data)

    async def run_program(self, data):
        """
        Run program
        """
        form_headers = data['form_headers']
        form_data = data['form_data']
        form_df = pd.DataFrame(form_data, columns=form_headers)

        form_df.replace(['', 'nan'], np.nan, inplace=True)
        form_df = form_df.dropna(subset=['#'])

        for i, row in form_df.iterrows():
            await self.send(json.dumps({"event": "return_output", "message": f"Encoding PDF for {row['#']}"}))
            error_code, file_name = generate_pdf(self.folder_name, row)

            print(error_code, file_name)

            if error_code == "FileNameError":
                await self.send(json.dumps({"event": "return_output", "message": f"Error found in file naming convention: {file_name}"}))

        await self.send(json.dumps({"event": "return_output", "message": "Zipping file..."}))
        with zipfile.ZipFile(f'{self.folder_name}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.folder_name):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)

        await self.send(json.dumps({"event": "return_output", "message": "Sending file..."}))
        with open(f'{self.folder_name}.zip', 'rb') as file:
            zip_data = file.read()
            encoded_zip_data = base64.b64encode(zip_data).decode('utf-8')

        await self.send(json.dumps({"event": "return_file", "data": encoded_zip_data}))
        os.remove(f'{self.folder_name}.zip')
        await self.send(json.dumps({"event": "return_output", "message": "Complete"}))
