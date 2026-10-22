=====================
Promotions framework
=====================

Promotions drive a large share of a fashion retailer's revenue, and they are far richer than
"10% off": slab offers, bundles at a fixed price, buy-and-get across different product pools,
bill-value tiers, markdowns on ageing stock, and different offers in different stores. The
merchandising team was used to building them in a dedicated retail ERP. Odoo's loyalty module
offers single-condition rules with no slabs, no reusable serial pools, no store allocation and no
way to stop one piece being in two offers at once.

We built the **MetaLogic Promotion Studio** at the head office and a matching **promotion engine
in the store POS**. Merchandisers design promotions in business terms; the Studio compiles them
into standard Odoo loyalty programs that the stores apply locally, in real time.

.. graphviz::
   :caption: Design at HO, apply at the till

   digraph promo {
      rankdir=TB; nodesep=0.3; ranksep=0.45;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      { rank=same;
        pool [label="Item pools\nbuy / get"];
        studio [label="Promotion Studio\nslabs, benefits", fillcolor="#f3eef1", color="#714B67"];
        test [label="Sample testing"];
        coll [label="One serial,\none promotion"]; }
      { rank=same;
        alloc [label="Allocation\nstores + period"];
        sync [label="Priority live sync\nto allocated stores"];
        pos [label="Store POS engine\nauto-apply", fillcolor="#e6f2f2", color="#017e84"]; }
      pool -> studio -> test -> coll;
      coll -> alloc [constraint=false];
      pool -> alloc [style=invis];
      alloc -> sync -> pos;
   }

Building blocks
===============

Item pools
----------

An item pool is a reusable set of **serials**, used as the pieces a customer buys (**buy pool**),
the pieces they get (**get pool**), or both. Membership is computed:

    *in-stock serials matching any include rule* − *those matching any exclude rule* +
    *hand-picked serials* − *an exclusion list that always wins*

Filters cover **29 fields in five groups**: the hierarchy (family, category, class, brick,
product, product category, tag), the nine attribute slots, the descriptor slots (including product
ageing and days ageing), RSP and MRP ranges, and store and GRC. Every filter supports *is* and
*is not*. A slush-bucket picker shows **Available**, **In pool** and **Excluded** lists;
*add all matching* and *remove all matching* are saved as rules, and serials or barcodes can be
pasted in. A pool can hold up to **300,000 serials**, and pools of running promotions are
refreshed every night before stores open so that new stock joins automatically.

Promotion types and slabs
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Condition
   * - Quantity, simple benefit
     - One threshold on the number of pieces bought from the buy pool.
   * - Quantity slabs
     - Several quantity thresholds, each with its own benefit.
   * - Bill-value slabs
     - Several bill-value thresholds, counted on buy-pool items.

Each slab has a **benefit**:

* **Flat discount** on the items: % off, ₹ off, or a **fixed price** for each item or for the slab
  quantity all together ("2 @ ₹1,499");
* **X units of the items bought**, cheapest first;
* **X units of a get pool**, N cheapest or any quantity.

Each benefit uses a **discount type**: free, % off, ₹ off or fixed price. A slab can add an **"also
get"** second benefit from another pool ("buy 3, get one at 50% *and* get a gift item at ₹500").

Program options: apply **per line** or to the **whole bill**; **repeat slabs** beyond the
highest; **spread the discount evenly** over the qualifying items; and a **rule order** that decides
which slab or promotion wins.

Validation catches bad designs before they reach a till: a simple benefit has one slab, no two
slabs start at the same point, percentages are between 0 and 100, a fixed price is not allowed on
"items bought", "free" needs a pool benefit, and so on.

How it compiles
---------------

Slab *n* becomes a standard loyalty **rule** *n* (one point when met) and **reward** *n* (needs *n*
points), paired explicitly. A bill that reaches slab 3 meets rules 1–3, collects three points and
the till keeps the highest slab. Rules and rewards are updated **in place**, so editing a live
promotion reaches the stores as an update, never as a delete and re-create.

Sample testing
--------------

Before publishing, merchandisers scan or paste up to 500 serials and see exactly which promotion,
slab and discount each line would get. The simulator uses the **same algorithm as the store POS**,
including bundle prices, cheapest-item logic, layout, conflict resolution and rounding.

One serial, one promotion
-------------------------

