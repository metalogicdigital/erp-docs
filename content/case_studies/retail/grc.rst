=================================
Goods receipt (GRC) and inwarding
=================================

The goods receipt, or **GRC**, is where a vendor's bales become sellable pieces. It is also
where most retail stock problems begin: a short shipment nobody claimed, a brand barcode not
captured, a price computed on the wrong cost, a piece that cannot be traced back to its PO. The
receipt flow is therefore the most heavily guarded process in the solution.

.. graphviz::
   :caption: Inbound flow at the head office

   digraph g {
      rankdir=TB; nodesep=0.3; ranksep=0.45;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      { rank=same;
        po [label="Purchase order"];
        le [label="Logistic entry\nLR, transporter, bales"];
        tc [label="Transport check"];
        dc [label="Delivery check\nbale scan"];
        op [label="Open parcel"]; }
      { rank=same;
        rq [label="Set received qty\nexcess / shortage"];
        vs [label="Verification scan"];
        md [label="Mandatory data\nfill-in"];
        val [label="Validate GRC\nserials minted, priced", fillcolor="#e6f2f2", color="#017e84"];
        bill [label="Draft bill +\ndebit note"]; }
      po -> le -> tc -> dc -> op;
      op -> rq [constraint=false];
      po -> rq [style=invis];
      rq -> vs -> md -> val -> bill;
   }

Inbound logistics before the goods arrive
=========================================

Logistic entry
   The transporter's **lorry receipt (LR)** number, transporter, number of bales, way bill,
   consignor and agent. It is created automatically when the purchase order is approved.

Transport check, then delivery check
   The vehicle arrives and is checked; bales are then received **one by one by barcode**, so a
   missing bale is known before any bale is opened.

Open parcel
   Bales are opened against the delivery check. The receipt cannot be validated until opening is
   complete.

Transport masters (transporters, routes, locations) and vehicles link inbound costs to the fleet,
and a logistic status screen shows every LR from booking to opened.

Receiving against the LR, not the PO
====================================

Standard Odoo pre-creates **one receipt line per piece** when a purchase order for
serial-tracked goods is confirmed: 50,000 lines for a 50,000-piece order. Every later step then
takes minutes. The receipt flow changes the model:

* No lines are created at order confirmation or for back-orders.
* Once an LR is linked, a **Set received quantity** step records what actually arrived against the
  LR's quantity, with **excess** and **shortage** captured explicitly. Lines are created only for
  what was received.
* At validation the system checks that **received = LR quantity + excess − shortage**.
* Validation creates a **draft vendor bill** for the expected LR quantity and a **draft debit
  note** for any shortage, linked to the purchase order lines, so a short shipment is claimed from
  the vendor automatically. Excess is recorded for the buyer to decide on.

Receipt types
=============

Vendor purchase, direct purchase, sub-contract (the resupply transfer must be done first), data
import and opening stock, inter- and intra-state receipts from HO at the stores, POS exchange,
GRC cancellation and advertisement receipts. The source is **against a PO**, **direct** or
**goods return**.

The validation rules
====================

Clicking **Validate** runs the guards in order; the first failure stops with a coded message.

#. **Quality checks** pending on the receipt block validation.
#. **LR quantity** must reconcile with received, excess and shortage, and opening must be done.
#. **Mandatory serial data**: every line needs **Brand**, **Design**, **web product** and
   **Offer**. Instead of failing, the button first opens a **Fill missing data** screen that lists
   the gaps and suggests the most common value on the receipt, with bulk update. The check runs
   again just before stock is moved.
#. Every product has a barcode and a brand type, **received never exceeds ordered**, and branded
   lines carry the vendor barcode.
#. **Landed cost decision**: the receiver must state whether landed cost is included in the RSP,
   and confirm.
#. **Approved quantities**: received quantities per article are checked against the purchase
   indent.
#. "Others" goods cannot carry serials.
#. **Serial numbers** are generated from the company's sequence in a confirmation step. Manual
   serial assignment is not allowed on HO receipts, so numbering stays unique and gap-free.

A **verification scan** runs alongside: each scan is matched to the receipt line, a line is
"matched" when scanned quantity equals received quantity, and a serial-tracked line cannot exceed
one per scan except for 13-digit barcodes.

Pricing at receipt
==================

When a serial is created, it is stamped with brand type, barcodes, HSN, taxes, every attribute and
descriptor slot, CP, RSP and MRP, segment, indent reference, GRC number, approved margin and
vendor.

Without landed cost
   Prices come from the purchase order line, converted for unit of measure, and the ageing
   bucket is set. MRP, RSP, HSN and both tax sets are mandatory.

With landed cost
   Attributes are set at validation, and **prices are set when the landed cost is validated**:
   CP = final landed cost ÷ quantity (with pre-landed cost kept as the actual CP), then RSP and
   MRP are recomputed from the category bands. Until then, those serials **cannot be scanned into
   an outward transfer**, so nothing is dispatched at a provisional price.

Protecting a validated receipt
==============================

Line-edit lock
   After validation, product, quantity, brand type, prices, barcode, HSN and hierarchy can be
   changed only by users or groups the company has authorised. **Nobody** can change them once
   any serial from the receipt is on an outgoing transfer.

Backdating
   A dedicated role can backdate a receipt: picking, moves, lines, valuation layers and their
   journal entries move together and ageing is recomputed, so books and stock stay consistent.

Big receipts in the background
   Receipts above a configurable size (500 lines by default) validate as a background job with a
   live progress bar. Any questions are asked first, in the click; the heavy work then runs
   without blocking the user.

Vendor bill linkage
   A bill is built from the receipt's moves, a receipt can be billed only once, a billed receipt
   cannot be cancelled, and the vendor's bill reference is unique per vendor.

Labels
======

Validated serials are labelled from uploaded ZPL templates (item, packet, set, promotion,
logistics), previewed on screen and sent straight to networked label printers. Labels can be
reprinted by serial, GRC or spreadsheet. Unbranded pieces get a GS1 barcode with the serial;
branded pieces keep the vendor barcode.

Goods return to vendor (GRT)
============================

Regular return
   Serials are scanned (up to 20 GRCs per document), returned to the vendor with the exact
   serials, and **one debit note per vendor** is posted at the serials' cost with purchase
   taxes, mapped to IGST for out-of-state vendors.

Direct debit note
   A price-difference claim per GRC with no stock movement.

Opening stock and data imports
==============================

Opening and closing stock files are split automatically into chunks the receipt can handle
(6,000 lines by default), carry age code, item code, barcode, RSP and cost, and are received as
data-import receipts with their own valuation.
