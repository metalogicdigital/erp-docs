=======================
Reporting and analytics
=======================

A fashion retailer runs on numbers that change by the hour: what sold in which store, what is
ageing on the shelf, what is in transit, and whether the books agree. The customer came from a
legacy retail ERP with a separate BI layer that rebuilt its data overnight through a chain of
extract jobs. Day-old dashboards, a stack of Excel side-files for targets and budgets, and
regular reconciliation gaps between BI and the ledger were part of daily life.

We replaced that with three layers that share one source of truth:

.. list-table::
   :header-rows: 1
   :widths: 22 39 39

   * - Layer
     - What it is for
     - Examples
   * - Odoo standard reports
     - Statutory and transactional reporting with drill-down to the source document.
     - P&L, balance sheet, general ledger, trial balance, aged receivables/payables, GSTR-1,
       GSTR-3B, stock valuation, moves analysis, POS orders analysis.
   * - Retail operational reports in Odoo
     - The reports store, merchandising, logistics and audit teams use every day, built into the
       ERP.
     - PI vs PO vs GRC, logistic status, transfer and dispatch summaries, product ageing, store
       audits, sales incentives, multi-store targets.
   * - Real-time analytics warehouse
     - Chain-wide, high-volume analysis and ad-hoc report building without loading the ERP.
     - Bill-wise MOP, HSN-wise sales, COGS roll-forward, sold vs SOH, ageing, sell-through,
       margin analysis.

Analytics architecture
======================

.. graphviz::
   :caption: From the head-office ledger to dashboards in about two seconds

   digraph analytics {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      ho [label="HO Odoo\nPostgreSQL"];
      replica [label="Hot-standby replica\n(read-only)"];
      bridge [label="Streaming bridge\nlogical decoding"];
      ch [label="Columnar warehouse\n(ClickHouse)"];
      bi [label="Dashboards and\nreport builder (Superset)"];
      ho -> replica [label="physical\nreplication", fontcolor="#888888"];
      ho -> bridge [label="change\nstream", fontcolor="#888888"];
      replica -> bridge [label="snapshots +\ndimensions", fontcolor="#888888"];
      bridge -> ch -> bi;
   }

Read-only replica
   A streaming hot standby of the head-office database. Heavy queries and snapshots never touch
   the production primary.

Change stream
   A logical-decoding slot streams every insert, update and delete on fifteen fact tables (POS
   orders, lines and payments, sale and purchase orders, pickings, stock moves and move lines,
   quants, valuation layers, journal entries and items, serials) into the warehouse. Each row is
   versioned by its log position and carries a delete flag, so the warehouse converges on
   exactly what the ERP holds.

Dimensions
   Products, categories, partners, locations, warehouses, companies, POS configurations and
   sessions, taxes, payment methods, employees and journals are refreshed from the replica every
   few minutes.

Report views
   Every report is a versioned SQL view (`rpt_<report>`), so report logic lives in source
   control and is reviewed like code. Dashboards are provisioned by an idempotent script, with
   date and store filters on each one.

.. raw:: html

   <div class="mtl_stats">
     <div class="mtl_stat"><b>~2 s</b><span>store sale to analytics, end to end</span></div>
     <div class="mtl_stat"><b>100%</b><span>row-count parity with the ledger on orders, lines and payments</span></div>
     <div class="mtl_stat"><b>77 / 70</b><span>dimensions / measures in the report builder model</span></div>
     <div class="mtl_stat"><b>31</b><span>business report templates catalogued</span></div>
   </div>

Accuracy is checked, not assumed. Bill-wise MOP totals and payment counts match the ledger
across all stores; HSN-wise sales match invoice, taxable value, quantity and line count; the COGS
roll-forward satisfies *opening + movements = closing* with closing quantity within 0.2% of
on-hand stock.

Report catalogue
================

