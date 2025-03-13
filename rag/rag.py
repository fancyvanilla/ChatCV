from langchain_huggingface import HuggingFaceEmbeddings
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from prompts import rag_prompt, refined_rag_prompt
from llm import groq_llm
from store.setup import Store
from utils import check_path
import os
import csv
import hashlib
from dotenv import load_dotenv
load_dotenv()

#The state of the application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    refined_answer:str
    weights:dict
    data_path:str


def get_env(name):
    try:
        return os.environ[name]
    except KeyError:
        raise Exception(f"Environment variable {name} not found")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store_path=check_path(get_env("VECTOR_STORE_DIR_PATH"))
vector_store=Store(collection="resume", persist_dir=vector_store_path, embeddings=embeddings)
def load_data(filename):
    documents=[]
    with open(filename, mode='r',encoding="utf-8") as file:
        csv_file = csv.DictReader(file)
        for idx, row in enumerate(csv_file):
            doc = Document(" ".join(row.values()))
            doc.metadata={"index":idx,"email":row["email"],"name":row["name"]}
            doc.id=hashlib.sha256(row["email"].encode('utf-8')).hexdigest()
            documents.append(doc)
    vector_store.add_documents(documents)
    print(f"Split the csv ino {idx+1} documents.")
def clear_data():
    ids=vector_store.get_all().get("ids",{})
    if len(ids):
      vector_store.remove_documents([doc for doc in ids])
def retrieve_docs():
    retrieved_docs = vector_store.get_all()
    return retrieved_docs
def retrieve(state: State):
    retrieved_docs = vector_store.retrieve(state["question"])
    return {
        "context":retrieved_docs
    }

def generate(state:State):
    docs_content= "\n\n".join(str(doc.metadata["index"])+":"+doc.page_content for doc in state["context"])
    messages=rag_prompt.invoke({"question":state["question"],"context":docs_content})
    response=groq_llm.invoke(messages)
    return {
        "answer":response.content
    }
def generate_refined(state:State):
    docs_content= "\n\n".join(str(doc.metadata["index"])+":"+doc.page_content for doc in state["context"])
    messages=refined_rag_prompt.invoke({"question":state["question"],"context":docs_content,"answer":state["answer"],"education":state["weights"]["education"],"experience":state["weights"]["experience"],"skills":state["weights"]["skills"],"certificates":state["weights"]["certificates"]})
    response=groq_llm.invoke(messages)
    return {
        "refined_answer":response.content
    }

def RAG(data_path):
    load_data(data_path)
    graph_builder=StateGraph(State).add_sequence([retrieve,generate,generate_refined])
    graph_builder.add_edge(START,"retrieve")
    graph=graph_builder.compile()
    return graph
def query_rag(query,weights,data_path):
    graph=RAG(data_path)
    response=graph.invoke({"question":query,"weights":weights})
    return response["refined_answer"]

