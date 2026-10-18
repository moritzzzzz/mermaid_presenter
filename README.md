# Solutions Architecture Tool for Discovery, Process Mapping and Architecture Design

A browser tool for solutions architects. Run a **guided technical discovery**, **map the process** as it runs today with its pains, **design the proposed architecture** that removes them, and **present** both, step by step. Everything lives in one Markdown file that people and AI agents can read, write and version.

![Edit mode: the proposed architecture of a deal desk approval, with step ④ selected and the pain it removes](screenshots/create.png)

## What it is for

| Stage | What the tool gives you |
|---|---|
| **1. Discover** | A structured discovery form: use case, current process, pains, quantification, blockers and risks, definition of success, decision process, rollout plan, open questions. Each section shows how complete it is. |
| **2. Map the process today** | An **As-is process** board: draw the people, systems and handoffs, write the steps with who, tool and wait time, and pin each pain (P1, P2 …) to the step where it happens. Pains show in orange in the diagram. |
| **3. Architect the solution** | A **Proposed architecture** board with its own diagram and steps: components grouped by system or team, human gates (🔒) where a person decides, an owner per step, and the pains each step removes. The **Pain check** flags pains no step removes and steps that remove none, and a scorecard holds a pilot measure per pain. |
| **4. Present and hand over** | **Present** walks through either board step by step, or as an **Overview** with one box per group. **Export .md** writes everything into one Markdown file, with a plain-language diff log of every change. |
| **5. Let an AI agent draft it** | **AI agent assisted technical discovery from meeting transcripts.** Give a discovery call transcript to the [`process-to-sketch` skill](agent_skill_for_SA_tool/README.md) in Cursor or Claude Code. The agent asks which software stack to prefer and researches it in the official documentation. It then drafts stages 1-3 for you: discovery answers and pains in the customer's words, the as-is process and a proposed architecture. Values it assumed are marked `ASSUMED`, and the result opens in Present and Edit mode for you to review. |

It also presents existing architecture documents: any Markdown file with a Mermaid flowchart and a step table ([format](format_specification.md)) can be walked through, and edited as a copy.

**Local and private.** It is one HTML file. Sketches are saved in your browser, and `serve.py` binds to localhost only. Use public or synthesized data in shared sessions.

## Quick start

```bash
cd architecture_viewer
python3 serve.py sample_sketch.md --open         # a process sketch: discovery, pains, as-is and proposed architecture
python3 serve.py sample_architecture.md --open   # an architecture walkthrough (bookstore order flow)
python3 serve.py                                 # ../architecture.md, or the bundled sample if that file doesn't exist
python3 serve.py path/to/other.md --port 8001 --open
```

Then open http://127.0.0.1:8000/. The **?** button in the top bar opens the [guide](guide.html) to every feature and to working with AI agents. Python 3.10+ standard library, nothing to install. The server serves the page and that one file, and reloads the page within about 2 seconds when the file changes.

Without the server, open `index.html` in a browser, and use **New**, **Load** or **Open file**, or drop a Markdown file onto it. That works without live reload.

The page loads Mermaid 11 (and, for the compact layout, its ELK plugin) from cdn.jsdelivr.net and IBM Plex fonts from Google Fonts, so it needs internet access.

## A discovery session, step by step

The screenshots show the bundled `sample_sketch.md`, **Deal desk discount approval** (synthesized): account execs ask for discounts by email, and Finance decides in the thread. Open it and click **Edit** to explore it, or start your own.

**1. Start.** The start page and the top bar offer three ways in:
- **Start a new sketch** (or **New**) opens an empty sketch in Edit mode.
- **Load a saved sketch** (or **Load ▾**) lists the sketches saved in this browser. Pick one to continue it in Edit mode.
- **Open file** opens a Markdown file. In Present mode it is shown; in Edit mode it is edited.

![The start page: Open file, Start a new sketch and Load a saved sketch, with the Load menu open](screenshots/start.png)

**2. Discover, capture the pains, and map the process today.**
- Give the sketch a name in the second bar, and fill in **Discovery** as you ask.
- In **Pains**, write each pain in the speaker's words, with what it costs.
- On the **As-is process** board, draw the boxes: type `Account exec -> Sales ops inbox : email` in the bar at the bottom, or right-click the canvas.
- In **Steps**, add the steps, **Link boxes** for each one (its boxes, and any arrow that should light up with it), and tag the pains that happen there. A tagged box shows `⚠ P1` in orange.
- **Click a pain** in the Pains tab (its token, or anywhere in its row) to highlight where it happens: the boxes of the steps tagged with it, and its tag in the box label. Click it again, click the canvas, or press `Esc` to clear.

