=============================================
Architecture: HO, virtual and physical stores
=============================================

The solution runs on **two layers of Odoo**: one head-office database that holds a mirror
"virtual" company for every store, and one database per physical store that runs the tills. Live
sync keeps the two in step. This page explains the design and why it pays off.

.. graphviz::
   :caption: Head office with virtual stores, linked to physical stores

   digraph arch {
      rankdir=LR;
      compound=true;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];

      subgraph cluster_ho {
         label="Head-office database"; color="#714B67"; fontcolor="#714B67";
         main [label="Main company\nbuying, GRC, warehouse,\nserial numbering", fillcolor="#f3eef1", color="#714B67"];
         v1 [label="Virtual store A\n(store company)"];
         v2 [label="Virtual store B\n(store company)"];
         v3 [label="Virtual store C\n(store company)"];
         main -> v1 [label="inter-company", fontcolor="#888888"];
         main -> v2; main -> v3;
      }

      s1 [label="Physical store A\nOdoo + POS", fillcolor="#e6f2f2", color="#017e84"];
      s2 [label="Physical store B\nOdoo + POS", fillcolor="#e6f2f2", color="#017e84"];
      s3 [label="Store C\nmanaged at HO", style="rounded,dashed", color="#888888"];

      v1 -> s1 [dir=both, label="live sync", fontcolor="#888888"];
      v2 -> s2 [dir=both, label="live sync", fontcolor="#888888"];
      v3 -> s3 [style=dashed, label="virtual", fontcolor="#888888"];
   }

The two layers
==============

Head office
   One database with the **main company** (vendor buying, goods receipt, central warehouse,
   serial numbering) and **one company per store**. Each store company has its own state and
   GSTIN, warehouse and locations, journals and POS orders.

Physical store
   A complete Odoo with POS, its own PostgreSQL and its own change-capture stack. It sells,
   receives, transfers and counts locally, and keeps working if the WAN goes down.

The link
   Every physical store is a **sync node** bound one-to-one to its store company at HO. Live sync
   (see :doc:`live_sync`) replicates masters and promotions down and transactions up.

What the virtual store holds
============================

For every store, the HO company receives:

* the inter-company purchase orders and receipts created by HO dispatches;
* the store's **POS orders**, which HO invoices again in that company;
* the store's stock movements (internal moves, POS deliveries, returns, damage), validated again
  at HO so that HO stock per store equals the store's own;
* the store's end-of-day entries, credit notes and vouchers;
* incentives, targets and audit results.

Each store's receipt channel is decided automatically: **live sync** for a connected physical
store, **virtual** for a store managed entirely at HO, and **unreachable** (dispatch blocked) when
a store's node is switched off. A store can start virtual and move to live sync later without
changing any document.

Why this architecture
=====================

Billing never depends on the network
   Each store bills against its own database. A WAN outage, an HO upgrade or a peak-hour load
   spike at HO does not stop a till. Changes queue and drain when the link returns.

One database for the whole business
   Consolidated stock, sales, margin and P&L by store come from a single database with a company
   filter: no consolidation tool, no nightly merge.

Real documents between real GSTINs
   HO and each store are separate companies with their own GSTIN, so a dispatch is a genuine
   inter-company sale and purchase, with the correct GST treatment chosen automatically from the
   two states, e-way bills and e-invoices, and inter-company payments.

Statutory books per state
   Because every store company has a state, exports to the external accounting system map
   cleanly to one statutory company per state GSTIN.

Central control, local speed
   Prices, promotions, MBQ plans, targets and incentives are defined once at HO and published to
   exactly the stores that need them; tills apply them locally without a round trip.

Flexible store models
   Franchise counters, pop-ups or a store waiting for its server can run **virtual** from day one,
   with HO validating their receipts, and move to a physical server when ready.

A clean audit trail
   Every inter-store movement passes through HO as a pair of documents, so stock in transit,
   transfer pricing and tax are always visible in one place.

Scaling the head office
=======================

The head office runs as a container stack built from one immutable image, with two kinds of
node:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Node
     - Role
   * - UI nodes
     - Serve users. Scheduled jobs are switched off on them, so a heavy job never slows a
       buyer's screen. Stateless and horizontally scalable.
   * - Job node
     - Runs scheduled jobs, inbound integrations and store sync. Store traffic is pinned per
       store code, so each store's stream is processed in order.
   * - Load balancer
     - Least-connections routing with sticky sessions, per-store pinning, websocket routing and
       health checks.

**Peak-season sales** multiply HO load: more re-pricing, more promotions published, more
dispatches, and far more POS orders flowing back to be invoiced. Capacity is a replica count:
scale the UI nodes up for the festive season and back down afterwards, with no application or
database change. Rollouts start the new node before stopping the old one and roll back
automatically if the new node does not become healthy.

Inside the stores, the same principle applies on a smaller scale: the change-capture delivery
workers are a consumer group that can be scaled out, and a separate priority worker pool carries
price and promotion changes so they never wait behind a backlog of transactions.

Scaling the stores
------------------

A store used to be one container: till users, scheduled jobs and sync traffic shared the same
processes. The **store stack** now has the head office's shape on a store-sized machine:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Node
     - Role
   * - UI nodes (two)
     - Serve cashiers and back-office users, with scheduled jobs off. Updating one while the
       other serves keeps the tills answering.
   * - Job node
     - Runs the store's scheduled jobs and the inbound integration calls.
   * - Sync node
     - A second job-type node with scheduled jobs off, dedicated to the change-capture traffic
       from head office, so a burst of price and promotion changes never starves the tills. The
       load balancer sends sync traffic to it first and to the job node only as a fallback.
   * - Load balancer
     - One address for the store's users and for head office, with health checks.

Rolling updates under load were tested with a probe every second: forcing an update of the UI
nodes lost no request, and killing a UI node mid-session lost one in thirty-eight. A store keeps
its **way back**: the old single-container deployment is preserved, so a store can return to it
with two commands.

The store's automatic upgrade understands both shapes. On a store stack it builds a release image,
runs the module migration in a separate container on the store's network, and rolls the stack; on
a single-container store it keeps the older in-place path.

.. seealso::
   :doc:`../../delivery/cicd` for how images are built, migrated and rolled out.
