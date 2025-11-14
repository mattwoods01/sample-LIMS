import os
import random
import shutil as sh
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from pdf2image import convert_from_path
from .pluritest import pluritest_generator
import base64
import json
import helper

class MyConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))
        self.image_path = None

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    async def connect(self):
        """
        Connect to client
        """
        await self.accept()
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Connected'}))
        print(f"Folder name set to: {self.folder_name}")

    async def disconnect(self, close_code):
        """
        disconnect from client
        """
        helper.remove_folder(self.folder_name)
        
        await self.send(text_data=json.dumps({'event': 'return_output', 'message': 'Client Disconnected'}))

    async def receive(self, text_data):
        """
        receive events from client
        """
        data = json.loads(text_data)
        event = data.get('event')

        print(event)

        if event == 'run_pluritest':
            await self.generate_pluritest(data)
        elif event == 'upload_pluritest':
            await self.upload_file(data)

    async def generate_pluritest(self, data):
        """
        run program
        """
        input_headers = data['input_headers']
        input_data = data['input_data']
        form_headers = data['form_headers']
        form_data = data['form_data']

        input_df = pd.DataFrame(input_data, columns=input_headers)
        form_df = pd.DataFrame(form_data, columns=form_headers)
        
        template_path = "pluritest_form_generator/pluritest_template.pptx"
        file_name = form_df['Project File Naming Convention'].values[0] + '.pptx'
        output_path = os.path.join(self.folder_name, file_name)
        
        pluritest_generator(template_path, form_df, output_path, input_df, self.image_path)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Encoding PDF..."}))
        with open(output_path, 'rb') as file:
            pdf_data = file.read()
            encoded_pdf_data = base64.b64encode(pdf_data).decode('utf-8')

        await self.send(text_data=json.dumps({"event": "return_file", "data": [file_name, encoded_pdf_data]}))

    async def upload_file(self, data):
        """
        upload file to client
        """
        print(data)
        file_data = bytes(data['file_data'])
        file_name = data['file_name']

        file_directory = os.path.join(self.folder_name, file_name)
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Creating Folder for uploaded file"}))

        try:
            with open(file_directory, "wb") as file:
                file.write(file_data)

            await self.send(text_data=json.dumps({"event": "return_output", "message": f"File saved to {file_directory}"}))

        except Exception as e:
            await self.send(text_data=json.dumps({"event": "return_output", "message": f"Error saving file: {str(e)}"}))
            return

        images = convert_from_path(file_directory, 500)
        image = images[0]

        crop_coords = (0, 300, image.width, image.height)
        cropped_image = image.crop(crop_coords)
        cropped_image_path = os.path.join(self.folder_name, 'cropped_image.jpeg')

        cropped_image.save(cropped_image_path, 'JPEG')
        self.image_path = cropped_image_path
        await self.send(text_data=json.dumps({"event": "return_output", "message": f"Cropped image saved at {cropped_image_path}"}))
