#!/usr/bin/env python3
"""Create a new, uniquely named project directory for a process sketch.

Usage:
    python3 scripts/new_project.py "<Title>" [--json]

Creates projects/<slug>-<YYYYMMDD-HHMMSS>/ (UTC) and prints its path, the sketch file path
projects/<slug>-<YYYYMMDD-HHMMSS>/<slug>.md and the stack research notes path .../stack-notes.md. If the directory already exists, -2, -3 ... is appended.
The directory name is also the sketch's JSON "id".

Exit codes: 0 created, 1 error.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"


def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40].rstrip("-") or "process"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a unique project directory for a process sketch.")
    parser.add_argument("title", help="sketch title, for example 'ACME hiring'")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    slug = slugify(args.title)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = "%s-%s" % (slug, stamp)
    name, n = base, 2
    try:
        PROJECTS.mkdir(exist_ok=True)
        while True:
            try:
                (PROJECTS / name).mkdir()
                break
            except FileExistsError:
                name, n = "%s-%d" % (base, n), n + 1
    except OSError as exc:
        print("cannot create project directory: %s" % exc, file=sys.stderr)
        return 1

    project_dir = Path("projects") / name
    result = {"id": name, "slug": slug, "project_dir": str(project_dir), "sketch": str(project_dir / ("%s.md" % slug)),
              "stack_notes": str(project_dir / "stack-notes.md")}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Created %s" % result["project_dir"])
        print("Write the sketch to %s" % result["sketch"])
        print("Write the stack research notes to %s" % result["stack_notes"])
        print('Use "id":"%s" in the sketch JSON' % result["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
