import streamlit as st
import requests
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("BACKEND_API_URL") 

if not API_URL:
    # Default to localhost for development
    API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="Titanic Dataset Chat Agent",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("<h1 style='text-align: center;'>🚢 Titanic Dataset Chat Agent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: gray;'>Ask natural language questions about the Titanic dataset</p>",
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# Backend Call Function
def ask_backend(question):
    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=30
        )

        if response.status_code != 200:
            return {
                "answer": f"Backend error (Status {response.status_code})",
                "image": None
            }

        try:
            return response.json()
        except ValueError:
            return {
                "answer": "Invalid response format from backend.",
                "image": None
            }

    except requests.exceptions.ConnectionError:
        return {
            "answer": "Cannot connect to backend. Make sure FastAPI server is running.",
            "image": None
        }

    except requests.exceptions.Timeout:
        return {
            "answer": "Request timed out. The model may be taking too long.",
            "image": None
        }

    except Exception as e:
        return {
            "answer": f"Unexpected error: {str(e)}",
            "image": None
        }


# Sidebar Example Questions
with st.sidebar:
    st.header("Example Questions")

    example_questions = [
        "What percentage of passengers were male?",
        "What was the average ticket fare?",
        "Show me a histogram of passenger ages",
        "How many passengers embarked from each port?",
        "Show survival count by passenger class",
        "Which class had the highest survival rate?",
        "How many passengers survived?",
        "Plot passenger count by sex",
        "Plot distribution of fares",
    ]

    for q in example_questions:
        if st.button(q):
            st.session_state.pending_question = q
            st.rerun()

    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:15px;
            font-size:15px;
            color:white;
            opacity:0.7;
        ">
            Titanic Dataset Chat Agent<br>
            Built with ❤️ by 
            <a href="https://github.com/msaif2729" target="_blank" 
            style="text-decoration:none; color:inherit; font-weight:bold;">
            Saif Ansari
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


# Manual Chat Input
user_input = st.chat_input("Ask something about the Titanic dataset...")

if user_input:
    st.session_state.pending_question = user_input
    st.rerun()


# If There Is a Question to Process
if st.session_state.pending_question:

    question = st.session_state.pending_question
    st.session_state.pending_question = None

    # Add user message immediately
    st.session_state.chat_history.append(("user", question))

    # Display chat so far
    for i, msg in enumerate(st.session_state.chat_history):
        if msg[0] == "user":
            with st.chat_message("user"):
                st.write(msg[1])
        else:
            with st.chat_message("assistant"):
                st.write(msg[1])
                if len(msg) > 2 and msg[2]:
                    decoded_image = base64.b64decode(msg[2])
                    st.image(decoded_image)

                    # ✅ Unique key added here
                    st.download_button(
                        "Download Plot",
                        data=decoded_image,
                        file_name="titanic_plot.png",
                        mime="image/png",
                        key=f"download_history_{i}"
                    )

    # Show spinner INSIDE chat
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            data = ask_backend(question)

        answer = data.get("answer", "")
        image = data.get("image")

        # Word-by-word typing
        placeholder = st.empty()
        full_text = ""

        for word in answer.split():
            full_text += word + " "
            placeholder.markdown(full_text)
            time.sleep(0.09)

        if image:
            decoded_image = base64.b64decode(image)
            st.image(decoded_image)

            # ✅ Unique key added here
            st.download_button(
                "Download Plot",
                data=decoded_image,
                file_name="titanic_plot.png",
                mime="image/png",
                key=f"download_new_{len(st.session_state.chat_history)}"
            )

    # Save assistant message
    st.session_state.chat_history.append(("assistant", answer, image))

    st.stop()


# Display Existing Chat
for i, msg in enumerate(st.session_state.chat_history):
    if msg[0] == "user":
        with st.chat_message("user"):
            st.write(msg[1])
    else:
        with st.chat_message("assistant"):
            st.write(msg[1])
            if len(msg) > 2 and msg[2]:
                decoded_image = base64.b64decode(msg[2])
                st.image(decoded_image)

                # ✅ Unique key added here
                st.download_button(
                    "Download Plot",
                    data=decoded_image,
                    file_name="titanic_plot.png",
                    mime="image/png",
                    key=f"download_existing_{i}"
                )
