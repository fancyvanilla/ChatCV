from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

groq_llm=ChatGroq(model="llama-3.3-70b-versatile")

def groq_llm_response(prompt):
    messages=[prompt]
    response=groq_llm.invoke(messages)
    return response.content
