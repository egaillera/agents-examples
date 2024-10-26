import streamlit as st
import random
import time
from streamlit_js_eval import streamlit_js_eval
from funds_agent import create_funds_agent
from langchain_community.callbacks import get_openai_callback


with st.sidebar:
        st.subheader("Configuration")
        if st.button("Restart"):
            st.session_state.main_agent = create_funds_agent()
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
            

st.title("Funds Analysis Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.extraction_agent = create_funds_agent()
    

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask anything about funds: "):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):

        with st.spinner("Processing ..."):

            result = st.session_state.extraction_agent.invoke({"input":prompt})
            st.write(result["output"])
            st.write("---------------")
            for item in result["intermediate_steps"]:
                st.write(item[0].log)
                #st.write(item[1])
            

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": result})