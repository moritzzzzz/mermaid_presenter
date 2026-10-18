---
name: process-to-sketch
description: "Turn a business workflow description or discovery transcript into an Architecture Viewer process sketch: technical discovery, pains, the as-is process, and a proposed human-in-the-loop architecture on a software stack the developer chooses (for example Mapbox, AWS, or Grok Bot + Cursor API + GitHub), researched from its official documentation. Use when asked to map, sketch or automate a process, or to create or update a sketch in projects/<id>/."
---

# Process to sketch

Apply the rules in `.cursor/rules/`: `data-boundaries.mdc`, `stack-proposal.mdc` and `sketch-format.mdc`. Cursor applies them itself, and Claude Code loads them through `CLAUDE.md`. Any other assistant reads them first. Write each new sketch to its own new project directory `projects/<slug>-<YYYYMMDD-HHMMSS>/<slug>.md`, from [sketch-template.md](sketch-template.md), in the format of [format_specification.md](format_specification.md) §8, with the roles and blocks of [architecture-pattern.md](architecture-pattern.md), filled with the stack the developer chose and researched as in [stack-research.md](stack-research.md).

## Procedure

0. **Ask which software stack to prefer.** The developer who launched you decides the stack of the proposed architecture. Before anything else:
   - If their prompt already names the stack (products, vendors or a platform), use it and don't ask again. Restate it in one line so they can correct you.
   - Otherwise ask them, in one message, and **wait for the answer** before you continue:
     1. Which software stacks or products should the proposed architecture prefer? For example "Mapbox (Studio, Tiling Service, Directions API)", "AWS Step Functions + Lambda + S3", or "Grok Bot + Cursor API + GitHub".
     2. Is anything ruled out (a vendor, a channel such as email, a hosting region)?
     3. Do you have documentation links or an existing reference design I should start from?
   - If they answer "you choose", propose one or two stacks that fit the input, each with a one-line reason, and wait for their pick.
   - Don't create files or design anything before the stack is settled. Reading the input to ask a better question is fine.

1. **Create a new project directory.** Every new sketch goes into a new directory with a unique name, never into an existing one. Pick a short title for the process (for example "ACME hiring") and run:

   ```bash
   python3 scripts/new_project.py "<Title>" --json
   ```

   It creates `projects/<slug>-<YYYYMMDD-HHMMSS>/` (UTC timestamp, with `-2`, `-3` … appended if the name is taken) and returns `id`, `project_dir`, `sketch` and `stack_notes`. Write the sketch to the `sketch` path and use `id` as the JSON `id`. Don't make up the directory name yourself, and don't create the directory any other way.

2. **Research the stack in its official documentation**, following [stack-research.md](stack-research.md). Do this before you design the proposed board:
   - Use only the vendor's own documentation, API reference, pricing and limits pages, and the developer's links. Not memory, not third-party posts.
   - Map the products onto the roles of [architecture-pattern.md](architecture-pattern.md) §1 and confirm each capability you plan to draw.
   - Write `stack-notes.md` to the `stack_notes` path, with the source URL for every claim and the role map at the end.
   - Without web access, ask the developer for the documentation (see stack-research.md §3) instead of guessing.

3. **Read the input completely.** It's the file or text the user names, for example `process_description_transcript.md`. Read [format_specification.md](format_specification.md) §8 and [architecture-pattern.md](architecture-pattern.md) before you write the sketch.

