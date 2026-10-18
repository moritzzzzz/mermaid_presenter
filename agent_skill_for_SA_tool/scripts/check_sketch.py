#!/usr/bin/env python3
"""Check an Architecture Viewer process sketch against format_specification.md section 8 and 10.

Usage:
    python3 scripts/check_sketch.py projects/<id>/<slug>.md [--json]

Exit codes: 0 no errors (warnings allowed), 1 errors found, 2 file not readable.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Key alphabets (by code point, to keep this file ASCII-safe).
ASIS_KEYS = [chr(c) for c in range(0x24B6, 0x24D0)]          # circled A-Z
TOBE_KEYS = [chr(c) for c in range(0x2460, 0x2474)]          # circled 1-20
CIRCLED_ALL = [chr(0x24EA)] + TOBE_KEYS                      # circled 0-20, for ranges
LOCK = chr(0x1F512)
WARN_SIGN = chr(0x26A0)

JSON_HEADER = "<!-- architecture-viewer-sketch"
RESERVED_IDS = {"end", "graph", "subgraph", "flowchart"}
NODE_DEF = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(\(\[|\[\(|\{\{|\(\(|\[|\{|\(|>)")
ARROW = re.compile(r"-\.->|==>|-->")
PAIN_ID = re.compile(r"\bP\d+\b")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


# ---------- Markdown helpers ----------

def h2_sections(text):
    """Map H2 title -> text until the next H2 (H3 content included). Code fences are skipped."""
    sections, current, buf, in_fence = {}, None, [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf)
            current, buf = line[3:].strip(), []
            continue
        if current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf)
    return sections


def first_mermaid(section):
    """Return (diagram source, text after the diagram) or (None, section)."""
    m = re.search(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$", section, re.S | re.M)
    if not m:
        return None, section
    return m.group(1), section[m.end():]


def split_row(line):
    """Split a Markdown table row on | that is not escaped and not inside backticks."""
    cells, buf, in_code, i = [], "", False, 0
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            buf += "|"
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append(buf.strip())
            buf = ""
        else:
            buf += ch
        i += 1
    cells.append(buf.strip())
    return cells


def first_table(text):
    """Return (header list, list of row lists) of the first table in text, or (None, [])."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].strip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            header = split_row(lines[i])
            rows = []
            for line in lines[i + 2:]:
                if not line.strip().startswith("|"):
                    break
                rows.append(split_row(line))
            return header, rows
    return None, []


def col(header, *names):
    for name in names:
        for idx, h in enumerate(header):
            if h.strip().lower() == name.lower():
                return idx
    return None


def cell(row, idx):
    if idx is None or idx >= len(row):
        return ""
    return row[idx]


# ---------- Mermaid helpers ----------

def is_alnum_ascii(ch):
    return ch.isascii() and (ch.isalnum() or ch == "_")


def keys_in(source):
    """Every whole-token key-like occurrence in source, with circled ranges expanded."""
    found = set()
    for idx, ch in enumerate(source):
        if ch in ASIS_KEYS or ch in CIRCLED_ALL:
            nxt = source[idx + 1] if idx + 1 < len(source) else ""
            if nxt and is_alnum_ascii(nxt):
                found.add(ch + nxt)  # e.g. a key like "12a" glued on purpose
                continue
            found.add(ch)
    for a, b in re.findall("([%s])-([%s])" % ("".join(CIRCLED_ALL), "".join(CIRCLED_ALL)), source):
        ia, ib = CIRCLED_ALL.index(a), CIRCLED_ALL.index(b)
        found.update(CIRCLED_ALL[min(ia, ib):max(ia, ib) + 1])
    return found


def diagram_lines(src):
    return [l for l in src.splitlines() if l.strip()]


