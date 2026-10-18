===========
Master data
===========

In fashion retail the unit that matters is the **piece**, not the product. Two shirts of the same
article can carry different prices, offers, ageing and even tax rates. The whole solution is built
on that fact, so master data is where the design starts.

Companies: one head office, one company per store
=================================================

The head-office database contains a **main company** and **one company per store**.

Main company
   Owns vendor buying, goods receipt, serial numbering and the central warehouse. Income
   accounts, sequences and serial minting all belong to it.

Store companies
   One per physical store, each with its own state and GSTIN, warehouse, location tree,
   operation types, POS orders and journals. Taxes and the chart of accounts are shared with the
   main company, so a tax configured once is available to every store.

Every store company has three stock locations with a defined role: **main** (saleable stock),
**damage** and **return**. Stores are grouped into **zones** and carry a short code used on
documents and labels.

A new store company can only be created once the branch contact tag and the branch numbering
sequence exist, so no store is ever half set up. See :doc:`new_store` for the full onboarding
process and :doc:`architecture` for why each store has a mirror company at HO.

The product hierarchy
=====================

Products are classified in a strict four-level tree, enforced by the system (a fifth level is
refused):

.. graphviz::
   :caption: Four-level merchandise hierarchy (illustrative)

   digraph h {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      f [label="Family\nMENS WEAR", fillcolor="#f3eef1", color="#714B67"];
      c [label="Category\nSHIRTS"];
      k [label="Class\nFORMAL SHIRTS"];
      b [label="Brick\nFULL SLEEVE", fillcolor="#e6f2f2", color="#017e84"];
      f -> c -> k -> b;
   }

* **Family › Category › Class › Brick** (also presented as Division › Section › Department ›
  Brick for planners used to that vocabulary).
* Names are upper-cased and unique at the root; each category carries an **HSN code** that must
  exist in the HSN master, a **placement zone** that decides where goods are received and
  stored at HO, and the **buyers** allowed to purchase in that tree.
* **Margin bands and MRP bands** live on the category (see `Pricing per piece`_).
* The full chain is copied onto every PO, indent and sale order line, stock move and serial, so
  reports, scanning filters and promotions can work at any level without joins.

Articles, variants and the serial
=================================

Article
   The product template. Storable articles **must** be serial- or lot-tracked; untracked stock
   is refused. Duplicate storable names are refused, and articles bought through HO operations
   are named from their category path.

Variant
   The product variant that orders and moves point to, with an automatic **internal reference**
   from a per-category prefix and sequence.

Serial
   The **piece**. Every unit received gets its own serial number from a per-company sequence.
   The serial is the merchandising record: it carries the prices, taxes and HSN, the vendor,
   the GRC and indent it came from, and nineteen descriptive slots.

.. list-table:: Descriptive slots on every serial
   :header-rows: 1
   :widths: 50 50

   * - Attribute slots
     - Descriptor slots
   * - Colour, Fit, **Brand**, Pattern, Border type, Border size, Size, **Design**, Variant
     - **Ageing bucket**, Range, Collection, Fabric, Exclusive, Print, Days ageing, **Offer**,
       Discount, Piece count

Brand, Design and Offer are mandatory at goods receipt (see :doc:`grc`). Editing a slot on a
receipt line updates the serial, and the same slots drive labels, promotions, incentives and
analytics.

**Ageing buckets.** A twelve-month ageing calendar generates one bucket per month; every serial
is stamped with the bucket of the month it was received. Promotions and incentives can then
target, for example, "stock older than six months".

Branded and unbranded goods
===========================

Each article is **branded**, **unbranded** or **others**. Pricing and tax rules are the same;
identity is not.

.. list-table::
   :header-rows: 1
   :widths: 24 38 38

   * -
     - Branded
     - Unbranded
   * - Identity
     - The vendor's barcode, mandatory at goods receipt.
     - The product barcode plus the piece's serial.
   * - Scanning
     - Matches the vendor barcode.
     - Matches the serial in a GS1 code.
   * - Barcode registry
     - The vendor barcode is added to the product's barcodes with inward and outward counts.
     - Not needed.
   * - Label
     - Vendor barcode.
     - GS1 `01` + 14-digit product code + `21` + serial.

Barcodes
========

* **Product barcodes** are generated automatically as 14-digit GTIN-style codes with a check
  digit.
* **Multiple barcodes per product**, each unique, with inward and outward quantities and
  supplier, are searchable everywhere a product is: sales, purchase, invoicing, stock and the POS.
* **Scanners accept three forms** everywhere (GRC verification, outward scanning, POS): a GS1
  string (`01` + GTIN + `21` + serial), a plain EAN, or an alphanumeric serial.
