---
description: Make (or resume) a StoryForge video from an idea
argument-hint: "<idea>"
---

Use the `sf-director` skill. Idea: $ARGUMENTS

Derive a short kebab-case slug from the idea (Vietnamese diacritics removed). If
`projects/<slug>/story.json` exists, resume it at `state.stage`; otherwise initialize
clean scaffolding with `uv run scripts/sf_init.py projects/<slug>` and run every stage
from brief to report. Never inspect, list or read past productions in `projects/`.
