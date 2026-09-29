---
name: sf-director
description: Orchestrates a StoryForge production from idea to final video and viral publishing package — stages, gates, resume, feedback. Entered by /story, /story-feedback and /story-redo; use it whenever a StoryForge production is created, resumed, redone or given feedback.
---

# sf-director

You run StoryForge productions in `/Users/irondev/Desktop/Projects/chauvanhieu/yt`.
Scripts do all mechanical work: `uv run scripts/<script>.py projects/<slug> [--only ids]`.
Each prints one JSON line; exit 0 ok, 1 bug, 2 needs human, 3 provider quota/auth.
Never edit fields scripts own (asset path/status/hash/attempts/last_error, audio measurements, words, output.*).

## On entry

1. Read `library/taste.md` and `library/checks.md`; keep only entries whose scope tags all
   match this production (language, aspect, genre, stage, or `global`). These are the rules.
2. Read `library/calibration.json` if it exists.
3. Read `references/platform-tuning.md` for platform targets and distribution specs.
4. Record applied rule/check ids in `story.json` `learnings_applied` when the production exists.

## Stages (`/story`)

| # | Stage | Do | Exit |
|---|---|---|---|
| 1 | brief | Fill `brief` from the idea. Defaults come from taste rules scoped `brief`; with none: language `vi`, aspect `9:16`, `target_seconds` 60, `platform_target` `youtube_shorts` (options: `youtube_shorts`, `tiktok`, `instagram_reels`), captions `karaoke`/`karaoke-bold`, `review_mode` `auto`. Ask the user only if the idea gives no premise to write from. | brief complete |
| 2 | canon + script | Dispatch one subagent that follows `sf-script` (pass: brief with `platform_target`, matching rules, calibration numbers, target paths, and references). | `sf_validate` ok; Story CLI `validate`, `links` clean |
| 3 | Gate 1 | auto: score `script.md` against **all 14 items** in `sf-script/references/rubric.md` (Part A Technical + Part B Viral Readiness) and the script-scoped rules; if any item fails (especially weak hook, flat escalation without But/Therefore, or missing payoff), send specific actionable failures back to the script subagent; max 2 rounds, then ask the user. gated: show `script.md`, wait. | pass all 14 checks |
| 4 | images | Follow `sf-visual` for prompts (Slide 1 must execute the Visual Hook); run `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>` then `sf_contact_sheet`. | all done |
| 5 | Gate 2 | auto: follow `sf-visual` self-review; redo flagged items; max 2 rounds, then ask the user. gated: show `out/contact_sheet.png`, wait. | pass |
| 6 | voice | Follow `sf-audio`; `sf_voice`. Line 1 must deliver punchy Verbal Hook delivery without hesitant pauses. | all lines done |
| 7 | finish | `sf_align`, `sf_captions`, `sf_render`, `sf_qc`. Auto-fix only: re-run captions after re-wrapping, re-render after a regenerated asset. | QC ok, or remaining failures reviewed (see below) |
| 8 | learn | `sf_learn`. If `library_problems` is non-empty, fix the library file format and re-run. | ok |
| 9 | report & publish | Video path, duration vs target, what was auto-fixed, open QC notes. **Generate the complete Publishing Package** per `references/platform-tuning.md` (Title, Caption, 3-5 Hashtags, Pinned Comment). End with: "Feedback? `/story-feedback <slug> \"...\"`". | done |

Update `state.stage` as you pass each stage so a later `/story` resumes where it stopped.
Check services before stages 4 and 6 (`references/services.md`).

QC failures you judge acceptable after inspection (e.g. a natural 10 ms-over pause at a comma)
are reported as reviewed, not hidden.

## Objective defects → `library/checks.md`

When a gate or QC finds an objective defect (visible error, wrong count, text in image,
timing failure, length miss > 10 %), fix it, then add a check or bump the `hits` of the
existing one that covers it. Keep ≤ 30 per scope: when adding past the cap, delete the
entry with the fewest hits, oldest first. Checks are workflow knowledge, not taste.

## Taste → only `/story-feedback`

Never write `library/taste.md` except in the feedback flow (`references/feedback.md`).
Without user feedback, taste stays exactly as it is.

## Errors

- exit 2: read the summary's `needs_human`; fix what a skill can fix (prompt, text, casting), else ask the user.
- exit 3: provider quota/auth — stop and tell the user which provider and what to do.
- exit 1: read `projects/<slug>/logs/<script>.log`, report the bug; do not work around engine bugs silently.

## Subagents

Dispatch writing work (canon, script, rewrites) to subagents with: the brief, the matching
rules and checks verbatim, calibration numbers, exact file paths, and the exit criterion.
They never dispatch further agents. Run engine scripts yourself, one at a time (the project
lock allows one script per production).
