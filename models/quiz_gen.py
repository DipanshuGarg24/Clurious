import streamlit as st
import google.generativeai as genai
import json
import random # Used for selecting RAG examples

# --- 1. Configuration ---
# In a real app, you would get your API key from secrets management
# For Streamlit, st.secrets is the correct way to do this.
try:
    # GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    GOOGLE_API_KEY = "AIzaSyCuuJKwu8krjaoaJ5jjExBYIQj2tDRgNjs"
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-2.5-flash" # Use a powerful, modern model
except (KeyError, FileNotFoundError):
    st.error("API Key not found. Please set it in your Streamlit secrets.")
    st.stop()


# --- 2. RAG Simulation (The "Librarian") ---
# In a real app, this function would connect to your Vector Database.
# For now, it simulates the process by returning hardcoded examples.
def _get_rag_examples_from_db(topic: str, difficulty: str) -> list:
    """
    Simulates retrieving 2-3 relevant question examples from a database
    to provide context to the LLM (Retrieval-Augmented Generation).
    """
    # This is a placeholder. A real implementation would query a vector DB.
    examples = {
        "AVL Trees": [
            '{"question_text": "What is the maximum height difference allowed between two subtrees in an AVL tree?", "correct_answer": "1"}',
            '{"question_text": "Which rotation is performed for a Left-Right (LR) imbalance case in an AVL tree?", "correct_answer": "A left rotation on the left child, followed by a right rotation on the parent."}'
        ],
        "Dynamic Programming": [
            '{"question_text": "What are the two key properties of a problem that suggest dynamic programming is a suitable solution?", "correct_answer": "Overlapping subproblems and optimal substructure."}',
            '{"question_text": "What is the time complexity of the naive recursive solution for the Fibonacci sequence?", "correct_answer": "O(2^n)"}'
        ]
    }
    # Return examples for the given topic, or a default if not found
    return random.sample(examples.get(topic, examples["Dynamic Programming"]), 2)


# --- 3. The Main Function (The "Master Chef") ---
def generate_quiz(user_profile: dict, quiz_ask: dict):
    """
    Generates a personalized quiz using the Gemini API, based on the user's
    profile and specific request.

    Args:
        user_profile (dict): The user's profile, containing their weaknesses.
        quiz_ask (dict): The user's request for the quiz (e.g., topic, num_questions).

    Returns:
        dict: The generated quiz data in the specified JSON format, or None if an error occurs.
    """
    print("LOG: Starting quiz generation process...")
    
    # --- Step 1: Intelligent Constraint Setting ---
    # This is where we use the user's data to create smart constraints.
    # topic = quiz_ask.get("topic", "Default Topic")
    # num_questions = quiz_ask.get("num_questions", 5)
    # difficulty = quiz_ask.get("difficulty", "Medium")

    # # Use the user's profile to add deep personalization to the prompt
    # cognitive_weakness = user_profile.get("cognitive_skill_weaknesses", ["Analytical-Multi-Step"])[0]
    
    # Get RAG examples
    # rag_examples = _get_rag_examples_from_db(topic, difficulty)

    # --- Step 2: Dynamic Prompt Generation ---
    # This is our master prompt. It's detailed, structured, and gives the AI
    # a very clear set of instructions.
    prompt = f"""
# ROLE & GOAL
You are a world-class question designer for the GATE Computer Science (CSE) exam. Your mission is to generate a new, original, high-quality quiz that perfectly targets a student's specific learning needs based on their profile.

# STUDENT PROFILE & QUIZ CONSTRAINTS
user_profile : {user_profile}
quiz_constraints : {quiz_ask}

# OUTPUT FORMAT REQUIREMENTS
You MUST provide your response in a single, clean JSON object. Do not include any text, explanations, or apologies outside of the JSON object. The JSON object must have the following exact structure:
{{
  "quiz_title": "A creative and relevant title for the quiz",
  "questions": [
    {{
      "question_id": "A unique identifier like Q1, Q2, etc.",
      "question_text": "The full, formatted text of the question.",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer_index": 2,
      "hint": "A short, helpful hint that guides the student without giving away the answer.",
      "explanation": "A detailed, step-by-step solution explaining how to arrive at the correct answer and why other options are incorrect.",
      "tags": {{
        "topic": 
        "difficulty": 
        "cognitive_skill_tested": 
      }}
    }}
  ]
}}
"""

    # --- Step 3: Secure and Robust API Call ---
    try:
        print("LOG: Making API call to Gemini...")
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7 # A bit of creativity
        )
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # --- Step 4: Clean and Validate the Output ---
        print("LOG: API call successful. Parsing response.")
        # The API now directly returns a JSON object because of response_mime_type
        quiz_data = json.loads(response.text)

        # Basic validation to ensure the structure is correct
        if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
            print("LOG: Response parsed and validated successfully.")
            return quiz_data
        else:
            st.error("AI returned an empty or invalid quiz structure. Please try again.")
            print("ERROR: Invalid quiz structure from AI.")
            return None

    except Exception as e:
        st.error(f"An error occurred while generating the quiz: {e}")
        print(f"ERROR: Exception during Gemini API call: {e}")
        return None



# --- 4. Streamlit Test Harness (For standalone testing) ---
if __name__ == "__main__":
    st.title("Clurious Quiz Generation Engine - Test Module")

    # --- Dummy Data ---
    # This simulates the data we would have for a real user.
    dummy_user_profile = {
        "user_id": "test_user_01",
        "cognitive_skill_weaknesses": ["Mathematical-Reasoning", "Analytical-Multi-Step"],
        "mastery_scores": {
            "Dynamic Programming": 45.0
        }
    }

    dummy_quiz_ask = {
        "topic": "Dynamic Programming",
        "num_questions": 5, # Keep it low for fast testing
        "difficulty": "Medium"
    }

    st.header("Test Case")
    st.write("Simulating a request for a user weak in 'Mathematical-Reasoning'.")
    st.json({"user_profile": dummy_user_profile, "quiz_ask": dummy_quiz_ask})

    if st.button("🚀 Generate Test Quiz"):
        with st.spinner("Generating quiz... Please wait."):
            generated_quiz = generate_quiz(dummy_user_profile, dummy_quiz_ask)
        
        st.header("Generated Quiz Response")
        if generated_quiz:
            st.success("Quiz generated successfully!")
            st.json(generated_quiz)
        else:
            st.error("Failed to generate quiz. Check the logs for details.")

