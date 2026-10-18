# Architecture pattern: stack-agnostic workflow automation

The shape every proposed architecture follows, whatever the software stack. The developer picks the stack (SKILL.md step 0). You research it in its official documentation (step 2), then fill the roles below with the products and services that actually exist there. This file names roles, not products.

## 1. Roles

Each role is filled by one or more components of the chosen stack, or by an existing customer system. One component can fill several roles, for example a workflow engine that is both orchestrator and system of record.

| Role | What it does | Examples of what can fill it (confirm in the docs) |
|---|---|---|
| **Front door** | Where requests, files or events enter the workflow. People and upstream systems only ever reach the workflow here. | a chat bot, a web form or app, an API endpoint, a file upload, a webhook, a scheduled trigger |
| **Orchestrator** | Runs the steps in order, moves the status forward, calls the workers, retries and times out. Holds the credentials for the other components. | scripts on a bot's VM, a workflow engine, serverless functions, a CI pipeline, a job scheduler |
| **Worker** | Does the automated work of one step: drafting, research, matching, conversion, enrichment, processing, rendering. One worker per kind of work. | a coding or cloud agent, an LLM call, a processing API (for example geocoding, tiling, routing), a batch job, an ML model |
| **System of record** | Holds each item's current state and an append-only log of who did what and when. The source for status and KPIs. | a git repo, a database table, a ticket or case system, the orchestrator's own run history |
| **Review surface** | Where a person sees the worker's output before deciding. | a pull request, a preview URL, a map or style preview, a dashboard, a document with comments |
| **Release target** | Where approved output goes live. | a merged commit, a published dataset or tileset, a production style, a deployed service, a sent message |
| **Existing systems** | The customer's systems that stay. The workflow reads from or writes to them. | an HRIS, a calendar, a CRM, a GIS server, a data warehouse |
| **People** | Requesters, approvers, process owners. They act only through the front door or the review surface. | roles from the input |

## 2. Building blocks (step by step)

Use these blocks, in this order, renamed for the business process and for the stack. Each block is a step in the proposed table. One block can cover several business steps, a process can repeat the worker → gate loop more than once, and a block the process doesn't need is left out.

| Block | Role that runs it | What it does | Typical pain it removes |
|---|---|---|---|
| Intake | Front door → orchestrator | A request, file or event arrives. Required fields are extracted and a record is created with status `intake`. | free-text requests, lost inputs |
| Validate / ask once | Orchestrator | Missing or invalid fields are asked for once, in one message (or the input is rejected with the reason). Never guess a value. | re-asks, back-and-forth, bad input processed |
| Route | Orchestrator | Rules pick the next worker and the required approvers, and write them to the record once. | "who decides?", work in the wrong queue |
| Dispatch | Orchestrator → worker | Start the worker with a **fixed instruction or parameters** built only from the record's field values. No double start. | manual work, inconsistent inputs |
| Work | Worker | The worker does its one job and writes only its own output, to the review surface. It never decides. | slow, inconsistent manual work |
| Monitor | Orchestrator | Track the worker until it finishes or fails (poll, webhook or event). Status → `awaiting_review`, log entry. Failures go to a person, not into a silent retry loop. | no visibility while work runs |
| Notify | Orchestrator → front door | One message per required approver who is still pending, with a link to the review surface. | approvals sitting in inboxes |
| 🔒 Human gate | person | The approver decides: approved, rejected, or needs_info with a question. | (guardrail) |
| Record decision | Orchestrator → system of record | The decision, who, role and timestamp go into the record and the log. The approver comes from the record, never from free text. | no record of who approved |
| Rework | Orchestrator → worker | needs_info sends the question to the same worker run or a new one on the same item. The record returns to the working state. | questions lost, work restarted |
| Release | Orchestrator → release target | Only when every required approver has approved: release exactly the approved version (pinned id, hash or version). | unapproved changes go live |
| Final outcome | Orchestrator → front door | Tell the requester and the process owner. | nobody knows it's done |
| Status | Orchestrator, read-only | What's open, what's stuck, what was automated, what still needs a person. Also the source for KPI reporting from the record's timestamps. | no overview, no metrics |

