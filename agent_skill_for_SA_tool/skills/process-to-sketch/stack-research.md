# Stack research: from the developer's stack choice to verified components

Before you draw a proposed architecture, learn the chosen stack from its **official documentation** and write what you found into `projects/<id>/stack-notes.md`. The proposed board may only use what these notes confirm.

## 1. What counts as official documentation

- **Use:** the vendor's own documentation site, API reference, SDK reference, changelog, pricing page, limits or quotas page, security or trust page, and the vendor's own GitHub organization (READMEs, examples). Examples: `docs.mapbox.com`, `docs.cursor.com`, `docs.github.com`, `docs.aws.amazon.com`, `learn.microsoft.com`.
- **Don't use as a source:** blog posts by third parties, Q&A sites, tutorials, forum answers, or what you remember from training. They can point you to an official page, but only the official page counts.
- **Prefer the current version.** Note the version or the "last updated" date if the page shows one. If a feature is beta, preview or deprecated, say so.
- If the developer gave you links or pasted documentation, start there.

## 2. How to research

1. **List the products** the developer named. If they named a vendor only ("Mapbox", "AWS"), find the vendor's product overview first and pick the products that can fill the roles of [architecture-pattern.md](architecture-pattern.md) §1 for this process. Note each pick and why.
2. **For each product, read** its overview, the API or SDK reference for the operations you plan to use, authentication, limits and pricing, and its data handling or security page.
3. **Confirm each capability you plan to draw**, for example "can be triggered by a webhook", "returns a job id that can be polled", "supports per-dataset access tokens". If you can't find it in the docs, it's not confirmed: either design around it or mark it `ASSUMED` and add a question to `next.questions`.
4. **Find the human touchpoints**: where can a person review output (a preview, a PR, a UI), and where can a person approve? If the stack has none, the review surface comes from another chosen product or an existing system.
5. **Stop when every role in the proposed design has a confirmed component.** Don't read the whole documentation site.

## 3. Tools

- **Web access** (Cursor: `@Web` or a docs entry added under `@Docs`; Claude Code: web search and web fetch; other assistants: their browsing tool): search with the vendor's docs domain in the query, then open the official page.
- **A vendor MCP server or docs connector**, if one is set up, counts as official when it serves the vendor's own documentation.
- **No web access?** Ask the developer for the documentation links or for the relevant pages as files. Don't design the proposed board from memory. If they tell you to go ahead anyway, mark every stack capability `ASSUMED` and write "not checked against documentation" at the top of `stack-notes.md`.

## 4. `stack-notes.md` template

Write it to `projects/<id>/stack-notes.md` (the `stack_notes` path that `scripts/new_project.py` returned). Keep it short: what the design needs, not a product summary.

````markdown
# Stack notes: <Title>

Stack chosen by the developer: <their words, quoted>
Researched on <D Mon YYYY> from official documentation.

## <Product name>

- **Role in the design:** <orchestrator | worker | front door | system of record | review surface | release target>
- **What we use:** <the operations, endpoints, SDK calls or features the design relies on>
- **Trigger and status:** <how it is started, how completion or failure is reported (poll, webhook, event)>
- **Authentication:** <token or key type, the narrowest scope available>
- **Limits and pricing:** <rate limits, quotas, pricing unit relevant to the customer's volume>
- **Data handling:** <where data is stored or processed, retention, relevant certifications, if documented>
- **Human touchpoint:** <where a person can review or approve, if any>
- **Not confirmed:** <capabilities the design wants but the docs don't show → ASSUMED>
- **Sources:**
  - <page title> — <URL>
  - <page title> — <URL>

## <Next product>

…

## Role map

| Role | Component | Confirmed by |
|---|---|---|
| Front door | <component> | <URL> |
| Orchestrator | <component> | <URL> |
| Worker: <kind of work> | <component> | <URL> |
| System of record | <component> | <URL> |
| Review surface | <component> | <URL> |
| Release target | <component> | <URL> |
````
