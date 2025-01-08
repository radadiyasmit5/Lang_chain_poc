from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st 
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACKING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system","you are helpfull assistant. please response to the user queries"),
        ("user","Questions:{question}"),
    ]
)


st.title('Langchain Demo With OPENAI API')
input_text = st.text_input("Search the topic u want")

llm = Ollama(model="llama3.2")
output_parsers=StrOutputParser()
chain=prompt|llm|output_parsers

if input_text:
    st.write(chain.invoke({'question':input_text}))