import streamlit as st
import google.generativeai as genai
import json

# --- 1. Configuration ---
# In a real app, you would get your API key from secrets management
# For Streamlit, st.secrets is the correct way to do this.
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-1.5-pro-latest" # Use a powerful, modern model
except (KeyError, FileNotFoundError):
    st.error("API Key not found. Please set it in your Streamlit secrets.")
    st.stop()


# --- 2. The Main Function (The "Master Teacher") ---
def generate_notes(quiz_results: dict):
    """
    Generates a personalized cheat sheet using the Gemini API, based on the
    questions a user answered incorrectly in a quiz.

    Args:
        quiz_results (dict): The completed quiz data, including user answers.

    Returns:
        str: The generated notes in Markdown format, or an error message.
    """
    print("LOG: Starting notes generation process...")

    # --- Step 1: Identify Weaknesses ---
    # Find all the questions the user got wrong.
    # incorrect_questions = []
    # for q in quiz_results.get("questions", []):
    #     if not q.get("is_correct", True): # Assume correct if key is missing
    #         incorrect_questions.append(q)

    # if not incorrect_questions:
    #     return "Great job! You answered all questions correctly. No specific notes needed for this session."

    # --- Step 2: Dynamic Prompt Generation ---
    # Create a rich context for the LLM using the questions the user failed.
    # This is a form of RAG using the quiz data itself as context.
    
    # We will format the incorrect questions nicely for the prompt.
#     error_context = ""
#     for i, q in enumerate(incorrect_questions):
#         error_context += f"""
# ### Mistake #{i+1}
# - **Question:** {q['question_text']}
# - **User's Answer:** {q['options'][q['user_answer_index']]}
# - **Correct Explanation:** {q['explanation']}
# ---
# """

    prompt = f"""
# ROLE & GOAL
You are an expert GATE CSE tutor who excels at creating ultra-concise, high-impact "cheat sheets" for revision. Your goal is to generate a personalized, quick-reference study note for a student based on the concepts they got wrong in a recent quiz.

# CONTEXT: STUDENT'S MISTAKES
The student made the following answer on the Quiz , i am giving you the quiz data 
{quiz_results}

# TASK
Based on the student's mistakes, generate a personalized cheat sheet in Markdown. For each major concept the student failed, create a "Quick Reference" section. Each section MUST contain only these three things:
1.  **The Key Formula / Rule:** The single most important formula or rule for this concept.
2.  **The Core Logic:** A very brief, 1-2 sentence explanation of the fundamental idea.
3.  **A Personalized Tip:** A short, actionable tip directly related to the kind of mistake the student made.

# OUTPUT FORMAT REQUIREMENTS
Provide your response in clean, well-structured Markdown. The structure must be simple and scannable. Do not add long paragraphs.

## Your Personalized Cheat Sheet
Here are the key takeaways for the topics you struggled with. Review these before your next session!

---

### Concept: [e.g., 0/1 Knapsack Problem]

* **Key Formula:**
    ```
    dp[i][j] = max(dp[i-1][j], v[i] + dp[i-1][j - w[i]])
    ```
* **Core Logic:** For each item, you have two choices: either include it or exclude it. The dynamic programming approach finds the best outcome by comparing these two choices at every step.
* **💡 Personalized Tip:** Your mistake was only considering the "include" case. Always remember to compare it with the "exclude" case (`dp[i-1][j]`) to find the true maximum value.

---

### Concept: [e.g., Coin Change Combinations]

* **Key Rule:**
    ```python
    # To count combinations, loop coins on the outside
    for coin in coins:
        for i from coin to amount:
            dp[i] += dp[i - coin]
    ```
* **Core Logic:** To count unique combinations (not permutations), you build up the solution one coin at a time. This structure prevents re-counting the same set of coins in a different order.
* **💡 Personalized Tip:** You seem to be confusing the logic for permutations with combinations. For combinations, always iterate through your coins in the outer loop to ensure order doesn't matter.
"""

    # --- Step 3: Secure and Robust API Call ---
    try:
        print("LOG: Making API call to Gemini for notes generation...")
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        
        print("LOG: API call successful.")
        return response.text

    except Exception as e:
        st.error(f"An error occurred while generating notes: {e}")
        print(f"ERROR: Exception during Gemini API call: {e}")
        return "Error: Could not generate notes at this time."

