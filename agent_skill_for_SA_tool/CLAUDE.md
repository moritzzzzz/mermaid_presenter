# Process sketch workspace

This folder turns business workflow descriptions into Architecture Viewer process sketches, with a proposed human-in-the-loop architecture on a software stack the developer chooses, researched from its official documentation. Use the `process-to-sketch` skill for that.

The skill and rules are shared with Cursor. They apply here exactly as written:

- Skill: `skills/process-to-sketch/SKILL.md`, the neutral folder. Claude Code's entry point `.claude/skills/process-to-sketch/SKILL.md` points to it.
- Rules: the three files imported below. Ignore their `---` frontmatter, which is Cursor metadata. `sketch-format.mdc` applies to every file under `projects/`.

@.cursor/rules/data-boundaries.mdc
@.cursor/rules/stack-proposal.mdc
@.cursor/rules/sketch-format.mdc
