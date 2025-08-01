#client.py
import subprocess

def call_ollama_model(user_prompt):
    print("Sending prompt to Ollama...")
    
    system_prompt = f"""
You are a task instruction generator for car rental automation testing.

Your job is to convert the user's natural language prompt into a strict JSON instruction based on the intent.

Use only one of the following formats:

1. For searching cars:
{{
  "action": "search_car",
  "query": "BMW"
}}

2. For filling booking form:
{{
  "action": "fill_booking_form",
  "form_data": {{
    "name": "Keerthana",
    "email": "keer@example.com",
    "start_date": "2025-08-01",
    "end_date": "2025-08-07",
    "car_type": "VAN",
    "cdw": true,
    "terms": true
  }}
}}

3. For submitting booking:
{{ "action": "submit_booking" }}

4. For resetting form:
{{ "action": "reset_form" }}

5. For navigating to a section:
{{ "action": "navigate_to_section", "section": "#cars" }}

6. For testing contact links:
{{ "action": "test_contact_links" }}

7. For checking pricing:
{{ "action": "check_pricing", "car_type": "Luxury" }}

8. For validating empty form:
{{ "action": "validate_empty_form" }}

9. For checking car details:
{{ "action": "check_car_details", "car_type": "SUV" }}

Now read the user's instruction below and reply **only** with a valid JSON object matching one of the above formats. Do not add any explanation or comments.

If dates or car type are not mentioned, you can use default values.

User Instruction: {user_prompt}
""" 
    result = subprocess.run(
        ["ollama", "run", "tinyllama", system_prompt],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    print("Response received from Ollama.")
    return result.stdout.strip()

