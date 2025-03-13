from langchain_core.documents import Document
from langchain.vectorstores import Chroma
import streamlit as st

class Store():
    def __init__(self,collection,persist_dir,embeddings):
        self.vector_store=Chroma(
            collection_name=collection,
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    def add_documents(self, documents:list[Document]):
        existing_documents=self.vector_store.get(ids=[doc.id for doc in documents])
        existing_ids=set(existing_documents["ids"])
        for doc in documents:
            if doc.id not in existing_ids:
                self.vector_store.add_documents([doc])
            else:
                self.vector_store.update_document(document_id=doc.id, document=doc)
    def get_all(self):
        return self.vector_store.get()
    def remove_documents(self,document_ids:list[str]):
        self.vector_store.delete(ids=document_ids)
    def retrieve(self, question:str):
        return self.vector_store.similarity_search(question,k=5)
   