import streamlit as st
import time
from streamlit.components.v1 import html
from models import notes_maker

# --- PAGE CONFIGURATION & STYLING ---
# This sets the page to a wide layout and a custom theme.
st.set_page_config(
    page_title="Clurious Quiz",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for a more beautiful and branded look
# This creates the "focus mode" you want for the quiz.
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


# --- 1. SETUP & DUMMY DATA ---
def initialize_quiz_state():
    """Initializes the session state for the quiz."""
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = [
            # ... (Dummy data remains the same) ...
            {
                "question_id": "DS_TREE_01",
                "question_text": "What is the maximum number of nodes in a binary tree of height h? (Assume height of a tree with a single node is 0)",
                "options": ["2^h - 1", "2^(h+1) - 1", "2^h", "h+1"],
                "correct_answer_index": 1,
                "hint": "The formula involves a sum of powers of 2, starting from 2^0 up to 2^h."
            },
            {
                "question_id": "ALGO_GRAPH_02",
                "question_text": "Which algorithm is used to find the shortest path in an unweighted graph?",
                "options": ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Breadth-First Search (BFS)", "Depth-First Search (DFS)"],
                "correct_answer_index": 2,
                "hint": "Think about which traversal algorithm explores layer by layer, which is ideal for finding the shortest path in terms of number of edges."
            },
            {
                "question_id": "OS_CPU_03",
                "question_text": "Which of the following scheduling algorithms can cause starvation of low-priority processes?",
                "options": ["First-Come, First-Served", "Priority Scheduling", "Round Robin", "Shortest Remaining Time First"],
                "correct_answer_index": 1,
                "hint": "Starvation occurs when a process is perpetually denied necessary resources. Which algorithm strictly favors one group of processes over another?"
            },
            {
                "question_id": "CN_LAYERS_04",
                "question_text": "The Physical Layer of the OSI model is responsible for:",
                "options": ["Routing packets", "Error detection and correction", "Bit-by-bit delivery over a physical medium", "Process-to-process delivery"],
                "correct_answer_index": 2,
                "hint": "This is the lowest layer of the OSI model, dealing with the raw physical connection."
            },
            {
                "question_id": "DB_NORMAL_05",
                "question_text": "A relation is in 2NF if it is in 1NF and...",
                "options": ["all attributes are dependent on the primary key.", "no transitive dependencies exist.", "it has no multi-valued attributes.", "all non-key attributes are fully functionally dependent on the primary key."],
                "correct_answer_index": 3,
                "hint": "2NF specifically deals with the problem of partial dependencies, where a non-key attribute depends on only a part of a composite primary key."
            },
            {
                "question_id": "DS_TREE_01",
                "question_text": "What is the maximum number of nodes in a binary tree of height h? (Assume height of a tree with a single node is 0)",
                "options": ["2^h - 1", "2^(h+1) - 1", "2^h", "h+1"],
                "correct_answer_index": 1,
                "hint": "The formula involves a sum of powers of 2, starting from 2^0 up to 2^h."
            },
            {
                "question_id": "ALGO_GRAPH_02",
                "question_text": "Which algorithm is used to find the shortest path in an unweighted graph?",
                "options": ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Breadth-First Search (BFS)", "Depth-First Search (DFS)"],
                "correct_answer_index": 2,
                "hint": "Think about which traversal algorithm explores layer by layer, which is ideal for finding the shortest path in terms of number of edges."
            },
            {
                "question_id": "OS_CPU_03",
                "question_text": "Which of the following scheduling algorithms can cause starvation of low-priority processes?",
                "options": ["First-Come, First-Served", "Priority Scheduling", "Round Robin", "Shortest Remaining Time First"],
                "correct_answer_index": 1,
                "hint": "Starvation occurs when a process is perpetually denied necessary resources. Which algorithm strictly favors one group of processes over another?"
            },
            {
                "question_id": "CN_LAYERS_04",
                "question_text": "The Physical Layer of the OSI model is responsible for:",
                "options": ["Routing packets", "Error detection and correction", "Bit-by-bit delivery over a physical medium", "Process-to-process delivery"],
                "correct_answer_index": 2,
                "hint": "This is the lowest layer of the OSI model, dealing with the raw physical connection."
            },
            {
                "question_id": "DB_NORMAL_05",
                "question_text": "A relation is in 2NF if it is in 1NF and...",
                "options": ["all attributes are dependent on the primary key.", "no transitive dependencies exist.", "it has no multi-valued attributes.", "all non-key attributes are fully functionally dependent on the primary key."],
                "correct_answer_index": 3,
                "hint": "2NF specifically deals with the problem of partial dependencies, where a non-key attribute depends on only a part of a composite primary key."
            }
        ]
    # Robustly initialize keys for each question on every run
    for item in st.session_state.quiz_data["questions"]:
        if 'user_answer_index' not in item:
            item['user_answer_index'] = None
        if 'status' not in item:
            item['status'] = "unanswered"
        # NEW: Key to store time spent on each question
        if 'time_spent_seconds' not in item:
            item['time_spent_seconds'] = 0.0

    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
        
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
    
    # NEW: Key to track when the user switched to the current question
    if 'last_question_switch_time' not in st.session_state:
        st.session_state.last_question_switch_time = time.time()


# --- UTILITY FUNCTION FOR TIME TRACKING ---
def _update_time_spent():
    """Calculates time spent on the previous question and updates the state."""
    time_spent = time.time() - st.session_state.last_question_switch_time
    # This ensures we only update the time for the question that was being viewed
    previous_index = st.session_state.get('previous_question_index', st.session_state.current_question_index)
    st.session_state.quiz_data["questions"][previous_index]['time_spent_seconds'] += time_spent
    st.session_state.last_question_switch_time = time.time()


# Call the initialization function at the start of the script
initialize_quiz_state()



@st.dialog("Are you sure you want to submit?")
def confirm_submit():
    st.write("Are you really want to submit the quiz ? ")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Submit"):
            # Record time for the final question before submitting
            st.session_state.previous_question_index = st.session_state.current_question_index
            _update_time_spent() 
            for q in st.session_state.quiz_data["questions"]:
                if q['user_answer_index'] == q['correct_answer_index']:
                    q['status'] = 'correct'
                else:
                    q['status'] = 'incorrect'
            st.session_state.quiz_submitted = True
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            st.session_state["submitted"] = False
            st.rerun()
# --- THE QUIZ INTERFACE ---

if st.session_state.quiz_submitted:
    # --- DISPLAY RESULTS ---
    st.title("🏆 Clurious Quiz Results")
    st.write("---")
    with st.sidebar:
        if st.button("Home"):
            st.switch_page("main.py")
            st.session_state.quiz_submitted = False
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
    st.write(notes_maker.generate_notes(st.session_state.quiz_data))
    #  update the user profile for the next outcome :) 
    
        # got the coginitive analysis and show and show the home button  :) 

else:
    # --- SIDEBAR FOR NAVIGATION & PROGRESS ---
    with st.sidebar:
        st.title("Clurious Navigator")
        st.write("---")

        # --- LIVE RUNNING CLOCK (Using JavaScript) ---
        # st.subheader("Current Time")
        # st.markdown("<div id='live-clock' class='live-display'></div>", unsafe_allow_html=True)
        
        # --- LIVE TIMER (Using JavaScript) ---
        st.subheader("Time Elapsed")
        st.markdown("<div id='live-timer' class='live-display' style='font-size: 1.75rem; font-weight: 600;'>00:00</div>", unsafe_allow_html=True)
        
        start_time_ms = int(st.session_state.start_time * 1000)
        live_update_js = f"""
        <script>
        function updateClock() {{
            var now = new Date();
            var clockElement = window.parent.document.getElementById('live-clock');
            if (clockElement) {{
                clockElement.textContent = now.toLocaleTimeString('en-US');
            }}
            setTimeout(updateClock, 1000);
        }}

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
        
        updateClock();
        updateTimer();
        </script>
        """
        html(live_update_js, height=0)
        
        total_questions = len(st.session_state.quiz_data["questions"])
        answered_questions = sum(1 for q in st.session_state.quiz_data["questions"] if q['user_answer_index'] is not None)
        # st.metric("Answered", f"{answered_questions} / {total_questions}")

        st.subheader("Question Palette")
        
        cols = st.columns(2)
        for i in range(total_questions):
            with cols[i % 2]:
                q_data = st.session_state.quiz_data["questions"][i]
                def on_nav_click(new_index):
                    # Store the current index before updating, to correctly calculate time spent
                    st.session_state.previous_question_index = st.session_state.current_question_index
                    _update_time_spent()
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
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("You have exited the quiz. Please refresh to start a new one.")
            st.switch_page("main.py")



    # --- MAIN CONTENT AREA ---
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

        # --- ADD THIS BLOCK FOR THE CLEAR BUTTON ---
        # This button only appears if an answer has been selected.
        hint,clr = st.columns(2)

        if question_data['user_answer_index'] is not None:
            if clr.button("Clear Selection 🗑️"):
                # Set the answer for the current question back to None
                st.session_state.quiz_data["questions"][index]['user_answer_index'] = None
                # Rerun the app to reflect the change immediately
                st.rerun()
        # --- END OF BLOCK ---
        st.write("")
        if hint.button("💡 Hint"):
            st.info(question_data['hint'])
            #  changing the tag that hint has been used :)

    st.write("---")

    def on_nav_button_click(direction):
        st.session_state.previous_question_index = st.session_state.current_question_index
        _update_time_spent()
        st.session_state.current_question_index += direction

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(index == 0), on_click=on_nav_button_click, args=(-1,)):
            pass

    with col3:
        if st.button("Next ➡️", use_container_width=True, disabled=(index >= total_questions - 1), on_click=on_nav_button_click, args=(1,)):
            pass
    
    st.write("")
    
    # if answered_questions == total_questions:
    if st.button("Submit Quiz ✅", type="primary", use_container_width=True):
        confirm_submit()
        st.stop()
        

