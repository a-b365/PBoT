#Standard library imports
import random

#Third party imports
import requests
import streamlit as st
import nltk

st.write("# Ask me anything\n\n")
st.divider()
input_text = st.text_area(label="# ***Input Context***", placeholder="Paste here...", height=300)
button_two = st.button("***Enter***", use_container_width=True)

if button_two:

    url = "http://127.0.0.1:80/gemini"
    response = requests.post(url, params={"q":str(input_text)})

    if response.status_code == 200:
        with st.container(border=True):
            st.write(response.json())
                
    else:
        print(f"Request failed with status code {response.status_code}")
        print(f"Response content: {response.content}")