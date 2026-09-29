---
description: Redo named items of a StoryForge production (no taste change)
argument-hint: "<slug> <id>[,<id>...]"
---

Use the `sf-director` skill. Arguments: $ARGUMENTS

Redo exactly these items (slides S##, lines L###, cast C## (voice re-cast), plates C##_face etc.,
locations LOC##): re-run the owning script with `--only <ids>` and then every downstream stage
(contact sheet; or align → captions → render → qc). Do not write `library/taste.md`.
