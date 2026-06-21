# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List
from botbuilder.core import (
    ConversationState,
    MessageFactory,
    UserState,
    TurnContext,
)
from botbuilder.schema import ChannelAccount

from .listening_bot import ListeningBot, INTRO_TEXT


class WelcomeBot(ListeningBot):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
    ):
        super(WelcomeBot, self).__init__(conversation_state, user_state)

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            # Greet anyone that was not the target (recipient) of this message.
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(f"Hi {member.name}. " + INTRO_TEXT)
                )
