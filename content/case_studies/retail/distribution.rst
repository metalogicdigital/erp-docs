===================================
Distribution: HO to stores and back
===================================

Once stock is received and priced at the head office it has to reach the right store quickly,
with every piece accounted for, the right GST document for the route, and the books of both
companies agreeing. Distribution in the new system is built on **Odoo's inter-company rules**:
a sale from HO to a store automatically becomes a purchase by that store.

Stock outward via automatic purchase orders
===========================================

.. graphviz::
   :caption: One click at HO creates the documents on both sides

   digraph o {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      subgraph cluster_ho { label="HO main company"; color="#714B67"; fontcolor="#714B67";
         so [label="Store sale order\n(with or without indent)"];
         del [label="Deliveries"];
         bat [label="Batch transfer\nLR, vehicle, parcels"];
         ewb [label="E-way bill /\ndelivery challan"];
         inv [label="Invoice to store\n(intra: no tax, inter: IGST)"];
      }
      subgraph cluster_st { label="Store company"; color="#017e84"; fontcolor="#017e84";
         po [label="Automatic\npurchase order"];
         rc [label="Store receipt"];
      }
      so -> po [label="inter-company\nrule", fontcolor="#888888"];
      so -> del -> bat -> ewb;
      bat -> rc [label="receipt packet\n/ validation", fontcolor="#888888"];
      rc -> inv [style=dashed, label="after store\nreceipt", fontcolor="#888888"];
      po -> rc;
   }

Step 1: The store sale order
----------------------------

The HO dispatcher creates a sale order from the main company to the store company.

* **With indent**: linked to the store's open indent, with an allocation table showing how much
  of each indent line is being met. When an indent is fully served, the store's draft indent is
  closed.
* **Without indent**: a push allocation, for example new-season stock.

Lines are filled by **scanning**, **spreadsheet import** or **document** (every in-stock serial
of a chosen HO receipt in one click). Each line carries its exact serials. The transfer price is
the serial's **cost**, and stock is drawn from main stock (regular) or damage stock.

Guards:

* at most 400 lines per order, to keep documents and e-way bills manageable;
* serials under an active **audit plan** cannot be dispatched;
* **a serial can sit on only one open order**, checked again at confirmation under a database
  advisory lock, so two dispatchers can never send the same piece;
* serials still waiting for **landed cost** cannot be scanned;
* orders not delivered within 14 days are cancelled automatically, releasing their serials.

Step 2: The automatic purchase order
------------------------------------

Confirming the sale order creates a **purchase order in the store company**, as the store's
inter-company user, with HO as vendor, the same intra- or inter-state type, the store's matching
receipt type, taxes recomputed for the route and the store's fiscal position, and auto-confirmed.
Each side references the other.

Step 3: Deliveries and batch transfers
--------------------------------------

Delivery reservations reserve **exactly the serials on the order**, and every serial's prices,
HSN, taxes and attributes are copied to the delivery line. Deliveries are grouped into **batch
transfers** (transfer out), each with transporter, route, LR, vehicle, driver and parcel count.

* **Bale barcodes** are generated per delivery for the store to scan on arrival.
* **Gate passes** are printed for outgoing batches.
* At batch completion, serials still reserved by idle orders are swapped in favour of the batch
  being shipped, and every line is checked for barcode, cost, MRP and both tax sets before
  anything leaves.
* An inter-state batch holds up to 1,000 lines.

Step 4: GST documents
---------------------

* **Intra-state** batches create one **e-way bill or delivery challan per batch**, lines grouped
  by product, HSN and price, without tax.
* **Inter-state** batches are invoiced with IGST; e-invoice references (IRN, acknowledgement) and
  e-way bill numbers are shown on the batch.
* E-way bills are generated through a GST suvidha provider, with vehicle and transporter updates,
  cancellation, extension, consolidated and multi-vehicle movements.

Step 5: Invoice
---------------

The HO invoices the store **only after the store receipt is confirmed**, so an invoice never
precedes the goods. On posting, intra-state invoices carry no tax and inter-state invoices are
forced to IGST at the rate matching the price band. Store payments to HO create the mirror
payment in the store company automatically.

Store and warehouse inwarding
=============================

How a dispatch becomes a store receipt depends on the store's **receipt channel**, decided
automatically from the store's configuration:

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Channel
     - What happens
   * - Live sync
     - Each delivery is packaged as a **receipt packet**: a header, the lines with every serial's
       attributes, prices and taxes, and the bale barcodes. It is sent over live sync, and the
       **store builds its own receipt** from it. HO does not validate the receipt itself, because
       that would count the stock twice.
   * - Virtual
     - For a store whose stock is managed at HO, HO validates the store company's receipt
       directly, rebuilding the lines from the delivery.
   * - Unreachable
     - The store has a sync node but it is switched off. Validation is refused with a coded error
       until the store is back, so stock is never shipped into a black hole.

At the store, the receiving team:

#. **Scans each bale** against the packet's bale barcodes.
#. **Scans every serial**, with the receipt saving scans as it goes so nothing is lost on a
   refresh.
#. **Acknowledges** the receipt back to HO, which records one of three outcomes:

   * **Received**: HO marks the store acknowledgement and completes its side.
   * **Missing**: the serial is flagged *missing in transit* at HO for investigation.
   * **Surplus**: an unmatched-serial record is opened for HO to resolve.

The transport dashboard at HO shows deliveries by category as **dispatched, received and
opened**, and the LR dashboard follows returns by LR.

Returns, damage and store-to-store transfers via HO
===================================================

There is no direct store-to-store document. **The head office is the hub**, which keeps one
place where every inter-store movement is visible, taxed correctly and valued.

.. graphviz::
   :caption: Store A to store B, in two legs through HO

   digraph s2s {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      a [label="Store A\nreturn / transfer out", fillcolor="#e6f2f2", color="#017e84"];
      ho [label="HO\nreturn receipt", fillcolor="#f3eef1", color="#714B67"];
      b [label="Store B\nreceipt", fillcolor="#e6f2f2", color="#017e84"];
      a -> ho [label="leg 1: store sale order\n→ HO purchase", fontcolor="#888888"];
      ho -> b [label="leg 2: HO sale order\n(document = leg-1 receipt)", fontcolor="#888888"];
   }

Leg 1: store A to HO
   Store A sends a regular, return or damage outward. It arrives at HO as a sale order in store
   A's mirror company with HO as customer, and the inter-company rule creates the HO purchase and
   its receipt of the matching type. Before the batch can move, **Get data** pulls each serial's
   brand type, barcode, ageing and attribute slots from the store, so the piece arrives at HO
   with its full identity. Returned serials are marked as returns.

Leg 2: HO to store B
   A normal HO dispatch, typically using **document** mode to load every serial of the leg-1
   receipt in one click.

Store-internal moves (main → damage, damage → main, return → main) and POS deliveries are
mirrored into the store's HO company and validated there, so HO stock for every store matches the
store's own stock. The inventory movement report shows each of these with the right sign.

Stock audits
============

HO defines **audit plans** per store: by attribute, ageing, brand type or serial list, as an HO
or store audit. Plans are pushed to the stores, serials under an active plan are frozen for
dispatch, counting sessions support scan, lock and recount, and adjustments approved at HO are
applied remotely. Audit reports compare HO's view with the store counts.
