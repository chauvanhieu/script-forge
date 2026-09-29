# StoryForge Plan 2: Director Skills and the Evolution Loop

Date: 2026-09-29. Builds on `2026-09-28-storyforge-design.md` (the engine spec, "base spec").
Where this document and the base spec disagree, this document wins; the base spec is
updated in the same change (see §8).

## 1. Goal

One command turns an idea into a finished video, and every use makes the next one
better along two separate channels:

- **Taste channel (skills):** changes **only** when the user gives feedback. With no
  feedback, nothing about taste changes. Over time the system matches the user's taste.
- **Workflow channel (mechanics):** updates **automatically after every run** from
  measurements and objective defects, so the next run is faster and more accurate.

The boundary: *taste* is anything only the user can judge (look, voice character,
writing style, pacing preference, defaults). *Workflow* is anything measurable or
objectively right/wrong (durations, speaking rates, timings, visible defects such as
two moons, text in an image, a wrong number of characters).

Evidence that motivates the workflow channel (from the first Vietnamese production,
`den-ong-sao`): the script estimate missed the target (64 s vs 60 s) because no measured
Vietnamese speaking rate existed; a moon scene rendered two moons; VoiceStudio's
Vietnamese word aligner is broken so karaoke must use anchored approximate timings;
QC constants needed calibration against real TTS pauses.

## 2. Commands

Files in `.claude/commands/`:

| Command | Does |
|---|---|
| `/story "<idea>"` | Idea → finished video. If a production for the idea's slug exists, resumes it at `state.stage`. |
| `/story-feedback <slug> "<feedback>"` | Splits the feedback into points; for each point, redoes the affected items and records a taste rule; re-runs the affected stages; runs `sf_learn`. |
| `/story-redo <slug> <id>[,<id>…]` | Mechanical redo of named items (`S05`, `L011`, `C02`, `LOC01`); records nothing in `taste.md`. |

`/story` replaces the base spec's `/story-new`.

## 3. Skills

Files in `.claude/skills/`. Each `SKILL.md` is short; depth lives in `references/`,
loaded only when needed. Four skills (the base spec's five, with `sf-finishing` folded
into `sf-director` because scripts do that work, and `sf-video-script` renamed `sf-script`
because it now also owns canon writing):

- **`sf-director`** — stage table, `state` transitions, resume, error policy (base spec
  §4.5), gate logic (§4), subagent dispatch, captions/render/QC orchestration, the final
  report. Loads `taste.md` rules for brief defaults.
- **`sf-script`** — canon via Story Skills (`story-init`, `scene-craft`, `chapter-writing`,
  `character-management`) and adaptation into `lines[]` + `slides[]` (base spec §6.1
  `sf-video-script` rules). Sizes the script from `calibration.json` (§6.3).
- **`sf-visual`** — style bible, plate and slide prompts (the base spec formula), and the
  Gate 2 self-review of the contact sheet.
- **`sf-audio`** — casting (`library/cast/<ref>` → design → clone), expressive controls,
  retake handling.

Every skill, on entry, reads the rules from `library/taste.md` and `library/checks.md`
whose scope matches the production (§6.1), and records their ids in `story.json`
`learnings_applied`.

Heavy writing (canon, adaptation) runs in subagents dispatched by `sf-director`, each
given only its brief, the relevant rules, and file paths.

## 4. `/story` flow and gates

`brief.review_mode` becomes `"gated" | "auto"` (schema change); default `"auto"`.

| Step | Owner | Exit criterion |
|---|---|---|
| 1 brief | `sf-director` | brief filled from the idea + taste defaults; asks the user only if the idea is too vague to pick genre/characters |
| 2 canon + script | `sf-script` (subagent) | `sf_validate` ok; Story CLI `validate`, `links` clean |
| 3 Gate 1 | `sf-director` | auto: script rubric (`sf-script/references/rubric.md`) + matching taste rules pass; ≤ 2 self-revisions, then ask the user. gated: user approves `script.md` |
| 4 images | `sf_image` (local provider via `SF_CONFIG`) | all done; contact sheet built |
| 5 Gate 2 | `sf-visual` | auto: agent inspects the contact sheet against `checks.md` + taste rules; redoes flagged slides/plates with a changed seed and prompt; ≤ 2 rounds, then ask the user. gated: user approves |
| 6 voice → align → captions → render → QC | scripts | QC ok, or only auto-fixable failures remain after fixing; otherwise report |
| 7 learn | `sf_learn` | `runs/`, `calibration.json` updated |
| 8 report | `sf-director` | video path, duration vs target, what was auto-fixed, and one line inviting feedback |

An auto gate never writes taste rules. When it finds an **objective** defect it records
or bumps a check in `checks.md` (§6.2) — that is workflow knowledge.

Services: before step 4 and step 6, `sf-director` checks the image provider config and
`GET /health` on VoiceStudio; if down it starts it with the command recorded in
`sf-director/references/services.md`, waiting up to 90 s.

## 5. `/story-feedback`

1. Split the feedback into points. Classify each as:
   - **item fix** (names or clearly implies slides/lines/characters) → the items to redo;
   - **taste rule** (a preference that should hold beyond this video) → a rule;
   - usually both.
2. Write or replace rules in `library/taste.md` (§6.1). A rule that contradicts an existing
   rule of the same or broader scope **replaces** it (`replaces T003`); the old line is
   deleted.
3. Apply fixes: prompt/text/voice edits through the owning skill, then reset only those
   items (base spec redo semantics) and re-run the affected stages and everything
   downstream of them (captions/render/QC as needed).
