import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="Titanic Dataset Chat Agent",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed"  
)

st.title("🚢 Titanic Dataset Chat Agent")
st.caption("Ask natural language questions about the Titanic dataset")

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

        # If backend returns error status
        if response.status_code != 200:
            return {
                "answer": f"Backend error (Status {response.status_code})",
                "image": None
            }

        # Try parsing JSON safely
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
        "How many passengers survived?",
        "Plot passenger count by sex",
        "Show survival count by passenger class",
        "Plot distribution of fares",
        "Which class had the highest survival rate?",
    ]

    for q in example_questions:
        if st.button(q):
            st.session_state.pending_question = q
            st.rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


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
    for msg in st.session_state.chat_history:
        if msg[0] == "user":
            with st.chat_message("user"):
                st.write(msg[1])
        else:
            with st.chat_message("assistant"):
                st.write(msg[1])
                if len(msg) > 2 and msg[2]:
                    st.image(base64.b64decode(msg[2]))

    # Show spinner INSIDE chat
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            data = ask_backend(question)

        answer = data.get("answer", "")
        image = data.get("image")

        st.write(answer)

        if image:
            st.image(base64.b64decode(image))

    # Save assistant message
    st.session_state.chat_history.append(("assistant", answer, image))

    st.stop()

# Display Existing Chat
for msg in st.session_state.chat_history:
    if msg[0] == "user":
        with st.chat_message("user"):
            st.write(msg[1])
    else:
        with st.chat_message("assistant"):
            st.write(msg[1])
            if len(msg) > 2 and msg[2]:
                st.image(base64.b64decode(msg[2]))