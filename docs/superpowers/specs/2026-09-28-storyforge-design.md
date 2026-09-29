# StoryForge — Design Spec

- **Date:** 2026-09-28
- **Status:** Draft, pending user review
- **Location:** `yt/` (workspace root)

## 1. Goal

StoryForge is an **agent project**, not an application: a set of Claude Code
skills, rules, slash-commands, and small deterministic scripts that turn an
idea into a finished **slide-story video**: a sequence of illustrated slides
with narration, per-character voices, and optional word-by-word karaoke
captions.

Claude Code is the conductor. The human types slash-commands, approves two
review gates, and Claude does everything else by loading skills and running
scripts.

## 2. Decisions

| Topic | Decision |
|---|---|
| Runtime model | Claude Code orchestrates in-session: skills + rules + slash-commands + scripts |
| Artifact language | All project artifacts (skills, rules, prompts, docs, schemas) are written in **English** |
| Video language | Any language the voice engine supports; declared per production (`brief.language`, BCP-47) |
| Aspect ratio | `9:16` or `16:9`, declared per production; images generated natively at that ratio (no cross-cropping) |
| Speakers | Narrator + a distinct, fixed voice per character (`speaker` on every line) |
| Voice | **VoiceStudio** local API (`http://localhost:3900`), default engine OmniVoice |
| Image | **Provider slot.** The user plugs in their own CLI wrapper around cho-vo's Antigravity image service. StoryForge does not contain or port that code. |
| Content types | `fiction`, `factual`, `adaptation`, plus free-form `genre` |
| Story source of truth | `fiction` and `adaptation` always go through a **Story Skills canon project**. `factual` goes straight to production with research notes. |
| Monetization | None. OmniVoice weights are CC-BY-NC; acceptable for non-commercial use only. |
| Review | Two gates: after the script, after the image contact sheet |
| Assembly | Python scripts + FFmpeg + ASS subtitles (libass). Claude never writes FFmpeg commands. |

## 3. Architecture

Two layers with one direction of flow: **canon → production**.

- **Canon** (`stories/<story-id>/`) is a Story Skills markdown project. It holds
  the story as prose plus its bible (characters, world, plot, continuity).
  Text only. Story Skills conventions and its CLI own this layer.
- **Production** (`projects/<slug>/`) is one video cut of a canon: one aspect
  ratio, one language, one or more chapters. It holds `story.json` and all
  binary assets. StoryForge skills and scripts own this layer.

One canon can yield many productions: a 9:16 short and a 16:9 long cut of the
same story, one production per episode of a serial, and later, one production
per language.

```text
yt/
├── CLAUDE.md                        # entry point: mission, pipeline map, hard rules, how to start
├── skills-lock.json                 # Story Skills install lock (existing)
├── .agents/skills/                  # Story Skills (installed, do not edit)
├── .claude/
│   ├── skills/
│   │   ├── <22 Story Skills symlinks>   # existing
│   │   ├── sf-director/             # stage machine, gates, resume, skill routing
│   │   ├── sf-video-script/         # canon prose / research → lines[] + slides[]
│   │   ├── sf-visual/               # style bible, identity + location plates, slide prompts
│   │   ├── sf-audio/                # casting, VoiceStudio generation, pronunciation, retakes
│   │   └── sf-finishing/            # captions/karaoke, render, QC
│   ├── commands/
│   │   ├── story-new.md             # idea → canon (or research) → production folder
│   │   ├── story-run.md             # advance to the next gate or to done
│   │   ├── story-status.md          # stage, blockers, what the next /story-run will do
│   │   └── story-redo.md            # redo one slide / line / character / plate
│   └── rules/
│       ├── language.md
│       ├── integrity.md
│       ├── data-contract.md
│       ├── canon.md
│       ├── providers.md
│       └── licensing.md
├── scripts/                         # Python 3.11, run with `uv run`
│   ├── sf_validate.py
│   ├── sf_voice.py
│   ├── sf_image.py
│   ├── sf_align.py
│   ├── sf_captions.py
│   ├── sf_contact_sheet.py
│   ├── sf_render.py
│   ├── sf_qc.py                     # deterministic measurements → out/qc.json
│   └── sflib/                       # shared helpers (project IO, text, timeline, media, VoiceStudio client)
├── tests/                           # one small test file per script + fixtures
├── schemas/story.schema.json        # the production data contract
├── config/
│   ├── providers.yaml               # voice + image provider settings
│   └── caption-styles/              # named ASS style presets
├── library/
│   ├── cast/<ref>/                  # reusable voice profile + plates for recurring characters
│   └── learnings.md                 # gate feedback distilled into rules of taste
├── stories/<story-id>/              # CANON (Story Skills project)
├── projects/<slug>/                 # PRODUCTION
│   ├── story.json
│   ├── script.md                    # generated, human-readable view for Gate 1
│   ├── plates/ audio/ images/ captions/
│   └── out/                         # final.mp4, captions.ass, contact_sheet.png, qc.json
├── VoiceStudio/                     # separate repo, voice backend (not modified)
└── docs/superpowers/specs/
```

