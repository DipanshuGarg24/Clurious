# we should have the subject :)

# then display 
import streamlit as st 

# diaply the clurious logo and all :) 

st.header("Clurious")

if "state" not in st.session_state:
    st.session_state["state"] = "create"


gate_cse_subjects = [
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
if st.session_state.state == "create":
    st.subheader("Design Your Custom Quiz")
    
    # Use st.radio for a clear, two-option choice and place it outside the forms
    quiz_type = st.radio("Choose Quiz Type", ["Full Syllabus", "Custom"], horizontal=True)

    # --- Display a different form based on the user's choice ---

    if quiz_type == "Full Syllabus":
        with st.form("full_syllabus_form"):
            numberQues_full = st.number_input("Number of Questions", min_value=1, max_value=10, value=5,help="Number of Question can be maximum 10")
            Mode = st.select_slider("Select the Level of Quiz",["Easy","Medium","Hard"],value="Medium")
            if st.form_submit_button("🚀 Generate Full Syllabus Quiz"):
                st.success("Quiz parameters received! Generating your quiz...")
                st.write("Quiz Type:", quiz_type)
                st.write("Number of Questions:", numberQues_full)

    elif quiz_type == "Custom":
        with st.form("custom_quiz_form"):
            subject_name = st.multiselect("Choose Subjects",
                                          gate_cse_subjects)
            
            numberQues_custom = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
            Mode = st.select_slider("Select the Level of Quiz",["Easy","Medium","Hard"],value="Medium")
            if st.form_submit_button("🚀 Generate Custom Quiz"):
                if not subject_name:
                    st.error("Please select at least one subject for a custom quiz.")
                else:
                    st.success("Quiz parameters received! Generating your quiz...")
                    st.write("Quiz Type:", quiz_type)
                    st.write("Subjects:", ", ".join(subject_name))
                    st.write("Number of Questions:", numberQues_custom)
else:
    # just show please select the name and the test to continue starting 
    st.info("Please select the exam to conintue")
    if st.button("Home"):
        st.switch_page("main.py")
