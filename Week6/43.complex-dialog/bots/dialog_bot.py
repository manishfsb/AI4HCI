# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import (
    ActivityHandler,
    ConversationState,
    MessageFactory,
    UserState,
    TurnContext,
)
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper

START_TRIGGERS = ("start", "restart", "begin")
QUESTION_STARTERS = (
    "how", "what", "why", "when", "where", "who", "which",
    "can you", "do you", "is it", "are you", "could you",
)

CAPABILITIES_TEXT = (
    "Here's what I can do:\n"
    "- Ask for your name and age\n"
    "- If you're 25 or older, let you pick companies to review\n"
    "- Remember your answers and choices\n"
    "\n"
    "Type 'start' to begin, or 'help' anytime to see this again."
)


def _looks_like_question(text: str) -> bool:
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)


class DialogBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
    ):
        if conversation_state is None:
            raise Exception(
                "[DialogBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        print(f"[on_turn] activity.type={turn_context.activity.type}")
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip().lower()
        print(f"[on_message_activity] received text={text!r}")

        # Global interruption: answer "what can you do" without disturbing
        # whatever waterfall step the dialog is currently waiting on.
        if text in ("help", "capabilities", "what can you do"):
            await turn_context.send_activity(MessageFactory.text(CAPABILITIES_TEXT))
            return

        # Only begin the dialog from idle if the user explicitly asked to start.
        # This frees up "idle" turns to be handled below (e.g. out-of-scope questions)
        # instead of being silently swallowed as the start of the name/age flow.
        is_start_trigger = text in START_TRIGGERS
        dialog_running = await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
            should_begin=is_start_trigger,
        )

        if not dialog_running:
            print(f"[on_message_activity] idle turn, not starting dialog: text={text!r}")
            if _looks_like_question(text):
                await turn_context.send_activity(
                    MessageFactory.text(
                        "I can't answer open-ended questions like that. "
                        "I'm a simple bot, not a general-knowledge assistant.\n\n"
                        + CAPABILITIES_TEXT
                    )
                )
            else:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "I didn't understand that. Type 'start' to begin, "
                        "or 'help' to see what I can do."
                    )
                )