**Division of labor**

- **Skills** hold judgment: story craft, adaptation choices, prompt writing,
  quality assessment.
- **Scripts** hold precision: API calls, duration measurement, word alignment,
  caption timing, rendering.
- **`story.json` is the single source of truth for a production.** Every stage
  reads and writes it, so any interruption resumes where it stopped.
- **Canon files are the single source of truth for the story.** A production
  never edits canon; it records adaptation choices in `story.json`.

## 4. Pipeline

### 4.1 Commands

```text
/story-new "<idea>"        interactive brief → canon (or research) → production folder
/story-run [slug]          advance until the next gate or done
/story-status [slug]       current stage, blockers, next action
/story-redo <slug> <id>    redo S07 | L023 | C01 (voice or plates) | LOC02 (location plate)
```

### 4.2 Stages

| # | Stage | Owner | Output |
|---|---|---|---|
| 0 | **brief** | `/story-new` | `language`, `aspect`, `content_type`, `genre`, `target_seconds`, `captions.mode`, canon target (new or existing story, which chapters) |
| 1 | **idea** (fiction/adaptation, new story only) | `premise-workshop` | Tested logline, premise, stakes, form (`flash` ≤ ~3 min, `short-story` for long 16:9, `serial` for series) |
| 2 | **canon** | `story-init`, `character-management`, `worldbuilding`, `plot-structure`, `genre-craft`, `scene-craft`, `chapter-writing` | Canon project with drafted prose for the chapters this production adapts |
| 2f | **research** (factual only) | `research` skill note format | `story.json.research`: sources, claims, status, confidence, risk |
| 3 | **adapt** | `sf-video-script` | `story.json` `cast[]`, `locations[]`, `lines[]`, `slides[]`, `style_bible`; `script.md` |
| 4 | **pre-gate checks** | `sf-director` | Story CLI checks on the canon, read-aloud pass, `sf_validate`, self-critique rubric |
| 🚦 | **GATE 1** | human | Approves `script.md`: story, cast, slide list, check results. Feedback edits canon (with approval) or `story.json`, then stage 4 re-runs. |
| 5 | **cast** | `sf-audio`, `sf-visual` | Voice profile per speaker; identity plates per character; location plates per recurring location |
| 6 | **voice** | `sf_voice` | One WAV per line + measured duration; automatic QC and retakes |
| 7 | **images** | `sf_image` | One image per slide (plates as references); `contact_sheet.png` |
| 🚦 | **GATE 2** | human | Reviews contact sheet; names slides/plates to redo and why; loop until approved |
| 8 | **captions** | `sf_align`, `sf_captions` | Word timings matched to script text; `captions.ass` |
| 9 | **render** | `sf_render` | `out/final.mp4` |
| 10 | **QC** | `sf-finishing` | `out/qc.json`; auto-fixes allowed fixes, reports the rest |

