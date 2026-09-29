---
name: sf-audio
description: Casts StoryForge voices (library, design, clone) and handles voice generation, expressive controls and retakes. Use for stage 6 (voice) and voice-related redos or feedback in a StoryForge production.
---

# sf-audio

## Casting (per cast member, `voice` in story.json)
1. `source: library` + `library_ref` when `library/cast/<ref>/voice.json` exists (`{"profile_id", "instruct"}`) — reuse across videos.
2. `source: design` + `design_prompt`: comma-separated attribute words only, from:
   gender `male|female`; age `child|teenager|young adult|middle-aged|elderly`;
   pitch `very low pitch|low pitch|moderate pitch|high pitch|very high pitch`; optional accent
   (`american accent`, `british accent`, …; leave out for Vietnamese); optional `whisper`.
   Free-form emotion words are not attributes: `/design/describe` drops them and VoiceStudio rejects them in `instruct` (400).
3. `source: clone` + a user-supplied reference clip (strongest control over delivery).
Apply matching audio taste rules (e.g. how young child voices should sound).

## Expressive controls
Punctuation; `[pause]`, `[pause 500ms]`, `[pause 1.5s]`; the 13 OmniVoice non-verbal tags in `scripts/sflib/text.py` (`NONVERBAL_TAGS`) — prefer `[laughter]` and `[sigh]`, the others are language-specific interjections; `[[written|spoken]]` pronunciation overrides; `whisper: true` on a line. Anything else in brackets is spoken literally, and `sf_validate` rejects it.

## Run
Check VoiceStudio (sf-director `references/services.md`), then `uv run scripts/sf_voice.py projects/<slug>`.
- `needs_human` for a line: read `audio.last_error` and `audio.qc`; fix text (punctuation, `[[written|spoken]]`
  for mispronounced words) and re-run with `--only <line id>`.
- Re-cast a voice: change `design_prompt`, run `sf_voice --only <cast id>`.

## Saving a recurring character
When the user asks to keep a voice for later videos, write `library/cast/<ref>/voice.json` with the
member's `profile_id` and `instruct`, and use `source: library` next time.
