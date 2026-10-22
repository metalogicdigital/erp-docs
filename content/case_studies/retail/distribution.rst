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

Physical stock audit plans
--------------------------

For a full physical count, **Stock Audit** (`mtl_stock_audit`) runs a plan through a fixed life
cycle: *New*, *Activated*, *Stock Updated*, *Completed*.

* A plan names the store, the stock point (an internal location, counted exactly, without its
  sub-locations), the plan date and the activation date.
* **Item-wise plans** list products or serials, imported from a spreadsheet with every rejected
  row reported. **Assortment-wise plans** describe the items by criteria (category and all its
  sub-categories, attribute values, articles, an RSP range), where every condition in a row must
  match and any row may match.
* **Activation** freezes the item set and stores the book quantity of each item and serial at the
  activation date as a snapshot. A backdated activation needs a profile right.
* Many people can record stock entries against one plan. **Verify / Update stock** posts a single
  adjustment for the plan from the variance, and a plan can be reverted until it is completed.
  *Completed* is final.
* Plans can be allocated to several stores, and variance reports compare the counts with the
  snapshot.

Daily stock audit from the salesperson's phone
----------------------------------------------

A full count is a project. The **daily audit** turns stock accuracy into a habit: each salesperson
counts one section of the store a day, blind, from an app, and only inside the store.
(`mtl_daily_audit`, with a mobile app and a gateway at head office.)

#. A manager **pairs** a phone by showing a one-time QR code in Odoo; the phone scans it.
#. The phone proves it is in the store: the store's Wi-Fi access point and/or a GPS position inside
   the geofence, no mock location, and optionally a device-integrity check. It receives a
   presence token that expires after fifteen minutes, and the **server** checks it on every call,
   so a modified app cannot skip the rule.
#. The salesperson signs in and sees today's assigned section, **without expected quantities**.
#. *Start* takes the section's snapshot on the server. Scans from the camera, a Bluetooth scanner
   or an RFID sled in keyboard mode are saved on the phone first and uploaded in batches, so
   nothing is lost when the Wi-Fi drops.
#. On *Finish count* the server compares the scans with the snapshot plus whatever was sold or
   moved meanwhile. With the recount pass on, the missing items are revealed once for a targeted
   search; then the count goes to the store manager, who decides each difference. **Only approved
   differences adjust stock.**

Everything is driven by the store's audit settings: presence rule, fence, access points, count
windows, device policy and approval levels. When the phone is on mobile data instead of store
Wi-Fi, the app starts a **phone VPN** to head office through the phone's own VPN system, only
while the app is in use and only for the store and HO networks. A short-lived certificate per
phone is issued after a successful presence check, and revoking the device in Odoo revokes the
certificate, so a lost phone cannot reconnect.

Gate passes
===========

Not everything that leaves a building is a sale or a purchase: a few pieces go to a photo shoot,
fabric to a tailor for repair, samples to an exhibition, a vendor's sample comes in without an
invoice. **Gate Pass** (`mtl_gatepass`) records every such movement through the gate.

* **Types** set the direction (outward or inward), the destination (another store, another
  location of the same company, or a contact), whether it is returnable and in how many days,
  whether approval is needed, and the numbering.
* **The request** records who asked, why, the source, the destination, the transport (transporter,
  vehicle, driver, LR and e-way bill number) and the items, with serials mandatory for tracked
  products.
* **Approval** is by users whose profile allows it, optionally up to a maximum value. Approving
  your own request needs an explicit policy switch.
* **On approval**, a type that creates a sale order raises one to the destination (for a store,
  the store company) at zero, cost or sales price. For a location or a contact, the delivery goes
  to a **transit location**, so the goods stay company stock while they are out.
* **Gate exit** and **inward at the destination** are recorded with who and when, with a
  difference per item between what left and what arrived, returns, and **overdue follow-up** for
  returnable passes.

.. example::
   Six dresses leave for a catalogue shoot. The gate pass is approved by the visual-merchandising
   head, the guard records the exit, and the six serials sit in the transit location, still on
   the books, until the shoot's stylist returns five. The difference of one is on the pass, and
   the overdue list shows who has not returned it.
