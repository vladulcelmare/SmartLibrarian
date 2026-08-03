import streamlit as st
import json
from backend.api import get_recommendation, call_function
from backend.utils import format_answer, filter_explicit_language
from backend.config import openai_client, CHAT_MODEL, CHAT_TOOLS, SYSTEM_PROMPT
from datetime import date

# main page configuration
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

# initialisation of message history to display in ui
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! Tell me what kind of story you would like to read.",
    }]

if "input_messages" not in st.session_state:
    st.session_state.input_messages = []



# banner
st.markdown(
    '<div class="hero"><h1>Smart Librarian</h1>'
    '<p>Book recommendations based on your preferences'
    '</p></div>',
    unsafe_allow_html = True,
)

# sidebar
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

    # reset conversation button
    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! Tell me what kind of story you would like to read.",
            }]
        st.session_state.input_messages = []
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

# display initial message
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# input box for user to ask questions
user_message = st.chat_input("Ask away about any book or story you want to read")


# message loop logic

## if the user has sent a message or selected a sample question, we process it
if user_message or sample:
    current_input = user_message if user_message is not None else sample

    st.session_state.messages.append(
        {
            "role": "user",
            "content": current_input,
        }
    )

    ## display
    with st.chat_message("user"):
        st.write(current_input)

    ## check before sending to the chatbot (the chatbot may ignore this step completely)
    if filter_explicit_language(current_input):
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Sorry, I cannot provide recommendations for content that contains explicit language. "
            "Please rephrase your request without using any explicit words or phrases.",
        })
        with st.chat_message("assistant"):
            st.write("Sorry, I cannot provide recommendations for content that contains explicit language. "
            "Please rephrase your request without using any explicit words or phrases.")
    else:
        ## a temporary list that holds the messages for this turn, in case its incomplete we simply dont append
        turn_messages = list(st.session_state.input_messages)

        turn_messages.append({
            "role": "user",
            "content": current_input,
        })

        try:
            ## design choice instead of st.spinner
            with st.status("Searching the library...", expanded=False) as status:
                st.write("Searching the book database...")

                ## first request to the chatbot to fetch the answer and the tool calls, if any
                response = openai_client.responses.create(
                    model=CHAT_MODEL,
                    instructions=SYSTEM_PROMPT,
                    tools=CHAT_TOOLS,
                    input=turn_messages,
                )

                turn_messages += response.output

                for tool_call in response.output:
                    if tool_call.type != "function_call":
                        continue
                    ## failsafe for errors
                    try:
                        args = json.loads(tool_call.arguments)
                        result = call_function(tool_call.name, args)
                        if isinstance(result, list):
                            result = [format_answer(item) for item in result]
                        else:
                            result = format_answer(result)

                        tool_output = {
                            "success": True,
                            "result": result,
                        }

                    except Exception:
                        tool_output = {
                            "success": False,
                            "error": "The local book database could not be queried.",
                        }
                    ## we append the result of first tool call
                    turn_messages.append({
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(tool_output, ensure_ascii=False),
                    })

                st.write("Preparing recommendations...")

                ## now second request to chatbot where it makes the answer more human readable
                response = openai_client.responses.create(
                    model=CHAT_MODEL,
                    instructions=SYSTEM_PROMPT,
                    tools=CHAT_TOOLS,
                    input=turn_messages,
                )

                answer = response.output_text
                turn_messages += response.output
            status.update(
                label="Answer ready!",
                state="complete",
            )
        ## failsafe for errors
        except Exception:
            answer = (
                "Sorry, something went wrong while processing your request. "
                "Please try again."
            )

        else:
            st.session_state.input_messages = turn_messages

        ## display and append
        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })
