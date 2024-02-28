import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header

from youtube_search import YoutubeSearch

import utils
import base64

st.set_page_config(page_title="Display Results",
                   layout="wide",
                   initial_sidebar_state="collapsed")

utils.load_tab_css()
utils.initialize_session_state()

######################################################################

st.title("Ask the BOT anything relating to the PDF you just uploaded")

st.session_state.chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

with st.session_state.chat_placeholder:
    for chat in st.session_state.history:
        if chat.role == "human":
            user = st.chat_message("user")
            user.write(chat.content)
        else:
            ai = st.chat_message("assistant")
            ai.write(chat.content)

with prompt_placeholder:
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    text_input = cols[0].text_input(
        "Chat",
        value="",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit",
        type="primary",
        on_click=st.session_state.agent.run_callback,
    )

buttons_placeholder = st.container()

with buttons_placeholder:
    cols = st.columns([0.15, 1])

    cols[0].button("Regenerate Response",
                    key="regenerate",
                    on_click=st.session_state.agent.regenerate_response)

    cols[-1].button("Clear Chat",
                    key="clear",
                    on_click=st.session_state.agent.clear_conversation)

    utils.enterKeypress_submit_button_html()

