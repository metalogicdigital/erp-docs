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
   Each vendor site is stored with its location and a geofence. The buyer checks in from a
   laptop or phone browser, and the check-in is accepted only when the device's location is
   inside the vendor's geofence. Time, coordinates and accuracy are recorded, so vendor meetings
   and travel claims can be verified, and the same check-in decides whether a purchase indent may
   be raised (see :ref:`planning/geofence` below).

Visit outcome
   Notes, photographs of selected designs and samples, quoted prices and proposed quantities
   are captured on the visit and become **purchase indent lines** directly, so the selection
   made on the vendor's floor reaches the PI without re-keying.

Visit analytics
   Visits per buyer and vendor, how many visits turned into indents and purchase orders, and the
   sell-through of what each visit bought, linking the buying trip to what happened on the shelf.

.. _planning/geofence:

Purchase indents only at the vendor's location
==============================================

The buying team's policy is that a purchase indent is raised **on the vendor's floor**, where the
designs are selected, and not later from the desk. **MetaLogic Vendor Geofence** (`mtl_geofence`)
enforces that policy and makes every part of it configurable.

.. graphviz::
   :caption: Raising a purchase indent under the geofence

   digraph gf {
      rankdir=TB; nodesep=0.35; ranksep=0.45;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      { rank=same;
        ci [label="Buyer checks in\nat the vendor"];
        lo [label="Browser location\n(Wi-Fi or GPS)"];
        zn [label="Inside the vendor's\nzone?", fillcolor="#fdf3e4", color="#f39c1e"];
        pi [label="Purchase indent\nsaved", fillcolor="#e6f2f2", color="#017e84"]; }
      { rank=same;
        bl [label="Save blocked\nwith the reason"];
        ov [label="Override\nrequested"];
        ap [label="Approver\napproves", fillcolor="#fdf3e4", color="#f39c1e"]; }
      ci -> lo -> zn;
      zn -> pi [label="yes", fontcolor="#888888"];
      ci -> bl [style=invis];
      zn -> bl [label="no", fontcolor="#888888", constraint=false];
      bl -> ov -> ap;
      ap -> pi [label="one indent", fontcolor="#888888", constraint=false];
   }

Rules
-----

A rule names the document it protects (the purchase indent first; any other document can be
added the same way) and how strictly it applies:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Setting
     - Options
   * - Mode
     - **Off**, **Log only** (nothing is stopped, every result is logged: used to roll out),
       **Warn** (saved, the buyer is warned and the indent gets a note) or **Block**.
   * - Validation
     - A **check-in** at the vendor that stays valid for a number of hours, the **live location**
       on every save, or **both**.
   * - What is checked
     - A new indent saved from the form, Duplicate, import from a file (not checked, checked per
       record, or not allowed) and any button, for example Confirm. Records created by the
       system, such as indents arriving from the stores or orders created by approvals, are never
       checked.
   * - Scope
     - A filter (for example only the PO types bought from a vendor), companies, user groups,
       exempt users and groups, and allowed days and hours.
   * - Devices
     - Laptop browser, phone browser and the mobile app, each allowed or not, with its own maximum
       location accuracy (a laptop locates itself from Wi-Fi, a phone from GPS) and check-in proof:
       location only, a **QR code** displayed at the vendor, a **photo**, or both. Optionally a
       valid QR code is accepted when the device cannot get a location, for example indoors.
   * - Overrides
     - Whether buyers can ask for an exception, which group approves it, and whether an approval
       covers one indent or a number of hours.
   * - Alerts
     - A group that is told about every blocked attempt.

Vendor locations
----------------

Each vendor site is a **circle** (centre and radius) or a **polygon** drawn on a map, with a
buffer added to absorb location error. Locations come from two sources:

#. **Geocoding in bulk**: every vendor address is placed on the map in the background, falling
   back from the street to the PIN code to the city. A geocoded location is *provisional* and gets
   a larger radius the coarser it is. OpenStreetMap is used by default; a self-hosted geocoder or
   Google can be configured instead.
#. **The first visit**: when a buyer checks in at a vendor without an approved location, the
   buyer's position is proposed as the vendor's location. A manager compares it on the map with
   the geocoded address and approves it, after which the normal radius applies. The rule decides
   whether the buyer may carry on meanwhile, must wait for the approval, or is blocked.

.. example::
   A buyer at a mill on the outskirts saves a new indent. The system answers *"You have not
   checked in at the vendor"* and offers **Check in at the vendor**. The check-in reads the
   laptop's location, 25 m accurate, finds it 12 m from the mill's geocoded address, accepts it
   and proposes the point as the mill's location. The indent then saves. The next day, from head
   office, the same buyer is told *"You are 14.2 km from the nearest location of the vendor
   (allowed: 250 m)"*; a request for an override, approved by the buying head, lets exactly one
   indent through.

Audit
-----

Every attempt is logged with the user, vendor, document, device, position, accuracy, distance
and result, including attempts that were blocked, so the buying head can see who raises indents
away from the vendor and why. Check-ins, pending locations and overrides each have their own
list, and old log entries are purged after a configurable period.

Rolling it out
--------------

The module is installed with the rule **Off**: no checks, no location requests and no new menus
for the buyers until a manager switches it on. The usual sequence is to geocode the vendors,
run in **Log only** for a few weeks to see who would have been blocked, then move to **Warn** and
**Block**.

.. note::
   Browsers only share the location with HTTPS sites. When the ERP is reached over a VPN on plain
   HTTP, IT adds its address to the browser policy *OverrideSecurityRestrictionsOnInsecureOrigin*
   (Chrome and Edge, pushed by group policy). Until then buyers get a clear message saying so
   rather than a silent failure.

.. seealso::
   :doc:`procurement` for how MBQ and margin rules gate the purchase indent.