![Edit mode, As-is board: pain P1 selected in the Pains tab, and the Finance manager box where it happens highlighted in orange](screenshots/pains.png)

**3. Architect the proposed solution.**
- Switch to **Proposed architecture** in the second bar. Each board has its **own diagram and its own steps**; Discovery and Pains are shared.
- Draw it, or start an empty board from **Start from the standard pattern** and rename the boxes and groups.
- Each proposed step has an **owner** (free text: a team, a system or a person), what happens, and the pains it **removes**.
- The **Pain check** below the steps lists pains that no step removes yet.

The screenshot at the top shows this board: step ④ selected, owned by the Approval service, removing P1.

**4. Present and hand over.**
- Click **Present**. The sketch shows on the board that was open, with its steps to click through, and the picker in the top bar switches between **As-is process** and **Proposed architecture**, each with its own steps.
- Pains and the pains a step removes are shown in orange in the step details.
- A board shows in Present even before it has steps: the steps pane then says so.
- **Edit** goes back. **Actions → Export .md** saves everything as one Markdown file.

![Present mode: the proposed architecture at step ④, with the owner, what happens, and the pain it removes in orange](screenshots/present.png)

## Present mode

Present walks through a diagram and its steps. It works for a sketch, and for any Markdown file in the viewer's format.

- **Click a step** in the sidebar (or press ← / →, or Play). The view zooms to the step and highlights its boxes and arrows, plus what it touches.
- **Click a box or group** in the diagram to see every step that uses it.
- **Overview** (or `O`) collapses each group into one box and merges the arrows between groups, for the big picture. Steps still work there. **Detail** goes back to every box. See section 6 of `format_specification.md`.
- **Several diagrams** (for example As-is process and Proposed architecture): the picker in the top bar switches between them, each with its own steps.
- **Fit** (or `F`) shows the whole diagram. The minimap in the corner shows where you are: click or drag in it to move.
- **Compact layout** (dropdown) uses Mermaid's ELK layout engine: a smaller diagram with right-angled arrows. The choice is remembered per browser.

![Detail mode: step 6 of the bookstore sample highlighted, with its details in the sidebar](screenshots/detail.png)

![Overview mode: one box per group, with merged arrows labelled by step](screenshots/overview.png)

*Both screenshots show `sample_architecture.md`, a fictional bookstore order flow, at step ⑥ "Payment confirmed". Top: **Detail**. Bottom: **Overview**.*

## Edit mode reference

One button in the top bar switches between **Edit** and **Present**. In Present it reads **Edit**, and in Edit it reads **Present**.

**What Edit opens**
- **A file shown in the viewer** (served, opened or dropped): Edit opens a **copy** of it. Each diagram that has a step table becomes a board, and you edit its boxes, arrows, groups and table rows. The file itself is never changed.
  - The copy is saved in the browser.
  - Its export puts the edited diagrams and tables back into the file's text, in place. Lines you didn't touch stay exactly as they were, and everything else in the file is kept.
  - Right after opening, the viewer draws the file's diagram and the editable copy and compares them. If they differ in boxes, groups, arrows or labels, it says so before you edit.
  - If you already have a copy of the same file, Edit asks whether to continue with it or start a new copy.
- **A file exported from Edit mode:** Edit reopens the sketch stored in it, including its diff log.
  - If the browser has newer changes to that sketch, you choose which version to keep.
  - If the file was changed by hand after the export, you choose between the file as it is now and the exported sketch.
- **New** (top bar, also on the start page) starts an empty sketch in Edit mode.
- **Load** (top bar, also on the start page) lists every sketch saved in this browser, newest first, and opens the one you pick in Edit mode.
- **Open file** (top bar) opens a Markdown file. In Present mode it is shown; in Edit mode it is edited.

**Sidebar tabs**
- **Discovery:** a form for a solutions architect's technical discovery, in collapsible sections:
  - use case
  - current process
  - pains
  - quantification
  - blockers and risks
  - definition of success
  - decision process
  - rollout plan
  - open questions

  Each section shows how many of its fields are filled.
