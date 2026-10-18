==============
CI/CD pipeline
==============

A multi-store retail ERP has two very different deployment targets: one head office that must
scale with peak-season load, and dozens of store servers on branch-office networks. Our pipeline
treats Git as the single source of truth for both and makes every upgrade **change-aware**: only
the modules a commit actually touched are upgraded.

Repositories
============

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Repository
     - Contents
   * - Head office
     - The HO Odoo tree: Odoo core, the retail addons, the HR and payroll suite, and HO-specific
       overrides of the shared addons.
   * - Store
     - The store Odoo tree: store addons, POS extensions and store-specific overrides.
   * - MetaLogic addons
     - The shared framework every project uses: live sync, error codes, background jobs, global
       search, POS performance, promotion studio, release manager, entity trace and the safe
       staging tools.
   * - Operations
     - Container orchestration, load balancer, CDC stack, deployment and cut-over plans,
       performance tuning and error-code tooling.
   * - End-to-end tests
     - The Playwright suite that drives real journeys across HO and store.
   * - Project Planner
     - The SDLC application described in :doc:`sdlc`.

How shared addons reach each side
=================================

Shared addons live once, in the MetaLogic addons repository. A sync step copies the addons a
side needs into its build and then lays that side's **overrides** on top: the HO and the stores
can ship different sync rules, error-code catalogues or tests for the same addon without forking
it. The sync records what it wrote, so a file deleted upstream disappears downstream on the next
run. The same step runs on developer machines (as a one-shot container before Odoo starts) and in
the release build, so a developer's environment is built exactly like a release.

The release flow
================

.. graphviz::
   :caption: From a merged pull request to a running release

   digraph release {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      merge [label="PR merged\nto main"];
      detect [label="Change detection\n(branch heads vs\ndeployed commits)"];
      select [label="Select touched\nmodules + new\nauto-install addons"];
      build [label="Build immutable\nrelease image"];
      migrate [label="One-off migrate\ncontainer\n(-i / -u, stop after init)"];
      roll [label="Rolling deploy\nhealth-checked"];
      record [label="Record deployed\ncommits in Odoo"];
      store [label="Store: backup tree,\nsync code, upgrade\ntouched modules, reload"];
      merge -> detect -> select;
      select -> build -> migrate -> roll -> record;
      select -> store -> record;
   }

Gated from inside Odoo
   The **MetaLogic Release Manager** (`mtl_release_manager`) gives administrators an
   auto-update switch, a check interval and a target branch per environment, plus a code-sync
   status list and an upgrade monitor. Scheduled runs act only when auto-update is on; manual
   runs always act.

Change detection
   The pipeline compares the remote branch heads with the commits recorded as deployed in that
   database. If nothing changed, it stops.

Only what changed
   Files in the diff are mapped to their nearest module manifest (and override folders to their
   addon). Only those installed modules are upgraded; newly shipped addons on the auto-install
   list are installed. The pipeline never sends an empty upgrade list, which Odoo would treat as
   "upgrade everything".

Immutable HO images
   The head office is built as a release image tagged
   `YYYYmmddHHMM-h<ho-sha>-a<addons-sha>`. A tag is the complete, reproducible unit that is
   rolled out and, if needed, rolled back.

Migrate once, then roll
   Database migrations run in a single one-off container. The serving replicas never run
   upgrades themselves; they are replaced one at a time behind the load balancer.

Store upgrades
   Each store keeps its own container. The pipeline backs up the current code tree on the store,
   syncs the new tree over SSH, upgrades the touched modules inside the running container and
   reloads it. On failure the backup is restored automatically.

Recorded in the ERP
   Deployed commits and a readable result message are written back into Odoo, so functional
   teams can see what version they are running without asking engineering.

Head-office runtime: UI and job nodes
=====================================

