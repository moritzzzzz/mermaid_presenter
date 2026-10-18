# ACME hiring process: technical discovery transcript

> **SYNTHETIC.** ACME and every person below are fictional. All numbers are synthesized for the exercise.
> Call date: 14 Oct 2026 · Duration: 30 min · Format: video call, notes taken by the SA

## Participants

| Name | Role at ACME | Role in the deal |
|---|---|---|
| Hannah Weber | Head of HR | Technical decision maker, champion |
| Tom Okafor | Recruiter | Runs the searches day to day |
| Lena Brandt | Engineering manager | Hiring manager |
| Chris Patel | Chief People Officer (CPO) | Economic buyer (not on the call, referred to by Hannah) |
| Alex Moreau | Solutions architect (vendor side) | Ran the call |

---

## Transcript

**Alex (SA):** Thanks for making the time. I'd like to understand how a hire happens at ACME today, once a role is open. Hannah, can you start?

**Hannah (Head of HR):** Sure. The budget is already approved by then. The hiring manager, Lena for example, emails Tom with the role and what she's looking for.

**Tom (Recruiter):** I post the job on our careers page. Applications arrive as emails with the CV attached in our shared recruiting inbox. I read every CV by hand, which takes me two or three days per role, and I email the best five or so to Lena.

**Alex (SA):** And then?

**Lena (Hiring manager):** I pick who I want to interview. Honestly, I reject about half of Tom's shortlist straight away, because the CVs don't match what we need.

**Tom (Recruiter):** Then I schedule the interviews by email with the candidate and Lena. That's about a week of back and forth.

**Lena (Hiring manager):** I do the interview, and if I like the person, I tell Hannah to make an offer.

**Hannah (Head of HR):** I write the offer letter and send it. That's it.

**Alex (SA):** How long does it take end to end?

**Hannah (Head of HR):** About six weeks from posting the job to a signed offer. That's our main pain: hiring is too slow, and we lose good candidates to faster companies. The second pain is the screening: Tom spends days reading CVs, and half of what he sends Lena is still wrong.

**Alex (SA):** What would success look like?

**Hannah (Head of HR):** Two weeks from posting to offer, and a shortlist Lena actually wants to interview.

**Alex (SA):** Anything that would block it?

**Hannah (Head of HR):** CVs are personal data, so GDPR applies and IT security will review any new tool. And a person has to decide who gets interviewed and who gets an offer. No software makes that call.

**Alex (SA):** How does a new tool get bought?

**Hannah (Head of HR):** I decide whether it fits how we work. Chris, our CPO, owns the budget. IT security does a review, then we run a pilot on Lena's engineering roles. If it works, Chris funds the rollout.

**Alex (SA):** Great. I'll come back with a sketch of the process as it is today, and a proposed architecture with people approving at every decision point.

---

## Discovery notes (SA summary)

| Section | Field | Answer |
|---|---|---|
| Use case | Name | Hiring: from job posting to signed offer |
| Use case | Line of business and team | HR / Talent Acquisition |
| Use case | Business owner | Hannah Weber, Head of HR |
| Use case | Users | Recruiter, hiring manager, HR |
| Use case | What starts it | A hiring manager emails the recruiter about an approved open role |
| Use case | Why now | Slow hiring loses candidates to faster companies |
| Process | Summary | Role emailed to recruiter → job posted on careers page → CVs land in shared inbox → manual screening → shortlist emailed to hiring manager → interview scheduled by email → interview → offer letter sent by HR |
| Process | Systems | Email, shared recruiting inbox, careers page |
| Process | Handoffs | Hiring manager → recruiter → hiring manager → recruiter → hiring manager → HR → candidate |
| Pains | List | P1 Hiring too slow (~6 weeks posting → offer) · P2 Manual screening takes days and half the shortlist is rejected |
| Quant | Cycle time | ~6 weeks posting → signed offer |
| Quant | Hands-on time | 2–3 recruiter days of CV screening per role |
| Quant | Rework | ~50% of the shortlist rejected by the hiring manager |
| Blockers | Security | IT security review required; CVs are personal data (GDPR) |
| Blockers | Change | A person decides who is interviewed and who gets an offer |
| Success | KPI | Time from posting to offer; share of shortlist the hiring manager accepts |
| Success | Baseline | ~6 weeks; ~50% accepted |
| Success | Target | ~2 weeks; most of the shortlist accepted |
| Decision | Economic buyer | Chris Patel, CPO |
| Decision | Technical decision maker | Hannah Weber, Head of HR |
| Decision | Process | IT security review → pilot → CPO funds rollout |
| Rollout | Pilot | Lena Brandt's engineering roles |
| Next | Steps | SA sends as-is sketch + proposed architecture |