On save, any serial in this promotion's pools that another running or future promotion already
holds is flagged as a **collision**. Publishing waits until each collision is decided: *stays with
the other promotion* or *moves here*. Moving runs as a background job that removes the serials from
the other promotions and re-sends those promotions to their stores. The till enforces the same rule:
a serial held by two programs cannot be scanned.

Allocation and publishing
-------------------------

An **allocation** is a set of stores plus a period. Allocating publishes the promotion to exactly
those stores over **priority live sync**. A store added later receives a full snapshot; a store
removed has the promotion withdrawn. Each allocation line shows the live state at each store:
pending, sending, active, removing. Gift cards, e-wallets and unrestricted promotions can also be
targeted automatically to every store, and serial-limited promotions to the stores that hold those
serials.

At the till
===========

The store engine re-evaluates promotions automatically, debounced, on every change to the cart:
add, remove, quantity, price, discount or serial.

* **Discounts are written onto the lines**, not as separate negative lines, so every piece keeps
  its own net price for GST, receipts, returns and analytics.
* **Price-band GST follows the net price**: a promotion that takes a piece below the GST threshold
  also lowers its tax rate (see :doc:`master_data`).
* **Layout mode** (spread evenly or repeat slabs) sorts buy-pool items **dearest first**, forms
  groups of the top slab's size, gives each group the highest slab it reaches plus its extras, and
  spreads the benefit as one percentage over the group. The result does not depend on the order in
  which the cashier scanned the items.
* **Conflict resolution** between promotions on the same line: the higher program order wins;
  with equal order, the **larger rupee saving on that line** wins.
* New serials received at a store join running promotions that name them within minutes.

Advanced examples
=================

The examples use illustrative GST bands of 5% up to ₹1,000 and a higher rate above. The real bands
are whatever the taxes are configured with. Tenders are rounded to whole rupees at payment.

.. example:: **Bundle: "Buy 2 @ ₹1,499"**

   *Studio*: quantity, simple benefit; buy pool "Shirts"; quantity 2; flat discount, **fixed price
   ₹1,499 for all together**.

   *Bill*: shirts at ₹1,299, ₹999 and ₹799. Dearest first, one complete bundle: the ₹1,299 and ₹999
   shirts become ₹749.50 each; the ₹799 shirt stays at full price.

   **Total ₹2,298** (saving ₹799). The ₹1,299 shirt now nets ₹749.50 and drops into the lower GST
   band, on the till and on the server.

.. example:: **Buy 3 get 1 free (cheapest)**

   *Studio*: quantity, simple benefit; quantity 4; **1 unit of the items bought, free**.

   *Bill*: ₹1,499, ₹1,299, ₹999 and ₹799. The ₹799 piece is free: **₹3,797**.

   With *spread evenly* on, the ₹799 saving becomes **17.38% off every line** (₹1,238.47,
   ₹1,073.23, ₹825.37, ₹660.13), which is fairer on returns: a customer who returns one piece
   is refunded its share of the offer, not its full price. With *repeat slabs* and eight items,
   the cheapest of **each** group of four is free.

.. example:: **Bill-value slabs: ₹2,999 → 10%, ₹4,999 → 15%**

   *Studio*: bill-value slabs, whole bill; slab 1 from ₹2,999 at 10%; slab 2 from ₹4,999 at 15%.

   *Bill*: buy-pool items at ₹2,499, ₹1,999 and ₹1,299 (₹5,797) plus a non-pool item at ₹699. The
   pool value passes ₹4,999, so the top slab applies: **15% on every line**, **₹5,521.60**.

   The customer puts back the ₹1,999 item: the pool value falls to ₹3,798, the bill drops to slab 1
   and the till re-prices instantly to **₹4,047.30**.

.. example:: **Buy 2 shirts, get a belt at ₹199**

   *Studio*: quantity, simple benefit; buy pool "Shirts", quantity 2; **1 unit of the get pool
   "Belts", lowest price first, fixed price ₹199**.

   *Bill*: shirts at ₹1,299 and ₹1,199, belt at ₹599. The belt becomes ₹199: **₹2,697**. The shirts
   only qualify the offer and keep full price. With two belts, only the cheaper one is ₹199; with
   *any quantity*, every belt on the bill is ₹199.

.. example:: **Markdown on ageing stock: flat 40% on pieces older than 180 days**

   *Item pool*: descriptor filter **days ageing is 180+**, added with *add all matching*. The nightly
   refresh keeps the pool current as stock ages.

   *Studio*: quantity, simple benefit; quantity 1; **flat 40%**, per line.

   *Bill*: an aged jacket at ₹2,499 becomes ₹1,499.40; an aged kurta at ₹1,499 becomes ₹899.40 and
   moves to the lower GST band; a fresh item on the same bill stays at full price.

