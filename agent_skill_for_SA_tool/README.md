# Agent skill for the SA tool: process → architecture sketch

An AI coding-assistant skill for **Cursor** and **Claude Code** that turns a business workflow description into a **process sketch** for the [Architecture Viewer](../README.md), the tool this folder sits in. The sketch has:

- **Technical discovery** and **Pains** from the description
- the **As-is process** as a Mermaid flowchart + step table
- a **Proposed architecture**: a human-in-the-loop automation on the **software stack you choose** (for example Mapbox, AWS, or Grok Bot + Cursor API + GitHub), researched from the stack's official documentation, with 🔒 approval gates where people decide
- a **Pain scorecard** and **Implementation notes**
- the sketch as JSON, so the viewer's Edit mode opens it

All data is synthetic.

The skill is stack-agnostic. At the start it asks you which software stacks to prefer, unless your prompt already names them. It then researches those stacks in their official documentation, writes what it found with sources to `stack-notes.md`, and only then designs the proposed process. A version that always uses the Grok Bot + Cursor API + GitHub stack is kept outside this repo as `agent_skill_for_SA_tool_grok_stack/`.

## What's in here

| Path | What it is |
|---|---|
| `process_description_transcript.md` | Test input: SYNTHETIC discovery call about ACME's email-driven hiring process |
| `skills/process-to-sketch/SKILL.md` | The skill: procedure from input to validated sketch. **Single source of truth**, in a neutral folder that no tool owns |
| `skills/process-to-sketch/format_specification.md` | Copy of the viewer's [`format_specification.md`](../format_specification.md), so this folder works as its own workspace. Keep the two in sync |
| `skills/process-to-sketch/architecture-pattern.md` | Stack-agnostic roles (front door, orchestrator, worker, system of record, review surface, release target), building blocks, guardrails and diagram conventions |
| `skills/process-to-sketch/stack-research.md` | How to research the chosen stack from official documentation, and the `stack-notes.md` template |
| `skills/process-to-sketch/sketch-template.md` | Skeleton of the sketch Markdown + JSON |
| `.cursor/rules/stack-proposal.mdc` | Always on: ask for the stack, use only documented components of it, human gates |
| `.cursor/rules/sketch-format.mdc` | For `projects/**/*.md`: location and hard format rules from spec §8 |
| `.cursor/rules/data-boundaries.mdc` | Always on: synthetic data, `ASSUMED` / `SYNTHETIC` labels |
| `.cursor/skills/process-to-sketch/SKILL.md` | Cursor entry point: same name and description, points to `skills/process-to-sketch/` |
| `.claude/skills/process-to-sketch/SKILL.md` | Claude Code entry point: same name and description, points to `skills/process-to-sketch/` |
| `CLAUDE.md` | Claude Code project memory: imports the three `.cursor/rules/*.mdc` files with `@` imports |
| `.claude/settings.json` | Claude Code: lets the two scripts run without a permission prompt |
| `scripts/check_sketch.py` | Validator for the spec's checklist (§10), standard library only |
| `scripts/new_project.py` | Creates a new, uniquely named project directory `projects/<slug>-<YYYYMMDD-HHMMSS>/` for each sketch, and returns the paths of the sketch and its `stack-notes.md` |
| `projects/` | Created on the first run. One directory per sketch (the sketch plus `stack-notes.md`), never overwritten |

## Run it

Every assistant does the same thing:
1. It asks which software stacks to prefer, unless your prompt names them, and waits for your answer.
2. It creates a new project directory with `python3 scripts/new_project.py "ACME hiring"`, for example `projects/acme-hiring-20261018-101500/`.
3. It researches the stack in its official documentation and writes `stack-notes.md` (sources included) into that directory.
4. It writes `acme-hiring.md` into that directory.
5. It runs `scripts/check_sketch.py` on the file and fixes errors until it prints `OK`.

Each run creates a new project, so you can compare runs, assistants and stacks side by side. You need Python 3.10+, and the assistant needs web access for the research step (or you give it the documentation pages).

### Cursor (IDE)

1. Open **this folder** (`agent_skill_for_SA_tool/`) as the workspace, so Cursor picks up `.cursor/rules/` and `.cursor/skills/`.
2. In the Agent chat, ask:
   > Use the process-to-sketch skill on `process_description_transcript.md`.

   or name the stack right away, so it doesn't ask:
   > Use the process-to-sketch skill on `process_description_transcript.md`. Prefer the Mapbox stack.

   For the research step, Cursor's agent uses web search. You can also add the vendor's documentation to Cursor as a doc (`@Docs` → add new doc) and mention it in the prompt.
