import os
import requests
import pandas as pd

def extract_serial_number(file_name):
    """
    Extract serial number by looking for ' - '
    """
    return file_name.split(' - ')[0]

def categorize_files(directory):

    """
    creates nested dictionary of the directory and filename of uploaded pdf attachments
    """

    files_dict = {}
    
    for file_name in os.listdir(directory):
        if file_name.endswith((".pdf", ".PDF")):
            serial_number = extract_serial_number(file_name)
            
            if serial_number not in files_dict:
                files_dict[serial_number] = {'scan': None}

            files_dict[serial_number]['scan'] = os.path.join(directory, file_name)

    return files_dict

def create_dataframe(files_dict):

    """
    Creates dataframe from dictionary
    """

    data = {
        'Serial Number': [],
        'Scan File': [],
    }
    
    for serial_number, files in files_dict.items():
        data['Serial Number'].append(serial_number)
        data['Scan File'].append(files['scan'])
    
    df = pd.DataFrame(data)
    return df

def update_description(id, description):
    """
    Function to update instrument description
    """
    print(id)
    print(description)

    base_url = 'https://thermofisher.labguru.com'
    payload = {
        "token": '5223e9371b618b588382bfa4daab92af1f8fcf32',
        "item": {
            "description": description,
        }
    }

    headers = {
        'Content-type': 'application/json'
    }

    print(payload)

    put_request = requests.put(base_url + f'/api/v1/instruments/{id}', json=payload, headers=headers)

    print(put_request)

def process_row(row):
    """
    checks if cell from dataframe is not NA
    runs labguru api function
    """
    print(row['Scan File'].iloc[0])
    if pd.notna(row['Scan File'].iloc[0]):
        attach_Labguru(row['Scan File'].iloc[0], row['uuid'].iloc[0], row['Serial Number'].iloc[0], row['As Left'].iloc[0])
        update_description(row['id'].iloc[0], row['Description'].iloc[0])

def attach_Labguru(file_path, uuid, title, description):
    print(file_path)
    """
    function to attach attachment to labguru item
    """
    with open(file_path, 'rb') as file:
    # The token and other data fields, excluding the file
        data = {
            'token': '5223e9371b618b588382bfa4daab92af1f8fcf32',
            'item[attach_to_uuid]': uuid,
            'item[title]': title,
            'item[description]': description  # Corrected field name here
        }

        # The file to be uploaded
        files = {
            'item[attachment]': (file_path, file, 'application/pdf')
        }

        # Make the POST request
        response = requests.post('https://thermofisher.labguru.com/api/v1/attachments', data=data, files=files)

        # Print the response from the server
        print(response.text)


        