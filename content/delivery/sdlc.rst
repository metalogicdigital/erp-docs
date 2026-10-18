============================
SDLC and the Project Planner
============================

We run delivery from our own Odoo application, the **MetaLogic Project Planner**. It holds the
whole software lifecycle in one place: from a stakeholder's requirement down to the commit that
implemented it, and from a production defect to the pull request that fixed it.

The work hierarchy
==================

.. graphviz::
   :caption: Planning hierarchy and development traceability

   digraph sdlc {
      rankdir=TB; nodesep=0.3; ranksep=0.4;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      project [label="Project"];
      req [label="Requirement"];
      theme [label="Theme"];
      feature [label="Feature"];
      epic [label="Epic"];
      story [label="Story\nSTRY#####", fillcolor="#f3eef1", color="#714B67"];
      defect [label="Defect\nDEF#####", fillcolor="#fbecec", color="#D9534F"];
      sprint [label="Sprint\nSPRT#####"];
      pr [label="Pull request"];
      commit [label="Commit"];
      test [label="Test case"];
      project -> req -> theme -> feature -> epic -> story;
      story -> defect [style=dashed];
      sprint -> story [style=dashed]; sprint -> defect [style=dashed];
      story -> pr; defect -> pr; pr -> commit;
      story -> test; defect -> test;
   }

Requirement
   Stakeholder, priority from low to critical, and approval status. Requirements link to the
   themes that deliver them.

Theme, feature, epic
   The planning hierarchy, each level with an owner, start and due dates.

Story (`STRY#####`)
   Acceptance criteria and a lifecycle of draft, in progress, in review, testing and done.

Defect (`DEF#####`)
   Steps to reproduce, the related story, engineering details, and precise closure states
   (resolved, duplicate of…, can't reproduce, working as designed, invalid) so defect metrics
   mean something.

Sprint (`SPRT#####`)
   Dates, objectives, retrospective and achievements, with stories and defects planned in and out.

Test case
   Steps, expected result and pass/fail, attached to a story or a defect.

Every record has full chatter and field tracking, so the history of a decision is never lost.

Traceability from code to requirement
=====================================

Pull requests link themselves to the board. Each product repository runs a small workflow on
every pull-request event:

#. The pull request description must start with the work item number, for example
   `DEF00124 Short-shipment receipt…` or `STRY00001 Promotion allocation`. A pull request
   without one fails the check.
#. The workflow collects every commit in the pull request and sends them to the Project
   Planner's API, authenticated as a dedicated integration user.
#. The planner creates or updates the pull request record (open, closed or merged) and its
   commits, and links them to the story or defect.

The result: from any defect you can open the fix, its commits, the tests that prove it and the
sprint it shipped in. From any commit you can find out *why* it exists.

Working rules that keep quality high
====================================

* **Trunk-based development** on short-lived branches (`feat/…`, `fix/…`, `DEF…`), merged
  through reviewed pull requests. Nobody merges their own pull request.
* **Shared framework first**: when a change spans repositories, the shared MetaLogic addons merge
  first, then the head-office and store repositories that depend on them.
* **Tests travel with the change**: Odoo unit tests in the module, plus an end-to-end journey in
  the Playwright suite when the flow crosses HO and store.
* **Production is read-only to engineers.** Investigation uses read-only database sessions and
  log access; changes reach production only through the release process.
* **A living knowledge base**: every resolved defect adds a pattern page (symptom, root cause,
  fix, how to detect, evidence) and updates the playbooks that engineers and AI agents follow.

.. seealso::
   :doc:`defect_pipeline` for how a defect moves from a screenshot to a merged fix.
