# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from google import genai
from google.genai import types
from config import DefaultConfig

GEMINI_MODEL = "gemini-2.5-flash"

# Keep the last N exchanges (user+model pairs) so token usage stays bounded.
MAX_HISTORY_TURNS = 10

# Persona (stable identity) vs. personality (traits/tone), kept as separate
# fields per the persona/personality distinction in Sun, Zhan & Such (2024).
PERSONA_INSTRUCTION = (
    "Identity: You are Sage, a supportive listening companion in this demo "
    "chatbot (a university HCI course project). You are not a licensed "
    "therapist or medical professional and must not diagnose, treat, or give "
    "clinical advice. You exist so that someone who feels comfortable doing so "
    "has a calm space to talk through what's on their mind."
)
PERSONALITY_INSTRUCTION = (
    "Personality: warm, patient, and unhurried. Primarily listen and reflect "
    "back what the user shares in your own words, validate their feelings, and "
    "ask gentle open-ended follow-up questions. When it seems welcome, you may "
    "offer one simple grounding or coping suggestion (e.g. a breathing "
    "exercise) but don't lecture, give multi-step advice, or rush to 'fix' "
    "the conversation. Keep replies short (1-4 sentences) and avoid sounding "
    "clinical."
)
# Harmful-interaction-pattern safeguard (Auernhammer, 2020): a listening
# persona that invites people to "talk something through" needs an explicit
# crisis path, not just a one-time disclaimer.
SAFETY_INSTRUCTION = (
    "Safety: If the user expresses thoughts of suicide, self-harm, or harming "
    "others, or describes being in immediate danger, gently acknowledge their "
    "pain without minimizing it, then clearly encourage them to reach out to a "
    "crisis line or emergency services right now. For example, in the US: call "
    "or text 988 (Suicide & Crisis Lifeline), or call 911 for immediate danger. "
    "Don't try to talk them out of it yourself, don't diagnose them, and don't "
    "continue the conversation as if it were a normal topic until they've "
    "acknowledged the resource. Outside of these situations, continue "
    "listening as usual."
)

SYSTEM_INSTRUCTION = (
    f"{PERSONA_INSTRUCTION}\n\n{PERSONALITY_INSTRUCTION}\n\n{SAFETY_INSTRUCTION}"
)

CONFIG = DefaultConfig()
_client = genai.Client(api_key=CONFIG.GEMINI_API_KEY) if CONFIG.GEMINI_API_KEY else None


def _trim_history(history: list) -> list:
    max_entries = MAX_HISTORY_TURNS * 2  # one user + one model entry per turn
    return history[-max_entries:]


async def get_ai_response(user_text: str, history: list) -> tuple[str, bool, list]:
    """Send user_text + prior turns to Gemini and return
    (reply_text, is_fallback, updated_history).

    history is a list of {"role": "user"|"model", "parts": [{"text": ...}]}
    entries representing this conversation's exchanges with Sage; callers
    persist it in conversation state so persona/memory survive across turns.
    is_fallback is True when no real model answer was produced (missing API
    key or a failed call); the failed turn is still appended to history so
    Sage's own memory of the exchange stays accurate.
    """
    user_turn = {"role": "user", "parts": [{"text": user_text}]}

    if _client is None:
        reply_text = "(AI assistant is not configured; missing GEMINI_API_KEY.)"
        return reply_text, True, _trim_history(history + [user_turn])

    contents = history + [user_turn]

    try:
        # DEBUG
        print(f"[ai_helper] Fetching response from {GEMINI_MODEL} for: {user_text!r}")
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        reply_text = response.text
        model_turn = {"role": "model", "parts": [{"text": reply_text}]}
        return reply_text, False, _trim_history(contents + [model_turn])
    except Exception as error:
        # DEBUG
        print(f"[ai_helper] Gemini call failed: {error}")
        reply_text = "Sorry, I couldn't reach the AI service right now."
        model_turn = {"role": "model", "parts": [{"text": reply_text}]}
        return reply_text, True, _trim_history(contents + [model_turn])
