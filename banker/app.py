import streamlit as st
import random
import time
from streamlit_js_eval import streamlit_js_eval
from main_agent import create_main_agent
from langchain_community.callbacks import get_openai_callback
import config


with st.sidebar:
        st.subheader("Configuración")
        if st.button("Reiniciar"):
            st.session_state.main_agent = create_main_agent()
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
            

st.title("Asistente para asesores de banca")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.main_agent = create_main_agent()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Escribe tu consulta"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        #response = st.write_stream(response_generator())
        config.model_call_cost = 0

        with st.spinner("Procesando ..."):

            with get_openai_callback() as cb:
                response = st.session_state.main_agent.invoke({"input":prompt})['output']
                cost = cb.total_cost + config.model_call_cost
                
            st.write(response)
            cost_string = f"_Coste en $USD: {cost}_"
            st.markdown(cost_string)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})