---
name: sf-script
description: Writes a StoryForge canon (Story Skills project) and adapts it into viral retention-optimized story.json lines and slides sized to the target duration. Use for stage 2 (canon + script) and Gate 1 rewrites of a StoryForge production.
---

# sf-script

## Inputs
Brief (including `platform_target`: `youtube_shorts` | `tiktok` | `instagram_reels`), matching taste rules and checks (verbatim), `library/calibration.json`, the slug, and references:
- `references/viral-storytelling.md` (Retention spine & But/Therefore escalation)
- `references/hook-archetypes-storyforge.md` (10 AI Hook Archetypes)
- `references/rubric.md` (Gate 1 Rubric: 14 items)

## Viral Scripting Workflow
Before writing, plan the 4 segments of the **Retention Spine**:
1. **Hook Selection:** Pick 1 of the 10 archetypes from `references/hook-archetypes-storyforge.md`. Construct the **3-Layer Hook**:
   - `Verbal Hook`: Line 1 (< 1.5 s of speech, concise, provocative).
   - `Visual Hook`: Slide 1 prompt (frozen action, intense angle, high contrast chiaroscuro).
   - `Text Hook`: On-screen overlay text providing complementary context.
2. **Escalation Engine:** Map the story progression strictly with **"But..."** (obstacle/conflict) and **"Therefore..."** (reaction/consequence) per `references/viral-storytelling.md`. Eliminate all linear "And then..." transitions.
3. **Payoff Delivery:** Ensure the climax/ending resolves the question or tension promised in the hook without clickbait.
4. **Platform-Tuned CTA:** Apply a single-action CTA matching `brief.platform_target` (or seamless loop for Shorts) per `../sf-director/references/platform-tuning.md`.

## Canon (fiction/adaptation)
- Create `stories/<slug>/` with `story-init` conventions (read `.agents/skills/story-init/SKILL.md`).
  Use `scene-craft`, `chapter-writing`, `character-management` only as needed.
- One chapter `chapter-01`, scenes `scenes/chapter-01-scene-NN.md`.
- Check from the canon root: `node /Users/irondev/Desktop/Projects/chauvanhieu/yt/.agents/skills/story-maintenance/scripts/story.js validate` and `links` — clean.
- Factual content has no canon: `canon: null` and `research` notes + claims (see `projects/smoke-test/story.json`).

## Budget
`chars = (target_seconds − Σ pause_after_ms / 1000) × chars_per_s`, where chars are display
characters without spaces and `chars_per_s` is `calibration.speaking_rate[<lang>].chars_per_s` (Vietnamese: ~12.92 chars/s);
without calibration use `references/speaking-rates.md`. Aim within ±5 % of the budget.

## story.json
- Follow `schemas/story.schema.json`; copy structure from `projects/den-ong-sao/story.json` (fiction) or `projects/smoke-test/story.json` (factual). All asset entries start `pending`.
- Metadata: Record `platform_target`, `hook_archetype`, and `text_hook` in the story or project notes.
- Lines: Written natively in `brief.language`; narration and dialogue on separate lines; short sentences; Line 1 is the Verbal Hook within ~1.5 s; punctuation where the voice should pause; `pause_after_ms` 250–600 (longer at scene turns); only allowed tags (`[pause]`, `[pause 500ms]`, `[pause 1.5s]`, the OmniVoice non-verbal tags in `scripts/sflib/text.py`, `[[written|spoken]]`), prefer none.
- Slides: 9:16 → slides of 2–4 s, one drawable moment each; Slide 1 visual prompt must execute the `Visual Hook`; `source` = canon scene id; no two consecutive slides share scene, pose and shot; vary `motion` (static, push_in, pull_out, pan_left, pan_right) every 3-5 s; `text_placement` lower_third. Visual prompts are written by `sf-visual` rules.
- Write `projects/<slug>/script.md`: story summary, hook archetype, cast table, lines by slide, and text hooks.
- `sf_validate` must print `{"ok": true, "errors": []}`.

## Gate 1 Self-Review
Self-score against **all 14 items** in `references/rubric.md` (Part A Technical + Part B Viral Readiness). Fix every failed item before handing back to `sf-director`.
