from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

user_description = "I had huge headache from 4 hrs"

try:
    prompt = f"""You are a medical symptom extraction assistant.

Analyze the user's description and identify all possible symptoms, health complaints, conditions, or concerns mentioned, even if they are described informally.

Return only a JSON array of symptom names that best match the user's description. Do not wrap in markdown or backticks, just output a valid JSON array.

User Description:
"{user_description}"
"""
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print("Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:")
    print(e)
