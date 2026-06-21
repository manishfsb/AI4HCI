# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Deterministic crisis screening for Sage.

This is a *safety net*, not a reliable classifier. It runs on the user's
incoming message BEFORE the Gemini call so that crisis resources surface even
when the model API is unavailable (a deliberate safety choice: crisis handling
must not depend on the API being up).

Known limitations, stated honestly (cf. Auernhammer, 2020 on harmful
interaction patterns): simple keyword matching misses indirect or paraphrased
ideation (false negatives) and can over-trigger on quoted, hypothetical, or
figurative language (false positives). The Gemini SAFETY_INSTRUCTION acts as a
second, complementary layer for phrasings this screen does not catch.

LOCALE: the crisis resources Sage surfaces (988 / 911) assume a US locale.
"""

import re

# Direct, high-signal phrases. Kept conservative to limit false positives; we
# accept that this list will not catch paraphrased ideation (see module docs).
_CRISIS_PHRASES = (
    "kill myself",
    "killing myself",
    "suicide",
    "suicidal",
    "end my life",
    "ending my life",
    "take my own life",
    "want to die",
    "wanna die",
    "don't want to live",
    "do not want to live",
    "no reason to live",
    "better off dead",
    "self harm",
    "self-harm",
    "hurt myself",
    "harm myself",
    "harming myself",
    "cut myself",
    "kill someone",
    "hurt someone",
    "end it all",
)

# Light-touch tokens that suggest the user has heard the resource and is
# stepping back from the moment, used only to clear a latched crisis state.
_ACK_PHRASES = (
    "i'm safe",
    "i am safe",
    "i'm okay",
    "i am okay",
    "i'm ok",
    "i am ok",
    "feeling better",
    "i'll call",
    "i will call",
    "i'll reach out",
    "thank you",
    "thanks",
)

_CRISIS_RE = re.compile(
    "|".join(re.escape(p) for p in _CRISIS_PHRASES), re.IGNORECASE
)
_ACK_RE = re.compile("|".join(re.escape(p) for p in _ACK_PHRASES), re.IGNORECASE)


def looks_like_crisis(text: str) -> bool:
    """True if the user's message contains direct crisis language."""
    return bool(text) and _CRISIS_RE.search(text) is not None


def is_acknowledgement(text: str) -> bool:
    """True if the message reads as the user acknowledging the crisis resource,
    used to release a latched crisis state."""
    return bool(text) and _ACK_RE.search(text) is not None