Stages 6 and 7 are independent and may run in either order once stage 5 is
done (not concurrently: each script holds the project lock and rewrites the
whole `story.json`).

### 4.3 Pre-gate checks (stage 4)

Run from the canon project root with
`node .agents/skills/story-maintenance/scripts/story.js <cmd> --json`:

- `validate`, `links`, `continuity`: canon is structurally sound.
- `pacing`: each adapted chapter has a `hook`; outcome runs flagged.
- `voices`: characters with 5+ lines do not sound alike (advisory for non-English canon).
- `names`: no clashing or look-alike names.
- `clues`: mystery genre only; fair-play matrix.

Then:

- **Read-aloud pass** (`line-editing/references/read-aloud-guide.md` +
  `adaptation/references/audiobook.md`) over `lines[]`: homographs, tagless
  dialogue runs, visual-only devices, numbers and symbols, names without
  `pronunciation`.
- **`sf_validate`** on `story.json`.
- **Self-critique rubric** (in `sf-video-script`): hook strength in the first
  slide, stakes, setup/payoff, every slide drawable, distinct character voices,
  no slide repeats the previous composition. A score below threshold triggers
  one rewrite before Gate 1.

Findings go into `script.md` under "Checks" so Gate 1 shows them.

### 4.4 Resume, cache, redo

- Every line and slide carries `status` and `input_hash`.
  - Line hash: text, speaker voice profile, whisper, language, engine, seed.
  - Slide hash: prompt, reference plate hashes, aspect, provider, seed.
- `/story-run` skips items whose status is `done` and whose hash still matches.
  Changing one line regenerates that line's audio, its captions, and the render.
- `/story-redo` resets the named items to `pending` (and, for a character or
  location, every slide that references its plates), then runs the affected
  stages.

### 4.5 Provider error policy

| Error code | Action |
|---|---|
| `transient` | Retry with backoff, max 3 |
| `content_blocked` | `sf-visual` rewrites the prompt once, then marks the item `needs_human` |
| `quota`, `auth` | Stop the run, report, exit code 3. Never switch provider silently. |
| `invalid` | Bug in our request; stop and report |

Automatic regeneration for quality (voice retakes, image retries) is capped at
2 attempts per item; after that the item becomes `needs_human`.

## 5. Data contract — `story.json`

`schemas/story.schema.json` is authoritative; this is the shape.

