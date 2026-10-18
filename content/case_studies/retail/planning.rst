======================================
Merchandise planning and vendor visits
======================================

Fashion buying is a bet on what each store will sell, at which price point, before the season
starts. Buy too little and the best stores run empty in week two; buy too much and the stock ages
into markdown. Planning in the new system answers three questions with data rather than
spreadsheets: *how much should each store hold*, *how much should we buy*, and *what did each
buying trip deliver*.

MBQ: minimum base quantity by price point
=========================================

Fashion assortments are planned by **price point**, not by SKU: "this store should always have
40 formal shirts between ₹500 and ₹999". The MBQ framework models exactly that.

Price grades
   A grid of RSP bands, each with a minimum and maximum quantity. Grades are masters, replicated
   to the stores.

Replenishment sources
   Groups of articles that are planned together (for example all formal shirts of a range).

Store MBQ plan
   Per store: the replenishment source, optional brand and age filters, the price grade and an
   effective date. The plan's lines are the grade's bands, and for each band the system
   computes:

   * **On hand**: store stock whose serial RSP falls in the band.
   * **Indent**: the store's open indent quantity in the band, less what has already arrived.
   * **Gap** = maximum − on hand; **to be indented** = gap − indent.

Combined MBQ report
-------------------

The MBQ team plans the chain, not one store. The combined report works per article × price point
× brand × age:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Measure
     - Calculation
   * - Store MBQ
     - Sum of the stores' maximum quantities in the band.
   * - Store and warehouse SOH
     - Stock in the stores and at HO, in the band.
   * - Average sales
     - POS quantity over the previous three full months, per month.
   * - Warehouse MBQ
     - (Months of cover × average sales) − store MBQ.
   * - Cover
     - (Store SOH + warehouse SOH) ÷ average sales, in months.
   * - **To refill**
     - Store MBQ + warehouse MBQ − store SOH − warehouse SOH.

The MBQ team records the quantity it agrees to buy and closes the report; that agreed figure is
what buyers see when they raise purchase indents.

.. example::
   Band ₹500–999, chain store MBQ 40. Stores hold 18 and have 10 on open indents. Average sales are
   15 a month and the warehouse should cover three months: warehouse MBQ = 45 − 40 = 5. HO holds
   7, so cover is 25 ÷ 15 ≈ 1.7 months and **to refill = 40 + 5 − 18 − 7 = 20**. A purchase
   indent line for 30 pieces in this band goes to the **MBQ approver** before it can become a
   purchase order.

Planning forecast
-----------------

For the season buy, a forecast takes three monthly sales buckets, projects stock on hand for the
"three plus one" months ahead, subtracts current stock and open HO purchase orders in the band,
and shows the **remaining buy plan** per price point.

Store targets
=============

Day-wise sales targets per store are planned by **Family and Category**: each combination's
share of the store's stock value gives its contribution, monthly value is spread over the days,
and **regular and festival uplift percentages** raise the target for festive weeks. Targets are
imported, pushed to the stores and used by the multi-store target report, the store-target
incentive and the analytics dashboards.

Vendor visits with geofenced check-in
=====================================

Fashion buying happens at the vendor's premises: buyers travel to mills, wholesalers and
manufacturers, select designs from the floor, negotiate prices and book quantities against the
season's MBQ plan. Those visits used to live in phone galleries and notebooks, and nobody could
tell from the system who visited whom, when, or what came of it.

**MetaLogic Vendor Visits** (`mtl_retail_vendor_visit`) brings the visit into the ERP.

Visit plan
   Buyers plan visits per vendor and date, linked to the categories and MBQ gaps they are buying
   for. Managers see the buying team's travel plan for the week.

Geofenced check-in
   Each vendor site is stored with its location and a geofence radius. The buyer checks in from
   a mobile browser, and the check-in is accepted only when the device's location is inside the
   vendor's geofence. Time and coordinates are recorded on the visit, and a visit cannot be
   closed without a valid check-in and check-out, so vendor meetings and travel claims can be
   verified.

Visit outcome
   Notes, photographs of selected designs and samples, quoted prices and proposed quantities
   are captured on the visit and become **purchase indent lines** directly, so the selection
   made on the vendor's floor reaches the PI without re-keying.

Visit analytics
   Visits per buyer and vendor, how many visits turned into indents and purchase orders, and the
   sell-through of what each visit bought, linking the buying trip to what happened on the shelf.

.. seealso::
   :doc:`procurement` for how MBQ and margin rules gate the purchase indent.
