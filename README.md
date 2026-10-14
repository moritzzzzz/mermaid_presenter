# Architecture Viewer

An interactive walkthrough of a Mermaid flowchart and its step table, both from one Markdown file. Use it to present a process step by step in a demo.

- **Click a step** in the sidebar (or press ← / →, or Play). The view zooms to the step and highlights its boxes and arrows, plus what it touches.
- **Click a box or group** in the diagram to see every step that uses it.
- **Overview** (or `O`) collapses each group (environment) into one box and merges the arrows between groups, for presenting the overall architecture. Steps still work there. **Detail** goes back to every box. See section 6 of `format_specification.md`.
- **Fit** (or `F`) shows the whole diagram. The minimap in the corner shows where you are: click or drag in it to move.
- **Compact layout** (dropdown) uses Mermaid's ELK layout engine: a smaller diagram with right-angled arrows. The choice is remembered per browser.
- **Edit the Markdown file** while the server runs, and the page updates within about 2 seconds.

![Detail mode: step 6 of the sample highlighted, with its details in the sidebar](screenshots/detail.png)

![Overview mode: one box per group, with merged arrows labelled by step](screenshots/overview.png)

*Both screenshots show `sample_architecture.md`, a fictional bookstore order flow, at step ⑥ "Payment confirmed". Top: **Detail**. Bottom: **Overview**.*

## Run

```bash
cd architecture_viewer
python3 serve.py sample_architecture.md --open   # the bundled sample
python3 serve.py                      # ../architecture.md, or the sample if that file doesn't exist
python3 serve.py path/to/other.md --port 8001 --open
```

Then open http://127.0.0.1:8000/. The server binds to localhost only and serves just the page and that one file. Python 3.10+ standard library, nothing to install.

Without the server, open `index.html` in a browser and drop a Markdown file onto it. That works without live reload.

The page loads Mermaid 11 (and, for the compact layout, its ELK plugin) from cdn.jsdelivr.net and IBM Plex fonts from Google Fonts, so it needs internet access.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole app: parser, linking, rendering, UI |
| `serve.py` | Local server: `/` (page), `/api/source` (file text), `/api/mtime` (change polling) |
| `format_specification.md` | How to write a compatible source file, with an example |
| `sample_architecture.md` | A fictional sample (bookstore order flow) to try the viewer |
| `screenshots/` | Detail and overview screenshots of the sample |

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
| Drag | Move the diagram |
| Pinch, or Ctrl/Cmd + scroll | Zoom at the pointer |
| Scroll | Move the diagram |
