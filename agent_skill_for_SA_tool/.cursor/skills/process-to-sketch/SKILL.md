---
name: process-to-sketch
description: "Turn a business workflow description or discovery transcript into an Architecture Viewer process sketch: technical discovery, pains, the as-is process, and a proposed human-in-the-loop architecture on a software stack the developer chooses (for example Mapbox, AWS, or Grok Bot + Cursor API + GitHub), researched from its official documentation. Use when asked to map, sketch or automate a process, or to create or update a sketch in projects/<id>/."
---

# Process to sketch (Cursor entry point)

The skill is shared between Cursor and Claude Code. Its procedure and reference files live in the neutral folder `skills/process-to-sketch/`, so every tool follows the same instructions.

1. Read `skills/process-to-sketch/SKILL.md` and follow it step by step, starting with step 0 (ask the developer which software stack to prefer, unless the prompt names one).
2. Links in that file (`format_specification.md`, `architecture-pattern.md`, `stack-research.md`, `sketch-template.md`) are relative to `skills/process-to-sketch/`. Read them from there.
3. The rules it names (`data-boundaries.mdc`, `stack-proposal.mdc`, `sketch-format.mdc`) are in `.cursor/rules/`. Cursor already applies them.
4. Run the scripts from the workspace root (this folder): `scripts/new_project.py` and `scripts/check_sketch.py`.
