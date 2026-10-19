
import os
import streamlit as st
from groq import Groq

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        color: #7567F8;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #888888;
        font-size: 16px;
        margin-bottom: 25px;
    }
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
    }
    [data-testid="stChatMessage"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🎓 AI Study Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Your personal AI tutor — learn, practice, and grow!</div>',
    unsafe_allow_html=True
)

# ---------------- GROQ API KEY ----------------
def get_api_key():
    # Streamlit Cloud Secrets
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # Environment variable fallback
    return os.getenv("GROQ_API_KEY", "")


api_key = get_api_key()

# ---------------- SIDEBAR SETTINGS ----------------
with st.sidebar:
    st.header("⚙️ Study Settings")

    subject = st.selectbox(
        "Choose a subject",
        [
            "General Study",
            "Mathematics",
            "Physics",
            "Chemistry",
            "Biology",
            "Computer Science",
            "English",
            "History"
        ]
    )

    level = st.selectbox(
        "Your learning level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    response_style = st.selectbox(
        "Answer style",
        [
            "Simple Explanation",
            "Step-by-Step",
            "Detailed Answer",
            "Quiz Me"
        ]
    )

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Groq AI")

# ---------------- INITIALIZE CHAT ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- WELCOME SCREEN ----------------
if not st.session_state.messages:
    st.info(
        "👋 Welcome to your AI Study Assistant!\n\n"
        "Ask questions, understand difficult concepts, "
        "solve problems step by step, or practice for exams."
    )

    st.markdown("### 💡 Try asking")
    col1, col2 = st.columns(2)

    with col1:
        st.caption("📘 Explain photosynthesis")
        st.caption("➗ Help me solve an equation")

    with col2:
        st.caption("💻 What is Python?")
        st.caption("📝 Create a science quiz")

# ---------------- DISPLAY CHAT HISTORY ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask your study question here...")

if prompt:
    # Save and display the user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error(
            "Groq API key is missing. Add GROQ_API_KEY "
            "in Streamlit Cloud → Settings → Secrets."
        )

    else:
        system_prompt = f"""
You are a friendly, knowledgeable AI Study Assistant.

Your purpose is to help students learn effectively.

Instructions:
- Explain difficult concepts in clear, simple language.
- Give step-by-step solutions when appropriate.
- Provide examples to improve understanding.
- Help students prepare for exams.
- Create practice questions and quizzes when requested.
- Be encouraging, respectful, and accurate.
- If you are unsure about something, say so honestly.
- Format responses using Markdown headings, lists, and equations
  when useful.

Student subject: {subject}
Learning level: {level}
Preferred answer style: {response_style}

Adapt your answer to the student's selected level and style.
For quiz requests, provide questions and let the student try
answering before revealing solutions when appropriate.
"""

        try:
            client = Groq(api_key=api_key)

            api_messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Include recent conversation context
            api_messages.extend(
                st.session_state.messages[-12:]
            )

            with st.chat_message("assistant"):
                with st.spinner("📚 Preparing your answer..."):
                    response = client.chat.completions.create(
                       model="llama-3.3-70b-versatile",
                        messages=api_messages,
                        temperature=0.5,
                        max_tokens=1500
                    )

                    answer = response.choices[0].message.content

                    if not answer:
                        answer = "I couldn't generate an answer. Please try again."

                    st.markdown(answer)

            # Save the assistant response
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as error:
            # Remove the unanswered user message from history,
            # so the user can retry without a broken conversation.
            if (
                st.session_state.messages
                and st.session_state.messages[-1]["role"] == "user"
                and st.session_state.messages[-1]["content"] == prompt
            ):
                st.session_state.messages.pop()

            error_message = str(error)
            st.error(
                "Sorry, I couldn't generate a response. "
                "Please check your API key, model availability, "
                "internet connection, and Groq usage limits."
            )

            # Show a safe diagnostic instead of exposing secrets
            if "authentication" in error_message.lower() or "api key" in error_message.lower():
                st.warning(
                    "Your API key may be invalid. Check GROQ_API_KEY "
                    "in Streamlit Cloud Secrets."
                )
            elif "model" in error_message.lower():
                st.warning(
                    "The selected model may be unavailable. "
                    "Check Groq Console for a currently supported model."
                )
            else:
                st.caption(
                    f"Error type: {type(error).__name__}. "
                    "Check Manage app → Logs for more details."
                )

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "🎓 AI Study Assistant | Built with Streamlit and Groq"
)
