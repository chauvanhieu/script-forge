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
1. **Hook Selection & Anti-Template Architecture (T034):**
   - Strictly rotate between 4 distinct Hook Archetypes (never repeat the previous video's archetype):
     - `Hook A (In Media Res / Clinical Trial Forensic Shock)`: Start inside a laboratory scanner, medical examination, or dramatic evidentiary breakthrough.
     - `Hook B (Sensory Shock / Physical Disruption)`: Open with an involuntary physiological reflex or bodily reaction (e.g. the sudden revulsion of "The Ick", pupil dilation in deceit).
     - `Hook C (Evolutionary Counter-Strike)`: Demolish a romantic assumption through brutal prehistoric survival economics.
     - `Hook D (High-Stakes Biological Tradeoff)`: Highlight the severe biochemical consequence of a modern pill, behavior, or habit.
   - **BANNED PHRASING:** Strictly FORBID the "Biology Absolution" sentence frame:
     - ❌ `If you [pain], it was not [weakness]. An [X] surge literally disabled...`
     - ❌ `You were never [foolish/weak], your biology was hijacked. Have you felt this? Share below.`
     - ❌ `Society calls X [myth], but its true purpose is...`
     - Any script containing these phrases FAILS Gate 1 immediately.
   - Construct the **3-Layer Hook**:
     - `Verbal Hook`: Line 1 (< 1.5 s of speech, concise, provocative).
     - `Visual Hook`: Slide 1 prompt (frozen action, intense angle, high contrast chiaroscuro).
     - `Text Hook`: On-screen overlay text providing complementary context.
2. **Escalation Engine:** Map the story progression strictly with **"But..."** (obstacle/conflict) and **"Therefore..."** (reaction/consequence) per `references/viral-storytelling.md`. Eliminate all linear "And then..." transitions.
3. **Payoff Delivery & Novel Outro (T034):** Ensure the climax/ending resolves the question or tension promised in the hook without clickbait. Banish generic outro questions ("Have you felt this? Share below"). Replace with:
   - *Actionable Neuro-Intervention:* A 60-second behavioral counter-hack.
   - *Evolutionary Paradox Dilemma:* A razor-sharp tension between primitive instinct and modern society.
   - *The Seamless Loop:* Final clause links back grammatically to Slide 1.
4. **Platform-Tuned CTA:** Apply a single-action CTA matching `brief.platform_target` per `../sf-director/references/platform-tuning.md`.

## Visual Trope Quarantine (T035)
When drafting slide visual briefs and prompts, verify against the **Quarantined Tropes Blacklist**:
- ❌ **No consecutive Macro Eye / Dilating Pupil opening shots**: If the prior video started with a macro eye, Slide 1 MUST use a human encounter, clinical tool, or architectural space.
- ❌ **No Ancient Campfires**: Strictly ban "ancient hunter-gatherers around a nighttime campfire" to explain evolution. Replace with cave petroglyphs, fossil excavations, ancient clay tokens, or daylight blizzard tracking.
- ❌ **No Translucent 3D Glowing Brains**: Strictly ban cliché 3D holographic glowing brains. Replace with scanning electron microscope (SEM) micrographs, histological tissue slices, retro fMRI thermography displays, or living capillary beds.
- ❌ **No Shattering Embers / Marionette Strings**: Ban abstract crumbling chains and glowing strings. Replace with physical biochemistry (precipitate reactions, protein coagulation, muscle fiber contraction).
- ❌ **No Duplicate Climax Closeups**: Never place two near-identical close-up portraits within 2 slides of each other (e.g. S19 and S21).
- ❌ **No Walking into Light Outros**: Ban solitary figures walking into light beams. Conclude with decisive, grounded physical actions (turning away in the rain, closing a ledger, buttoning a trenchcoat, looking into a microscope).

## Canon (fiction/adaptation)
- Create `stories/<slug>/` with `story-init` conventions (read `.agents/skills/story-init/SKILL.md`).
  Use `scene-craft`, `chapter-writing`, `character-management` only as needed.
- One chapter `chapter-01`, scenes `scenes/chapter-01-scene-NN.md`.
- Check from the canon root: `node /Users/irondev/Desktop/Projects/chauvanhieu/yt/.agents/skills/story-maintenance/scripts/story.js validate` and `links` — clean.
- Factual content has no canon: `canon: null` and `research` notes + claims (see `projects/smoke-test/story.json`).

## Budget & Duration Sweet Spot (T024)
- **Short-Form Target:** Strictly calibrate duration to **48s – 54s** (130–150 words for English, 140–160 words for Vietnamese). Never write bloated scripts over 160 words for Shorts.
- `chars = (target_seconds − Σ pause_after_ms / 1000) × chars_per_s`, where chars are display
characters without spaces and `chars_per_s` is `calibration.speaking_rate[<lang>].chars_per_s` (Vietnamese: ~12.92 chars/s, English fast-paced: ~15.5 chars/s);
without calibration use `references/speaking-rates.md`. Aim within ±5 % of the budget.

## story.json
- **Initialization & Scaffolding:** ALWAYS initialize a new production via `uv run scripts/sf_init.py projects/<slug> [--type factual|fiction|adaptation]`. `sf_init` will automatically prepend a timestamp `YYYYMMDD-HHMMSS-<slug>`. NEVER read, list, or inspect past productions in `projects/`. All asset entries start `pending`. Follow `schemas/story.schema.json`.
- **SEO & 3-Zone Search Indexing Metadata:** Populate `story.seo` using the **3-Zone SEO Architecture**:
  - `title`: High-CTR title (< 65 chars) with primary keyword in first 5 words + power word (SHOCKING, SECRET, DEADLY, IMPOSSIBLE).
  - `hook_title_variants`: 3 ranked variants using proven formulas (Question hook, Statement shock, Number + Stakes).
  - `description`: Structured into 3 zones:
    - **Zone 1 (Above the fold, < 150 chars):** Hook sentence restating title promise + CTA (like/subscribe).
    - **Zone 2 (Body):** Story narrative synopsis, key takeaways, and chapter timestamps.
    - **Zone 3 (Footer Compliance & Discoverability):** Transparent AI disclosure statement (`"Visuals and audio recreated with AI; based on historical records and factual accounts"`), followed by relevant hashtags.
  - `keywords`: 8-15 high-intent niche keywords matching target channel blueprint (`channels/<channel-slug>.md`).
  - `tags_block`: Dedicated comma-separated string (`tag1,tag2,tag3...`) formatted for 1-click copy-pasting directly into YouTube Studio Tags box (< 500 chars).
  - `author`: Channel name or creator brand per channel blueprint.
- Metadata: Record `platform_target`, `hook_archetype`, and `text_hook` in the story or project notes.
- **Entity Taxonomy & Character Continuity (T020/T022):** Define immutable visual anchor traits in `story.cast[].anchor_traits`:
  - `entity_type`: Categorize into 6 precise types:
    - `character`: Human or humanoid individual (base look in ONE outfit only; scene variants come from slide prompts).
    - `location`: Specific setting, architectural space, or landscape.
    - `creature`: Animal, mythical beast, organism, or monster.
    - `visual_asset`: Key prop, vehicle, weapon, evidence item, or relic.
    - `generic_troop`: Crowd, army regiment, civilian gathering, or police unit.
    - `faction`: Organization, government body, clan, or corporation.
  - `tokens`: Concise micro-anchors under 15 words (exact age, facial structure, hair color/style, core clothing, signature prop) repeated verbatim in prompt subjects.
  - `signature_clothing`: Base outfit tokens.
  - `negative_archetypes`: Explicit forbidden roles/gear (e.g. `["no SWAT", "no tactical gear", "no modern police badges", "no combat helmets"]`). Strictly use grounded civilian descriptors (`petty prowler`, `civilian trespasser`) instead of combat triggers (`breach`, `tactical raid`).
- **Real-People & Historical Figures Safety Escalation Ladder:**
  When depicting recognizable real people (presidents, military leaders, historical celebrities), AI safety filters may trigger `PUBLIC_ERROR_UNSAFE_GENERATION`. Follow the battle-tested 4-level escalation:
  1. *Level 1 (Angle Concealment — Recommended Default):* `role_alias` in English (e.g. `The Commander`, `The Iron Premier`). Reference plates and slide prompts MUST specify back view or profile: `"seen from behind"` or `"seen from the left side three-quarter profile"`. Viewers identify the leader from silhouette, posture, and context without showing full facial features. Real names are strictly spoken in voiceover narration, NEVER in image prompts.
  2. *Level 2 (Strip Names):* Remove alias from prompt text; describe physical appearance only (`"distinguished older leader in dark navy suit standing at podium"`).
  3. *Level 3 (Remove Ref Plates):* Clear reference plates on the scene (`character_names: []`) and generate from prompt text alone.
  4. *Level 4 (Negative Archetype Sanitization):* Remove all political/combat trigger words and iconic context.
- Location Catalog & Consistency: Populate `story.locations` with concrete environmental DNA for every unique setting:
  - `era_anchors`: Concrete era markers & prohibited era elements (e.g. `1970s rural midwest, vintage analog era, no modern LED lights, no modern electronics`).
  - `architectural_dna`: Materials, textures, wall/floor finishes, architectural layout.
  - `lighting_palette`: Dominant lighting scheme and shadow temperatures.
  - `negative_filters`: Prohibited modern elements (`no modern vinyl siding`, `no drywall`, `no modern electric sockets`).
  - Slide briefs must reference valid location IDs (`brief.location = "LOC01"`) instead of leaving it null.
- Lines & Zero Dead Air (T024): Written natively in `brief.language`; narration and dialogue on separate lines; short sentences; Line 1 is the Verbal Hook within ~1.5 s; punctuation where the voice should pause; **`pause_after_ms` strictly 60–100ms** (0ms between closely linked clauses to eliminate dead air completely); only reserve 200ms pause after major shock numbers or dramatic verdict reversals. Only allowed tags (`[pause]`, `[pause 500ms]`, `[pause 1.5s]`, the OmniVoice non-verbal tags in `scripts/sflib/text.py`, `[[written|spoken]]`), prefer none.
- Slides & Hyper-Fast Hook Pacing (T027): 
  - **Hook Visual Blitz (0:00–0:06):** In the first 6 seconds, enforce rapid cuts of **1.0s – 1.5s per slide**. Line 1 (Hook narration) MUST be mapped to **3 to 4 distinct image slides** (e.g. extreme macro tension -> wide scene shock -> intense character reaction -> catalytic object). Never let a single image linger more than 1.8s during the opening hook.
  - **Mid-Roll Transitions (6s–40s):** Maintain 1.8s–2.2s per slide cut.
  - **Climax & Outro (40s–54s):** 1.5s–2.2s per slide cut; Slide 1 visual prompt must execute the `Visual Hook`; `source` = canon scene id; no two consecutive slides share scene, pose and shot; vary `motion` (static, push_in, pull_out, pan_left, pan_right) every 2-3 slides; `text_placement` lower_third. Visual prompts are written by `sf-visual` rules.

- Mechanical Logic & Spatial Physics (T023): When describing mechanical traps, crime devices, or props, define `slide.brief.spatial_physics`:
  - Structure visual beats into a **2-Shot Cause-and-Effect Pair**:
    - **Shot 1 (Trigger Setup):** `shot_pair_type: "trigger_setup"`, `contact_point` (macro view of static geometry, e.g. `"taut braided hemp wire looped firmly behind the curved iron trigger shoe"`), `paired_slide_id` pointing to Shot 2.
    - **Shot 2 (Vector Perspective):** `shot_pair_type: "vector_threat"`, `force_direction` (perspective angle along threat vector, e.g. `"downward view from gun barrel toward door gap at ankle height"`), `paired_slide_id` pointing to Shot 1.
  - Provide `physics_negatives` (e.g. `["no floating ropes", "no forward-pointing cords", "no modern lasers"]`). Never compress impossible Rube Goldberg mechanics into a single slide or dilute retention with 4+ slides.
- Write `projects/<slug>/script.md`: story summary, hook archetype, cast table, lines by slide, and text hooks.
- `sf_validate` must print `{"ok": true, "errors": []}`.

## Gate 1 Self-Review
Self-score against **all 14 items** in `references/rubric.md` (Part A Technical + Part B Viral Readiness). Fix every failed item before handing back to `sf-director`.
