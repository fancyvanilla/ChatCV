import requests
import urllib.parse
import base64
from dotenv import load_dotenv
from constants import GMAIL_API
import os
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
    if not os.path.isdir(os.environ["USER_GMAIL_DATA_PATH"]):
        os.makedirs(os.environ["USER_GMAIL_DATA_PATH"])
    for _ ,data in attachements.items():
        file_path=os.path.join(os.environ["USER_GMAIL_DATA_PATH"],data["filename"] )
        with open( file_path ,"wb") as f:
            f.write(base64.urlsafe_b64decode(data["data"]))
        files.append(file_path)
    return files

        
