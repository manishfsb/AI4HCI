# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from google import genai
from config import DefaultConfig

GEMINI_MODEL = "gemini-2.5-flash"

CONFIG = DefaultConfig()
_client = genai.Client(api_key=CONFIG.GEMINI_API_KEY) if CONFIG.GEMINI_API_KEY else None


async def get_ai_response(user_text: str) -> str:
    """Send user_text to Gemini and return its reply, or a fallback message
    if the API key is missing or the call fails."""
    if _client is None:
        return "(AI assistant is not configured; missing GEMINI_API_KEY.)"

    try:
        # DEBUG
        print(f"[ai_helper] Fetching response from {GEMINI_MODEL} for: {user_text!r}")  
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_text,
        )
        return response.text
    except Exception as error:
        #DEBUG
        print(f"[ai_helper] Gemini call failed: {error}") 
        return "Sorry, I couldn't reach the AI service right now."