def parse_diagram(src):
    """Return dict with node ids, arrow count, top-level subgraph ids, overview ids, exact keys, step-line keys."""
    info = {"nodes": [], "arrows": 0, "top_groups": [], "all_groups": [], "overview": set(),
            "exact_keys": [], "exact_last": False, "step_keys": set(), "header": "", "gates": []}
    lines = diagram_lines(src)
    if lines:
        info["header"] = lines[0].strip()
    depth = 0
    for raw in lines[1:]:
        line = raw.strip()
        if line.startswith("%%"):
            m = re.match(r"%%\s*@overview\s+([A-Za-z0-9_]+)\s*:", line)
            if m:
                info["overview"].add(m.group(1))
            m = re.match(r"%%\s*@exact\s+(.*)$", line)
            if m:
                info["exact_keys"].extend(k for k in re.split(r"[\s,]+", m.group(1)) if k)
            m = re.match(r"%%\s*@step\s+(\S+)\s*:", line)
            if m:
                info["step_keys"].add(m.group(1))
            if "Steps without a box" in line:
                info["step_keys"].update(keys_in(line))
            continue
        m = re.match(r"subgraph\s+([A-Za-z0-9_]+)", line)
        if m:
            info["all_groups"].append(m.group(1))
            if depth == 0:
                info["top_groups"].append(m.group(1))
            depth += 1
            continue
        if line == "end":
            depth = max(0, depth - 1)
            continue
        if line.startswith(("direction ", "classDef ", "class ", "style ", "click ", "linkStyle ")):
            continue
        info["arrows"] += len(ARROW.findall(line))
        # node definitions: at line start, and after each arrow
        parts = ARROW.split(line)
        for part in parts:
            part = re.sub(r'^\s*\|[^|]*\|', "", part)  # strip -->|label|
            m = NODE_DEF.match(part)
            if m and m.group(1) not in info["nodes"]:
                info["nodes"].append(m.group(1))
                if m.group(2) == "{{" and LOCK in part:
                    info["gates"].append(m.group(1))
    last = lines[-1].strip() if lines else ""
    info["exact_last"] = last.startswith("%% @exact") or last.startswith("%%@exact")
    return info


# ---------- checks ----------

def check_board(rep, name, sections, title, key_alphabet):
    section = sections.get(title)
    if section is None:
        rep.error("missing section '## %s'" % title)
        return None
    src, after = first_mermaid(section)
    if src is None:
        if "No diagram yet." in section:
            rep.warn("%s: 'No diagram yet.'" % name)
        else:
            rep.error("%s: no ```mermaid block in '## %s'" % (name, title))
        return None
    info = parse_diagram(src)
    if not re.match(r"^(flowchart|graph)\s+(LR|TD|TB|RL|BT)\b", info["header"]):
        rep.error("%s: diagram must start with 'flowchart LR' or 'flowchart TD' (found '%s')" % (name, info["header"]))
    for nid in info["nodes"] + info["all_groups"]:
        if nid.lower() in RESERVED_IDS:
            rep.error("%s: Mermaid keyword '%s' used as an id" % (name, nid))
        if len(nid) > 24:
            rep.warn("%s: id '%s' is longer than 24 characters" % (name, nid))
    header, rows = first_table(after)
    if header is None:
        rep.error("%s: no step table after the diagram" % name)
        return {"info": info, "rows": [], "header": [], "src": src}
    key_col = 0
    keys = [cell(r, key_col) for r in rows]
    labels_only = "\n".join(l for l in src.splitlines() if not l.strip().startswith("%%"))
    present = keys_in(labels_only) | info["step_keys"]
    for i, k in enumerate(keys):
        if not k:
            rep.error("%s: row %d has no key in the first column" % (name, i + 1))
            continue
        if i < len(key_alphabet) and k != key_alphabet[i]:
            rep.warn("%s: row %d key is '%s', expected '%s' (keys in row order)" % (name, i + 1, k, key_alphabet[i]))
        if k not in present:
            rep.error("%s: key %s is in the table but not in any diagram label or @step line" % (name, k))
    if len(set(keys)) != len(keys):
        rep.warn("%s: repeated keys in the step table" % name)
    if not info["exact_last"]:
        rep.error("%s: the last line of the diagram must be '%%%% @exact' with all step keys" % name)
    missing_exact = [k for k in keys if k and k not in info["exact_keys"]]
    if missing_exact:
        rep.error("%s: @exact is missing keys: %s" % (name, " ".join(missing_exact)))
    for g in info["top_groups"]:
        if g not in info["overview"]:
            rep.warn("%s: top-level subgraph '%s' has no '%%%% @overview %s:' line" % (name, g, g))
    return {"info": info, "rows": rows, "header": header, "src": src}


