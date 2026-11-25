# Question quality

Budget: **two rounds, batched**. A round is one message containing every question you have. Two rounds is not a
target to spend — most tickets need one, and some need none.

## The test

Ask only if **both** hold:

1. The answer **changes the plan** — a different requirement, a different order, a different contract. Not a
   different sentence in it.
2. You **cannot get it** from the code, the docs, the tests or the ticket. You have to have looked (see
   `discovery-checklist.md`) before you may claim this.

Everything else is stated as an assumption and carried into the plan's Assumptions block. **A decision with a stated
assumption beats a question**: the human corrects a wrong assumption in five seconds, and answers a question in five
minutes.

## Shapes

| Ask | Do not ask |
|-----|-----------|
| A **domain rule nobody wrote down**: "The ticket does not say what happens to an order already in `SHIPPED` when a refund is requested — reject, or allow with a manual flag?" | Anything `ARCHITECTURE.md` answers: "Which folder should this go in?" |
| A **trade-off with no technically right answer**, where the ranked goals do not separate the options | Anything the constitution answers: "Should I write tests?" (rule B1), "Should the PR be a draft?" (rule A4) |
| A **contract decision that binds someone outside this repo**: a shipped mobile client, a third party, a partner integration | Permission to do the thing you were asked to do: "Shall I start?", "Is this approach OK?" |
| A **missing acceptance criterion** for a case the ticket clearly implies but never states | A question whose answer you would ignore anyway because the code already settles it |
| **Access you do not have**: a credential, a sandbox, a fixture, a design frame | Anything you have not tried to answer yet |

## Form

- **Batch.** One message, numbered. Three questions in one message cost one context switch; three messages cost three.
- **Carry your answer.** Every question ships with the answer you will use if nobody replies: *"…— I will assume
  reject, because goal 2 ranks correctness over conversion."* This turns a blocking question into a confirmation.
- **Closed beats open.** Offer the two or three real options with their consequence, rather than "how should this
  work?". Use `AskUserQuestion` when the options are genuinely discrete.
- **Name the cost.** "If this is wrong, R4 and R5 change" tells the reader how hard to think about it.
- **No stacking.** Do not ask a question whose answer depends on an answer you are still waiting for; make the
  dependent one round two, or assume through it.

## The failure mode this budget exists to prevent

An interrogation is not diligence. Every question you ask that the code already answered teaches the reader that
the agent did not read the code — and the next plan gets less attention, not more. Two rounds of good questions and
a plan full of explicit assumptions is the target; ten precise questions is a worse outcome than three questions and
seven assumptions, even when every one of the ten is reasonable.
