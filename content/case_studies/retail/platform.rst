===========================
Platform and supportability
===========================

Retail volumes break assumptions that hold for most Odoo deployments: purchase orders with tens
of thousands of serial-tracked pieces, millions of serial numbers to search, hundreds of users
across shifts who are not ERP specialists, and a support team that must answer "what happened to
this bill?" in minutes. These platform modules sit underneath every business flow.

Coded errors with a built-in support playbook
=============================================

**MetaLogic Error Codes** (`mtl_error_codes`) gives every user-facing error a stable code,
shown as `[MTLD-STOCK-0007] message`. Behind each code sits a registry entry that turns an error
into an action:

* a plain-language definition and where in the process it is raised;
* a **user hint**, a **remediation** and a **workaround**;
* severity (info, warning, error, critical) and side (HO, store or both);
* a **resolution type**: a diagnostic script, **escalation to a named persona** with the
  information that persona needs, or a guarded data fix an administrator can run.

* **1,800+ codes** across the HO and store, with almost all of them hand-reviewed.
* **Seven escalation personas** in three levels: warehouse and inventory operators (L1); master
  data, finance and tax, application support and store IT (L2); engineering (L3).
* **Occurrence log**: every coded error, failed scheduled job, coded warning and uncoded
  user-facing error is recorded in its own transaction, so the log survives the rollback of
  the action that failed. Counters show how often each code fires and when it was last seen.
* **Guarded data fixes**: a fix first runs `diagnose()` in a savepoint that is always rolled
  back, then `apply()`, then diagnoses again. The change is kept only if the second diagnosis is
  clean. Every run is logged.
* **Printable catalogue** for the service desk, and a codemod that wraps every `raise` in a
  module so new code is covered automatically.

.. example::
   A cashier sees `[DLV-027] Delivery blocked: the destination store is unreachable`. The
   service desk looks the code up, sees that L2 store IT owns it, and that the hint is to check
   the store's sync heartbeat. The dispatch can be released as soon as the store is back online,
   with nothing lost.

Background jobs with live progress
==================================

Standard Odoo runs a button click inside the web request: a long action freezes the screen and
can hit an HTTP timeout. **MetaLogic Background Jobs** (`mtl_background_jobs`) moves heavy
actions to a queue without changing how users work.

* A developer calls `enqueue(records, method, ...)`; the task runs as the user who clicked, with
  their language, timezone and allowed companies.
* Parallel worker slots claim tasks with `FOR UPDATE SKIP LOCKED`; enqueuing wakes a slot at
  once.
* Progress is committed on its own cursor and pushed to the user's browser over the Odoo bus. A
  progress bar appears in the top bar on every page and on the record itself, and survives a
  page reload.
* A failed task rolls back completely and keeps its error for the user and for support.

It is used for **purchase order confirmation** above 2,000 serial-tracked units (receipt lines
are created in chunks of 1,000), **receipt validation** above 500 lines, promotion serial
re-allocation, and bulk master updates.

Global number search
====================

Retail staff think in numbers, not menus: an indent, a lorry receipt, a PO, a barcode, a serial,
an inward or outward, a journal entry, a gate pass or a loyalty card. **MetaLogic Global Search**
(`mtl_global_search`) adds one search box in the top bar and the command palette that finds any
of **22 number types across 18 models** and opens the record directly.

* Keys are normalised (`WH/OUT/42135` matches `whout42135`), with exact, then prefix, then
  substring matching.
* A dedicated PostgreSQL index is the durable store, and an in-memory RediSearch index serves
  recently active records in milliseconds.
* Indexing happens after commit on a background executor, so saving a document never waits for
  search. A catch-up job backfills history and anything missed.
* Every hit is re-checked through the ORM for access rights and record rules, so search never
  reveals a record the user could not open.
* A **related-records panel** shows lines, deliveries, invoices and loyalty cards linked to the
  hit.
* If the cache is down, the database answers; if both are down, Odoo keeps working.

Entity trace: the story of a record
===================================

When something goes wrong with a delivery, a sale order or a serial, support needs every
connected record, who touched it and in what order. **MetaLogic Entity Trace**
(`mtl_entity_trace`) crawls relations in both directions from any record and captures a portable
bundle:

* every stored field, the field schema, external ids and audit columns;
* a dependency-first import order;
* the users involved and the role they played;
* a timeline of creation, writes, chatter and tracked state changes.

The bundle opens in a visualiser with a swimlane timeline per user, a lineage graph and a
generated step-by-step runbook. It can be imported into a test database (with a dry-run mode) to
rebuild the exact scenario for root-cause analysis. Secrets and user credentials are stripped by
design.

Governance and access control
=============================

Profile-based access
   Field, menu, button, tab, report and action visibility per access profile, read-only fields,
   domain rules and password expiry, on top of Odoo groups.

Per-user menus
   Hide any menu for chosen users, with bulk assignment from a spreadsheet.

Module audit trail
   Every install, upgrade and uninstall is logged with user, host and database. Uninstall is
   restricted to a dedicated role.

Session timeout
   Idle sessions are logged out automatically on shared store terminals.

Automated backups
   Scheduled database backups to local, remote or cloud storage.

Mass editing and advanced list search
   Mass-edit actions for administrators, and per-column search bars in list views (date ranges,
   many-to-one, multi-value).

Report delivery options
   Print, download or open-in-tab for every PDF report, with a default per report.

Safe staging copies and the admin toolkit
=========================================

Test and training environments are restored from production, so they must never send a real
email, take a payment or call an external service. **MetaLogic Safe Staging**
(`mtl_safe_staging`) neutralises every non-production copy automatically on start-up, using
switches that survive a database restore, and keeps MetaLogic's own background services running
so that sync, search and job queues can be tested realistically.

The **MetaLogic Admin Toolkit** (`mtl_admin_toolkit`) gives administrators one place to see what
each system parameter is for and which addon owns it, the fields each addon adds to settings, a
record explorer for any model with saved filters, and an inspector showing resolved form views,
field paths and related tables.
