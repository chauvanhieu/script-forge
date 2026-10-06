---
name: sf-visual
description: Writes StoryForge style bibles, character/location plate prompts and slide prompts, and self-reviews the contact sheet at Gate 2. Use for stage 4 (images) and 5 (Gate 2) of a StoryForge production.
---

# sf-visual

## Prompts
- Formula: style → subject/appearance → action → setting → shot → light → continuity → exclusions.
- **Character Visual Continuity (T020):** Every recurring character MUST have an immutable set of visual anchor traits (exact age, hairstyle/hair color, facial structure, consistent wardrobe and signature accessories) defined in `cast`. Repeat these descriptive anchor tokens verbatim in every slide prompt where the character appears. Leverage character face/half plates (`plates/c_*.png` or passed via `ImagePaths` in Gemini `generate_image` calls) to maintain unmistakable cross-shot character fidelity throughout the story. **Single-Hero Plate Injection:** In each slide prompt, inject at most ONE character reference plate into `ImagePaths` representing the focal hero of that shot. Never inject multiple character plates into a single prompt to avoid AI blending faces or wardrobes between different characters.
- **Role Archetype Sanitization & Era Anchoring (T022):** Prevent role/archetype divergence (e.g. AI turning a vintage petty thief into a modern tactical SWAT officer). Apply Semantic Substitution: replace heavy combat triggers (`breach`, `raid`, `operative`) with period-accurate civilian terms (`petty prowler`, `vintage civilian trespasser`, `prying an old iron latch`). Enforce Negative Archetype Filters for civilian/criminal prompts: `(no SWAT, no tactical gear, no bulletproof armor, no modern police badges, no combat helmets, no modern weapons)`. Anchor historical era and retro props: `1970s vintage era, incandescent warm yellow bulb flashlight, worn retro attire, no modern LED lights, no modern digital devices`.
- **Physical Plausibility & 2-Shot Mechanical Framing (T023):** Diffusion models cannot compute complex 3D mechanics in one frame. For mechanical traps, devices, and physical mechanisms, mandate the **2-Shot Cause-and-Effect Pair**: Shot 1 (The Trigger Setup — macro close-up of the exact mechanical contact point with force vector, e.g. cord looped securely behind the trigger shoe from an anchor post) followed by Shot 2 (The Vector Perspective — downward angle from gun barrel toward the door gap at ankle height). Never cram impossible Rube Goldberg mechanics into one shot or over-segment into 4+ slides that destroy video pacing.
- **Ultra-Contrast Visual Shock & Hook Optical Power (T025):** Slide 1 and Slide 2 (Hook 0:00–0:06) must command instantaneous visual attention with Ultra-High Contrast Chiaroscuro: pair 80% deep obsidian shadows with 20% intense warm amber rim lighting (`#F5A623`) or cutting volumetric spotlights. Ban flat lighting, washed-out palettes, and low-contrast midtones in the opening hook to guarantee thumb-stopping power on mobile screens. Mandate tokens for Slide 1-2: `ultra-high contrast chiaroscuro noir, blinding amber rim lighting against ink obsidian black, extreme macro focus, visceral tension, hyper-crisp 8k documentary still, no washed-out tones, zero flat lighting`.

- Face plates: "head-and-shoulders portrait, face fills the frame". Half: waist up. Full: head to toe, neutral background.
- State counts explicitly (people, moons, lanterns). End every prompt with: full-frame dynamic composition, no text, no letters, no logos, no watermarks (per T002: do not mandate an empty lower third or text section at the bottom).
- Apply every matching image check in `library/checks.md` and every visual taste rule while writing, not only when reviewing.

## Generate
- **Image Model Preference (Antigravity first):** When running in Google Antigravity, prioritize generating video slide images using Gemini 3.1 Flash Image via the agent's built-in image tool (`generate_image`) for ultra-fast generation and high fidelity. Only fallback to local FLUX.2 (`SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>`) when running in other IDEs (Cursor, Claude Code, terminal) or when the native tool is unavailable.
- **The 2-Turn Production Pipeline (Plate-First Architecture):**
  1. **Turn 1 (Master Anchor Plates Batch):**
     Before generating slide images, generate character reference plates for recurring characters (`cast[].plates.face`, `1:1`) and key location master plates (`locations[].plate`, aspect matching brief) using `generate_image`.
     Naming format: `<slug>_c01_face`, `<slug>_c02_face`, `<slug>_loc01_master`.
     Immediately run:
     `uv run scripts/sf_sync_gemini_images.py projects/<slug>`
     This syncs plates into `plates/`, updates hashes, and verifies base visual anchors before rendering slides.
  2. **Turn 2 (Full Video Slides Mega-Batch with Single-Hero Injection):**
     The agent MUST read all visual prompts directly from `story.json` and dispatch ALL `generate_image` tool calls (20–26 slides) in ONE single turn (concurrent tool call array).
     Naming format: `<slug>_s01`, `<slug>_s02`, ... `<slug>_sXX`.
     **Single-Hero Plate Injection:** If the slide features a recurring character, pass `ImagePaths: ["plates/<hero_id>_face.png"]` (e.g. `["plates/C01_face.png"]`). Never pass multiple character plates into the same call to avoid blending. If the scene has no characters, optionally pass `ImagePaths: ["plates/<loc_id>.png"]` to fix room geometry.
     Immediately run:
     `uv run scripts/sf_sync_gemini_images.py projects/<slug>`
     This automatically syncs all images into `images/`, computes sha256 input_hashes, updates `story.json`, and generates `out/contact_sheet.png` in under 1 second.
- **Targeted Fallback:** If any individual slide fails or gets blocked, fallback only for that specific slide: `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug> --only Sxx`.
- **Image Diversity & Pacing (T003):** Maintain high image count targeting rapid transitions of 1.5s–2.5s per slide cut. When multiple slides share the same voice segment to increase pacing, THE GENERATED IMAGES MUST BE TRULY DISTINCT (different camera angles, actions, shot sizes). Absolutely do not duplicate or clone the same image across multiple slides.

## Gate 2 self-review
1. Read `projects/<slug>/out/contact_sheet.png`; open any doubtful tile at full size (`images/<id>.png`, `plates/<id>.png`).
2. Flag objective defects: wrong count, duplicated objects, text/signatures, wrong character look vs its plates,
   missing `must_show`, present `must_not_show`, cluttered lower third, anatomy errors.
3. For each flagged item: edit the prompt (fix the cause), change `image.seed`, run `sf_image --only <ids>`,
   rebuild the contact sheet. Max 2 rounds, then ask the user with the sheet path.
4. Record each defect in `library/checks.md` (new check or `hits` bump) per sf-director rules.
