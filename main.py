#  this is the main file where the user will get login first and then he or she can give there quiz but for now i am 

import streamlit as st

# the mmain thing we will start with via maintaing the session state only 
# this is the prototype and does not show the full potential of the idea 

st.title("Clurious")

st.subheader("AI to help you in every Exam ")


if "crnt_state" not in st.session_state:
    st.session_state.crnt_state = "first"

if "userdata" not in st.session_state:
    st.session_state.userdata = {}


if st.session_state.crnt_state != "first":
    st.write(f"Welcome {st.session_state.userdata['name']} \n Target Exam : {st.session_state.userdata['exam']}")
    #  here we can show the quiz maker 
    #  wrong questions
    #  build foundations 
    #  Analysis 
    #  cheat sheet
    st.divider()
    if st.button("Give Quiz",use_container_width=True,type="primary"):
        # we will change the screen here :) 
        # and then create the quiz here :) 
        st.switch_page("pages/quiz.py")
    x = list(st.columns(2))
    y = list(st.columns(2))
    if x[0].button("Wrong Buckets",use_container_width=True):
        pass
    if x[1].button("Analysis",use_container_width=True):
        pass
    if y[0].button("Cheat Sheet",use_container_width=True):
        pass 
    if y[1].button("Build Foundation",use_container_width=True):
        pass




else:
    with st.form("exam"):
        name = st.text_input("Enter Your Name")
        exam_name = st.selectbox("Choose Your exam",["None","GATE CSE","CAT"])
        if st.form_submit_button("Submit",type="primary"):
            # after submitting the state should changed and then the user data should get updated 
            if name and exam_name!="None":
                st.session_state.userdata["name"] = name
                st.session_state.userdata["exam"] = exam_name
                st.session_state.crnt_state = "second"
                st.rerun()
            else:
                st.error("Enter your name and the exam to continue")



st.divider()

st.info("""
**A Note on This Prototype:**

This is an interactive demo designed to showcase the core vision of **Clurious**.

**The Problem We're Solving:** We believe the current "one-size-fits-all" approach to test series is broken. It fails to personalize and often leads to student demotivation rather than targeted improvement.

**Our Mission with Clurious:** To build a truly adaptive learning platform where the focus shifts from generic testing to personalized growth. We empower students to compete with themselves, turning every quiz into a clear, actionable step towards success.
""")

st.write("<p style='text-align:center'>Made with 💖 by Dipanshu Garg </p>",unsafe_allow_html=True)

