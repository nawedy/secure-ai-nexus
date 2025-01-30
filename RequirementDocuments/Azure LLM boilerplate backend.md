\# Azure LLM Boilerplate (Backend \- FastAPI)

from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel  
import os  
import ssl  
import certifi

try:  
    import openai  
except ModuleNotFoundError:  
    raise ImportError("The 'openai' module is not installed. Please install it using 'pip install openai'.")

\# Ensure SSL certificates are correctly loaded  
ssl\_context \= ssl.create\_default\_context(cafile=certifi.where())

\# Load OpenAI API Key from Azure Key Vault or Environment  
api\_key \= os.getenv("OPENAI\_API\_KEY")  
if not api\_key:  
    raise ValueError("Missing OpenAI API key. Set the 'OPENAI\_API\_KEY' environment variable.")  
openai.api\_key \= api\_key

app \= FastAPI()

class Query(BaseModel):  
    prompt: str

@app.post("/chat")  
def chat(query: Query):  
    try:  
        response \= openai.ChatCompletion.create(  
            model="gpt-4",  
            messages=\[{"role": "user", "content": query.prompt}\],  
            request\_timeout=10  \# Prevent long-running requests  
        )  
        return {"response": response\["choices"\]\[0\]\["message"\]\["content"\]}  
    except openai.error.OpenAIError as e:  
        raise HTTPException(status\_code=500, detail=f"OpenAI API error: {str(e)}")  
    except Exception as e:  
        raise HTTPException(status\_code=500, detail=f"Internal server error: {str(e)}")

\# Run locally with: uvicorn main:app \--reload

