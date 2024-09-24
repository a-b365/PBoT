import streamlit as st
from llama_index.core import VectorStoreIndex, Document, Settings, SimpleDirectoryReader
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from google.api_core.exceptions import InvalidArgument
from google.auth.exceptions import DefaultCredentialsError

# Configure the API key
# genai.configure(api_key = st.secrets["gemini_api_key"])
st.set_page_config(page_title="PBoT")

# Authentication function for validating the API key
def validate_api_key(api_key):
    try:
        # Attempt to create a Gemini instance with the provided API key
        Gemini(api_key) # Assuming this initiates the client and checks the key
        return True
    
    except InvalidArgument or DefaultCredentialsError:
        return False

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state["authenticated"]:
    st.markdown('<h2 class="main-title", align="center">Gemini API Authentication</h2>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-title" align="center">Please enter your API key to access the app</h3>', unsafe_allow_html=True)
    # Create a login box with custom styling
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
        # Text input for API key
        api_key = st.text_input("Gemini Api Key", type="password", help="Enter Your Gemini Api Key Here.")
            
        # Validate button
        login_button = st.button("Input Api Key")

        # Handle login button click
        if login_button:
            if validate_api_key(api_key):
                st.session_state['authenticated'] = True
                st.session_state['api_key'] = api_key
                # st.success("Login Successful!")
                st.rerun()  # Immediately rerun to move to the main app
            else:
                st.write("Invalid Api Key. Please Try Again.")
    
    # Container for additional information
    with st.container():
        st.markdown("<h3 align='center'>Get your API key from Google AI Studio.</h3>", unsafe_allow_html=True)
        
        # Link to the Gemini API page in Google AI Studio
        st.markdown("""
            <p align='center'>To generate your API key, visit the <a href="https://ai.google.dev/gemini-api" target="_blank">
            Google AI Studio</a>.</p>
        """, unsafe_allow_html=True)


    st.divider()
    
    st.markdown("<p style='color:blue;text-align:center;'>Note: To use the model without api key leave the api field blank and continue.</p>", unsafe_allow_html=True)

else:
    st.header("Chat With Your own Docs 💬 📚")

    with st.sidebar:
        with st.popover("Choose a model", use_container_width=True):
            st.button("Gemini")

        st.divider()
        uploaded_files = st.file_uploader(label="Upload Files", accept_multiple_files=True)
        if uploaded_files:
            for file in uploaded_files:
                # st.write(f"{file.name}")
                with open(f"data/{file.name}", "wb") as f:
                    f.write(file.getbuffer())


        st.header("Get your API key from Google AI Studio.")
    
        # Link to the Gemini API page in Google AI Studio
        st.markdown("""
            <p>To generate your API key, visit the <a href="https://ai.google.dev/gemini-api" target="_blank">
            Google AI Studio</a>.</p>
        """, unsafe_allow_html=True)

        st.divider()
        logout_button = st.sidebar.button("Logout", use_container_width=True)
        if logout_button:
            st.session_state["authenticated"] = False
            st.session_state["api_key"] = None
            st.rerun()  # Rerun to force logout and show login page


    if "messages" not in st.session_state.keys():  # Initialize the chat message history
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me about yourself!"}
        ]

    @st.cache_resource(show_spinner=False)
    def load_data():
        with st.spinner(text="Loading and indexing the files – hang on! This should take a few minutes."):
            reader = SimpleDirectoryReader(input_dir="data", recursive=True)
            docs = reader.load_data()
            # Create the LLM (Gemini) instance directly
            Settings.llm = Gemini(api_key=st.secrets["gemini_api_key"], model="models/gemini-pro", temperature=0.5)
            Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=st.secrets["gemini_api_key"])
            # Directly use the LLM when creating the VectorStoreIndex
            index = VectorStoreIndex.from_documents(docs, llm=Settings.llm, embed_model=Settings.embed_model)
            return index

    index = load_data()

    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message) # Add response to message history