#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langserve import add_routes
from langchain_community.llms import Ollama
from custome_runable import MyApiRunnable

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    ChatOpenAI(model="gpt-3.5-turbo-0125"),
    path="/openai",
)

add_routes(
    app,
   Ollama(model="llama3.2"),
    path="/llama",
)


llama_model = Ollama(model="llama3.2")
email_prompt = ChatPromptTemplate.from_template("{topic} Please generate a email from the given prompt please dont have any place holders and try to have names and information try to avoid place holders. please do not add any metadata, only include the content. cosider sender as smit radadiya")
add_routes(
    app,
    email_prompt | llama_model,
    path="/email/llama",
)


API_prompt = ChatPromptTemplate.from_template("{prompt} please conver this in to a API response and make sure it has subject,email body,recipents,sender fields and make sure is in in applicaiotn/json format.  please do not add any metadata, only include the content")
add_routes(
    app,
  email_prompt |llama_model|  API_prompt | llama_model,
    path="/email/api/llama",
)

model = ChatOpenAI(model="gpt-3.5-turbo-0125")
prompt = ChatPromptTemplate.from_template("{topic} Please formate the email on the given prompt and give me the response in key value pair in a API formate so I can use this response to send email from generated response with google apis")
add_routes(
    app,
    prompt | model,
    path="/email/gpt",
)

my_api_runnable = MyApiRunnable()

# Then you can expose it via add_routes
add_routes(
    app,
    my_api_runnable,
    path="/test",
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)