```jsonc
{
  "schema_version": "1.0",
  "slug": "skerry-light-ch01-916-vi",
  "canon": { "path": "stories/skerry-light", "chapters": ["chapter-01"] },   // null for factual
  "brief": {
    "idea": "…",
    "language": "vi",
    "aspect": "9:16",
    "content_type": "fiction",
    "genre": "mystery",
    "target_seconds": 90,
    "captions": { "mode": "karaoke", "style": "karaoke-bold" },            // karaoke | plain | none
    "review_mode": "gated"
  },
  "state": {
    "stage": "images",
    "gates": { "script": { "approved_at": null }, "images": { "approved_at": null } }
  },
  "style_bible": {
    "medium": "…", "palette": ["…"], "lighting": "…", "composition": "…",
    "avoid": ["generated text", "logos", "watermarks"]
  },
  "cast": [
    {
      "id": "narrator", "canon_id": null, "name": "Narrator", "role": "narrator",
      "voice": { "source": "design", "design_prompt": "…", "profile_id": null },
      "caption_color": "#FFFFFF"
    },
    {
      "id": "C01", "canon_id": "mara-quill", "name": "Mara", "role": "protagonist",
      "appearance": "…",                                   // fixed visual spec, repeated in prompts
      "pronunciation": "MAH-rah",
      "voice": { "source": "library", "library_ref": "mara", "design_prompt": "…", "profile_id": "…" },
      "caption_color": "#FFD166",
      "plates": {
        "face": { "prompt": "…", "path": null, "input_hash": null, "status": "pending", "attempts": 0 },
        "half": { "…": "…" },
        "full": { "…": "…" }
      }
    }
  ],
  "locations": [
    {
      "id": "LOC01", "canon_id": "skerry-light", "name": "Skerry Light",
      "appearance": "…",
      "plate": { "prompt": "…", "path": null, "input_hash": null, "status": "pending", "attempts": 0 }
    }
  ],
  "slides": [
    {
      "id": "S01",
      "source": "chapter-01-scene-01",                     // canon scene id, or claim ids for factual
      "line_ids": ["L001", "L002"],
      "brief": {
        "moment": "…",                                     // the single drawable instant
        "characters": ["C01"],
        "location": "LOC01",
        "must_show": ["…"],
        "must_not_show": ["…"],                            // what the next slide reveals
        "continuity": ["…"],                               // clothing, props, colors
        "beat": "question"                                 // setup | question | reveal | reversal | emotional | resolution
      },
      "visual": {
        "prompt": "…",
        "shot": "close-up",                                // extreme-close | close-up | medium | wide | extreme-wide
        "motion": "push_in",                               // static | push_in | pull_out | pan_left | pan_right
        "text_placement": "lower_third"                    // caption safe zone kept clear in the composition
      },
      "image": { "path": null, "seed": 1234, "input_hash": null, "status": "pending", "attempts": 0 }
    }
  ],
  "lines": [
    {
      "id": "L001", "speaker": "narrator", "text": "…",   // may contain allowed expressive tags (§6.1 sf-audio)
      "whisper": false,                                    // true → adds OmniVoice `whisper` style for this line
      "pause_after_ms": 250,
      "claim_ids": [],                                     // factual only
      "audio": {
        "path": null, "duration_ms": null, "seed": null, "input_hash": null,
        "status": "pending", "attempts": 0,
        "qc": null,                                        // { "cer", "cps" } from the transcribe-back check
        "asr_words": null                                  // raw ASR words kept for sf_align
      },
      "words": [],                                         // [{ "text", "start_ms", "end_ms", "approx" }], relative to line start
      "words_hash": null                                   // audio.input_hash the words were aligned against
    }
  ],
  "research": null,       // factual: { "notes": [...], "claims": [...] } using the Story Skills research note fields
  "source_work": null,    // adaptation: { "title", "author", "rights_basis", "translation_used" }
  "learnings_applied": [],
  "output": { "video": null, "captions": null, "contact_sheet": null, "qc": null }
}
```

**Contract rules**

- **Stable ids:** `S01…`, `L001…`, `C01…`, `LOC01…`. Inserting an item takes a
  new id; ids are never renumbered. Order comes from array position.
- **`canon_id`** links a production entity to its canon file
  (`characters/<id>.md`, `worldbuilding/locations/<id>.md`); `source` links a
  slide to its canon scene. Every adapted beat traces back to canon.
- **Write ownership:** skills write creative fields. Only scripts write `path`,
  `duration_ms`, `words`, `input_hash`, `status` of generated assets, and
  `output`. A skill that needs a regenerate sets `status: "pending"` through
  `/story-redo` semantics, never by editing measured fields.
- **`sf_validate` checks:** schema; every line belongs to exactly one slide;
  every `speaker` and slide character exists in `cast`; every slide `location`
  exists in `locations`; enums (`motion`, `shot`, `beat`, `text_placement`,
  `captions.mode`); bracket tags in `text` are only the allowed expressive tags
  (§6.1 `sf-audio`) or `[[written|spoken]]` overrides (the pipe form is
  required so captions can show the written word); `factual` lines with factual assertions carry `claim_ids`
  that resolve; `adaptation` has `source_work.rights_basis`; `canon.path`
  exists and each `source` scene id exists in canon.

## 6. Skills

### 6.1 StoryForge skills (`.claude/skills/sf-*`)