def check(text):
    rep = Report()
    if not re.search(r"^# \S", text, re.M):
        rep.error("no '# Title' (H1) heading")
    h1 = re.search(r"^# (.+)$", text, re.M)
    title = h1.group(1).strip() if h1 else ""
    if "Sketched in Architecture Viewer on" not in text:
        rep.warn("missing the 'Sketched in Architecture Viewer on <date>.' line")

    sections = h2_sections(text)

    # Pains table
    pains = {}
    if "Pains" in sections:
        ph, prow = first_table(sections["Pains"])
        if ph is None:
            rep.error("'## Pains' has no table")
        else:
            id_col = col(ph, "#")
            text_col = col(ph, "Pain")
            for r in prow:
                pid = cell(r, id_col).strip()
                if not re.fullmatch(r"P\d+", pid):
                    rep.error("Pains table: '%s' is not a pain id (P1, P2 ...)" % pid)
                    continue
                pains[pid] = cell(r, text_col)
    else:
        rep.warn("no '## Pains' section")

    asis = check_board(rep, "As-is", sections, "As-is process", ASIS_KEYS)
    tobe = check_board(rep, "Proposed", sections, "Proposed architecture", TOBE_KEYS)

    # Pains on as-is steps and removed by proposed steps
    asis_pains, tobe_pains = set(), set()
    if asis and asis["header"]:
        pc = col(asis["header"], "Pain", "Pains", "Pains (tagged)")
        for r in asis["rows"]:
            asis_pains.update(PAIN_ID.findall(cell(r, pc)))
        for pid in sorted(asis_pains - set(pains)):
            rep.error("As-is: pain %s is tagged on a step but not in the Pains table" % pid)
        for pid in sorted(set(pains) - asis_pains):
            rep.error("As-is: pain %s is not tagged on any as-is step" % pid)
        if WARN_SIGN not in asis["src"] and pains:
            rep.warn("As-is: no box carries a pain tag line (e.g. '%s P1')" % WARN_SIGN)
    if tobe and tobe["header"]:
        rc = col(tobe["header"], "Removes")
        oc = col(tobe["header"], "Owner")
        if oc is None:
            rep.error("Proposed: step table has no 'Owner' column")
        for i, r in enumerate(tobe["rows"]):
            tobe_pains.update(PAIN_ID.findall(cell(r, rc)))
            if oc is not None and not cell(r, oc):
                rep.error("Proposed: step %s has no owner" % cell(r, 0))
        if WARN_SIGN in tobe["src"]:
            rep.error("Proposed: diagram must not carry '%s' pain tags" % WARN_SIGN)
        if not tobe["info"]["gates"]:
            rep.warn("Proposed: no human gate ({{\"%s ...\"}}) in the diagram. stack-proposal.mdc allows that only "
                     "when no person decides anything; say why in the release step" % LOCK)

    scorecard = sections.get("Pain scorecard", "")
    if not scorecard:
        rep.warn("no '## Pain scorecard' section")
    sh, srows = first_table(scorecard) if scorecard else (None, [])
    score_text = {}
    for r in srows:
        ids = PAIN_ID.findall(cell(r, 0))
        if ids:
            score_text[ids[0]] = " ".join(r)
    for pid in sorted(pains):
        if pid not in tobe_pains and "Not removed yet" not in score_text.get(pid, ""):
            rep.error("pain %s is not removed by any proposed step and the scorecard doesn't say 'Not removed yet'" % pid)
        if scorecard and pid not in score_text:
            rep.warn("Pain scorecard: no row for %s" % pid)

    check_json(rep, text, title, pains, asis, tobe)
    return rep


def check_json(rep, text, title, pains, asis, tobe):
    idx = text.find(JSON_HEADER)
    if idx < 0:
        rep.error("no '%s' JSON comment at the end of the file" % JSON_HEADER)
        return
    rest = text[idx:]
    first_nl = rest.find("\n")
    header_line = rest[:first_nl]
    if not re.fullmatch(re.escape(JSON_HEADER) + r"( fnv=[0-9a-f]+)?\s*", header_line):
        rep.error("JSON header line must be exactly '%s' (found '%s')" % (JSON_HEADER, header_line.strip()))
    body_and_tail = rest[first_nl + 1:]
    m = re.search(r"^-->\s*$", body_and_tail, re.M)
    if not m:
        rep.error("JSON comment has no closing '-->' on its own line")
        return
    body = body_and_tail[:m.start()]
    tail = body_and_tail[m.end():]
    if tail.strip():
        rep.error("the JSON comment must be the last thing in the file")
    if "fnv=" in header_line:
        rep.warn("header has an fnv= fingerprint: remove it if the Markdown was changed by hand")
    if "--" in body:
        rep.error("raw '--' inside the JSON comment: write it as '-\\u002d' in JSON strings")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        rep.error("JSON does not parse: %s (line %d col %d of the JSON)" % (exc.msg, exc.lineno, exc.colno))
        return
    if data.get("v") != 3:
        rep.error("JSON: \"v\" must be 3")
    if not data.get("id"):
        rep.error("JSON: missing stable \"id\"")
    if title and data.get("title") != title:
        rep.warn("JSON: title '%s' differs from the H1 '%s'" % (data.get("title"), title))
    jpains = {p.get("id"): p for p in data.get("pains", []) if isinstance(p, dict)}
    if set(jpains) != set(pains):
        rep.error("JSON pains %s differ from the Pains table %s" % (sorted(jpains), sorted(pains)))
    boards = data.get("boards") or {}
    for key, md in (("asis", asis), ("tobe", tobe)):
        board = boards.get(key)
        if not isinstance(board, dict):
            rep.error("JSON: boards.%s missing" % key)
            continue
        check_json_board(rep, key, board, md, set(jpains))


