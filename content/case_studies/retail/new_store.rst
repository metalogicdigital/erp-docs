===================
Opening a new store
===================

A retail chain grows by opening stores, often several in a season. In the legacy setup a new
store meant weeks of master-data loading, manual checks and a nervous first day of billing. In the
new design a store is a **configuration**, not a project: the same steps every time, each one
checked by the system.

.. graphviz::
   :caption: New store go-live, from company to first bill

   digraph ns {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      a [label="1. Store company\nstate, GSTIN, zone"];
      b [label="2. Warehouse,\nlocations, operations"];
      c [label="3. Store node\nand licence"];
      d [label="4. Store server\n(container stack)"];
      e [label="5. Masters\ninitial load"];
      f [label="6. POS, users,\nopening stock"];
      g [label="7. Verify\nand go live", fillcolor="#e6f2f2", color="#017e84"];
      a -> b -> c -> d -> e -> f -> g;
   }

Step 1: Create the store company
================================

At the head office, create the store's company with its **state and GSTIN** (which decide
intra- or inter-state tax on every transfer), short code and zone. Two settings make inter-company
trading automatic:

* the **inter-company user** that creates the store's purchase orders when HO confirms a sale to
  the store;
* **auto-validation**, so those purchase orders confirm themselves.

The system will not create a store company until the branch contact tag and the branch numbering
sequence exist, and the store's warehouse must belong to the store's company.

Step 2: Warehouse, locations and operations
===========================================

Each store gets its **main**, **damage** and **return** locations and the operation types the
retail flows rely on: receipt, delivery, goods return, customer exchange, POS order, and the
internal moves between main, damage and return stock. A serial-number sequence is configured for
any company that mints serials.

Step 3: Register the store node and licence
===========================================

Store node
   The store is registered as a sync node: its code, the store company it belongs to (one node
   per company), its address and a per-node API key. The node is what live sync routes
   company-scoped documents to (see :doc:`live_sync`).

Replication switches
   Per store, administrators choose which master types replicate there (for example incentive
   structures or targets), so a store can be brought on in stages.

Store licence
   An encrypted licence key per store fixes the number of cashier and back-office users,
   permanent or temporary, with an expiry date. It is generated and emailed from HO.

Step 4: Bring up the store server
=================================

Every store server is installed by the same scripted runbook, phase by phase, each one safe to
re-run:

#. **Preflight**: read-only checks of the machine and network.
#. **Container runtime and network**.
#. **Database**: PostgreSQL configured for change capture.
#. **Change-capture infrastructure**: the store's own Kafka and Debezium.
#. **Build and deploy** the store Odoo image; on start the container upgrades its modules and
   claims its node identity.
#. **Reverse proxy**, then the **change-capture pipeline**.
#. **Verify**: the HO node address is correct, only HO and the store itself are registered
   nodes, HO is reachable and every container is healthy.

Step 5: Load masters
====================

With the node active, HO bootstraps the store over live sync:

* **Reconcile identities** first, if the store already holds data, so that existing records are
  linked to HO's by natural key and never duplicated.
* **Initial load** next: categories (parents first), attributes and values, articles and
  variants, employees (whose badge number is used for sales incentives), taxes with their price
  bands, units, price grades, offers, replenishment sources, incentive structures and
  promotions. Masters arrive exactly the way future changes will.

A master-data comparison shows HO count vs store count vs difference per master type, so
completeness is a number, not a feeling.

Step 6: POS, users and opening stock
====================================

POS terminals and payment methods are configured at the store; seats follow the licence.
Cashiers and floor staff come from the replicated employee master with their discount limits.
Opening stock arrives either as a normal HO dispatch or as an opening-stock import, split into
manageable files automatically (see :doc:`grc`).

Step 7: Verify and go live
==========================

The go-live order is always **division → zone → warehouse → store**. Before the first bill:

* the sync dashboard shows the store as live with no master backlog;
* a test dispatch from HO arrives as a store receipt and is acknowledged back;
* a test POS sale reaches HO and is invoiced in the store's mirror company;
* the store appears in the analytics filters.

Because every step is the same for every store, a store can go live on its own night, and the
next one can follow the next night.
