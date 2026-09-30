---
name: sf-visual
description: Writes StoryForge style bibles, character/location plate prompts and slide prompts, and self-reviews the contact sheet at Gate 2. Use for stage 4 (images) and 5 (Gate 2) of a StoryForge production.
---

# sf-visual

## Prompts
- Formula: style → subject/appearance → action → setting → shot → light → continuity → exclusions.
- The image model sees only the prompt plus the slide's character **face** plates and location plate
  (max 4). Repeat each visible character's key appearance words verbatim in every slide prompt.
- Face plates: "head-and-shoulders portrait, face fills the frame". Half: waist up. Full: head to toe, neutral background.
- State counts explicitly (people, moons, lanterns). End every prompt with: clean lower third, no text, no letters, no logos, no watermarks.
- Apply every matching image check in `library/checks.md` and every visual taste rule while writing, not only when reviewing.

## Generate
`SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>` then
`uv run scripts/sf_contact_sheet.py projects/<slug>`.

- **Image Model Preference:** Prioritize generating images using `nanobanana` (optimized for Antigravity environment with Gemini 3.1 flash image) for better performance. Only fallback to `flux` if `nanobanana` fails or is unavailable.
- **Image Diversity:** When multiple slides share the same voice segment to increase pacing, THE GENERATED IMAGES MUST BE TRULY DISTINCT (different camera angles, actions, shot sizes). Absolutely do not duplicate or clone the same image across multiple slides just to meet the slide count.

## Gate 2 self-review
1. Read `projects/<slug>/out/contact_sheet.png`; open any doubtful tile at full size (`images/<id>.png`, `plates/<id>.png`).
2. Flag objective defects: wrong count, duplicated objects, text/signatures, wrong character look vs its plates,
   missing `must_show`, present `must_not_show`, cluttered lower third, anatomy errors.
3. For each flagged item: edit the prompt (fix the cause), change `image.seed`, run `sf_image --only <ids>`,
   rebuild the contact sheet. Max 2 rounds, then ask the user with the sheet path.
4. Record each defect in `library/checks.md` (new check or `hits` bump) per sf-director rules.
