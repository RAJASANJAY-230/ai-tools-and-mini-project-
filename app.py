import streamlit as st
from google import genai

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI Study Assistant")
st.write("Turn your notes into summaries, quizzes, flashcards, and study plans.")

st.info(
    "Your notes are sent to Google's Gemini API only when you click Generate. "
    "Do not enter private, confidential, or sensitive information."
)

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API key",
        type="password",
        help="Get an API key from Google AI Studio. Do not share it or upload it to GitHub."
    )
    st.caption("Your API key is used for this session and is not saved by this app.")
    st.markdown("[Get a Gemini API key](https://aistudio.google.com/apikey)")

st.subheader("1. Add your study material")
notes = st.text_area(
    "Paste your notes or a topic here",
    height=220,
    placeholder="Example: Photosynthesis is the process by which green plants..."
)

col1, col2 = st.columns(2)
with col1:
    subject = st.text_input("Subject", placeholder="e.g. Biology")
with col2:
    level = st.selectbox(
        "Study level",
        ["Beginner", "Intermediate", "Advanced"]
    )

st.subheader("2. Choose a learning tool")
feature = st.selectbox(
    "What would you like to create?",
    [
        "Simple Summary",
        "Practice Quiz",
        "Flashcards",
        "Study Plan"
    ]
)

quiz_count = 5
if feature == "Practice Quiz":
    quiz_count = st.slider("Number of questions", 3, 15, 5)

extra_instructions = st.text_input(
    "Optional instructions",
    placeholder="e.g. Focus on exam-important concepts"
)

def make_prompt(feature_name, material, subject_name, level_name, count, extra):
    common = (
        f"Subject: {subject_name or 'Not specified'}\n"
        f"Student level: {level_name}\n"
        f"Study material:\n{material}\n\n"
        "Use clear, student-friendly language. Be accurate and do not invent facts. "
        "If the notes do not contain enough information, say so."
    )

    if feature_name == "Simple Summary":
        task = (
            "Create a well-organized study summary. Include a short overview, "
            "key concepts, important definitions, and a brief recap."
        )
    elif feature_name == "Practice Quiz":
        task = (
            f"Create {count} practice questions based on the study material. "
            "Use a mix of multiple-choice and short-answer questions. "
            "For multiple-choice questions, give four options. Put the answer key "
            "and concise explanations in a separate section after all questions."
        )
    elif feature_name == "Flashcards":
        task = (
            "Create 10 revision flashcards. Format each as 'Question:' followed by "
            "'Answer:'. Keep answers concise and useful for revision."
        )
    else:
        task = (
            "Create a practical 7-day study plan based on the material. "
            "For each day, include a learning goal, tasks, and a short self-test. "
            "Keep the workload realistic for a student."
        )

    if extra.strip():
        task += "\nAdditional instructions: " + extra.strip()

    return task + "\n\n" + common

if st.button("✨ Generate Study Material", type="primary", use_container_width=True):
    if not notes.strip():
        st.warning("Please paste your study notes or enter a topic first.")
    elif not api_key.strip():
        st.warning("Enter your Gemini API key in the sidebar to use the AI features.")
    else:
        try:
            with st.spinner("Creating your study material..."):
                client = genai.Client(api_key=api_key.strip())
                prompt = make_prompt(
                    feature, notes, subject, level, quiz_count, extra_instructions
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                result = response.text

            if result:
                st.success("Your study material is ready!")
                st.markdown(result)
                st.download_button(
                    label="⬇️ Download as text file",
                    data=result,
                    file_name="ai_study_material.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error("The AI returned an empty response. Please try again.")
        except Exception as error:
            st.error(
                "Could not generate content. Check your internet connection and "
                "API key, then try again. If the issue continues, review the API "
                "key and model access in Google AI Studio."
            )
            with st.expander("Technical details"):
                st.code(str(error))

st.divider()
st.caption(
    "Learning support only. Review AI-generated answers against your textbook, "
    "class notes, or trusted sources before using them for exams."
)
