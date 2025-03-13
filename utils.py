import requests
import urllib.parse
import base64
from dotenv import load_dotenv
from constants import GMAIL_API
import os
import streamlit as st
import json
load_dotenv()

def get_messages(email,before,after,subject,token)->list[str]:
    if not token:
        raise Exception("No token provided")
    
    headers={'Authorization': 'Bearer '+token}
    encoded_subject=urllib.parse.quote(subject)
    params={
        "q": f"after:{after} before:{before} subject:{encoded_subject} filename:pdf"
    }
    url=GMAIL_API["base_gmail_url"].format(email=email)
    response=requests.get(url, headers=headers, params=params)

    if response.status_code!=200:
        raise Exception("Error while fetching messages: "+response.text)
    data=response.json()
    # return data
    if not data.get("resultSizeEstimate",0):
        return []
    attachements={}
    files=[]
    for message in data["messages"]:
        message_id=message["id"]
        url=GMAIL_API["base_messages_url"].format(email=email,message_id=message_id)
        response=requests.get(url, headers=headers)
        if response.status_code!=200:
            raise Exception("Error while fetching message: "+response.text)
        message=response.json()
        parts=message.get("payload", {}).get("parts", [])
        for part in parts:
            if part["mimeType"]=="application/pdf" and part["filename"].endswith(".pdf"):
                if part["body"]["size"]>2000000:
                    continue
                filename=part["filename"]
                url=GMAIL_API["base_attachments_url"].format(email=email,message_id=message_id,attachment_id=part["body"]["attachmentId"])
                response=requests.get(url, headers=headers)
                if response.status_code!=200:
                    raise Exception("Error while fetching attachment: "+response.text)
                part=response.json()
                data=part["data"]
                attachements[message["id"]]={"filename":filename,"data":data}
                break
    data_path=check_path(os.environ["USER_GMAIL_DIR_PATH"])
    for _ ,data in attachements.items():
        file_path=os.path.join(data_path, data["filename"] )
        with open( file_path ,"wb") as f:
            f.write(base64.urlsafe_b64decode(data["data"]))
        files.append(file_path)
    return files


def check_path(path):
    dir_path=os.path.abspath(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    return dir_path
       
def get_config_variable(variable):
    with open("config.json", "r") as f:
        config=json.load(f)
    return config[variable]