Each `SKILL.md` stays lean; depth lives in `references/` and is loaded only
when the brief needs it.

**`sf-director`**, entered by every slash-command.
- Owns the stage table (§4.2): which skill to load, which script to run, exit
  criteria per stage.
- Reads `state`, stops at gates, resumes after interruption, applies the error
  policy (§4.5).
- **Routing table** for Story Skills by stage (§6.2).
- Appends one line per gate correction to `library/learnings.md`, phrased as a
  reusable rule with its scope (genre, aspect, language).

**`sf-video-script`**, the adaptation skill: canon prose or factual research → `lines[]` + `slides[]`.
- Pacing per aspect:
  - `9:16`: hook on slide 1 within ~1.5 s; 60–180 s; slides of 2–4 s; one idea per slide.
  - `16:9`: 3–12 min; slides of 4–8 s; room for explanation.
- **Written natively in `brief.language`** (the canon's language, or the
  target language for a translated canon), never translated at this step.
- Line rules for TTS: narration and dialogue on separate lines; dialogue
  attributed by `speaker`, not tags; no stage directions in `text`; numbers and
  symbols written as spoken in that language; tagless dialogue runs broken up.
- Slide rules, adapted from `adaptation/references/comics-script.md` and
  `picture-book.md`:
  - One slide is one drawable moment.
  - Beat-ending slides pose, the next slide reveals.
  - No two consecutive slides share scene, pose, and shot.
  - Pictures do not repeat what the words say.
  - Wordless or quiet slides are allowed before a big reveal.
- Word budget from `target_seconds` and a per-language speaking-rate table
  (calibrated from measured durations over time); rough estimate first, real
  durations always win.
- References: `aspects/{9x16,16x9}.md`, `content-types/{fiction,factual,adaptation}.md`,
  `rubric.md`, `speaking-rates.md`.

**`sf-visual`**, images and consistency.
- Style bible presets (`references/styles/*.md`) and the prompt formula:
  style → subject/appearance → action → setting → shot → light → continuity → exclusions.
- **Identity plates** per character (face / half / full, generated
  independently so one failure does not block another), following the cho-vo
  KOL-plate pattern. **Location plates** per recurring location. Every slide
  sends the plates of its characters and location as references (max 4; the
  priority order is the character face plates, then the location plate).
- Shot-variety rules and caption safe zones per aspect.
- `content_blocked` rewrite policy; translating Gate 2 feedback into prompt edits.

**`sf-audio`**, voices.
- Casting order: `library/cast/<ref>` → voice design → clone from a
  user-supplied clip.
  - **Design:** a free-text description from the canon character (gender, age,
    pitch, accent) goes to `POST /design/describe`, which returns `attrs` and a
    validator-safe `instruct`. Then `POST /profiles` with `kind=design`,
    `vd_states=<attrs JSON>`, `instruct`, `language` returns the profile `id`.
  - **Clone:** `POST /profiles` with `kind=clone` and `ref_audio`. The clip's
    delivery is cloned along with its timbre, so an animated reference gives an
    animated voice. This is the strongest expressive control available.
- **Expressive controls OmniVoice actually supports** (anything else is spoken
  as literal text):
  - punctuation (ellipses, dashes, exclamations, short fragments);
  - `[pause]`, `[pause 500ms]`, `[pause 1.5s]` inside `text`;
  - the 13 non-verbal tags `[laughter]`, `[sigh]`, `[confirmation-en]`,
    `[question-en|ah|oh|ei|yi]`, `[surprise-ah|oh|wa|yo]`,
    `[dissatisfaction-hnn]` (only `[laughter]` and `[sigh]` are broadly useful);
  - `whisper: true` on a line, which appends `whisper` to the `instruct`.
  - Free-form emotion words in `instruct` are rejected by VoiceStudio (400).
- Picks `seed`; syncs canon `pronunciation` fields into VoiceStudio's
  `/pronunciation` dictionary, or uses inline `[[written|spoken]]` overrides
  (VoiceStudio speaks `spoken`; captions show `written`).