3. Optional: if **Cursor Settings → "Include third-party Plugins, Skills, and other configs"** is on, Cursor also loads `CLAUDE.md` and `.claude/skills/`. That's harmless here: they point to the same rules and the same skill, so Cursor just sees them twice. You can turn the setting off to avoid that. `.cursorignore` doesn't stop this loading, so don't add `CLAUDE.md` there.

### Claude Code

1. Start Claude Code **in this folder**, so it picks up `CLAUDE.md`, `.claude/skills/` and `.claude/settings.json`:
   ```bash
   cd agent_skill_for_SA_tool && claude
   ```
2. Ask the same question, or call the skill by name:
   > /process-to-sketch process_description_transcript.md, prefer Mapbox

   Claude Code asks before its first web search or fetch in the research step. Approve those, or allow them in `.claude/settings.json`.
3. Check the setup if needed:
   - `/memory` should list `CLAUDE.md`, with the three imported rules.
   - The skill should appear when you type `/`.
   - On the first start, Claude Code asks once to approve the `@` imports in `CLAUDE.md` and the project settings. Approve both, or the rules and the script permissions aren't loaded.

### Other assistants (Codex, Copilot, Windsurf, a chat model …)

The skill is plain Markdown plus two Python scripts, so any assistant that can read files and run commands can use it:
1. Give it the three files in `.cursor/rules/` as standing instructions (system prompt, custom instructions or the tool's rules file, for example `AGENTS.md`).
2. Ask it to follow `skills/process-to-sketch/SKILL.md` on `process_description_transcript.md`.

A chat model without file access gets the transcript, `SKILL.md`, `architecture-pattern.md`, `stack-research.md`, `sketch-template.md` and spec §8 pasted in, plus your stack choice and, if it can't browse, the relevant documentation pages. You then run the two scripts yourself.

### View the result

```bash
python3 ../serve.py projects/<id>/acme-hiring.md --open
```

The page reloads when the file changes. You can also start `python3 ../serve.py` and open the file with the file picker or by drag and drop. Then check:
- **Present:** both boards, with the as-is steps Ⓐ… showing ⚠ pain tags and the proposed steps ①… walking through
- **Overview** (`O`): one group per environment of the chosen stack (`E1 · <product>`, `E2 · <product>` …) plus Existing systems
- **Edit:** opens the sketch with discovery, pains and owners filled in

## How Cursor and Claude Code share one skill

| Need | Cursor reads | Claude Code reads | Shared file |
|---|---|---|---|
| Skill (procedure) | `.cursor/skills/process-to-sketch/SKILL.md`, a thin pointer | `.claude/skills/process-to-sketch/SKILL.md`, a thin pointer | `skills/process-to-sketch/` (SKILL.md and its reference files) |
| Always-on rules | `.cursor/rules/*.mdc` (`alwaysApply`, `globs`) | `CLAUDE.md`, which `@`-imports the same `.mdc` files | `.cursor/rules/*.mdc` |
| Running the scripts | Cursor's own run approval | `.claude/settings.json` allow list | `scripts/*.py` |

Edit the procedure only in `skills/process-to-sketch/`, and the rules only in `.cursor/rules/`. The rules stay there because Cursor needs their `alwaysApply` / `globs` frontmatter, and Claude Code imports them as they are. If the skill's `name` or `description` changes, update it in all three `SKILL.md` files, so every tool triggers the same way.

One difference: in Cursor, `sketch-format.mdc` loads only for `projects/**/*.md`. Claude Code has no glob-scoped rules, so `CLAUDE.md` loads it all the time. It's short, so that's fine.

## What a good result looks like

- 3 pains in the customer's words: P1 insufficient sourcing / thin pipeline, P2 candidate quality, P3 pipeline too slow
- 🔒 gates at least for headcount approval, job description, interview shortlist and offer, matching the transcript's "a person has to approve"
- Worker boxes, on the chosen stack, for drafting the JD, sourcing and matching candidates, and summarizing interview feedback. They draft, people decide
- Every component and capability on the proposed board is listed in `stack-notes.md` with an official documentation link, or marked `ASSUMED`
- The scorecard measures hiring duration (~3 months → < 4 weeks) and interview pass rate (10% → 50%)
- Candidate personal data (GDPR) and ACME's vendor process (research pack → IT security review → purchasing system → pilot) show up in blockers, decision and next steps

## Validator

```bash
python3 scripts/check_sketch.py <file.md>          # human-readable
python3 scripts/check_sketch.py <file.md> --json   # machine-readable
```

Exit 0 means no errors (warnings allowed), 1 means errors, 2 means the file can't be read. `../sample_sketch.md` passes, with 4 expected warnings: 3 because the viewer wrote it, and 1 because it has no `stack-notes.md` next to it.
