import os
from dotenv import load_dotenv
from google import genai
from database import getUserData
import json
from datetime import datetime, timedelta

# Initialize Gemini AI Client

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_TOKEN'))


async def askAItoAnswer(tgID, userMessage, history=''):
    """Communicates with Gemini AI to parse user intent and return structured JSON."""
    data = getUserData(tgID)
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    after_tomorrow = today + timedelta(days=2)

    # System instructions for the AI to ensure consistent JSON output
    base_rules = f"""
            RULES:
            1. DATA RULE: If Name, Phone, or City exists in the "CONTEXT", fill the "data" block. 
               Do not leave them null if information is available!
            2. LOGIC: If user mentions a day (e.g., "Saturday"), calculate the date based on days:
                Today is {today.strftime('%d.%m.%Y, %A')}.
                Tomorrow is {tomorrow.strftime('%d.%m.%Y')}.
                After tomorrow is {after_tomorrow.strftime('%d.%m.%Y')}..
            3. IS_COMPLETE: Set to true only if ALL fields (name, phone, city, date) are filled.
            4. NORMALIZATION: All city names MUST be in the nominative case (називний відмінок).
               Example: "у Києві" -> "Київ", "в Обухові" -> "Обухів", "у Чабанах" -> "Чабани".

            JSON STRUCTURE:
            {{
                "reply": "Your polite response or a question about missing info",
                "is_complete": true/false,
                "data": {{ "name": "name/null", "phone": "number/null", "date": "DD.MM.YYYY/null", "city": "city/null" }}
            }}
        """

    context = f"DB Data: Name: {data.get('name')}, Tel: {data.get('phone')}, City: {data.get('city')}" if data else "New client, no history."

    prompt = f"""
            Role: Epiland Administrator. 
            GOAL: Update the JSON structure.

            CRITICAL INSTRUCTION: 
            - If the user provides NEW information (like a new date), UPDATE the existing field in "data" but KEEP all other fields that were already known from CONTEXT.
            - Do not ask for information that is already present in the CONTEXT unless the user explicitly wants to change it.

            CONTEXT (Already known): {context}
            PREVIOUS MESSAGES: {history}
            USER CURRENT MESSAGE: "{userMessage}"

            {base_rules}
        """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',  # Updated to a stable flash model
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty response from AI")

        # Clean Markdown formatting from AI response to get pure JSON
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"AI/JSON Error: {e}")
        return {
            "reply": "Ой. Мої мізки трохи перегрілись, повторіть будь ласка через декілька хвилин!",
            "is_complete": False,
            "data": {"name": None, "phone": None, "date": None, "city": None}
        }