# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    MessageFactory,
    UserState,
    TurnContext,
)
from helpers.ai_helper import get_ai_response

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

        history = await self.ai_history_accessor.get(turn_context, list)
        ai_reply, is_fallback, history = await get_ai_response(
            turn_context.activity.text, history
        )
        await self.ai_history_accessor.set(turn_context, history)
        await turn_context.send_activity(MessageFactory.text(ai_reply))

        fallback_count = await self.fallback_count_accessor.get(turn_context, lambda: 0)
        fallback_count = fallback_count + 1 if is_fallback else 0
        await self.fallback_count_accessor.set(turn_context, fallback_count)

        if is_fallback and fallback_count >= FALLBACK_LIMIT:
            await turn_context.send_activity(MessageFactory.text(ESCALATION_TEXT))
            await self.fallback_count_accessor.set(turn_context, 0)
