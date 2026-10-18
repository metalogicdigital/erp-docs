======================
Defect-fixing pipeline
======================

Store staff report problems the way anyone would: a screenshot of an error, a bill number, "the
delivery won't validate". Our defect pipeline turns that into a proven root cause, a tested fix
and a linked pull request, with production never touched along the way. Engineers follow it as a
playbook, and an AI agent can run the same loop end to end.

.. graphviz::
   :caption: From a production report to a released fix

   digraph defect {
      rankdir=TB;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      report [label="Screenshot / error code / bill number", shape=oval];
      kb [label="1. Knowledge-base lookup\n(known patterns)"];
      prod [label="2. Read-only production investigation\ncode, logs, read-only SQL, timeline"];
      repro [label="3. Local reproduction\nbaseline must FAIL"];
      rca [label="4. Root cause\nproven vs inferred, ruled out"];
      fix [label="5. Fix on a branch\npatched code must PASS"];
      tests [label="6. Regression tests\nunit + end-to-end, red then green"];
      board [label="7. Defect on the board\nDEF##### with blast radius"];
      pr [label="8. Pull request\nauto-linked to the defect"];
      review [label="9. Human review and merge"];
      ship [label="10. Auto-upgrade to sandboxes,\nregression, planned release"];
      learn [label="11. Pattern page + playbook update"];
      report -> kb -> prod -> repro -> rca -> fix -> tests -> board -> pr -> review -> ship -> learn;
   }

The steps
=========

Step 1: Check what we already know
----------------------------------

Every resolved defect leaves a pattern page (symptom, root cause, fix, how to detect,
evidence). The error code or message is looked up first; many issues are recognised in
minutes.

Step 2: Investigate production read-only
----------------------------------------

The investigation reads the screenshot carefully (including timezone), finds the message in
the live code, reads the log around the event, and queries the database through a session
that is **read-only by construction** with a statement timeout. It builds a timeline per
record and writes down which hypotheses were ruled out. Helper tools refuse any command that
looks like a write.

Step 3: Reproduce locally
-------------------------

The scenario is rebuilt on the local HO and store containers, in a transaction that is rolled
back, or on a scratch database. :doc:`Entity trace <../case_studies/retail/platform>` bundles
can recreate the exact production records. The fix is tested from an isolated worktree in a
throwaway container, so the running environment never masks the result. **The baseline must
fail and the patched code must pass.**

Step 4: Root cause
------------------

Recorded as proven or inferred, with the evidence, the scale in production and what was ruled
out.

Step 5: Fix
-----------

The smallest change that addresses the cause, on a branch from `main`, with the commit
message starting with the defect number.

Step 6: Prove it
----------------

The reproduction script is the first proof. Where the flow can be driven end to end, a
Playwright spec is added that is **red on the baseline and green on the fix** and cleans up its
own records; module unit tests are added where they fit.

Step 7: Log it on the board
---------------------------

A defect is created on the Project Planner with where it was seen, the exact error, steps to
reproduce, timeline, root cause, fix, verification, **blast radius and areas to test**, and
what is not fixed. Repeat sightings are appended, never filed twice.

Step 8: Open the pull request
-----------------------------

Title and description start with `DEF#####`, and the body carries problem, root cause, fix,
verification (baseline vs fixed), impact areas to test and known gaps. The link workflow
attaches the pull request and its commits to the defect automatically.

Step 9: Review and merge
------------------------

Always by someone else. Shared framework changes merge before the HO and store changes that
depend on them.

Step 10: Ship
-------------

The release manager upgrades the sandboxes from `main` within minutes; regression runs
there, and production follows the planned release path.

Step 11: Learn
--------------

Scratch data is removed (only the records the investigation created), the pattern page is
written and the playbooks are updated, so the next occurrence is faster.

The AI defect agent
===================

On the Project Planner, ticking **AI Agent Ready** on a defect starts an automated turn of the
same pipeline on dedicated runners:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Stage
     - What happens
   * - Prepare
     - The defect, its linked pull requests and commits, earlier AI turns and up to eight similar
       resolved defects are gathered as context. Repositories are checked out into isolated
       worktrees.
   * - Root cause
     - The agent runs a read-only production diagnosis through an allow-listed tool: approved
       read commands only, a single `SELECT` in a read-only transaction, no configuration or
       credential files.
   * - Fix
     - The agent reproduces the problem, fixes it, deploys the branch to the HO and store
       sandboxes through the normal release mechanism, and validates the result there.
   * - Regression
     - The impacted end-to-end specs are chosen and run headless, separating pre-existing failures
       from new ones.
   * - Finalise
     - Only if the gate passes (reproduced on the baseline, fixed, validated on both sandboxes,
       regression green) are branches pushed and pull requests opened, labelled as AI-proposed.
       The defect moves to **Review** with the root-cause report attached.
   * - Clean up
     - Always runs and returns the sandboxes to their previous branch.

The agent never sees the repository credentials (only the finalise stage can push), production
access is read-only at every layer, and a human still reviews and merges. If the gate fails, the
turn is recorded as "no fix proposed" with its findings. Feedback can be added to the defect and
the agent re-run, with every previous turn in context, up to a turn limit.

Supportability built into the product
=====================================

The pipeline starts long before a defect is filed. Every user-facing error carries a stable code
with a hint, remediation, workaround and escalation persona, and every occurrence is logged even
when the action rolls back (see :doc:`../case_studies/retail/platform`). Support teams can
resolve the common cases with guarded data fixes; the rest arrive at engineering with the code,
the occurrence history and the persona's findings already attached.
