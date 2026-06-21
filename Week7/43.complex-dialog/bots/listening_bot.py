# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import cast

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    MessageFactory,
    UserState,
    TurnContext,
)
from helpers.ai_helper import get_ai_response
from helpers.safety import looks_like_crisis, is_acknowledgement

# CUX Guide: limit graceful fallbacks to two before escalating (Microsoft, 2021).
FALLBACK_LIMIT = 2
ESCALATION_TEXT = (
    "I'm having trouble responding right now. Feel free to try again in a moment, "
    "or type 'help' to see what this bot is for."
)

INTRO_TEXT = (
    "I'm Sage, a supportive listening companion. I'm not a licensed therapist and "
    "can't give clinical or medical advice; but if you'd like a calm space to talk "
    "something through, I'm here to listen.\n"
    "\n"
    "Type 'help' anytime to see this again."
)

# Crisis-path copy. The "not a therapist" framing is repeated here (not just in
# the welcome/help text) so it is present at the highest-stakes moment. The
# resources are US-specific (see helpers/safety.py for the locale caveat).
CRISIS_TEXT = (
    "It sounds like you're carrying something really painful right now, and I'm "
    "glad you told me. I'm not a therapist and I can't keep you safe on my own, "
    "but you deserve real support. If you're in the US, you can call or text 988 "
    "(Suicide & Crisis Lifeline) to reach someone any time, or call 911 if you "
    "might be in immediate danger. I'm still here with you."
)
CRISIS_HOLD_TEXT = (
    "I'm still here, and I still want you to be safe. Please consider reaching out "
    "to 988 (call or text) or 911 if you're in immediate danger. We can keep "
    "talking once you've had a chance to connect with someone who can help."
)
CRISIS_STEPDOWN_TEXT = (
    "Thank you for telling me that. I'm really glad. I'm here whenever you want "
    "to keep talking."
)


class ListeningBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
    ):
        if conversation_state is None:
            raise Exception(
                "[ListeningBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[ListeningBot]: Missing parameter. user_state is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.fallback_count_accessor = conversation_state.create_property("FallbackCount")
        self.ai_history_accessor = conversation_state.create_property("AiChatHistory")
        # Sticky crisis flag: once latched, Sage stays in the crisis path and
        # does not resume normal small talk until the user acknowledges.
        self.in_crisis_accessor = conversation_state.create_property("InCrisis")

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip().lower()

        if text in ("help", "capabilities", "what can you do"):
            await turn_context.send_activity(MessageFactory.text(INTRO_TEXT))
            return

        # Crisis screen runs on the user's INPUT, before the Gemini call, so
        # resources surface even if the model is unavailable. The keyword screen
        # is a deliberately imperfect safety net (see helpers/safety.py); the
        # Gemini SAFETY_INSTRUCTION is a second layer for what it misses.
        in_crisis = await self.in_crisis_accessor.get(turn_context, lambda: False)
        if looks_like_crisis(text):
            await turn_context.send_activity(MessageFactory.text(CRISIS_TEXT))
            await self.in_crisis_accessor.set(turn_context, True)
            return
        if in_crisis:
            if is_acknowledgement(text):
                await turn_context.send_activity(
                    MessageFactory.text(CRISIS_STEPDOWN_TEXT)
                )
                await self.in_crisis_accessor.set(turn_context, False)
            else:
                await turn_context.send_activity(MessageFactory.text(CRISIS_HOLD_TEXT))
            return

        history = await self.ai_history_accessor.get(turn_context, list)
        ai_reply, is_fallback, history = await get_ai_response(
            turn_context.activity.text, history
        )
        await self.ai_history_accessor.set(turn_context, history)

        # Fallback lifecycle (R3): exactly one message per turn. A successful
        # call resets the *consecutive*-failure streak; the first failure sends
        # an apologetic retry; the second consecutive failure escalates instead
        # (and resets the count). The retry and escalation are mutually
        # exclusive — see the success?/RETRY/ESCALATE branches in the diagram.
        if not is_fallback:
            await self.fallback_count_accessor.set(turn_context, 0)
            await turn_context.send_activity(MessageFactory.text(ai_reply))
            return

        fallback_count = (
            cast(int, await self.fallback_count_accessor.get(turn_context, lambda: 0)) + 1
        )
        if fallback_count >= FALLBACK_LIMIT:
            await self.fallback_count_accessor.set(turn_context, 0)
            await turn_context.send_activity(MessageFactory.text(ESCALATION_TEXT))
        else:
            await self.fallback_count_accessor.set(turn_context, fallback_count)
            await turn_context.send_activity(MessageFactory.text(ai_reply))
