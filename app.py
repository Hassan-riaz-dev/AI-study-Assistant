try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY", "")

# ---------------- SIDEBAR ----------------
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
        ["Simple Explanation", "Step-by-Step", "Detailed Answer", "Quiz Me"]
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by Groq AI")

# ---------------- CHAT HISTORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY MESSAGES ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- WELCOME MESSAGE ----------------
if not st.session_state.messages:
    st.info(
        "👋 Welcome! Ask me anything about your studies. "
        "I can explain concepts, solve problems, create quizzes, "
        "and help you prepare for exams."
    )

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Ask your study question here...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        st.error(
            "Groq API key is missing. Add GROQ_API_KEY in "
            "Streamlit Secrets or set it as an environment variable."
        )
    else:
        try:
            client = Groq(api_key=api_key)

            system_prompt = f"""
You are a friendly, helpful AI Study Assistant.

Your role:
- Help students understand academic topics.
- Explain difficult concepts in clear, simple language.
- Give step-by-step solutions when appropriate.
- Provide examples and practice questions.
- Help students prepare for exams.
- If asked for a quiz, ask relevant questions and explain answers.
- Be encouraging, accurate, and honest when uncertain.
- Do not simply provide an answer when teaching the student
  would be more useful.

Student's subject: {subject}
Student's learning level: {level}
Preferred answer style: {response_style}

Adapt your answers to the selected subject, level, and style.
Use readable Markdown, headings, and lists when helpful.
"""

            api_messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Keep recent messages to limit token usage
            api_messages.extend(st.session_state.messages[-12:])

            with st.chat_message("assistant"):
                with st.spinner("📚 Thinking and preparing your answer..."):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=api_messages,
                        temperature=0.5,
                        max_tokens=1500
                    )

                    answer = response.choices[0].message.content
                    st.markdown(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error(
                "Sorry, I couldn't generate a response. "
                "Please check your Groq API key, model availability, "
                "and internet connection."
            )
            st.caption(f"Technical details: {e}")
