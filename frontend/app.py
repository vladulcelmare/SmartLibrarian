import streamlit as st
from api import get_recommendation
from backend.utils import format_answer
from datetime import date


st.set_page_config(page_title = "Smart Librarian", page_icon = "", layout = "wide")
st.markdown(
    """
    <style>
    .block-container { 
    max-width: 1100px; 
    padding-top: 3.5rem;
    }

    .hero { 
    padding: 1.2rem 1.4rem;
    border-radius: 20px;
    background: linear-gradient(
        135deg,
        rgba(37, 99, 235, 0.45),
        rgba(124, 58, 237, 0.45)
    );
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 1.2rem;
    }
    .hero h1 { 
    margin: 0; 
    font-size: 2.2rem;
    text-align: center;
    }
    .hero p { 
    margin: .45rem 0 0;
    color: rgba(255, 255, 255, 0.82);
    text-align: center;
    }

    .status { 
    border-radius: 10px; 
    padding: .7rem .9rem; 
    background: #000000; 
    font-size: .9rem;
    color: rgba(255, 255, 255, 1);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    height: 2.25rem;
    margin-bottom: 0;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
    text-align: center;
    margin-top: 0;
    }

   
    </style>
    """,
    unsafe_allow_html = True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! Tell me what kind of story you would like to read.",
    }]

st.markdown(
    '<div class="hero"><h1>Smart Librarian</h1>'
    '<p>Book recommendations based on your preferences'
    '</p></div>',
    unsafe_allow_html = True,
)


with st.sidebar:
    

    st.header("Settings")
    st.markdown('<div class="status">Demo mode — backend is yet to be connected</div>', 
                unsafe_allow_html=True)
    st.divider()

    st.subheader("Options")
    enable_tts = st.checkbox("Text-to-speech", disabled = True, help = "Not yet implemented")
    enable_voice = st.checkbox("Voice mode", disabled = True, help = "Not yet implemented")
    enable_image = st.checkbox("Image generation", disabled = True, help = "Not yet implemented")
    st.divider()

    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! Tell me what kind of story you would like to read.",
            }]
        st.session_state["sample_questions"] = None
        st.rerun()
    st.divider()

    st.caption("Smart Librarian app, demo project developed by LVTA®, 2026. \nPowered by Streamlit and OpenAI. All rights reserved.")

st.caption("Sample questions")

sample = st.pills(
    "Sample questions",
    [
        "I want a book about freedom and social control.",
        "What do you recommend if I love fantasy stories?",
        "What is 1984?",
        f"Top ten books of {date.today().year}",
    ],
    
    selection_mode = "single",
    key = "sample_questions",
    label_visibility = "collapsed"
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("Ask away about any book or story you want to read")

if user_message or sample:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message if user_message is not None else sample,
        }
    )

    with st.chat_message("user"):
        st.write(user_message if user_message is not None else sample)

    assistant_answer = get_recommendation(
        user_message if user_message is not None else sample,
        st.session_state.messages
    )
    final_reply = format_answer(assistant_answer)
    with st.chat_message("assistant"):
        st.write(final_reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final_reply,
        }
    )