- Retake policy and audio QC thresholds (§8.3).

**`sf-finishing`**, captions, render, QC.
- Caption presets. Karaoke tokenization by language: space-delimited languages
  by word; CJK/Thai/Lao/Khmer/Burmese by character cluster. 1–2 lines per cue,
  max characters per line by aspect, speaker colors, captions only inside the
  slide's `text_placement` zone.
- QC checklist and the list of auto-fixable failures.

### 6.2 Story Skills routing (used by `sf-director`)

| Stage | Story Skills loaded |
|---|---|
| idea | `premise-workshop` (then `story-init`) |
| canon — setup | `story-init`, `character-management`, `worldbuilding` (locations only unless the story needs systems) |
| canon — structure | `plot-structure` (`short-story-form.md` for flash/short; `structure-models.md` for kishōtenketsu and others), `genre-craft` (the genre pack; `serial-episodic.md` for series), `theme-craft` (controlling idea, light touch) |
| canon — draft | `scene-craft` (`openings.md` for the hook, `try-fail.md`, `dialogue-subtext.md`), `chapter-writing` |
| series | `series-continuity` for new seasons or spin-offs; within a serial, one episode = one chapter with `episode-question` |
| adapt | `adaptation` references (`comics-script.md`, `picture-book.md`, `audiobook.md`) as inputs to `sf-video-script` |
| pre-gate | `story-maintenance` (CLI), `line-editing` (read-aloud), `voice-style` (style sheet, dialect) |
| factual | `research` (note fields and practice) |
| any, on trigger | `editorial-review` (real people, defamation, lyrics and quote permissions, AI disclosure, sensitivity), `verse-craft` (rhyming stories), `revision-continuity` (canon revisions after Gate 1 feedback) |

Not used: `publishing`, `submission`, `feedback-triage`, `discovery-drafting`.

## 7. Rules (`.claude/rules/`, always loaded)

- **`language.md`**: all artifacts in English; video content in `brief.language`.
- **`integrity.md`**: never fabricate facts, quotes, sources, statistics, or
  credentials; label reconstructions and hypotheticals; unresolved factual
  claims block Gate 1.
- **`data-contract.md`**: `story.json` write ownership (§5); Claude never
  writes FFmpeg or provider calls by hand; all mechanical work goes through
  `scripts/`.
- **`canon.md`**: the Story Skills hard rules. Never change canon to suit an
  adaptation without approval; no scripts or binaries under `stories/`; run the
  Story CLI in place, never copy it; ids stay ASCII kebab-case.
- **`providers.md`**: error codes and policy (§4.5); attempt caps; no silent
  provider fallback.
- **`licensing.md`**: OmniVoice weights are CC-BY-NC (non-commercial); the
  image provider and its terms are the user's responsibility; adaptations need
  a recorded `rights_basis`.

## 8. Scripts

### 8.1 Common interface

- Python 3.11, dependencies in one `pyproject.toml` at `yt/`: `httpx`,
  `jsonschema`, `Pillow`, `PyYAML`. System: `ffmpeg` and `ffprobe` with libass.
- Invocation: `uv run scripts/sf_<name>.py projects/<slug> [--only S07,L023]`.
- `story.json` writes are atomic (temp file + rename) and hold a lock file for
  the duration of the run.
- Stdout: exactly one JSON summary line
  (`{"ok": true, "done": 12, "skipped": 30, "needs_human": ["S07"], "errors": []}`).
  Detailed logs go to `projects/<slug>/logs/`.
- Exit codes: `0` success, `1` bug, `2` needs human, `3` provider quota/auth.

### 8.2 Provider slots — `config/providers.yaml`

```yaml
voice:
  base_url: http://localhost:3900     # VoiceStudio; sf_voice checks GET /health first
  engine: null                        # null = VoiceStudio default (OmniVoice)
image:
  provider: command                   # command | fake
  command: ["node", "/path/to/generate-image.js"]   # user-supplied wrapper
  timeout_s: 1200
  max_refs: 4
```