def check_json_board(rep, key, board, md, pain_ids):
    if board.get("dir") not in ("LR", "TD"):
        rep.warn("JSON %s: dir is '%s', an agent should set 'LR' or 'TD'" % (key, board.get("dir")))
    groups = {g.get("id") for g in board.get("groups", [])}
    nodes = board.get("nodes", [])
    node_ids = [n.get("id") for n in nodes]
    if len(set(node_ids)) != len(node_ids):
        rep.error("JSON %s: duplicate node ids" % key)
    for n in nodes:
        if n.get("group") and n.get("group") not in groups:
            rep.error("JSON %s: node '%s' has unknown group '%s'" % (key, n.get("id"), n.get("group")))
        if n.get("shape", "box") not in ("box", "person", "store", "decision", "gate"):
            rep.error("JSON %s: node '%s' has unknown shape '%s'" % (key, n.get("id"), n.get("shape")))
        label = (n.get("label") or "") + " " + (n.get("sub") or "")
        if WARN_SIGN in label or any(k in label for k in ASIS_KEYS + TOBE_KEYS):
            rep.warn("JSON %s: node '%s' label carries a step key or pain tag (Edit mode adds them)" % (key, n.get("id")))
    endpoints = set(node_ids) | groups
    edges = board.get("edges", [])
    edge_ids = {e.get("id") for e in edges if e.get("id")}
    for e in edges:
        for end in ("from", "to"):
            if e.get(end) not in endpoints:
                rep.error("JSON %s: edge %s -> %s refers to unknown '%s'" % (key, e.get("from"), e.get("to"), e.get(end)))
    steps = board.get("steps", [])
    for s in steps:
        for nid in s.get("nodes", []):
            if nid not in node_ids:
                rep.error("JSON %s: step '%s' uses unknown node '%s'" % (key, s.get("name"), nid))
        for eid in s.get("edges", []):
            if eid not in edge_ids:
                rep.error("JSON %s: step '%s' uses unknown edge id '%s'" % (key, s.get("name"), eid))
        for pid in s.get("pains", []):
            if pid not in pain_ids:
                rep.error("JSON %s: step '%s' names unknown pain '%s'" % (key, s.get("name"), pid))
        if key == "tobe" and not s.get("owner"):
            rep.error("JSON tobe: step '%s' has no owner" % s.get("name"))
    if md:
        rows = md["rows"]
        if len(steps) != len(rows):
            rep.error("JSON %s: %d steps, but the Markdown table has %d rows" % (key, len(steps), len(rows)))
        name_col = 1
        for i, (s, r) in enumerate(zip(steps, rows)):
            if (s.get("name") or "").strip() != cell(r, name_col).strip():
                rep.warn("JSON %s: step %d is '%s' in JSON but '%s' in the table" % (key, i + 1, s.get("name"), cell(r, name_col)))
        info = md["info"]
        if len(nodes) != len(info["nodes"]):
            rep.warn("JSON %s: %d nodes, but the diagram defines %d boxes" % (key, len(nodes), len(info["nodes"])))
        if len(edges) != info["arrows"]:
            rep.warn("JSON %s: %d edges, but the diagram has %d arrows" % (key, len(edges), info["arrows"]))
        if len(groups) != len(info["all_groups"]):
            rep.warn("JSON %s: %d groups, but the diagram has %d subgraphs" % (key, len(groups), len(info["all_groups"])))
        gates_json = sum(1 for n in nodes if n.get("shape") == "gate")
        if gates_json != len(info["gates"]):
            rep.warn("JSON %s: %d gate nodes, but the diagram has %d 🔒 gates" % (key, gates_json, len(info["gates"])))


def main():
    parser = argparse.ArgumentParser(description="Check an Architecture Viewer process sketch.")
    parser.add_argument("path", help="sketch Markdown file")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    try:
        text = Path(args.path).read_text(encoding="utf-8")
    except OSError as exc:
        print("cannot read %s: %s" % (args.path, exc), file=sys.stderr)
        return 2
    rep = check(text)
    if not (Path(args.path).parent / "stack-notes.md").is_file():
        rep.warn("no stack-notes.md next to the sketch: research the stack first (stack-research.md)")
    ok = not rep.errors
    if args.json:
        print(json.dumps({"file": args.path, "ok": ok, "errors": rep.errors, "warnings": rep.warnings},
                         ensure_ascii=False, indent=2))
    else:
        for e in rep.errors:
            print("ERROR: " + e)
        for w in rep.warnings:
            print("WARN:  " + w)
        if ok:
            print("OK: %s (%d warnings)" % (args.path, len(rep.warnings)))
        else:
            print("FAILED: %s (%d errors, %d warnings)" % (args.path, len(rep.errors), len(rep.warnings)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
