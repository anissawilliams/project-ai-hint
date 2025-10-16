import streamlit as st
import sys
import os
from ai_hint_project.src.ai_hint_project.crew import create_crew

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

st.title("🧠 AI Programming Tutor Crew")
depth = st.sidebar.radio("Explanation depth", ["Fast", "Thorough"])


user_level = st.selectbox(
    "What is your experience level in programming?",
    ("Beginner", "Intermediate", "Advanced"),
)

user_query = st.text_area("Enter your programming question:")
user_code = st.text_area("Paste your code (optional):")

if st.button("Run Crew"):
    with st.spinner("Running your AI tutor crew..."):
        result = create_crew(user_query, user_level.lower(), user_code, depth=depth)  

    st.markdown("### ✨ Optimized Query")
    st.markdown(result["optimized_query"])
    st.markdown("### 🧾 Explanation")
    st.markdown(result["explanation"])
    st.markdown("### ✨ Guide")
    st.markdown(result["guide"])
    st.markdown("### Debugging")
    st.markdown(result["debugging"])
    st.markdown("### Optimization")
    st.markdown(result["optimization"])
    st.markdown("### Theory")
    st.markdown(result["theory"])