.. tabs::

   .. tab:: Operations

      .. list-table::
         :header-rows: 1
         :widths: 35 65

         * - Report
           - What it answers
         * - Daily sales dashboard (Daily, WTD, MTD, QTD, YTD)
           - Net and gross sales, bills, average basket value and size, conversion, sales per
             square foot, against target and last year.
         * - Bill-wise sales summary
           - Every bill with product hierarchy, discounts and tax, for store audits.
         * - Hourly and site-wise sales
           - When and where the floor is busy, for staffing and promotion timing.
         * - Target vs achievement
           - Daily targets by store, family and category, with festival uplift.
         * - Sales incentive (detailed, summary, employee-wise, designation-wise, ageing)
           - What each salesperson sold and earned under the active incentive structure.
         * - Offer summary
           - Stock and sales by promotion, to decide what to extend or end.
         * - Cancelled bills, credit-note bills, MOP by terminal
           - Cash-desk control and fraud signals.
         * - Live sync dashboard
           - Live stores, pending transfers, failed transactions and master backlog.

   .. tab:: Inventory and merchandising

      .. list-table::
         :header-rows: 1
         :widths: 35 65

         * - Report
           - What it answers
         * - Sold vs SOH (chain and site)
           - Sell-through and refill suggestions by hierarchy.
         * - SOH vs MBQ, MBQ gap
           - Which stores are below their minimum base quantity, and by how much.
         * - Ageing sales and stock
           - Sales and stock mix by age bucket; candidates for markdown.
         * - Stock movement and rolling inventory
           - Opening, receipts, transfers, returns, sales and closing by period.
         * - Brand sales, SOH and returns
           - Brand-level sell-through for vendor negotiations.
         * - Vendor inward, sales and SOH
           - Vendor sell-through and return exposure.
         * - Transfer-order tracking, scanning summary
           - Where every dispatch, bale and serial is, from HO picking to store receipt.
         * - Store audit and negative stock
           - Audit plan results, variances and negative-stock exceptions.

   .. tab:: Procurement and logistics

      .. list-table::
         :header-rows: 1
         :widths: 35 65

         * - Report
           - What it answers
         * - PI vs PO vs GRC
           - Indent to order to receipt, with quantities, margins and age.
         * - PO status for merchandisers
           - Open, partial and closed orders with MBQ plan.
         * - Inward summary
           - Receipts against orders, with shortage, excess and debit notes.
         * - LR delivery status
           - Lorry receipts and bales in transit, delivered and opened.
         * - Indent raised, planning vs procurement
           - Whether demand turned into orders on time.
         * - Transport and LR dashboards
           - Deliveries by category, received vs opened, returns by LR.

   .. tab:: Accounting and finance

      .. list-table::
         :header-rows: 1
         :widths: 35 65

         * - Report
           - What it answers
         * - Bill-wise MOP details
           - Collections per store, date and mode of payment (cash, card, UPI, voucher, credit
             note).
         * - Bill document summary
           - First and last bill number per store and day, for continuity checks.
         * - Sales HSN report
           - Quantity, taxable value, CGST, SGST and tax by HSN, store and hierarchy.
         * - Purchase and purchase-return summaries
           - Supplier invoices with GSTIN, PO, receipt, LR, e-way bill and tax split.
         * - Inter-branch transfer in/out HSN summary
           - Branch transfers with e-invoice and e-way bill references, by HSN.
         * - COGS summary, COGS at HSN level
           - Site-wise quantity and value roll-forward: opening, receipts, returns, transfers,
             conversions, shrinkage, sales and closing.
         * - Statutory and ledger reports
           - P&L, balance sheet, cash flow, general ledger, trial balance, partner ledger, aged
             balances, GSTR-1, GSTR-3B, TDS and TCS, e-way bills.

The report builder
==================

Merchandisers were used to picking any combination of dimensions and measures. The analytics
model keeps that freedom: **77 dimensions** (store and geography, the full product hierarchy,
brand and attribute slots, price points, vendor, calendar, inward and stock ageing, sale type)
and **70 measures**, including:

* **Sales**: net and gross sales, quantity, bills, average daily sale, basket value and size,
  net realisation %.
* **Store productivity**: footfall, conversion %, sales per square foot per day.
* **Full price vs discount**: full-price sale quantity and value and their share, discount %.
* **Margin**: COGS, gross and net margin and margin %.
* **Stock**: opening and closing at cost, RSP and MRP, warehouse and in-transit stock.
* **Flows**: purchases, purchase returns, transfers in and out, customer returns, pending POs.
* **Turns**: sell-through %, stock-turn ratio, inventory days on COGS and on quantity.

Single-period, comparison-period and to-date variants are all expressed from the same model, with
export to Excel and CSV from every view.

From overnight batch to live
============================

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * -
     - Legacy BI chain
     - New analytics stack
   * - Freshness
     - About an hour for intraday views at best, next day for the main retail apps.
     - About two seconds from the store till.
   * - Data path
     - 23 chained extract, transform and load tasks on extract files.
     - One continuous change stream; no batch chain to fail.
   * - Reconciliation
     - BI and ledger rebuilt separately.
     - Same rows as the ledger, verified by count and totals.
   * - Business inputs
     - Excel side-files for targets, budgets, MBQ and price segments.
     - Targets, MBQ and price grades are masters in the ERP.
   * - Report logic
     - Inside BI app scripts.
     - Versioned SQL views, reviewed like code.
