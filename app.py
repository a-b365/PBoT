#Standard library imports
import os
import string
from typing import Union

#Third party imports
# import llama_index
from pydantic import model_validator, BaseModel
from fastapi import FastAPI
from llama_index.llms.openai import OpenAI
# from llama_index.llms.gemini import Gemini


GOOGLE_API_KEY = "AIzaSyAHuQtUbzh5DhUm_aNAwX1JC5M0DczVTmY"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

app = FastAPI()

@app.get("/")
def read_root():
    pass

@app.post("/gemini")
def remote(q:str):
    res = Gemini().complete(q)
    return {
        "res":res.text
    }