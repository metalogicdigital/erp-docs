================================
Indent, purchase indent and PO
================================

Procurement in a store chain starts at the store, is consolidated at the head office, and is
approved against two numbers that protect the business: the **MBQ plan** (are we buying more than
the stores can hold?) and the **margin** (are we buying at a price that sells profitably?).

.. graphviz::
   :caption: From store demand to purchase order

   digraph p {
      rankdir=TB; nodesep=0.4; ranksep=0.4;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      si [label="Store indent\n(each store)"];
      ii [label="Internal indent\nHO consolidation"];
      pi [label="Purchase indent (PI)\nper vendor"];
      mbq [label="MBQ approval", fillcolor="#fdf3e4", color="#f39c1e"];
      mg [label="RSP-margin approval", fillcolor="#fdf3e4", color="#f39c1e"];
      po [label="Purchase order", fillcolor="#e6f2f2", color="#017e84"];
      lg [label="Logistic entry\n(LR, bales)"];
      si -> ii -> pi;
      pi -> mbq [label="qty > MBQ max", fontcolor="#888888"];
      pi -> mg [label="margin < default", fontcolor="#888888"];
      mbq -> mg [style=dashed];
      pi -> po; mbq -> po; mg -> po;
      po -> lg;
   }

Store indents
=============

A store raises its demand as an **indent**: a draft purchase order in the store's own company,
typed intra- or inter-state, with lines planned against the store's MBQ price bands. Indents sync
to HO. Once HO has taken an indent into consolidation, later edits from the store are ignored, so
the store cannot change the demand under the buyer.

Internal indent: consolidation at HO
====================================

The **internal indent** collects every store indent line not yet consolidated, for a date range
and filtered by store, category, variant or document. It builds a product summary that puts each
article's indented quantity next to HO's on-hand, forecast, incoming and outgoing quantities, so
the buyer orders only what HO cannot already cover. Selected lines and quantities become a
**purchase indent** for the chosen vendor, and each store's indent is marked as taken.

A spreadsheet-upload variant handles indents prepared offline with barcode, brand, size, design,
fit, colour and prices.

Purchase indent (PI)
====================

The PI is the buyer's proposal to the vendor, built on Odoo Approvals with retail stages:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - State
     - Meaning
   * - New
     - Being prepared.
   * - Pending
     - Submitted.
   * - MBQ approved
     - The MBQ approver accepted quantities above plan.
   * - Margin approved
     - The RSP-margin approver accepted margins below the category default.
   * - Approved
     - Ready to become a purchase order.

Each PI line carries the unit price, the default and entered margins, RSP, MRP, HSN, design,
offer, variant attributes, placement zone and the full hierarchy. Purchases are typed **ad hoc**,
**custom set** or **multiple set**.

Submission is guarded:

* the validity runs from today for 60 days;
* all lines belong to one placement zone;
* unit price, margin, RSP and MRP are all positive;
* categories that require a manager approver have one, and the minimum number of approvers is
  met.

Routing at submit is automatic:

#. A line whose quantity exceeds the **MBQ maximum** for its price band goes to the **MBQ
   approver** group. The band and its maximum are picked from the replenishment view of the line,
   which shows store and HO stock, open orders and the MBQ team's agreed refill.
#. A line whose entered margin is **below the category default** goes to the **RSP-margin
   approver** group.
#. Otherwise the PI goes to its normal approvers.

Choosing an **offer** on a line overrides the category's default margin with the offer's margin,
so a planned promotion is priced in at the buying stage.

Purchase order
==============

An approved PI becomes **one purchase order** with every line attribute carried across. On
approval of an HO-operation order the system creates the **logistic entry** automatically for the
order's placement zone, so inbound tracking starts the moment the order is placed (see
:doc:`grc`).

Other controls on the order:

* A **vendor change** on the order is written back to the PI, so the approval record stays true.
* At goods receipt, received quantities per article are checked against the PI: **a PO cannot
  quietly receive more than was approved**.
* **Advertisement purchases** (signage, media) have their own lifecycle with start, end and
  renewal dates and a daily alert before they lapse.
* **Spreadsheet import** of order lines, and a **splitter** that cuts very large vendor files into
  order- and receipt-sized chunks.
* Orders with thousands of serial-tracked units **confirm in the background** with a progress
  bar, so buyers keep working while the receipt lines are prepared.
