---
name: sf-script
description: Writes a StoryForge canon (Story Skills project) and adapts it into story.json lines and slides sized to the target duration. Use for stage 2 (canon + script) and Gate 1 rewrites of a StoryForge production.
---

# sf-script

## Inputs
Brief, matching taste rules and checks (verbatim), `library/calibration.json`, the slug.

## Canon (fiction/adaptation)
- Create `stories/<slug>/` with `story-init` conventions (read `.agents/skills/story-init/SKILL.md`).
  Use `scene-craft`, `chapter-writing`, `character-management` only as needed.
- One chapter `chapter-01`, scenes `scenes/chapter-01-scene-NN.md`.
- Check from the canon root: `node /Users/irondev/Desktop/Projects/chauvanhieu/yt/.agents/skills/story-maintenance/scripts/story.js validate` and `links` — clean.
- Factual content has no canon: `canon: null` and `research` notes + claims (see `projects/smoke-test/story.json`).

## Budget
`chars = (target_seconds − Σ pause_after_ms / 1000) × chars_per_s`, where chars are display
characters without spaces and `chars_per_s` is `calibration.speaking_rate[<lang>].chars_per_s`;
without calibration use `references/speaking-rates.md`. Aim within ±5 % of the budget.

## story.json
- Follow `schemas/story.schema.json`; copy structure from `projects/den-ong-sao/story.json` (fiction) or `projects/smoke-test/story.json` (factual). All asset entries start `pending`.
- Lines: written natively in `brief.language`; narration and dialogue on separate lines; short sentences; the first line is a hook within ~1.5 s; punctuation where the voice should pause; `pause_after_ms` 250–600 (longer at scene turns); only allowed tags (`[pause]`, `[pause 500ms]`, `[pause 1.5s]`, the OmniVoice non-verbal tags in `scripts/sflib/text.py`, `[[written|spoken]]`), prefer none.
- Slides: 9:16 → slides of 2–4 s, one drawable moment each; `source` = canon scene id; no two consecutive slides share scene, pose and shot; vary `motion` (static, push_in, pull_out, pan_left, pan_right); `text_placement` lower_third. Visual prompts are written by `sf-visual` rules.
- Write `projects/<slug>/script.md`: story summary, cast table, lines by slide.
- `sf_validate` must print `{"ok": true, "errors": []}`.

## Gate 1
Self-score with `references/rubric.md`; fix every failed item before handing back.
