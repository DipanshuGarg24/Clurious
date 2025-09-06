import google.generativeai as genai
import json
import time

# --- 1. Configuration ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-1.5-pro-latest"
except (KeyError, FileNotFoundError):
    # This allows the file to be run even without an API key for testing UI
    print("Warning: API Key not found. AI features will be disabled.")
    MODEL = None


# --- 2. Helper Functions for Data Handling ---
def _load_user_profile(file_path: str = 'user.json') -> dict:
    """Loads the user's current profile from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {} # Return an empty profile if it's a new user

def _save_user_profile(profile_data: dict, file_path: str = 'user.json'):
    """Saves the updated user profile to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(profile_data, f, indent=2)


# --- 3. The Core Logic (The "Nurse" + "Doctor") ---

def _calculate_updated_metrics(old_profile: dict, quiz_data: dict) -> dict:
    """
    (The Nurse) Calculates the new user metrics based on quiz performance.
    NO AI is used here - this is fast, deterministic math.
    """
    new_profile = old_profile.copy()
    
    # Example Logic: Update Mastery Score with a weighted average
    weakest_topic = quiz_data['ai_analysis']['performance_highlights']['weakest_topic']
    strongest_topic = quiz_data['ai_analysis']['performance_highlights']['strongest_topic']
    
    # Simulate score changes based on this quiz
    # A real implementation would be more complex
    if weakest_topic in new_profile['mastery_scores']:
        new_profile['mastery_scores'][weakest_topic] = round(new_profile['mastery_scores'][weakest_topic] * 0.8 + 70.0 * 0.2, 1)
    
    if strongest_topic in new_profile['mastery_scores']:
         new_profile['mastery_scores'][strongest_topic] = round(new_profile['mastery_scores'][strongest_topic] * 0.8 + 95.0 * 0.2, 1)

    # Example: Update cognitive skill fingerprint
    new_profile['cognitive_skill_fingerprint']['Mathematical-Reasoning'] = round(new_profile['cognitive_skill_fingerprint']['Mathematical-Reasoning'] * 0.8 + 55.0 * 0.2, 1)

    return new_profile


def _generate_profile_update_insight(old_profile: dict, new_profile: dict) -> str:
    """
    (The Doctor) Calls an LLM to generate a human-like summary of the
    user's progress by comparing the old and new profiles.
    """
    if not MODEL:
        return "AI insight disabled. API key not found."

    prompt = f"""
# ROLE & GOAL
You are an expert GATE CSE learning coach. Your goal is to analyze a student's progress by comparing their profile before and after a quiz. You need to provide a concise, encouraging summary of the most important changes.

# CONTEXT: STUDENT'S PROGRESS
- **Old Profile Snapshot:** {json.dumps(old_profile)}
- **New Profile Snapshot (After Quiz):** {json.dumps(new_profile)}

# TASK
Based on the change from the old to the new profile, write a short, human-like summary (2-3 sentences) for the user. Highlight one key improvement and one area that still needs focus.

# OUTPUT FORMAT
A single paragraph of encouraging text.
"""
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"ERROR: AI insight generation failed: {e}")
        return "Could not generate AI insight at this time."


# --- 4. The Main Orchestrator Function ---
def update_user_profile(quiz_data: dict):
    """
    The main public function for this module. It orchestrates the entire
    profile update process.
    """
    print("LOG: Starting user profile update...")
    
    # 1. Load the user's state before the quiz
    old_profile = _load_user_profile()
    if not old_profile:
        return {"error": "User profile not found."}

    # 2. (Nurse) Calculate the new numerical metrics
    updated_profile_data = _calculate_updated_metrics(old_profile, quiz_data)
    
    # 3. (Doctor) Call the LLM to get a qualitative summary of the changes
    ai_insight_text = _generate_profile_update_insight(old_profile, updated_profile_data)
    
    # 4. Save the new profile to persist the changes
    _save_user_profile(updated_profile_data)
    print("LOG: User profile successfully updated and saved.")
    
    # 5. Return the complete package for the UI
    return {
        "old_profile_data": old_profile,
        "updated_profile_data": updated_profile_data,
        "ai_insight_text": ai_insight_text
    }
