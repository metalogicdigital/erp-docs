:show-content:
:show-toc:

=================================================
Retail: a multi-store fashion and lifestyle chain
=================================================

.. raw:: html

   <div class="mtl_stats">
     <div class="mtl_stat"><b>~50</b><span>stores, each with its own Odoo and POS</span></div>
     <div class="mtl_stat"><b>1</b><span>head-office database with a mirror company per store</span></div>
     <div class="mtl_stat"><b>1 : 1</b><span>one serial per piece, each priced and taxed individually</span></div>
     <div class="mtl_stat"><b>~2 s</b><span>from a store sale to chain-wide analytics</span></div>
   </div>

The customer
============

A fashion and lifestyle retail chain in South India: apparel, sarees, footwear, cosmetics and
accessories across roughly fifty stores in more than one state, supplied by a central head office
and warehouse that buys from hundreds of vendors. Most goods are serial-tracked piece by piece,
each with its own price, offer and ageing.

The chain ran on a legacy retail ERP with a separate BI layer, spreadsheets for planning and
targets, and point integrations between the head office and the stores.

The challenge
=============

Piece-level retail at chain scale
   Every unit is unique: its own cost, RSP, MRP, offer and age. Purchase orders run to tens of
   thousands of pieces, and stores hold hundreds of thousands of serials.

GST that depends on the price
   Apparel and footwear tax rates change at a price threshold, so the right tax depends on the
   final selling price after discounts, line by line.

Stores that must never stop billing
   Each store needs its own database for speed and resilience, yet HO needs one consistent view
   of stock, sales and books.

Promotions as a weapon
   Slabs, bundles, buy-and-get across pools, bill-value tiers and ageing markdowns, published to
   chosen stores, applied instantly at the till and never double-counted on a piece.

Control without friction
   MBQ and margin approvals, audited receipts, guarded dispatches and a full inter-company
   paper trail, without slowing the people on the floor.

Answers in hours, not days
   Merchandisers and finance needed live data, not yesterday's extract.

The solution at a glance
========================

We implemented **Odoo 17** at the head office and in every store, and built a set of retail addons
and MetaLogic platform modules on top of the standard apps:

.. graphviz::
   :caption: The retail value chain, end to end

   digraph vc {
      rankdir=TB; nodesep=0.3; ranksep=0.45;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      { rank=same;
        md [label="Master data\nhierarchy, prices,\nGST bands"];
        pl [label="Planning\nMBQ, targets,\nvendor visits"];
        pr [label="Procurement\nindent, PI, PO"];
        gr [label="GRC\nreceive, serialise,\nprice"];
        ds [label="Distribution\nauto PO, batches,\ne-way bills"]; }
      { rank=same;
        st [label="Store\ninwarding"];
        ps [label="POS\npiece-level sale"];
        ho [label="Back to HO\ninventory, journals,\nincentives"];
        an [label="Analytics\nreal time", fillcolor="#f3eef1", color="#714B67"]; }
      pm [label="Promotions\nstudio + engine"];
      md -> pl -> pr -> gr -> ds;
      ds -> st [constraint=false];
      md -> st [style=invis];
      st -> ps -> ho -> an;
      ps -> pm [dir=back];
   }

Highlights:

* **Serial-level merchandising** with nineteen attribute and descriptor slots, computed RSP and
  MRP from category margin bands, and price-ending rounding.
* **Price-band GST** chosen from the actual net price at every step, including the till, plus
  automatic intra/inter-state treatment and IGST forcing.
* **MBQ planning by price point** feeding purchase indents, with MBQ and RSP-margin approval
  stages.
* **A guarded GRC**: receive against the lorry receipt, excess and shortage with automatic debit
  notes, mandatory serial data with guided fill-in, landed cost before dispatch, background
  validation of very large receipts.
* **Distribution through inter-company rules**: one HO sale order creates the store's purchase
  order, batches, e-way bills and invoices, and the store receives by scanning bales and serials.
* **The Promotion Studio**: item pools, slabs, bundles, get pools, allocation to stores, sample
  testing and one-serial-one-promotion, applied by a matching engine at the till.
* **Fast, resilient tills** that load in about a second, patch price and stock changes live and
  keep selling offline.
* **Live sync** by change data capture between HO and every store, in both directions, ordered,
  idempotent and loop-free.
* **A virtual company per store at HO**, giving one database for consolidated books and genuine
  inter-company documents between GSTINs.
* **Real-time analytics** with full parity to the ledger.
* **Supportability built in**: 1,800+ coded errors with remediation and escalation, background
  jobs, global number search and record lineage tracing.

Explore the solution
====================

The pages follow the flow of goods and money through the business:

.. toctree::
   :titlesonly:

   retail/master_data
   retail/new_store
   retail/planning
   retail/procurement
   retail/grc
   retail/distribution
   retail/promotions
   retail/pos
   retail/accounting
   retail/workforce
   retail/live_sync
   retail/architecture
   retail/analytics
   retail/platform
   retail/module_catalogue
