=================================
Live sync between HO and stores
=================================

Every store runs its own Odoo database so that billing never depends on the WAN. That decision
creates the hardest problem in the whole programme: keeping one head office and dozens of store
databases consistent, in both directions, in near real time, without double-posting a sale or
losing a promotion.

Standard Odoo has no answer for this. It has no multi-database replication, no cross-database
record identity, no ordered and idempotent delivery, and no loop protection. **MetaLogic Live
Sync** (`mtl_live_sync`) is the engine we built to provide all four.

.. graphviz::
   :caption: Change-data-capture pipeline, one per site

   digraph cdc {
      rankdir=TB; nodesep=0.35; ranksep=0.45;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];

      subgraph cluster_ho {
         label="Sending site (HO or store)"; color="#714B67"; fontcolor="#714B67";
         { rank=same; hodb [label="Odoo DB\n(PostgreSQL WAL)"]; deb [label="Debezium\nlogical decoding"];
           kafka [label="Kafka\nordered topic"]; mapper [label="Mapper\napplies sync rules"]; }
         { rank=same; workers [label="Delivery workers\n(scale out)"]; ctrl [label="Controller\noutbox per record"];
           ledger [label="CDC ledger\nevents + deliveries"]; }
         hodb -> deb -> kafka -> mapper;
         mapper -> ledger -> ctrl -> workers;
      }

      subgraph cluster_store {
         label="Receiving site"; color="#017e84"; fontcolor="#017e84";
         { rank=same; recv [label="Receiver /apply\nORM, idempotent"]; sdb [label="Odoo DB"]; }
         recv -> sdb;
      }

      workers -> recv [label="HTTPS / push stream\nper-node key", fontcolor="#888888"];
   }

Capture without touching the application
========================================

Changes are read from PostgreSQL's write-ahead log by Debezium through a logical replication
slot. Odoo code is not patched, no triggers are installed, and a busy save pays nothing extra for
being replicated. Only tables on an explicit allow-list are captured; activating one sets
`REPLICA IDENTITY FULL` so that updates and deletes carry the full previous row. Many2many join
tables are watched directly, so adding a tag to a product or a serial to a promotion is a sync
event too.

Each captured change goes through three stages:

#. **Capture event**: the raw row change with its log sequence number (the ordering key),
   transaction id, operation and before/after images.
#. **Business event**: scalar values in a payload, and every many2one expressed as
   `(model, source id)` so that the receiver can translate it.
#. **Delivery**: one row per event per target node, with status, attempts, next retry time,
   error class (network, rejected, configuration) and a hold key of `node:model:record` that
   keeps changes to one record in order while different records flow in parallel.

Rules that say what goes where
==============================

Replication is driven by **sync rules** that business administrators maintain in Odoo, not by
code:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Setting
     - What it controls
   * - Direction
     - HO → stores, stores → HO, or both.
   * - Operations
     - Create, update and delete toggled separately (for example: stores may create customers but
       never delete them).
   * - Fields
     - All fields except a list, or only a list. Audit columns are always excluded.
   * - Scope
     - **Global** (master data to every store), **company-scoped** (a store's own documents only
       go to that store) or **record targets** (each record carries its own list of stores; this
       is how a promotion reaches exactly the stores it was allocated to).
   * - Natural keys
     - Fields that match an incoming record to an existing local one instead of creating a
       duplicate (barcode, serial number, tax name, account code…).
   * - Priority
     - Its own topic and worker pool, retried within seconds. Used for price and promotion
       changes that must reach open tills immediately.
   * - Relay
     - HO re-emits a store's change to the other stores (a loyalty card or a credit note issued
       in one store becomes usable in all of them).

The head office ships with **49 rules covering 47 business models** and **68 watched tables**,
from products, taxes and accounts down to receipt packets, credit notes and loyalty cards.

Applying a change safely
========================

The receiver at the other end never writes SQL. It applies every change **through the Odoo
ORM**, so constraints, computed fields and business logic run exactly as if a user had made the
change. On top of that:

Idempotency
   Each delivery has a UUID. A delivery that is replayed, retried or taken over by another
   worker after a crash is recognised and skipped.

Cross-database identity
   Record ids are never trusted across databases; two databases restored from the same backup
   and then diverged will reuse ids. An identity map translates `(source node, model, source
   id)` into the local id, and natural keys reconcile records that already existed on both sides
   before sync was switched on.

Dependency auto-fetch
   If a sale arrives for a customer the HO has never seen, the receiver fetches the customer
   from the sender first (recursively, with a depth limit and cycle guard), then applies the
   sale.

Reference data by key
   Nineteen reference models (locations, operation types, products, units, accounts, journals,
   taxes, POS sessions, payment methods…) are resolved by key inside the sender's company and are
   never created from a copy.

Accounting as posted
   Journal entries are applied exactly as the sender balanced them, without recomputing lines,
   then posted. HO and store books therefore agree to the paisa.

Loop prevention
   The first thing every apply does is record its own transaction id. The mapper skips any
   change produced by such a transaction, so a document that syncs in both directions (a sale
   order, a picking) never ping-pongs between HO and a store.

Business hooks
   A model can filter what it accepts (HO accepts only invoiced POS orders), prepare incoming
   values, and run follow-up actions after apply (invoice the POS order, confirm the sale order,
   validate the reported picking).

Built for unreliable networks
=============================

A store that loses connectivity keeps billing. Its outgoing changes queue locally and its
incoming ones queue at HO. When the five-minute heartbeat sees the store again, failed
deliveries are re-queued automatically and drain in order. Retries back off exponentially up to
a configurable cap, every node can override the maximum number of attempts, and operators can
retry or re-queue from Odoo itself.

Operators see the pipeline from inside Odoo
===========================================

The CDC ledger lives in its own PostgreSQL database so that replication volume never bloats the
ERP. Odoo reads it through `postgres_fdw` foreign tables, so the standard list, search, filter
and group-by work on events and deliveries. A field-by-field before/after diff widget shows
exactly what changed in each captured row. A live dashboard summarises live stores, pending and
processed transfers, failures today and master-data backlog per type.

Bootstrapping a store
=====================

Bringing a store onto live sync is a two-step operation from the same screen:

* **Initial load** re-emits existing rows through the normal pipeline in batches, so a new store
  receives masters exactly the way it will receive future changes.
* **Reconcile identities** pages through the peer's natural keys and links only unambiguous
  matches, so a store that already had data is joined without duplicates.

.. seealso::
   - :doc:`architecture` for how live sync fits into the HO and virtual-store design.
   - :doc:`promotions` for record-targeted publishing of promotions to selected stores.
   - :doc:`../../delivery/cicd` for how the sync stack is deployed and scaled.
