"""Script text handling: expressive tags, display text, caption tokens."""
from __future__ import annotations

import re
import unicodedata

NONVERBAL_TAGS = (
    "laughter", "sigh", "confirmation-en", "question-en", "question-ah", "question-oh",
    "question-ei", "question-yi", "surprise-ah", "surprise-oh", "surprise-wa",
    "surprise-yo", "dissatisfaction-hnn",
)
_PAUSE = r"\[pause(?:\s+\d+(?:\.\d+)?(?:ms|s))?\]"
EXPRESSIVE_RE = re.compile(r"\[(?:" + "|".join(NONVERBAL_TAGS) + r")\]|" + _PAUSE)
OVERRIDE_RE = re.compile(r"\[\[([^\[\]|]+)\|([^\[\]]+)\]\]")
BRACKET_RE = re.compile(r"\[\[[^\]]*\]\]|\[[^\]]*\]")
CLUSTER_LANGS = {"zh", "ja", "th", "lo", "km", "my"}
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.!?;:…。，！？、])")


def invalid_tags(text: str) -> list[str]:
    rest = EXPRESSIVE_RE.sub("", OVERRIDE_RE.sub("", text))
    return BRACKET_RE.findall(rest)


def display_text(text: str) -> str:
    shown = OVERRIDE_RE.sub(lambda m: m.group(1), text)
    shown = EXPRESSIVE_RE.sub(" ", shown)
    shown = re.sub(r"\s+", " ", shown).strip()
    return _SPACE_BEFORE_PUNCT.sub(r"\1", shown)


def uses_clusters(language: str) -> bool:
    return language.split("-")[0].lower() in CLUSTER_LANGS


def _is_punct(ch: str) -> bool:
    return unicodedata.category(ch).startswith("P")


def clusters(text: str) -> list[str]:
    out: list[str] = []
    for ch in unicodedata.normalize("NFC", text):
        if ch.isspace():
            continue
        if out and (unicodedata.category(ch).startswith("M") or _is_punct(ch)):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def tokens(text: str, language: str) -> list[str]:
    shown = display_text(text)
    return clusters(shown) if uses_clusters(language) else shown.split()


def norm(token: str) -> str:
    folded = unicodedata.normalize("NFC", token).casefold()
    return "".join(ch for ch in folded if not _is_punct(ch))
