import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import random
import pandas as pd
import base64
import numpy as np
import helper
import zipfile

class MyConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_name = str(random.randint(1, 1000000))
        self.instrument_df = None

    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Connected"}))
        os.mkdir(self.folder_name)

        print("Connected")

    async def disconnect(self, close_code):
        helper.remove_folder(self.folder_name)

        await self.send(text_data=json.dumps({"event": "return_output", "message": "Client Disconnected"}))
        print("Disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data.get("event")
        print(event)

        if event == "run_program":
            await self.run_program(data)
        elif event == 'file_upload':
            await self.file_upload(data)

    async def file_upload(self, data):
        print(data)
