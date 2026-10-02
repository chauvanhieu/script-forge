# Feedback flow (`/story-feedback <slug> "<feedback>"`)

The pathway for continuous learning, fixing projects, and updating taste rules.

1. Determine the project's channel:
   - Check `projects/<slug>/story.json` -> `brief.channel`.
   - If not set, check project's metadata or default to the active channel (e.g. `the-grey-verdict`).
2. Split the feedback into points. For each point decide:
   - **item fix** — names or clearly implies slides, lines, characters or locations (`S03`, "voice tone", "the ending");
   - **taste rule** — a preference that should hold beyond this video ("less text per slide", "warmer colors", "child voices younger");
   - usually both.
3. **2-Tier Feedback Routing (CRITICAL):**
   - **Tier 1 (Channel-Specific Aesthetics & Taste):** If the preference relates to the channel's creative identity, narrative formula, brand palette, character archetype, or thumbnail styling, append it to `channels/<channel-slug>/taste.md`. Do NOT write it to `library/taste.md` of the core engine to prevent cross-channel cognitive bleed.
   - **Tier 2 (Universal Engine Mechanics):** If the rule is a core technical principle for all channels (FFmpeg container flags, safe margins, subtitle alignment, general pacing), append to `library/taste.md` and/or `library/checks.md`.
4. Formatting rules:
   - In `library/taste.md` or `channels/<channel-slug>/taste.md`:
     - T### [scope tags] <rule, imperative, one sentence>
       ← <slug> · <YYYY-MM-DD> · "<the user's words, verbatim>"
5. Apply item fixes through the owning skill: `sf-script` (text), `sf-visual` (prompts, seed), `sf-audio`
   (voice description, casting — re-cast with `--only <cast id>`). Then re-run only the affected
   stages and everything downstream: images → contact sheet; voice → align → captions → render → qc.
6. Run `sf_learn`; confirm `library_problems` is empty.
7. Report: channel taste updated, rule ids written or replaced, items redone, new video path.