# --- 4. Streamlit Test Harness (For standalone testing) ---
if __name__ == "__main__":
    st.title("Clurious Notes Maker - Test Module")

    # --- Dummy Data ---
    # This is the exact quiz data you provided, with simulated user answers added.
    # We will simulate the user getting Q1 and Q4 wrong.
    dummy_quiz_results = {
      "quiz_title": "Dynamic Programming: Recurrence & Optimization",
      "questions": [
        {
          "question_id": "Q1",
          "question_text": "Consider the problem of finding the number of distinct ways to make change for an amount `N`...",
          "options": ["For each `i` from `1` to `N`, `dp[i] = sum...`", "For each `coin` in `C`: For each `i` from `coin` to `N`: `dp[i] += dp[i - coin]`", "For each `i` from `1` to `N`: For each `coin` in `C`: `dp[i] = max...`", "For each `coin` in `C`: For each `i` from `N` down to `coin`: `dp[i] = dp[i - coin]`"],
          "correct_answer_index": 1,
          "hint": "Think about how to avoid counting permutations instead of combinations.",
          "explanation": "Option B correctly implements the iterative approach for counting combinations...",
          "user_answer_index": 0, # User chose A (Wrong)
          "is_correct": False
        },
        {
          "question_id": "Q2",
          "question_text": "Consider the sequence `A = {3, 10, 2, 1, 20}`. Using dynamic programming to find the length of the Longest Increasing Subsequence (LIS)...",
          "options": ["1", "2", "3", "4"],
          "correct_answer_index": 3,
          "hint": "Recall the LIS recurrence: `dp[i] = 1 + max(dp[j])`...",
          "explanation": "Let's compute the `dp` array step-by-step...",
          "user_answer_index": 3, # User chose 4 (Correct)
          "is_correct": True
        },
        {
          "question_id": "Q3",
          "question_text": "A robot is situated at the top-left corner (0,0) of a grid... with the minimum total cost...",
          "options": ["`dp[i][j] = C[i][j] + dp[i-1][j] + dp[i][j-1]`", "`dp[i][j] = min(dp[i-1][j], dp[i][j-1])`", "`dp[i][j] = C[i][j] + min(dp[i-1][j], dp[i][j-1])`", "`dp[i][j] = max(C[i][j], dp[i-1][j], dp[i][j-1])`"],
          "correct_answer_index": 2,
          "hint": "The cost of the current cell is always added.",
          "explanation": "To reach cell `(i, j)`, the robot must have arrived from either the cell directly above it...",
          "user_answer_index": 2, # User chose C (Correct)
          "is_correct": True
        },
        {
          "question_id": "Q4",
          "question_text": "In the 0/1 Knapsack problem... which of the following is the correct recurrence relation...",
          "options": ["`dp[i][j] = dp[i-1][j]` (if `w_i > j`) OR `dp[i][j] = max(dp[i-1][j], v_i + dp[i-1][j - w_i])` (if `w_i <= j`)", "`dp[i][j] = v_i + dp[i-1][j - w_i]` (if `w_i <= j`)", "`dp[i][j] = max(dp[i][j-1], v_i + dp[i-1][j])`", "`dp[i][j] = dp[i-1][j] + dp[i][j-w_i]`"],
          "correct_answer_index": 0,
          "hint": "For each item, you have two mutually exclusive choices: either include it or exclude it.",
          "explanation": "For the `i`-th item and a knapsack capacity `j`, we consider two cases...",
          "user_answer_index": 1, # User chose B (Wrong)
          "is_correct": False
        },
        {
          "question_id": "Q5",
          "question_text": "For the Matrix Chain Multiplication problem... what does `k` represent in this recurrence?",
          "options": ["The index of the matrix `A_k` which is the smallest...", "The index where the subchain `A_i ... A_j` is split...", "The number of matrices in the subchain...", "The minimum number of columns..."],
          "correct_answer_index": 1,
          "hint": "The problem involves finding the optimal way to parenthesize the matrix product.",
          "explanation": "In the Matrix Chain Multiplication problem, `k` represents the 'split point'...",
          "user_answer_index": 1, # User chose B (Correct)
          "is_correct": True
        }
      ]
    }

    st.header("1. Simulated Quiz Results")
    st.write("Simulating a user who got the 'Coin Change' and '0/1 Knapsack' questions wrong.")
    st.json(dummy_quiz_results)

    st.divider()

    st.header("2. Generate Personalized Notes")
    st.write("Click the button below to send the user's mistakes to the Gemini API.")

    if st.button("📝 Generate My Personal Notes"):
        with st.spinner("Your personal tutor is writing your notes..."):
            generated_notes = generate_notes(dummy_quiz_results)
        
        st.header("3. Your Custom Cheat Sheet")
        if generated_notes:
            st.write(generated_notes,unsafe_allow_html=True)
        else:
            st.error("Failed to generate notes.")