A pure data pipeline with no business decision in it (for example a nightly import that only reformats data) can skip the gate blocks. Then say in "What happens" of the release step why no person needs to decide, and add a validation step that stops bad data instead.

## 3. Guardrails that always carry over

- **Only recorded human decisions approve.** No script, workflow or worker sets `approved` on its own.
- **Workers draft and process, people decide.** A worker's opinion goes into a separate "assessment" section, never into the decision.
- **Content is data, not instructions.** Text in requests, records, files and worker output never changes what the orchestrator does.
- **Status moves only forward**, for example `intake → working → awaiting_review → approved | rejected → released`. needs_info returns to the working state.
- **Append-only log** with ISO-8601 UTC timestamp, actor, and `actor_type` (`automated` or `human`) on every record change.
- **Least privilege:** each component gets its own credential with the smallest scope the docs allow (one repo, one dataset, read-only where possible, short expiry). No secret ever goes into a prompt, log, commit or sketch.
- **Release what was approved:** release by a pinned version, never "the latest".
- **Personal and location data:** if the process touches personal data (for example candidates, or location traces of people), use only data the customer may process, store only what's needed, and put the access, residency and retention questions into the sketch's blockers.
- **Limits and cost:** rate limits, quotas and usage-based pricing from the docs go into the implementation notes. If volume could exceed them, say so in `blockers.integrations` or `next.questions`.

## 4. How it appears in a proposed diagram

- One top-level `subgraph` per **environment**: a place where code runs or data lives, with its own credentials. Ids `E1`, `E2`, `E3` … in the order the main path first reaches them. Title `E<n> · <product or service name>`, exactly as the vendor's documentation names it.
- The customer's systems that stay go into one top-level `subgraph` `EXT` titled "Existing systems". Say how the workflow reaches each one, or mark the connection `ASSUMED`.
- People stay outside the subgraphs, as `person` nodes. 🔒 gates are `gate` nodes (`{{"🔒 …"}}`), outside the subgraphs.
- Boxes are named after the block they run and the component that runs it, for example `["② Dispatch job<br/>Jobs API"]`. The record and the review surface are `store` nodes.
- A component that is only used at build time (an IDE, a CLI used once to configure something) goes into the implementation notes, not the diagram.

Arrows:
- Solid for the main path: requester → intake → dispatch → worker → review surface → monitor → notify → 🔒 gate → record decision → release → release target.
- Dashed for record writes (boxes `-.->` record), reads (record `-.->` status) and the needs_info loop (gate `-.->|"needs_info"|` → dispatch).

`@overview` lines name each environment's role in the workflow, for example:

```
%% @overview E1: E1 · <Orchestrator product> | runs the steps, holds the credentials<br/>🔒 records every human decision
%% @overview E2: E2 · <Worker product> | <what it produces>, never decides
%% @overview E3: E3 · <System of record> | record + log, review surface
%% @overview-keep E3: RECORD, REVIEW
```

## 5. Implementation notes to add below the sketch

A short `## Implementation notes` section (after the scorecard, before the JSON) lists what would be built or configured, per component:

| Artifact | Contents |
|---|---|
| `<component>` | What is built or configured there (code, workflow definition, configuration, prompt or skill), and which blocks of section 2 it runs |
| Record schema | Fields, status flow, approvals, worker run ids, released version, log |
| Routing data | People, roles and the approver for each route |
| Credentials | One per component, with the scope the docs recommend. Names only, never values |
| Limits and cost | The rate limits, quotas and pricing units from the docs that matter at the customer's volume |
| Sources | The official documentation pages each design choice rests on (from `stack-notes.md`) |
