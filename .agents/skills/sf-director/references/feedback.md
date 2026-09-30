# Feedback flow (`/story-feedback <slug> "<feedback>"`)

The only path that writes `library/taste.md`.

1. Split the feedback into points. For each point decide:
   - **item fix** — names or clearly implies slides, lines, characters or locations (`S03`, "Bống's voice", "the ending");
   - **taste rule** — a preference that should hold beyond this video ("less text per slide", "warmer colors", "child voices younger");
   - usually both.
2. For each taste rule, append to `library/taste.md`:

       - T### [scope tags] <rule, imperative, one sentence>
         ← <slug> · <YYYY-MM-DD> · "<the user's words, verbatim>"

   Next id = highest existing T number + 1. Scope as narrow as the feedback implies
   (e.g. `vi · audio` for a Vietnamese voice remark; `global` only if the user says always/every).
   If it contradicts an existing rule of the same or broader scope, delete that rule and write
   "(replaces T###)" at the end of the new rule. If an existing rule already says the same, do nothing.
3. **Agent Evolution & Knowledge Persistence (CRITICAL):**
   - In addition to `library/taste.md` (and `library/checks.md` for objective bugs), actively update `AGENTS.md` and the relevant skill markdown files (`sf-visual`, `sf-script`, `sf-audio`, `sf-director`) to permanently record the user's feedback lessons. Future agent sessions read these files upon startup and will immediately inherit the refined behavior without repeating past mistakes.
4. Apply item fixes through the owning skill: `sf-script` (text), `sf-visual` (prompts, seed), `sf-audio`
   (voice description, casting — re-cast with `--only <cast id>`). Then re-run only the affected
   stages and everything downstream: images → contact sheet; voice → align → captions → render → qc.
5. Run `sf_learn`; confirm `library_problems` is empty.
6. Report: rule ids written or replaced, items redone, new video path.

