import streamlit as st
import json
from backend.api import get_recommendation, call_function
from backend.utils import format_answer, filter_explicit_language, fetch_data
from backend.config import openai_client, CHAT_MODEL, CHAT_VOICEMODEL, CHAT_TOOLS, SYSTEM_PROMPT
import backend.users as users
from datetime import date
import random

# main page configuration
st.set_page_config(page_title = "Smart Librarian", page_icon = "", layout = "wide")

# get user authentication status
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None

# mini popup with two buttons from which to select login or guest 
@st.dialog("Login page")
def login_dialog():
    st.write("Welcome to Smart Librarian! Click below to sign in/register or continue as a guest.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign in / Register", use_container_width = True):
            st.login("google")

    with c2:
        if st.button("Continue as guest", use_container_width = True):
            st.session_state.auth_mode = "guest"
            st.rerun()

# checks the authetication status, if not logged in and no mode set, prompt popup
is_logged_in = getattr(st.user, "is_logged_in", False)
if not is_logged_in and st.session_state.auth_mode is None:
    login_dialog()

# get user id if logged in
user_id = st.user.sub if is_logged_in else None

# if its a valid user we put in database if not already there
if is_logged_in:
    users.ensure_user(
        user_id,
        getattr(st.user, "name", user_id),
        getattr(st.user, "email", user_id),
    )


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

    # reset conversation button
    if st.button("New conversation", use_container_width = True):
        st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! Tell me what kind of story you would like to read.",
            }]
        st.session_state.input_messages = []
        st.session_state.pop("conversation_id", None)
        st.session_state["sample_questions"] = None
        st.rerun()
            
    st.divider()
        
    st.header("Settings")

    # user info logic
    if is_logged_in:
        st.info(f"Logged in as: {st.user.name}", title = "User info")

        # retrieve all conversations not older than 7days for the current user and display in sidebar
        conversations = users.retrieve_conversation(user_id)

        if conversations:
            st.subheader("Recent conversations")
            for conv_id, title, creation_date in conversations:
                st.write(f"**{title}** - {creation_date.strftime('%Y-%m-%d')}")

                if st.button(f"Continue conversation", key = f"continue_{conv_id}", use_container_width = True):
                    saved_messages = users.load_conversation(conv_id)
                    st.session_state.conversation_id = conv_id
                    st.session_state.messages = [
                        {"role": role, "content": content}
                        for content, role in saved_messages
                    ]

                    st.session_state.input_messages = [
                        {"role": role, "content": content}
                        for content, role in saved_messages
                    ]
                    st.rerun()
                    
                if st.button(f"Delete conversation", key = f"delete_{conv_id}", use_container_width = True):
                    users.delete_conversation(conv_id)
                    st.session_state.conversation_id = None
                    st.session_state.messages = [
                        {"role": "assistant",
                        "content": "Hello! Tell me what kind of story you would like to read.",
                        }]
                    st.session_state.input_messages = []
                    st.rerun()

        if st.button("Logout", use_container_width = True):
            st.session_state["sample_questions"] = None
            st.logout()

    else:
        st.info("Guest mode", title = "User info")

        if st.button("Login", use_container_width = True):
            st.session_state["sample_questions"] = None
            st.login("google")

    st.divider()

    st.subheader("Options")
    
    enable_voice = st.checkbox("Voice mode", disabled = True, help = "Not yet implemented")
    enable_image = st.checkbox("Image generation", disabled = False, help = "Image generation, a drop down box from which user can select title")

    if enable_image:
        @st.dialog("Image generation")
        def generate_image():
            data = fetch_data()

            st.write("Please select a title to generate an image for")

            title = st.selectbox("Choose title", [item["pretty_title"] for item in data.values()])
            summary = data[title.upper()]["summary"]

            if st.button("Generate image", use_container_width = True):
                with st.spinner("Generating image..."):
                    response = openai_client.images.generate(
                        model = "gpt-image-1",
                        prompt = f"Generate an image for the book '{title}' based on the following summary: {summary}",
                        size = "1024x1024",
                        quality = "medium"
                    )

                    import base64

                    image_data = base64.b64decode(response.data[0].b64_json)
                    st.image(image_data, caption = f"Generated image for '{title}'", width = "stretch")

        generate_image()

    st.divider()

    

    st.caption("Smart Librarian app, demo project developed by LVTA®, 2026. \nPowered by Streamlit and OpenAI. All rights reserved.")

st.caption("Sample questions")
def select_sample_question():
    st.session_state["pending_sample"] = st.session_state["sample_questions"]
    st.session_state["sample_questions"] = None

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
    on_change = select_sample_question,
    label_visibility = "collapsed"
)

# display initial message(s)
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant":
            if st.button("🔊", key = f"tts_{index}"):
                
                response = openai_client.audio.speech.create(
                    model = CHAT_VOICEMODEL,
                    voice = "alloy",
                    input = message["content"],
                )

                st.audio(response.read(), format = "audio/mp3")

# input box for user to ask questions
user_message = st.chat_input("Ask away about any book or story you want to read")


# message loop logic

## if the user has sent a message or selected a sample question, we process it
sample = st.session_state.pop("pending_sample", None)

if user_message or sample:
    current_input = user_message if user_message is not None else sample

    if is_logged_in:
        conversation_id = st.session_state.get("conversation_id")
        if conversation_id is None:
            conversation_id = users.new_conversation(user_id, current_input)
            st.session_state.conversation_id = conversation_id
        users.add_message(conversation_id, current_input, "user")

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
                    model = CHAT_MODEL,
                    instructions = SYSTEM_PROMPT,
                    tools = CHAT_TOOLS,
                    input = turn_messages,
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
                    model = CHAT_MODEL,
                    instructions = SYSTEM_PROMPT,
                    tools = CHAT_TOOLS,
                    input = turn_messages,
                )

                answer = response.output_text
                if not answer or not answer.strip():
                    answer = "Sorry, I could not find any recommendations based on your request."
                turn_messages += response.output
                
            status.update(
                label = "Answer ready!",
                state = "complete",
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
            if st.button("🔊", key=f"tts_{st.session_state.conversation_id}_{len(st.session_state.messages)}" if st.session_state.auth_mode != "guest" else f"tts_{len(st.session_state.messages) * random.randint(0,1000)}"):

                response = openai_client.audio.speech.create(
                    model = CHAT_VOICEMODEL,
                    voice = "alloy",
                    input = answer,
                )

                st.audio(response.read(), format = "audio/mp3")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })

        if is_logged_in:
            users.add_message(st.session_state.conversation_id, answer, "assistant")

        
