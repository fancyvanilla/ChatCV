import pypdf
import sys
import os
import json
import re
import csv
from .types import Candidate
from constants import CANDIDATE_FIELD_NAMES
from llm import groq_llm_response
from prompts import json_loader_prompt as prompt
from utils import check_path, get_config_variable
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

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

def email_exists(email, data_path):
    try:
        df=pd.read_csv(data_path)
        return email in df["email"].values
    except Exception as e:
        return False

def cvs2csv(filenames):
    output_path=os.path.join(check_path(os.environ["OUTPUT_DIR_PATH"]), get_config_variable("CSV_FILE_NAME"))
    emails=set()
    with open(output_path, mode="a+", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=CANDIDATE_FIELD_NAMES)
        if f.tell()==0:
            writer.writeheader()
        for file in filenames:
            json_data=cv2json(file)
            if json_data and not json_data["email"] in emails and not email_exists(json_data["email"], output_path):
              writer.writerow(json_data)
              emails.add(json_data["email"])

def clear_csv():
    data_path=os.path.join(check_path(os.environ["OUTPUT_DIR_PATH"]), get_config_variable("CSV_FILE_NAME"))
    with open(data_path, mode="w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=CANDIDATE_FIELD_NAMES)
        writer.writerows([])
        