**Image command contract** (the user's wrapper implements it):

```text
<command> --prompt-file <p.txt> --aspect <1:1|3:4|9:16|16:9> [--ref <a.png> ...] [--seed <n>] --out <S07.png>
success: exit 0 and a PNG at --out
failure: exit ≠ 0, stderr = {"error": "quota|auth|content_blocked|transient|invalid", "message": "…"}
```

The **`fake`** provider renders a solid-color PNG with the slide id, so the
whole pipeline can run without spending quota.

### 8.3 Script responsibilities

- **`sf_validate`**: contract checks from §5.
- **`sf_voice`**:
  - Checks `GET /health`, creates missing profiles, then calls
    `POST /generate` per pending line (`text`, `language`, `profile_id`,
    `seed`, `engine`, and `instruct` only when `whisper` is true).
  - A `design` profile's `POST /profiles` call includes `ref_text`: the
    display text (tags stripped, `[[written|spoken]]` shown as written) of
    the speaker's first line with non-empty display text, or omitted if none.
    VoiceStudio renders its preview from this text and stores it as the
    profile's reference audio; without `ref_text` it falls back to its own
    sample script, so the transcript that OmniVoice needs at every later
    `/generate` call isn't known and must be auto-transcribed — which fails
    outright for some design voices (e.g. no usable speech, or ASR silently
    returns empty) if no fallback ASR model is installed.
  - The response body is the WAV; `X-Audio-Duration` and `X-Seed` headers are
    recorded. `503` with `X-OmniVoice-Retryable: true` maps to `transient`;
    `409 model_not_downloaded` maps to `auth` (a setup problem that stops the
    run); `400` maps to `invalid`.
  - Saves the WAV, trims its take edges to 50 ms of padding around the audible
    audio (VoiceStudio leaves ~150-200 ms of silence on each edge), and
    measures duration with ffprobe, so `pause_after_ms` is the actual audible
    gap between lines rather than pause_after_ms plus untrimmed take padding.
  - QC per line: transcribe back via `POST /v1/audio/transcriptions` (`response_format=verbose_json`, `timestamp_granularities[]=word`), compute the character
    error rate against `text`, and check the speaking rate against the language
    band. On failure, retake with a new seed (max 2).
- **`sf_image`**: builds each plate or slide request (prompt file + references),
  calls the provider, validates the output (exists, decodable, correct aspect
  within tolerance), records hash and status. Plates run before slides.
- **`sf_contact_sheet`**: grid of plates then slides, labeled with ids and the
  first words of each slide's lines.
- **`sf_align`**:
  - Per line, sends the WAV to `POST /v1/audio/transcriptions` (`response_format=verbose_json`, `timestamp_granularities[]=word`) and reads word times from the top-level `words` list it returns. A startup probe on the first line checks
    that shape; if word times are absent, every line takes the approx
    fallback and QC reports it.
  - Aligns ASR tokens to the **script's** tokens with difflib and transfers the
    times. Captions always show script text, never ASR text. Script tokens
    are the line's display text: expressive tags removed and each
    `[[written|spoken]]` override replaced by its `written` half.
  - Unmatched tokens are interpolated between matched neighbors. A line with no
    usable match falls back to a character-length-weighted split, flagged
    `approx: true`.
  - Stores word times **relative to the line start**, so changing one line
    never invalidates another line's words. Captions and render add the
    line's start from the timeline.
- **Plate aspects:** face `1:1`, half `3:4`, full `9:16`; location plates use
  the production aspect.
- **`sf_captions`**: builds `captions.ass` from the named style preset:
  - `karaoke`: `\kf` tags per token.
  - `plain`: one cue per line chunk.
  - `none`: no file.
  - Speaker colors come from `cast[].caption_color`; placement from
    `text_placement`; the ASS canvas matches the output resolution.
- **`sf_render`**:
  - Timeline: line start = previous start + measured duration + `pause_after_ms`.
    Accumulated in milliseconds, converted to frames only at slide boundaries,
    so there is no drift. A slide spans its lines.
  - Picture: scale/crop each image to 1080×1920 or 1920×1080; `zoompan` motion
    per `motion`; hard cuts.
  - Audio: concatenate the line WAVs with pauses; resample to 48 kHz; `loudnorm`.
  - Output: burn `captions.ass`; H.264 yuv420p, 30 fps, AAC 48 kHz.

### 8.4 QC (`sf_qc.py` measures and writes `out/qc.json`; `sf-finishing` interprets and acts)

- Every line has audio and every slide has an image (`done`).
- Final duration equals audio timeline ±1 frame.
- No caption cue ends after its line or overlaps the next speaker's cue.
- No caption runs outside its safe zone (line length vs preset limits).
- No silence gap longer than `pause_after_ms` + 300 ms; a silence that instead
  falls inside a line's own audio span (e.g. a rendered in-line `[pause]` tag)
  is allowed up to that tag's duration + 300 ms + a 400 ms engine-calibration
  allowance for VoiceStudio's per-span synthesis padding, or up to 1.3 s
  (a 1 s engine-calibration allowance for OmniVoice's natural sentence-break
  pause + 300 ms) when the line's display text has a sentence break (`. ! ? … ; :`)
  before its final character, whichever allowance is larger. No clipped final
  line.
- Output resolution matches `aspect`.

Auto-fixable: caption re-wrapping, re-render after a regenerated asset.
Everything else is reported.

## 9. Series and localization

- **Series:** the canon uses `form: serial`, `season-goal` in `story.md`, and
  `episode-question` per chapter. One production per episode:
  `projects/<story-id>-e<NN>-<aspect>-<lang>/`. Recurring characters resolve
  through `library/cast/<ref>` so voices and plates are shared across episodes.
- **Localization (v1.1, designed for now):**
  1. Translate the canon with the `adaptation` translation workflow into
     `stories/<story-id>-<lang>/`, keeping the same ids.
  2. Create a production for that language with a top-level `image_source`
     field (added to the schema in v1.1) pointing at the base production.
     Slides with the same id reuse its images, because images never contain
     text.
  3. Only voices, captions, and the render are generated anew.

## 10. Testing

- One `tests/test_<script>.py` per script, run with pytest, against a
  fixture production:
  - `validate`: rejects dangling references and bad enums.
  - `align`: a known word/time set maps onto script tokens, including an
    ASR substitution and a missing word.
  - `captions`: snapshot of the generated ASS for karaoke and plain.
  - `render`: fake images + synthetic sine WAVs → MP4 whose duration matches
    the audio timeline within one frame.
- **Smoke run:** `projects/smoke-test` through the whole pipeline with the `fake`
  image provider and real VoiceStudio.

## 11. Out of scope for v1

- Background music and SFX (addable later as an optional stage between
  captions and render).
- Upload, SEO metadata, thumbnails.
- Remotion or any render path other than FFmpeg/ASS.
- Scheduling many videos unattended.
- Commercial-license engine filtering.
- Localization implementation (§9 is v1.1).

## 12. Risks and prerequisites

- **Image provider availability** depends on the user's Antigravity wrapper;
  its terms-of-service and account risk are the user's. The `fake` provider
  keeps development unblocked.
- **VoiceStudio must be running** (desktop app or backend) with the OmniVoice
  model installed; `sf_voice` fails fast with instructions otherwise.
- **FFmpeg needs libass** for caption burn-in; `sf_render` checks it at start.
- **Story CLI checks are English-centric** (`prose`, `voices`): advisory only
  for non-English canon.
- **ASR alignment quality varies by language**; low-resource languages may fall
  back to `approx` timings more often. QC reports the approx ratio per
  production.