.. graphviz::
   :caption: Head-office container topology

   digraph topo {
      rankdir=TB;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      users [label="HO users\n(browser)", shape=oval];
      stores [label="Store servers\n(sync + API)", shape=oval];
      lb [label="Load balancer\n(2 replicas)"];
      ui [label="UI nodes  ×N\nno scheduled jobs", fillcolor="#f3eef1", color="#714B67"];
      job [label="Job node\nscheduled jobs, inbound API,\nstore sync", fillcolor="#e6f2f2", color="#017e84"];
      db [label="PostgreSQL", shape=cylinder];
      users -> lb; stores -> lb;
      lb -> ui [label="sticky sessions,\nleast connections", fontcolor="#888888"];
      lb -> job [label="store traffic,\npinned per store", fontcolor="#888888"];
      ui -> db; job -> db;
   }

The head office runs as a container stack with two kinds of Odoo node built from the same image:

UI nodes
   Serve interactive users. Scheduled jobs are disabled on them, so a heavy job never slows a
   buyer's screen. They are stateless and scale horizontally.

Job node
   Runs scheduled jobs, inbound integrations and store sync. Store traffic is pinned to a
   backend by store code, so one store's stream is always handled in order by the same worker.

Load balancer
   Least-connections routing with sticky sessions for users, header-based pinning for stores,
   websocket routing to UI nodes, and health checks on every node.

**Scaling for peak season.** Festive and end-of-season sales multiply HO traffic: more buyers
re-pricing, more promotions published, more dispatches and more store transactions flowing back.
Because UI nodes are stateless replicas of one image, capacity is a replica count: scale UI nodes
up for the season and back down afterwards, with no change to the application or the database.
Updates start the new replica before stopping the old one, and a node that does not become
healthy within the monitoring window rolls back automatically.

Production cut-overs
====================

Moving production to a new capability (for example from REST integration to live sync) follows
a written, phased plan rather than a single big bang:

#. Decisions and preparation, including a **mandatory rehearsal on a restored backup**.
#. A head-office night window with a validation gate after every step.
#. A soak period, then a **pilot store**, then a pilot soak.
#. **Waves of two to five stores per night** until every store is live.
#. Steady state.

Every step has a validation check and a rollback step. A store-level **canary route** on the
load balancer moves an individual store onto the new backend, or back, with a one-line map change
and no application or database change.

Rollback and backups
====================

* **Code**: an unhealthy rollout rolls back on its own; any earlier image tag can be redeployed
  with one command. A failed upgrade leaves the previous version running and says so in Odoo.
* **Data**: database migrations are designed to be backward compatible for one release (add
  first, remove a release later). Releases that cannot meet that rule take a full backup before
  migrating.
* **Stores**: a code backup is taken on the store before every sync and restored automatically
  on failure.
* **Go/no-go for production**: a verified full backup less than 24 hours old, a tested restore,
  and a rehearsal that included one rollback.

Environments
============

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Environment
     - Purpose
   * - Developer
     - Head office and store on Docker Compose, with a database restored from a sanitised dump on
       first start, change-capture enabled, and the same addon sync as a release. One script sets
       it up on Windows or Linux.
   * - Sandbox
     - A neutralised copy of production: the HO container stack and store sandboxes that are
       upgraded automatically from `main` within minutes of a merge. The end-to-end suite and the
       AI defect pipeline run here.
   * - Production
     - Released in planned windows, backup first, following the cut-over plan.

Quality gates
=============

* **300+ Odoo unit tests** in the shared framework addons, plus module tests in the HO and store
  addons.
* **About 950 end-to-end test cases in 317 Playwright specs** covering standard flows, the
  custom retail modules, HO↔store sync journeys, live-sync guarantees (delete propagation,
  dependency fetch, identity mapping, loop prevention, idempotent replay, retry exhaustion) and
  promotion publishing.
* End-to-end specs create their own data, drive state changes through the real UI, and clean up
  after themselves, so they can run against a production-like sandbox.

.. seealso::
   :doc:`defect_pipeline` for how a fix is proven before it is merged.
