# Standing Context

**Attach this file to every layer run.** A fresh chat knows nothing about this
project. This is the minimum briefing; everything else arrives as scoped
attachments named by the layer's own prompt.

Keep it short. It is read every time, and anything added here is paid for on
every run.

---

## The project

A senior professor has recorded lectures — a time-based transcript plus the
original slides. We are converting the slides into **guided animation** so the
session becomes interactive and the visuals stay in sync with the narration.

**Deliverable:** 5 videos, each with its own PPTX, produced in this order:

| Order | Video | Topic | Duration |
|---|---|---|---|
| 1 | V017 | OS · Bounded Buffer Problem | 8 min |
| 2 | V018 | OS · Reader Writer Problem | 17 min |
| 3 | V028 | OS · Banker's Algorithm Overview | 4 min |
| 4 | V029 | OS · Banker's Algorithm Data Structures | 8 min |
| 5 | V030 | OS · Safety Algorithm | 12 min |

## The invariant

**Narration content and timing are fixed.** Audio quality may improve; the
words and when they are spoken must not change. Every decision is subordinate
to this.

## How the work is organised

The job is split into layers. Each layer owns one decision and hands a defined
artifact to the next. You are being asked to run **exactly one layer** — the
prompt will say which. Do not do a neighbouring layer's job, even if you can
see how.

| # | Layer | Owns |
|---|---|---|
| 1 | Target spec | What the finished output must be |
| 2 | Global theme | What an element looks like, unconditionally |
| 3 | Asset deconstruction | What is on each slide, as data |
| 4 | Transcript + timing | What is said, and exactly when |
| 5 | Slide representation | What each element *means*; the slide's layout |
| 6 | Visual vocabulary | What each meaning looks like |
| 7 | Audio mastering | Delivered sound quality |
| 8 | Sequence / beats | Timed beats bound to the narration |
| 9 | Defects & automation boundary | What is worth automating |

## Requirement IDs

Requirements are cited by prefixed ID, never by restating them:

| Prefix | Means | Lives in |
|---|---|---|
| **TGT** | Delivery Target — a number measurable on the finished file | `delivery-targets.md` |
| **VGR** | Visual Grammar Rule — how content is generated | `visual-grammar.md` |
| **RC** | Root Cause finding — why something failed before | `findings-and-decisions.md` |
| **DEC** / **PROP** | Decision / Proposal | `findings-and-decisions.md` |

## How to answer

1. **Reasoning before values.** Where a prompt asks for a rationale, give it
   *before* the answer, not after — otherwise it becomes a justification for
   something already decided.
2. **Never guess a measurable value.** If it must be measured, return `null`
   and say what needs measuring and from what source. A guessed number gets
   adopted and then defended.
3. **Stay inside the scope you are given.** If a requirement outside your
   listed IDs appears relevant, **name it and stop** — do not act on it.
4. **End every response with:**

```
UNRESOLVED  — what you could not determine, and why
ASSUMPTIONS — what you decided without being told
FLAGS       — anything that contradicts an input, or that a later layer
              needs to know
```

Silence is not an acceptable answer to any of these three. If a section is
genuinely empty, write "none" — an omitted section reads as "not applicable"
when it usually means "not considered".
