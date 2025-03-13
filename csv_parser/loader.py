import pypdf
import sys
import os
import json
import re
import csv
from .types import Candidate
from llm import groq_llm_response
from prompts import json_loader_prompt as prompt
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
field_names=["name","email","skills","certificates","education","experiences"]

def extract_json(text):
    match = re.search(r'({.*})', text, re.DOTALL)

    if match:
        json_text=match.group(0)
        json_text=json_text.replace("json\n","")
        try:
            json_data=json.loads(json_text)
            return json_data
        except json.JSONDecodeError as e:
            print("Error decoding JSON: ", e)
    else:
        print("JSON not found in text")


def cv2json(file)->Candidate:
    pdfReader=pypdf.PdfReader(file)
    pageobjs=[pdfReader.get_page(i) for i in range(pdfReader.get_num_pages())]
    full_text=[i.extract_text().split("\n") for i in pageobjs]
    full_text = "\n".join(item for sublist in full_text for item in sublist)
    cleaned_text=''.join(c for c in full_text if c.isprintable())
    llm_res=groq_llm_response(prompt.format(resume=cleaned_text))
    llm_response=extract_json(llm_res)
    try:
      candidate=Candidate(**llm_response)
      return candidate.flatten()
    except Exception as  e:
        print("Validation error: ",e)

def email_exists(email):
    try:
        df=pd.read_csv(os.environ["OUTPUT_DATA_PATH"],encoding="utf-8")
        return df["email"].str.contains(email).any()
    except:
      return False

def cvs2csv(filenames):
    emails=set()
    with open(os.environ["OUTPUT_DATA_PATH"], mode="a+", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=field_names)
        if f.tell()==0:
            writer.writeheader()
        for file in filenames:
            json_data=cv2json(file)
            if json_data and not email_exists(json_data["email"]) and not json_data["email"] in emails:
              writer.writerow(json_data)
              emails.add(json_data["email"])
    
def clear_csv():
    with open(os.environ["OUTPUT_DATA_PATH"], mode="w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=field_names)
        writer.writerows([])
        