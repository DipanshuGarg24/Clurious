# we should have the subject :)

# then display 
import streamlit as st 
import time
# diaply the clurious logo and all :) 
from models import quiz_gen

st.header("Clurious")
hide_pages_css = """
<style>
    /* Hide the default Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    /* Style the primary button for a custom look */
    .stButton>button {
        border-radius: 10px;
    }
    /* Custom styles for containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="stExpander"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    /* Style for the live clock and timer */
    .live-display {
        font-size: 1.1rem;
        font-weight: 500;
        text-align: center;
        padding: 0.25rem;
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 10px;
        margin-bottom: 1rem; /* Add some space below */
    }
    .stMetric {
        text-align: center;
    }
</style>
"""
st.markdown(hide_pages_css, unsafe_allow_html=True)


gate_cse_subjects =  [
        "Engineering Mathematics",
        "Digital Logic",
        "Computer Organization and Architecture",
        "Programming and Data Structures",
        "Algorithms",
        "Theory of Computation",
        "Compiler Design",
        "Operating System",
        "Databases",
        "Computer Networks"
      ]
dummy_user_profile = {
        "user_id": "test_user_01",
        "cognitive_skill_weaknesses": ["Mathematical-Reasoning", "Analytical-Multi-Step"],
        "mastery_scores": {
            "Dynamic Programming": 45.0
        }
    }

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}

if st.session_state.quiz_state == "create":
    st.subheader("Design Your Custom Quiz")
    
    # Use st.radio for a clear, two-option choice and place it outside the forms
    quiz_type = st.radio("Choose Quiz Type", ["Full Syllabus", "Custom"], horizontal=True)

    # --- Display a different form based on the user's choice ---

    if quiz_type == "Full Syllabus":
        with st.form("full_syllabus_form"):
            numberQues_full = st.number_input("Number of Questions", min_value=1, max_value=5, value=5,help="Number of Question can be maximum 5")
            Mode = st.select_slider("Select the Level of Quiz",["Easy","Medium","Hard"],value="Medium")
            if st.form_submit_button("🚀 Generate Full Syllabus Quiz"):
                st.success("Quiz parameters received! Generating your quiz...")
                st.write("Quiz Type:", quiz_type)
                st.write("Number of Questions:", numberQues_full)

    elif quiz_type == "Custom":
        with st.form("custom_quiz_form"):
            subject_name = st.multiselect("Choose Subjects",
                                          gate_cse_subjects,help="You can select Multiple Subjects")
            
            numberQues_custom = st.number_input("Number of Questions", min_value=1, max_value=5, value=5,help="Number of Question can be maximum 5")
            Mode = st.select_slider("Select the Level of Quiz",["Easy","Medium","Hard"],value="Medium")
            if st.form_submit_button("🚀 Generate Custom Quiz"):
                if not subject_name:
                    st.error("Please select at least one subject for a custom quiz.")
                else:
                    st.success("Quiz parameters received! Generating your quiz...")
                    quiz_info = {"subject/topic":subject_name,"Num ques":numberQues_custom,"difficulty":Mode}
                    with st.empty():
                        # call the model which setup the quiz data
                        with st.spinner("Please Wait"):
                            st.session_state.quiz_data = quiz_gen.generate_quiz(dummy_user_profile,quiz_info)
                        # st.write(st.session_state.quiz_data)
                    st.switch_page("pages/crnt_quiz.py")
else:
    # just show please select the name and the test to continue starting 
    st.info("Please select the exam to conintue")
    if st.button("Home"):
        st.switch_page("main.py")
