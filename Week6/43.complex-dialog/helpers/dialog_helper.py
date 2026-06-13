# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import StatePropertyAccessor, TurnContext
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus


class DialogHelper:
    @staticmethod
    async def run_dialog(
        dialog: Dialog,
        turn_context: TurnContext,
        accessor: StatePropertyAccessor,
        should_begin: bool = True,
    ) -> bool:
        """Continue the active dialog, or begin it if idle and `should_begin` is True.

        Returns True if a dialog is now running (continued or begun), False if the
        dialog stack was empty and `should_begin` was False (caller should handle
        the idle turn itself).
        """
        dialog_set = DialogSet(accessor)
        dialog_set.add(dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:
            if not should_begin:
                return False
            await dialog_context.begin_dialog(dialog.id)

        return True