4. Run `sf_learn`; report what changed and which rule ids were written.

No other path writes `taste.md`.

## 6. Data (`library/`)

### 6.1 `library/taste.md` — taste rules (written only by `/story-feedback`)

One rule per list item, two lines:

```
- T007 [vi · 9:16] Child voices must sound younger than described; prefer "child, high pitch".
  ← den-ong-sao · 2026-09-29 · "giọng Bống trẻ hơn nữa"
```

- Id `T` + 3+ digits, never reused. Scope tags in brackets: `global`, a language code, an
  aspect, a genre, or a stage (`script`, `visual`, `audio`, `captions`); multiple tags
  mean all must match. Second line: slug, date, the user's words verbatim.
- Brief defaults live here as rules too (e.g. `T001 [global · brief] Default language vi,
  9:16, karaoke-bold, 60 s.`). With no default rule, `sf-director` uses vi, 9:16, 60 s,
  karaoke / karaoke-bold.
- No retired entries in the file; git history is the record.

### 6.2 `library/checks.md` — objective checks (written by auto gates and QC)

```
- K004 [image] Moon scenes: state the count in the prompt ("exactly one full moon").  hits: 1 · den-ong-sao/S05
```

- Id `K` + 3+ digits. Scope: `script`, `image`, `audio`, `captions`, optionally with a
  language code. `hits` increments each time the check catches a defect again (with the
  latest slug/id).
- Skills apply checks **proactively** (e.g. `sf-visual` writes counts into prompts) and
  during self-review.
- Cap: 30 checks per scope. When adding past the cap, drop the entry with the fewest
  hits, oldest first.

### 6.3 `library/calibration.json` — measured constants (written only by `sf_learn`)

```json
{
  "version": 1,
  "speaking_rate": {"vi": {"chars_per_s": 13.1, "lines": 16}},
  "stage_seconds": {"image": {"mean": 26.1, "n": 17}, "voice_line": {"mean": 9.8, "n": 22}}
}
```

- `speaking_rate[lang].chars_per_s`: display characters without spaces
  (`sflib.text.display_text` + `norm`) per second of measured line audio (`duration_ms`),
  as an exponential moving average over lines (α = 0.2), seeded by the first run's mean.
- `sf-script` budget: `chars = (target_seconds − Σ pause_after_ms/1000) × chars_per_s`;
  no calibration for the language → the base spec's rough table.
- `stage_seconds`: mean wall time per image, per voiced line, per render, from
  `logs/runs.jsonl`; used for the ETA in the `/story` start message.

### 6.4 `library/runs/<slug>.json` — run history (written only by `sf_learn`)

A JSON list, one entry per `sf_learn` run: `run_id`, date, target vs actual seconds,
predicted seconds (from the script budget), counts (images generated, image redos,
retakes, needs_human, untrusted timings), QC failed checks, stage wall times.

### 6.5 Engine change: `logs/runs.jsonl`

`sflib.project.main_wrapper` appends one JSON line per script invocation to
`projects/<slug>/logs/runs.jsonl`: `{"script", "started", "elapsed_s", "exit", "counts"}`
where `counts` holds the lengths of the summary's list fields. `sf_learn` reads it.

## 7. `sf_learn` (new script)

`uv run scripts/sf_learn.py projects/<slug>` — deterministic, same stdout/exit contract
as every other script.

- Reads `story.json`, `logs/runs.jsonl`, `out/qc.json`; writes `library/runs/<slug>.json`
  and `library/calibration.json` atomically.
- **Idempotent:** `run_id` = hash of the `runs.jsonl` entries it consumed; an existing
  `run_id` is skipped; each line contributes to `speaking_rate` once per `audio.input_hash`
  (tracked in the run entry).
- Every run validates `taste.md` and `checks.md` (`check_library`); problems are listed
  in `library_problems` and the script exits 2.

## 8. Changes to existing files

- `schemas/story.schema.json`: `review_mode` enum `gated|auto`.
- `scripts/sflib/project.py`: `runs.jsonl` append in `main_wrapper`.
- Base spec: §3 commands table (`/story`, `/story-feedback`), §4.2 gates (auto mode),
  §6.1 skill list (four skills), `library/learnings.md` → `taste.md` + `checks.md` +
  `calibration.json` + `runs/`.
- `projects/den-ong-sao`: seed `calibration.json` and `checks.md` from it by running
  `sf_learn` once and adding K001–K00n for the defects found in its Gate 2 (two moons).

## 9. Testing

- **Unit (`tests/test_sf_learn.py`):** EWMA math; idempotency (running twice changes
  nothing); speaking rate counts each `input_hash` once; `runs/` entry fields;
  `check_library` accepts valid files and rejects duplicates / unknown scopes /
  malformed taste entries, and its problems make `sf_learn` exit 2; `main_wrapper`
  appends a well-formed `runs.jsonl` line.
- **Acceptance (end to end, manual by the controller):**
  1. `/story "<new idea>"` in auto mode produces a video with no user input; duration
     within ±10 % of `target_seconds`.
  2. `/story-feedback` with one point writes exactly one taste rule, redoes only the named
     items, and leaves every skill file unchanged.
  3. A second `/story` run without feedback leaves `taste.md` byte-identical.

## 10. Out of scope

Self-patching engine code; automatic QC-threshold tuning; parallel image + voice
generation (the per-project lock stays); localization (base spec §9).
