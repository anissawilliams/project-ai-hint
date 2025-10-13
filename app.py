import streamlit as st


import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_hint_project.src.ai_hint_project.crew import create_crew

st.title("AI Programming Tutor 👨‍🏫")

#topic = st.text_input("Enter a programming topic (e.g., recursion, OOP, Python loops)")
user_query = st.text_area("Ask a programming question")

if st.button("Optimize and Explain"):
    if user_query:
        with st.spinner("Running your AI tutor crew..."):
            try:
                result = create_crew(user_query)
                st.success("CrewAI completed successfully!")
                st.markdown("### 🧠 CrewAI Response") 

                st.markdown("### 📝 Original Query")
                st.markdown(user_query)

                st.markdown("### ✨ Optimized Query")
                st.markdown(result["optimized_query"])

                st.markdown("### 📘 Explanation")
                st.markdown(result["explanation"])

                #st.write(result)  # Show raw output
                    
            except Exception as e:
                st.error("❌ Error running CrewAI")
                st.code(str(e))

if st.button("Save session"):
    st.success("Session saved!")
     # Build log entry
    
