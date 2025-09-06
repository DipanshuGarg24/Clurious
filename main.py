import streamlit as st
import time
from streamlit.components.v1 import html

# Assuming these models exist; if not, they can be mocked or implemented as needed
from models import quiz_gen, notes_maker

# Page configuration
st.set_page_config(
    page_title="Clurious Quiz",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
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
    /* Additional enhancements for better look */
    body {
        background-color: #f0f2f6;
    }
    
    
</style>
"""
st.markdown(hide_pages_css, unsafe_allow_html=True)

# GATE CSE subjects
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

# Dummy user profile for quiz generation
dummy_user_profile = {
    "user_id": "test_user_01",
    "cognitive_skill_weaknesses": ["Mathematical-Reasoning", "Analytical-Multi-Step"],
    "mastery_scores": {
        "Dynamic Programming": 45.0
    }
}

# Initialize session states
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "userdata" not in st.session_state:
    st.session_state.userdata = {}
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = "none"
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "last_question_switch_time" not in st.session_state:
    st.session_state.last_question_switch_time = time.time()

# Function to initialize quiz data with dummy if not set
def initialize_quiz_data():
    if not st.session_state.quiz_data:
        st.session_state.quiz_data = {
            "questions": [
                {
                    "question_id": "DS_TREE_01",
                    "question_text": "What is the maximum number of nodes in a binary tree of height h? (Assume height of a tree with a single node is 0)",
                    "options": ["2^h - 1", "2^(h+1) - 1", "2^h", "h+1"],
                    "correct_answer_index": 1,
                    "hint": "The formula involves a sum of powers of 2, starting from 2^0 up to 2^h.",
                    "explanation": "A full binary tree of height h has 2^(h+1) - 1 nodes."
                },
                {
                    "question_id": "ALGO_GRAPH_02",
                    "question_text": "Which algorithm is used to find the shortest path in an unweighted graph?",
                    "options": ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Breadth-First Search (BFS)", "Depth-First Search (DFS)"],
                    "correct_answer_index": 2,
                    "hint": "Think about which traversal algorithm explores layer by layer, which is ideal for finding the shortest path in terms of number of edges.",
                    "explanation": "BFS is used for shortest path in unweighted graphs as it explores level by level."
                },
                {
                    "question_id": "OS_CPU_03",
                    "question_text": "Which of the following scheduling algorithms can cause starvation of low-priority processes?",
                    "options": ["First-Come, First-Served", "Priority Scheduling", "Round Robin", "Shortest Remaining Time First"],
                    "correct_answer_index": 1,
                    "hint": "Starvation occurs when a process is perpetually denied necessary resources. Which algorithm strictly favors one group of processes over another?",
                    "explanation": "Priority Scheduling can lead to starvation if higher priority processes keep arriving."
                },
                {
                    "question_id": "CN_LAYERS_04",
                    "question_text": "The Physical Layer of the OSI model is responsible for:",
                    "options": ["Routing packets", "Error detection and correction", "Bit-by-bit delivery over a physical medium", "Process-to-process delivery"],
                    "correct_answer_index": 2,
                    "hint": "This is the lowest layer of the OSI model, dealing with the raw physical connection.",
                    "explanation": "The Physical Layer handles the transmission of raw bits over a physical medium."
                },
                {
                    "question_id": "DB_NORMAL_05",
                    "question_text": "A relation is in 2NF if it is in 1NF and...",
                    "options": ["all attributes are dependent on the primary key.", "no transitive dependencies exist.", "it has no multi-valued attributes.", "all non-key attributes are fully functionally dependent on the primary key."],
                    "correct_answer_index": 3,
                    "hint": "2NF specifically deals with the problem of partial dependencies, where a non-key attribute depends on only a part of a composite primary key.",
                    "explanation": "2NF eliminates partial dependencies on the primary key."
                }
            ]
        }
    for item in st.session_state.quiz_data["questions"]:
        if 'user_answer_index' not in item:
            item['user_answer_index'] = None
        if 'status' not in item:
            item['status'] = "unanswered"
        if 'time_spent_seconds' not in item:
            item['time_spent_seconds'] = 0.0

# Utility function for time tracking
def update_time_spent():
    time_spent = time.time() - st.session_state.last_question_switch_time
    previous_index = st.session_state.get('previous_question_index', st.session_state.current_question_index)
    st.session_state.quiz_data["questions"][previous_index]['time_spent_seconds'] += time_spent
    st.session_state.last_question_switch_time = time.time()

# Confirmation dialog for submission
@st.dialog("Are you sure you want to submit?")
def confirm_submit():
    st.write("Do you really want to submit the quiz?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Submit"):
            update_time_spent()
            for q in st.session_state.quiz_data["questions"]:
                if q['user_answer_index'] == q['correct_answer_index']:
                    q['status'] = 'correct'
                else:
                    q['status'] = 'incorrect'
            st.session_state.quiz_submitted = True
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            st.rerun()

# Main logic based on current_page
if st.session_state.current_page == "login":
    st.title("Clurious")
    st.subheader("AI to help you in every Exam")

    with st.form("exam"):
        name = st.text_input("Enter Your Name")
        exam_name = st.selectbox("Choose Your exam", ["None", "GATE CSE"])
        if st.form_submit_button("Submit", type="primary"):
            if name and exam_name != "None":
                st.session_state.userdata["name"] = name
                st.session_state.userdata["exam"] = exam_name
                st.session_state.current_page = "home"
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
    st.write("<p style='text-align:center'>Made with 💖 by Dipanshu Garg </p>", unsafe_allow_html=True)

elif st.session_state.current_page == "home":
    st.title("Clurious")
    st.write(f"Welcome {st.session_state.userdata['name']} \n Target Exam: {st.session_state.userdata['exam']}")
    st.divider()
    if st.button("Give Quiz", use_container_width=True, type="primary"):
        st.session_state.quiz_state = "create"
        st.session_state.current_page = "quiz_design"
        st.rerun()

    # Additional options can be added here (wrong questions, build foundations, etc.)

    st.divider()
    if st.button("Logout"):
        st.session_state.current_page = "login"
        st.rerun()

elif st.session_state.current_page == "quiz_design":
    st.header("Clurious")
    st.subheader("Design Your Custom Quiz")

    x,y = st.tabs(["Full Syllabus","Custom"])

    with x:
    # if quiz_type == "Full Syllabus":
        with st.form("full_syllabus_form"):
            numberQues_full = st.number_input("Number of Questions", min_value=1, max_value=5, value=5, help="Number of Question can be maximum 5")
            Mode = st.select_slider("Select the Level of Quiz", ["Easy", "Medium", "Hard"], value="Medium")
            if st.form_submit_button("🚀 Generate Full Syllabus Quiz"):
                st.success("Quiz parameters received! Generating your quiz...")
                quiz_info = {"subject/topic": "Full Syllabus", "Num ques": numberQues_full, "difficulty": Mode}
                with st.spinner("Please Wait"):
                    st.session_state.quiz_data = quiz_gen.generate_quiz(dummy_user_profile, quiz_info)
                st.session_state.current_page = "quiz_take"
                initialize_quiz_data()  # Ensure initialization
                st.rerun()

    # elif quiz_type == "Custom":
    with y:
        with st.form("custom_quiz_form"):
            subject_name = st.multiselect("Choose Subjects", gate_cse_subjects, help="You can select Multiple Subjects")
            numberQues_custom = st.number_input("Number of Questions", min_value=1, max_value=5, value=5, help="Number of Question can be maximum 5")
            Mode = st.select_slider("Select the Level of Quiz", ["Easy", "Medium", "Hard"], value="Medium")
            if st.form_submit_button("🚀 Generate Custom Quiz"):
                if not subject_name:
                    st.error("Please select at least one subject for a custom quiz.")
                else:
                    st.success("Quiz parameters received! Generating your quiz...")
                    quiz_info = {"subject/topic": subject_name, "Num ques": numberQues_custom, "difficulty": Mode}
                    with st.spinner("Please Wait"):
                        st.session_state.quiz_data = quiz_gen.generate_quiz(dummy_user_profile, quiz_info)
                    st.session_state.current_page = "quiz_take"
                    initialize_quiz_data()  # Ensure initialization
                    st.rerun()

    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()

elif st.session_state.current_page == "quiz_take":
    initialize_quiz_data()

    if st.session_state.quiz_submitted:
        st.session_state.current_page = "results"
        st.rerun()

    # Sidebar for navigation & progress
    with st.sidebar:
        st.title("Clurious Navigator")
        st.write("---")

        st.subheader("Time Elapsed")
        st.markdown("<div id='live-timer' class='live-display' style='font-size: 1.75rem; font-weight: 600;'>00:00</div>", unsafe_allow_html=True)

        start_time_ms = int(st.session_state.start_time * 1000)
        live_update_js = f"""
        <script>
        var startTime = {start_time_ms};
        function updateTimer() {{
            var now = new Date().getTime();
            var distance = now - startTime;
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            var timerElement = window.parent.document.getElementById('live-timer');
            if (timerElement) {{
                timerElement.textContent = minutes + ":" + seconds;
            }}
            setTimeout(updateTimer, 1000);
        }}
        
        updateTimer();
        </script>
        """
        html(live_update_js, height=0)

        total_questions = len(st.session_state.quiz_data["questions"])
        answered_questions = sum(1 for q in st.session_state.quiz_data["questions"] if q['user_answer_index'] is not None)

        st.subheader("Question Palette")
        
        cols = st.columns(2)
        for i in range(total_questions):
            with cols[i % 2]:
                q_data = st.session_state.quiz_data["questions"][i]
                def on_nav_click(new_index):
                    st.session_state.previous_question_index = st.session_state.current_question_index
                    update_time_spent()
                    st.session_state.current_question_index = new_index

                if st.session_state.current_question_index == i:
                    if q_data['user_answer_index'] is not None:
                        st.button(f"✅ Q {i+1}", key=f"nav_{i}", use_container_width=True, type="primary")
                    else:
                        st.button(f"Q {i+1}", key=f"nav_{i}", use_container_width=True, type="primary")
                elif q_data['user_answer_index'] is not None:
                    st.button(f"✅ Q {i+1}", key=f"nav_{i}", use_container_width=True, on_click=on_nav_click, args=(i,))
                else:
                    st.button(f"Q {i+1}", key=f"nav_{i}", use_container_width=True, on_click=on_nav_click, args=(i,))

        st.write("---")
        if st.button("Exit Quiz 🚪", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

    # Main quiz content
    st.title("Clurious Micro-Quiz")
    st.progress(answered_questions / total_questions, text=f"{answered_questions} of {total_questions} Answered")
    st.write("---")

    index = st.session_state.current_question_index
    question_data = st.session_state.quiz_data["questions"][index]
    
    with st.container(border=True):
        st.subheader(f"Question {index + 1}")
        st.markdown(f"**{question_data['question_text']}**")

        user_answer_index = st.radio(
            "Choose your answer:",
            options=range(len(question_data['options'])),
            format_func=lambda i: question_data['options'][i],
            index=question_data['user_answer_index'],
            key=f"q_{question_data['question_id']}"
        )
        
        if user_answer_index is not None and st.session_state.quiz_data["questions"][index]['user_answer_index'] != user_answer_index:
            st.session_state.quiz_data["questions"][index]['user_answer_index'] = user_answer_index
            st.rerun()

        hint, clr = st.columns(2)
        if question_data['user_answer_index'] is not None:
            if clr.button("Clear Selection 🗑️"):
                st.session_state.quiz_data["questions"][index]['user_answer_index'] = None
                st.rerun()
        st.write("")
        if hint.button("💡 Hint"):
            st.info(question_data['hint'])

    st.write("---")

    def on_nav_button_click(direction):
        st.session_state.previous_question_index = st.session_state.current_question_index
        update_time_spent()
        st.session_state.current_question_index += direction

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(index == 0), on_click=on_nav_button_click, args=(-1,)):
            pass

    with col3:
        if st.button("Next ➡️", use_container_width=True, disabled=(index >= total_questions - 1), on_click=on_nav_button_click, args=(1,)):
            pass
    
    st.write("")
    
    if st.button("Submit Quiz ✅", type="primary", use_container_width=True):
        confirm_submit()

elif st.session_state.current_page == "results":
    st.title("🏆 Clurious Quiz Results")
    st.write("---")
    with st.sidebar:
        if st.button("Home"):
            st.session_state.current_page = "home"
            st.session_state.quiz_submitted = False
            st.rerun()

    correct_answers = sum(1 for q in st.session_state.quiz_data["questions"] if q['status'] == 'correct')
    score = (correct_answers / len(st.session_state.quiz_data["questions"])) * 100
    total_time = sum(q['time_spent_seconds'] for q in st.session_state.quiz_data['questions'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", f"{score:.2f}%")
    with col2:
        st.metric("Correct Answers", f"{correct_answers} / {len(st.session_state.quiz_data['questions'])}")
    with col3:
        st.metric("Total Time", f"{int(total_time // 60)}m {int(total_time % 60)}s")

    st.progress(score / 100)

    st.write("---")
    st.subheader("Detailed Review:")
    for i, q in enumerate(st.session_state.quiz_data["questions"]):
        with st.expander(f"**Question {i+1}: { 'Correct ✅' if q['status'] == 'correct' else 'Incorrect ❌'}**"):
            st.markdown(f"**{q['question_text']}**")
            user_answer = q['options'][q['user_answer_index']] if q['user_answer_index'] is not None else "Not Answered"
            correct_answer = q['options'][q['correct_answer_index']]
            
            time_spent = q['time_spent_seconds']
            st.caption(f"Time spent on this question: {int(time_spent // 60)}m {int(time_spent % 60)}s")

            if q['status'] == 'correct':
                st.success(f"✔️ Your answer: {user_answer}")
            else:
                st.error(f"❌ Your answer: {user_answer}")
                st.info(f"💡 Correct answer: {correct_answer}")

            st.write(q["explanation"])

    st.write("---")
    st.subheader("Personalized Notes and Analysis")
    st.write(notes_maker.generate_notes(st.session_state.quiz_data))

    # Proper user analysis (cognitive analysis placeholder)
    st.subheader("Cognitive Skill Analysis")
    # This can be expanded with actual analysis logic based on quiz_data
    weaknesses = dummy_user_profile["cognitive_skill_weaknesses"]
    mastery = dummy_user_profile["mastery_scores"]
    st.write("Based on your performance:")
    st.write(f"- Weaknesses identified: {', '.join(weaknesses)}")
    for topic, score in mastery.items():
        st.write(f"- Mastery in {topic}: {score}%")
    st.info("Recommendations: Focus on multi-step analytical problems and revise Dynamic Programming concepts.")