import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header

from youtube_search import YoutubeSearch
import base64

from Conversation.conversation import ConversationalAgent
from utils import load_tab_css, initialize_session_state, run_html

st.set_page_config(page_title="Display Results",
                   layout="wide",
                   initial_sidebar_state="collapsed")

load_tab_css()
initialize_session_state()
agent = ConversationalAgent()

######################################################################

st.title("Have fun Researching! 📚")

tab1, gap1, tab2, gap2, tab3, gap3, tab4 = st.tabs(["PDF", "   ", "Google", "   ", "Youtube", " ", "Chat"])

with tab1:
    st.subheader("PDF Display")
    col1, col2, col3 = st.columns([1.8, 7, 1])

    with col2:
        pdf_bytes = st.session_state["pdf_bytes"]
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="900" height="800" ' \
                      f'type="application/pdf"></iframe> '
        st.markdown(pdf_display, unsafe_allow_html=True)

with tab2:
    st.subheader("Google Results")
    cols = st.columns(5)
    buttons = []
    for i, keyword in enumerate(st.session_state.search_keywords):
        buttons.append(cols[i].button(keyword, use_container_width=True))

    search_g = ""

    for i, button in enumerate(buttons):
        if button:
            search_g = st.session_state.search_keywords[i]

    components.iframe(f"https://www.google.com/search?igu=1&ei=&q={search_g}", height=1000, scrolling=True)

with tab3:
    st.subheader("Youtube Results")
    cols = st.columns(5)
    buttons = []
    results = []
    for i, keyword in enumerate(st.session_state.search_keywords):
        buttons.append(cols[i].button(keyword, use_container_width=True, key=i))

    search_y = st.text_input("What do you want to search for?", key='youtube')

    for i, button in enumerate(buttons):
        if button:
            search_y = st.session_state.search_keywords[i]

    if search_y:
        results = YoutubeSearch(search_y, max_results=3).to_dict()

    _, col2, _ = st.columns([1.8, 5, 1])

    with col2:
        for i in range(len(results)):
            colored_header(
                label=results[i]['title'],
                description=f"Duration: {results[i]['duration']} \t Views: {results[i]['views'][:-6]}  \t  Published: {results[i]['publish_time']}",
                color_name="blue-green-70",
            )
            st.video(f"https://www.youtube.com/watch?v={results[i]['id']}")

            add_vertical_space(5)

with tab4:
    st.subheader("Chatbot")
    st.text("Ask the chatbot anything! If the chatbot is unable to fetch the answer from the provided document,")
    st.text("it will also perform an additional Web Search to gather more context. You can view the sources below.")

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
            on_click=agent.run_callback,
        )

    st.button("Clear Chat",
              on_click=agent.clear_conversation,
              )

    with st.expander("View Web Sources"):

        if len(st.session_state.google_sources) != 0:
            colored_header(label="Google Searches", description="Related Web Search Results",
                           color_name="light-blue-70")

            for source_dict in st.session_state.google_sources:
                st.divider()
                source_text = f"Title: {source_dict['title']}\n\nLink: {source_dict['link']}\n\nSnippet: {source_dict['snippet']}\n\n"
                st.write(source_text)
                answer = f"\n\nScraped Results: {source_dict['answer']}"
                st.write(answer)

        else:
            colored_header(label="Google Searches", description="Related Web Search Results",
                           color_name="light-blue-70")
            st.write("No google sources found")

    with st.expander("View Document Sources"):

        if len(st.session_state.doc_sources) != 0:
            colored_header(label="Source Documents", description="Related Document Chunks", color_name="orange-70")
            for document in st.session_state.doc_sources:
                st.divider()
                source_text = f"{document.page_content}\n\nPage Number: {document.metadata['page_number']}\nChunk: {document.metadata['chunk']}"
                st.write(source_text)

        else:
            colored_header(label="Source Documents", description="Related Document Chunk Results",
                           color_name="orange-70")
            st.write("No document sources found")

    run_html()

    credit_card_placeholder.caption(f"""
    Used {st.session_state.token_count} tokens
    """)
