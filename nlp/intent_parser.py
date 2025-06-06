import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Or set it directly

system_prompt = """
You are Sofi AI, an intelligent assistant for Nigerian users.
You understand when a user wants to perform actions like sending money, buying airtime, checking balance, etc.
Return a JSON with this format:

{
  "intent": "intent_name",
  "details": {
    ...
  }
}

If the user wants to send money, extract:
- amount
- recipient_name
- account_number
- bank
- narration (if present)

If it's just a question or message, return:
{ "intent": "general_chat" }

Always respond in valid JSON.
"""

def extract_intent(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        reply = response.choices[0].message.content.strip()
        return reply  # JSON string — parse in main.py
    except Exception as e:
        return '{"intent": "general_chat", "error": "%s"}' % str(e)
