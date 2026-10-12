
import re


BANNED_WORDS = {
    "idiot",
    "stupid",
    "moron",
    "damn",
    "shit",
    "fuck",
}

AGGRESSIVE_PHRASES = {
    "i will hurt you",
    "you deserve to suffer",
    "i hate you",
    "shut up",
}


def moderate_content(content: str) -> list[str]:
    """
    Return all moderation reasons.

    An empty list means the content passed moderation.
    """
    reasons = []

    normalized_content = content.casefold()
    words = set(re.findall(r"\b\w+\b", normalized_content))

    # Minimum content length
    if len(content) < 50:
        reasons.append(
            "Content must contain at least 50 characters."
        )

    # Maximum content length
    if len(content) > 2000:
        reasons.append(
            "Content must not exceed 2000 characters."
        )

    # Banned word detection
    detected_words = sorted(words.intersection(BANNED_WORDS))

    if detected_words:
        reasons.append(
            "Banned words detected: "
            + ", ".join(detected_words)
            + "."
        )

    # ALL-CAPS detection
    letters = [char for char in content if char.isalpha()]

    if len(letters) >= 5 and all(char.isupper() for char in letters):
        reasons.append(
            "Content appears to use an aggressive ALL-CAPS tone."
        )

    # Aggressive phrase detection
    detected_phrases = [
        phrase
        for phrase in AGGRESSIVE_PHRASES
        if phrase in normalized_content
    ]

    if detected_phrases:
        reasons.append(
            "Aggressive language detected: "
            + ", ".join(detected_phrases)
            + "."
        )

    return reasons