.. example:: **Buy 3, get one at 50%, and also get a gift item for ₹500**

   *Studio*: quantity, simple benefit; quantity 3; **1 unit of the items bought at 50% off**, plus
   **also get** 1 unit from the "Gift items" pool at a **fixed price of ₹500**.

   *Bill*: ₹1,499, ₹1,299 and ₹899, plus a gift item with an RSP of ₹1,200. The ₹899 piece is
   ₹449.50 and the gift item ₹500: **₹3,747.50** (saving ₹1,149.50).

.. example:: **Slabs that repeat: 1 → 10%, 2 → 20%, 3 → cheapest free**

   *Studio*: quantity slabs with **repeat slabs beyond the highest** and spread evenly.

   *Bill*: seven items from ₹1,999 down to ₹699 (₹9,193).

   .. list-table::
      :header-rows: 1
      :widths: 12 38 30 20

      * - Group
        - Items
        - Benefit
        - Net
      * - 1
        - ₹1,999, ₹1,799, ₹1,499
        - ₹1,499 free, spread 28.30%
        - ₹3,797.95
      * - 2
        - ₹1,299, ₹999, ₹899
        - ₹899 free, spread 28.12%
        - ₹2,298.00
      * - 3
        - ₹699
        - Slab 1, 10%
        - ₹629.10

   **Total ≈ ₹6,725** (saving ≈ ₹2,468). Without repeat, the seven items form one group and only
   the ₹699 piece is free: ≈ ₹8,494.

.. example:: **Two promotions on one bill**

   *Promotion A*: flat 20% on denim, per line. *Promotion B*: bill-value slab ₹3,999 → 10% on the
   whole bill, buy pool "Tops". Both have the same order.

   *Bill*: denim at ₹2,499 (A), tops at ₹2,299 and ₹1,899 (B's pool reaches ₹4,198, so B applies).
   B's whole-bill 10% also reaches the denim, so the engine compares savings on that line: A saves
   ₹499.80, B saves ₹249.90, and **the denim keeps A's 20%**. **Total ₹5,777.40.**

   If HO gives B a higher order, B wins every line, including the denim at 10%: ₹6,027.30. The
   merchandiser decides the policy; the till applies it consistently.

Vouchers, cards and vendor-funded offers
========================================

* **Gift cards and e-wallets** run as loyalty programs at one point per rupee; redemption adds a
  matching gift-voucher tender automatically.
* **Printed gift vouchers and loyalty cards** (three per A4 sheet, with card types) are issued from
  HO.
* **Vendor-funded promotions** can be invoiced to the vendor.
* A card or voucher **used in one store is relayed through HO** to every other store.
* **Classic attribute-filter promotions** remain available: rules by any attribute or descriptor
  slot, category list or **days-ageing slab** (0–30 up to 330–360 days), by serial list, by GRC or
  by cart, with bulk import of promotions.

Numbered gift vouchers
----------------------

Where the business needs a traceable register of every voucher, **Gift Vouchers**
(`mtl_gift_voucher`) adds numbered vouchers on top of the gift-card program.

* **Two kinds**. *Promotional* vouchers are given away, for example against a bill-value offer:
  no liability, and redemption is a discount. *Prepaid* vouchers are sold to a customer or a
  business buyer: issuing raises a customer invoice that credits a prepaid-voucher liability
  account, and redemption debits it.
* **Numbering by pattern**. A category defines prefix, suffix, number length, padding and start
  number, with tokens for the day, month and year of generation, so `SO/` + `/[MON][YY]` gives
  `SO/000001/OCT26`. Generation locks the category, so two users never receive the same numbers.
* **Life cycle**: new, allocated, issued, redeemed, cancelled, expired. Vouchers are **allocated
  to stores** by number range, booklet or selection, and a voucher allocated to a store can only
  be redeemed there unless policy allows any store. Validity is a number of days from issue and an
  absolute date, whichever ends first, in the store's time zone.
* **Issue and redeem**: issued at the back office (free issue with approval above the user's
  limit, or a sale with an invoice and an optional discount) or at the till, and redeemed at the
  till as a tender.
* **Register and statistics**: allocated to, issued from, on and against which bill, redeemed
  where, when and against which bill, with counts by status and denomination. Every change is
  appended to a history that cannot be edited.