- **Pains:** P1, P2 … in the speaker's words, with what each one costs. Each pain says where it happens and which proposed step removes it. Click a pain to highlight it in the diagram.
- **Steps:** the steps of the board that is open. Switching the board switches the steps. Selecting a step highlights the same boxes and arrows as in Present mode.
  - **Link boxes** links boxes **and arrows** to a step: while it is on, click a box or an arrow (or its label) to link it, and click it again to unlink. The linked items show under **Linked**, arrows as `From → To`.
  - **What a step highlights,** in Edit mode and in Present:
    - **Steps made here** (every step of a sketch, and steps added to a copy): its linked boxes, the arrows between them, and its linked arrows. Nothing else is added, so link an arrow when it should light up with the step.
    - **Steps of an opened file:** as in the original file, including the arrows that lead into its boxes. Once you link or unlink a box or an arrow of such a step, that step switches to the rule above; the other steps stay as they were.
  - **As-is** steps (Ⓐ Ⓑ Ⓒ) have who, tool, wait, and the pains that happen there.
  - **Proposed architecture** steps (① ② ③) have an owner (free text: a team, a system or a person), what happens, and the pains they remove.
  - A linked box shows the step key in its label.
  - The **Pain check** under the proposed steps lists pains that no step removes, and steps that remove no pain. It also has a scorecard with a pilot measure per pain.
- **Notes:** free text.
- **Diffs:** the diff log, newest first. Every change is one entry: a run of typing in one field, an added box, a drag, an undo, a restore. Each entry says what changed in plain words.
  - **Select an entry** to show that state on the canvas, read-only, with what changed in that step.
  - **Restore this state** makes it the current state. The restore is itself a new entry and can be undone, so no state is ever lost.
  - **Back to now**, or `Esc`, leaves the preview.

**File boards** (from an opened file) keep the file's own step keys and columns. The Steps tab edits every cell of the table, and each step can be tagged with pains from the Pains tab. When a step has pains, the table gets a **Pains** column at the end, so Present and the export show them with each step. The file's own cells are kept as they are. The Pain check is only on sketch boards.

**Drawing.** Mermaid lays out the boxes. **Drag** a box to move it, or drag a group by its title to move it with everything in it. Dragging anywhere else, including the inside of a group, moves the diagram. In Edit mode the **scroll wheel zooms** at the pointer. A moved box is pinned: it keeps its place, its arrows are drawn straight to it, and its group grows or shrinks to fit. **Reset positions** in the Actions menu, or **Reset position** in a box's right-click menu, hands the layout back to Mermaid. Changing a board's direction also resets its positions.
- **Quick-add bar** at the bottom of the canvas (press `/`):
  - `Requester -> Ops inbox : email` adds both boxes and a labelled arrow.
  - `A -> B -> C` chains boxes.
  - `..>` draws a dashed arrow.
  - `[Finance]` puts that line's new boxes into that group. Without it, new boxes go outside any group.
  - `person:`, `store:`, `decision:` or `gate:` in front of a name sets its shape.
- **Right-click** the canvas. New boxes go outside any group, except when you add them from a group's menu:
  - **empty space:** add a shape or a group
  - **a group:** add a shape inside it
  - **a box:** add a shape connected from it, draw an arrow, rename or delete
- **Actions menu** (second bar), with four sections:
  - **Add:** a shape (box, person, system of record, decision, human gate), a group, or Connect (click the start box, then the end box).
  - **Layout:** the board's direction, and Reset positions. **Auto direction** keeps whichever of left-to-right or top-down fits the screen better. The first drag fixes the board's direction at whatever it is then.
  - **Share:** Copy Markdown and Export .md.
  - **Delete this sketch** (or **this copy**), after a confirmation. A copy's file is not affected.

  `N` adds another box of the last shape you picked.
- **Editing a box:** click it to edit its name, its further lines, its shape, its group and its arrows in the sidebar. Double-click it to rename.
- **Starting the proposed architecture board:** on an empty board, **Start from the standard pattern** fills in front door, intake, agent work, routing, a human gate, act and log, and status, in a Platform and an Agent group. Rename the boxes and groups to fit.

**Saving.** Every change saves in the browser's local storage within a second, and survives reloads and restarts. Undo and redo (`⌘Z`, `⇧⌘Z`) go back up to 50 steps, and the diff log keeps everything.
- **Separate entries:** each sketch is its own storage entry, and a save writes only that entry, so one sketch can't overwrite another.
- **Two tabs:** when another tab saves newer changes to the open sketch, this tab takes them over instead of overwriting them.
- **Checks on opening:** a sketch that can't be read is listed as damaged and never opened or replaced. A diff log that doesn't lead to the saved state is restarted instead of being trusted.
- **One address:** `127.0.0.1:8000` and `localhost:8000`, or another port, each have their own sketches.
- **Clearing site data** deletes them. **Export .md** is the backup.