4. **Discovery.** Fill the discovery keys of spec §8.2 (`usecase.*`, `process.*`, `pains.*`, `quant.*`, `blockers.*`, `success.*`, `decision.*`, `rollout.*`, `next.*`) from the input:
   - Take the customer's words and numbers. Keep `SYNTHETIC` labels from the input.
   - Mark what you assume as `ASSUMED`. Write "Not stated" where the input is silent, or leave the key out.
   - Put the customer's decision process (who decides, who pays, how a vendor gets bought) into `decision.*`. Put the metrics leadership watches into `decision.criteria` and `success.kpi`.
   - Put stack constraints the research found (data residency, limits at the customer's volume, missing capabilities) into `blockers.*` or `next.questions`.

5. **Pains.**
   - One row per pain the customer named: P1, P2, … in the order they gave them, in their words, each with its cost (time, money, risk or rework) taken from the input.
   - Don't add pains the customer didn't name. Put observations of your own into `next.questions`.

6. **As-is board** (keys `Ⓐ Ⓑ Ⓒ …`):
   - Write one step per handoff or wait, in the order the work happens. Each step has its `Who`, `Tool` and `Wait`, taken from the input.
   - People and roles are `person`, tools are `box`, inboxes, spreadsheets and shared drives are `store`. Group by team or department as top-level subgraphs. People who act across teams stay outside.
   - Tag each pain on the step(s) where it happens: `⚠ P1` as the last line of the box label, and `⚠ P1 <text>` in the `Pain` cell.
   - Use as many steps as the process has: enough that every wait the customer described is visible. For a complex process, 8-14 steps is a good range; a simpler process can have fewer. Don't add steps to reach a number.

7. **Proposed board** (keys `① ② ③ …`):
   - Build it from the blocks in [architecture-pattern.md](architecture-pattern.md) §2, renamed for this process, and run each block on the component that `stack-notes.md` maps to its role. Draw it as in §4: environments `E1`, `E2` … named after the products, plus `EXT`.
   - Use only components confirmed in `stack-notes.md`. Anything else is `ASSUMED` with a question in `next.questions`.
   - Find every point where the customer said a person decides, and every decision the business can't hand to software (spend, anything affecting a person, anything sent outside or published). Put a 🔒 gate there. Each gate is followed by "record decision", and has a dashed `needs_info` loop back to the worker when the worker's output is what's being judged.
   - Give each kind of automated work (drafting, research, matching, processing, conversion) its own worker box, named after the product feature that does it. Its output goes to the review surface.
   - Add the guardrail blocks: append-only record, release of the approved version only, status/stuck view. The status view also reports the customer's KPIs from the record timestamps.
   - Every step has an owner and one sentence of what happens. `Removes` names the pains it removes. A guardrail leaves `Removes` empty.
   - For a complex process, 10-18 steps is a good range; a simpler process can have fewer. Prefer a clear main path over completeness.

8. **Close the loop.**
   - Every pain must be removed by at least one proposed step. If not, write `**Not removed yet**` in the scorecard and say why under `next.questions`.
   - The scorecard's `Measure` uses the customer's own metrics and baseline → target where they gave them, for example "hiring duration: ~3 months → < 4 weeks".

9. **Implementation notes.** Add the `## Implementation notes` table of [architecture-pattern.md](architecture-pattern.md) §5, filled for this process and stack: what is built or configured on each component, the record schema's key fields, the routing rules, credentials (names and scopes only), limits and cost at the customer's volume, and the main documentation sources. Also add one line on how the proposal passes the customer's vendor process (for example security review: where data is stored, least-privilege credentials, humans approve).

10. **Write the JSON** (spec §8.2) as the last thing in the file. It describes exactly the same groups, boxes, arrows, steps and pains as the Markdown:
    - `"v":3`, `id` = the project's `id` from step 1 (the directory name, so each project opens as its own sketch in the viewer), `dir` set to `"LR"` or `"TD"` on both boards
    - Labels without keys or `⚠` tags
    - Every edge with an `id`
    - Never a raw `--` (see `sketch-format.mdc`)

    Build the JSON by walking the two diagrams line by line: one node per box, one edge per arrow, one step per table row, in the same order.

11. **Validate.** Run:

    ```bash
    python3 scripts/check_sketch.py projects/<id>/<slug>.md
    ```

    Fix every `ERROR` and re-run until it prints `OK`. Look at each `WARN` and fix it unless you have a reason not to.

12. **Report back** in a few lines:
    - the stack used, and any product you added beyond the developer's preference, with the reason
    - the project directory, the sketch path and the `stack-notes.md` path
    - the number of pains, as-is steps, proposed steps and 🔒 gates
    - any `ASSUMED` values (including unconfirmed stack capabilities) and pains `Not removed yet`
    - how to open it: `python3 ../serve.py projects/<id>/<slug>.md --open`, run from this workspace (Present for the walkthrough, Edit for discovery and pains, `O` for the overview)

## Updating a sketch

- Update a sketch only when the user names its project (for example `projects/acme-hiring-20261018-101500/`). Then edit the file in that directory, don't create a new project, and keep its JSON `id`, so the viewer updates the stored sketch instead of opening a second one. Keep the step keys stable where steps are unchanged.
- Keep the stack recorded in that project's `stack-notes.md` unless the user asks for a different one. A new stack means new research (step 2) and an updated `stack-notes.md`.
- If the file has an `fnv=` fingerprint in the JSON header line, the viewer wrote it. Remove the `fnv=…` part when you change the Markdown, so Edit doesn't ask which version to use. Keep `log` and other fields as they are.

## Don'ts

- Don't choose the stack for the developer, and don't design before it's settled.
- Don't draw a component or capability from memory. It comes from `stack-notes.md`, or it's marked `ASSUMED`.
- Don't add products outside the chosen stack to the proposed board without saying why. Existing customer systems that stay go into `EXT`.
- Don't let a worker decide anything. A worker box never leads straight to an outcome without a 🔒 gate in between, unless no person decides anything in the process.
- Don't invent customer numbers or quotes.
- Don't overwrite, move or delete another project's directory. A new run of the skill on the same input is a new project.