* **Weight-sold articles** use a table of weight barcodes with a price per barcode.

Pricing per piece
=================

The customer does not use price lists. Every serial carries three prices:

* **CP**: cost price, landed (and the pre-landed actual cost).
* **RSP**: retail selling price, what the customer pays before promotions.
* **MRP**: maximum retail price printed on the label; RSP may never exceed it.

RSP and MRP are computed, not typed, from **margin bands** on the category:

#. **Default margin** from the category's cost-price band (for example "CP 0–999 → 60%"). A
   cost with no matching band is refused.
#. **Pre-tax price** = CP × (1 + margin).
#. **GST** for that price band is added (see `Price-band GST`_).
#. **Price-ending rounding**: the last two digits become **49** if below 50, otherwise **99**.
#. **MRP** = RSP × (1 + MRP mark-up from the category's RSP band), rounded the same way.

.. example::
   CP ₹500 in a category whose band gives 60%, with illustrative GST rates of 5% up to ₹1,000
   and a higher rate above:

   * Pre-tax: 500 × 1.60 = ₹800, which is in the 5% band → 800 × 1.05 = ₹840.
   * Rounding: 40 is below 50 → **RSP ₹849**.
   * MRP band 20%: 849 × 1.20 = ₹1,018.80 → ₹1,019 → **MRP ₹1,049**.

Buyers can also work backwards: type the RSP and the system derives the margin. A margin below
the category default is allowed but needs **RSP-margin approval** (see :doc:`procurement`).

**Price-zone guards** stop an RSP from landing just above a GST threshold, where a few rupees of
price would cost far more in tax. The guard bands are configured per product tag (readymade,
footwear and so on).

**Re-pricing live stock.** A margin-change request selects serials by barcode, document,
attribute conditions or GRC, recomputes RSP and MRP with the same rounding, goes through manager
approval (with a daily reminder) and on approval **pushes the new prices to every store** that
holds those serials.

Taxes
=====

Price-band GST
--------------

Indian GST on apparel and footwear depends on the selling price: the same HSN is taxed at a
lower rate below a threshold and a higher rate above it. Standard Odoo picks taxes per product,
which cannot express that.

Every GST tax carries a **minimum and maximum amount**. All candidate rates for an HSN are kept on
the product and on every serial, and the right one is chosen **at transaction time from the
actual price**:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Where
     - Price used to choose the rate
   * - Computing RSP at purchase
     - Pre-tax cost plus margin.
   * - Vendor purchase order line
     - Unit price after line or order discount.
   * - HO → store transfer line
     - Transfer price after discount, from the serial's sale taxes.
   * - Invoice posting
     - Unit price after discount; exactly one band must match.
   * - E-way bill
     - E-way bill unit price.
   * - **Store POS**
     - Serial RSP after line and bill discounts, so a discount that drops a piece below the
       threshold also drops its tax rate.

Intra-state and inter-state supply
----------------------------------

Every purchase order, sale order and transfer is typed **intra-state** or **inter-state** by
comparing the partner's state with the company's.

Intra-state HO → store
   The same GSTIN: a stock transfer, not a supply. Transfer lines carry no tax, and any tax on an
   invoice to a same-state company is stripped at posting.

Inter-state HO → store
   Taxes come from the serial's GST band mapped through the fiscal position, and posting
   **forces IGST**: the system finds the GST slab for the price, sums its CGST and SGST rates and
   applies the company's IGST tax of the same rate. Exactly one match is required.

Vendors
   Purchase lines pick the GST band and swap it for the matching IGST tax for out-of-state
   vendors; vendor returns map through the vendor's fiscal position.

The serial itself always keeps **CGST + SGST** taxes, because the store POS charges those taxes
to walk-in customers, an intra-state retail sale. IGST belongs only on the HO → store invoice.
The dispatch check refuses any transfer line whose serial carries IGST, which catches a bad
master before it reaches a till.

HSN master
----------

The HSN master holds one row per HSN code with its GST groups (sale and purchase) and IGST taxes.
Choosing a chapter (1–99) imports that chapter's published GST rates and maps them to the
company's taxes automatically, including nil-rated codes. Setting an HSN on a product sets its
sale and purchase taxes; goods receipt resolves HSN and taxes onto every serial and refuses
validation without them.

TDS, TCS and cess
-----------------

Taxes can be classified as TDS, TCS or cess. Selecting them on a bill or invoice applies them to
every line while keeping the GST already on the line.

Units of measure
================

Standard Odoo units, replicated to stores. When the receipt unit differs from the purchase unit,
CP, RSP and MRP are converted by the unit ratio so that a dozen bought is priced per piece sold.