**Export and present**
- **Export .md** (Actions menu) downloads the sketch as a Markdown file in this viewer's format. For a copy of a file, the name is `<file>-edited.md`. The export holds:
  - the discovery and the pains, when filled in
  - one diagram and one step table per board. For a copy, these are the file's text with the edits in place.
  - a pain scorecard, for sketches
  - a **Diffs** section with every change, in plain words
  - the sketch itself, with its full diff log, in an HTML comment, so opening the file and clicking **Edit** brings it all back
- **Copy Markdown** puts the same text on the clipboard.
- **Present** leaves Edit mode and shows the sketch in the viewer, with Detail, Overview and the steps to click through. A board without steps is still drawn.

| Key (Edit mode) | Action |
|---|---|
| / | Jump to the quick-add bar |
| N | New box, in the last shape you picked |
| G | New group |
| C | Connect two boxes |
| Enter | Rename the selected box |
| Delete | Delete the selected box or group |
| Esc | Leave a Diffs preview, cancel connecting or linking, then clear the selection |
| ⌘Z / ⇧⌘Z | Undo / redo |

## Working with AI agents

[`format_specification.md`](format_specification.md) is written so that an AI agent can produce files this tool opens:
- **Architecture walkthroughs:** a Mermaid flowchart with a step table, for presenting a system or a request flow step by step (sections 1-7).
- **Process sketches:** discovery, pains, the as-is process and the proposed architecture, as Markdown plus the sketch as JSON, so Edit mode opens it with everything (section 8).

The spec has tested examples, a method for mapping a process, and a checklist. A typical loop: the agent drafts a sketch from discovery notes, you open it, refine it live with the customer in Edit mode, and export the result.

**Agent skill:** [`agent_skill_for_SA_tool/`](agent_skill_for_SA_tool/) contains a ready-made skill for **Cursor** and **Claude Code** (`process-to-sketch`). It turns a business workflow description or discovery transcript into a process sketch for this viewer: discovery, pains, the as-is process, and a proposed human-in-the-loop architecture on a software stack the developer chooses (for example Mapbox or Grok Bot + Cursor API + GitHub). It asks which stack to prefer and researches it from the official documentation before it designs the proposal. It also includes a validator script and a sample discovery transcript (ACME hiring, synthesized). Setup and usage for each assistant: [`agent_skill_for_SA_tool/README.md`](agent_skill_for_SA_tool/README.md).

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app: discovery, process mapping and architecture editing (Edit mode), and the step-by-step presentation (Present mode) |
| `guide.html` | The guide: every feature, and how to draft sketches with an AI agent on a stack you choose. Opens from the **?** button in the top bar, or with `?` |
| `serve.py` | Local server: `/` (page), `/guide.html` and `/screenshots/*.png` (guide), `/api/source` (file text), `/api/mtime` (change polling) |
| `format_specification.md` | How to write a compatible file, for people and AI agents: walkthrough files for architectures, and process sketches (as-is process, pains, proposed architecture), with tested examples and a checklist |
| `sample_architecture.md` | An architecture walkthrough (fictional bookstore order flow) |
| `sample_sketch.md` | A sketch exported from Edit mode (deal desk discount approval, synthesized): discovery, pains, both boards with their steps, and the pain scorecard. **Edit** reopens it as a sketch |
| `agent_skill_for_SA_tool/` | Agent skill (Cursor and Claude Code) that writes process sketches from a workflow description. See its [README](agent_skill_for_SA_tool/README.md) |
| `screenshots/` | Detail and overview of the bookstore sample; the start page, Edit mode (pains, proposed architecture) and Present mode of the deal desk sketch |
| `LICENSE`, `NOTICE` | Apache License 2.0 and the attribution notice |

## Keys

| Key | Action |
|---|---|
| → / ↓ | Next step |
| ← / ↑ | Previous step |
| Space | Play or pause (3 s per step) |
| Esc | Clear the highlight |
| O | Switch between Detail and Overview |
| F | Fit the whole diagram |
| + / − | Zoom in or out |
| ? | Open the guide in a new tab |
| Drag | Move the diagram |
| Pinch, or Ctrl/Cmd + scroll | Zoom at the pointer |
| Scroll | Move the diagram |

## License

Copyright 2026 Moritz Foerster. Licensed under the [Apache License 2.0](LICENSE): free to use, change and redistribute. Copies and derived works must keep the license and the attribution in [NOTICE](NOTICE).
