================
Module catalogue
================

The retail solution is delivered as a set of focused Odoo 17 addons on top of standard Odoo
(Inventory, Purchase, Sales, Point of Sale, Accounting, Approvals, Loyalty, Fleet, Employees,
Recruitment, Indian localisation). Retail addons carry the `mtl_retail_` prefix; the MetaLogic
platform addons (`mtl_`) are shared across every industry we serve.

Merchandising and master data
=============================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_product_hierarchy`
     - Family › Category › Class › Brick hierarchy with Division, Section and Department views;
       branded/unbranded, apparel/non-apparel and inventory/non-inventory product types;
       category-prefixed product references.
   * - `mtl_retail_serial_merchandise`
     - Piece-level serial master: nine attribute slots (colour, fit, brand, pattern, border type,
       border size, size, design, variant), ten descriptor slots (ageing, range, collection,
       fabric, exclusive, print, days ageing, offer, discount), cost, RSP and MRP per piece,
       vendor, GRC and indent references.
   * - `mtl_retail_pricing`
     - Category margin bands by cost range, RSP and MRP computation, price-ending rounding,
       margin-change approvals with re-pricing pushed to stores, monthly ageing buckets.
   * - `mtl_retail_gst`
     - Price-band GST selection, HSN master with automatic tax mapping, inter-state and
       intra-state tax handling, TDS, TCS and cess categories.
   * - `mtl_retail_barcode`
     - Multiple barcodes per product with inward/outward tracking, EAN generation, barcode
       search across sales, purchase, invoicing, stock and POS.
   * - `mtl_retail_labels`
     - Uploadable ZPL label templates (item, packet, set, promotion, logistics), preview, direct
       printing to networked label printers, reprint by serial, GRC or spreadsheet.

Store network and planning
==========================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_store_network`
     - Head-office company plus one company per store, zones, clusters and short codes, main,
       damage and return locations, virtual and physical store receipt ownership.
   * - `mtl_retail_store_onboarding`
     - Store node registry, store licences for cashier and back-office users, master posting to
       new stores, live-sync bootstrap.
   * - `mtl_retail_mbq_planning`
     - Price grades with minimum base quantity, store replenishment (regular and fashion),
       planning forecast, MBQ reports.
   * - `mtl_retail_store_targets`
     - Day-wise store targets by Family, Category, Class and Brick with regular and festival
       uplift, pushed to stores.
   * - `mtl_retail_vendor_visit`
     - Buyer visit planning, geofenced check-in at the vendor site, visit notes and samples
       linked to indents.
   * - `mtl_geofence`
     - Rules that let a document such as the purchase indent be created only at the vendor's
       location: check-in or live location, per-device accuracy and QR / photo proof, circle and
       polygon vendor zones, bulk geocoding, first-visit locations approved on a map, overrides
       and a full log. Installed switched off.

Procurement and inbound
=======================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_indent`
     - Store indents, HO consolidation into a purchase indent (PI) per vendor with on-hand,
       forecast, incoming and outgoing context, PT-upload indents, PI vs PO vs GRC report.
   * - `mtl_retail_purchase`
     - MBQ and RSP-margin approval stages, ad-hoc, custom-set and multiple-set purchases,
       spreadsheet import and splitting, advertisement purchase lifecycle, background
       confirmation of very large orders.
   * - `mtl_retail_inbound_logistics`
     - Lorry receipt (LR), transporter, bales, way bill, transport check, bale-level delivery
       check, open parcel, logistic status, transport masters.
   * - `mtl_retail_grc`
     - Goods receipt (GRC) types, verification scan, excess and shortage against LR, mandatory
       serial data with guided fill-in, landed cost, backdating, line locks, automatic serial
       numbering, background validation, draft bill and debit note.
   * - `mtl_retail_vendor_return`
     - Goods return to vendor (GRT) with regular or direct debit notes.

Distribution and stores
=======================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_dispatch`
     - Store sale orders with or without indent, automatic store purchase orders through
       inter-company rules, serial allocation, batch transfers with transporter, route, vehicle
       and parcel count, bale barcodes, gate passes.
   * - `mtl_retail_store_receipt`
     - Store receipts built from HO receipt packets, bale and serial verification, discrepancy
       acknowledgement (missing, surplus, received), virtual validation for HO-owned stores.
   * - `mtl_retail_stock_returns`
     - Return and damage movements between stores and the main warehouse, store-to-store
       transfers routed through HO.
   * - `mtl_retail_eway_bill`
     - E-way bills through a GST suvidha provider, one e-way bill or delivery challan per
       intra-state batch, vehicle and transporter updates, cancel and extend, consolidated bills.
   * - `mtl_retail_stock_audit`
     - Audit plans by store, attribute and ageing, counting sessions with scan, lock and recount,
       remote adjustments, HO audit reports.
   * - `mtl_retail_transport_dashboard`
     - Deliveries by category received vs opened, LR and returns dashboards, stock by company.

Point of sale and customer
==========================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_pos`
     - Serial scanning at the till, per-line price-band tax, salesperson per line, exchanges,
       returns and credit notes, cash rounding.
   * - `mtl_pos_performance`
     - POS data cache, in-memory cache and payload trimming so tills open and scan fast with
       very large catalogues.
   * - `mtl_promotion_studio`
     - Quantity and bill-value slab promotions, reusable item pools, store and period allocation,
       sample testing, one serial one promotion.
   * - `mtl_promotion_publish`
     - Publish promotions to automatically or manually targeted stores, live updates and
       withdrawal, scalable serial picker.
   * - `mtl_retail_vouchers`
     - Customer credit notes with balances, gift vouchers, loyalty cards, cross-store redemption
       guard, vendor-funded promotions.

Finance and compliance
======================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_accounting`
     - POS orders invoiced at HO per store company, inter-company invoices and bills for
       dispatches, GRC bills and debit notes, vehicle-cost journals, inter-company payments.
   * - `mtl_accounting_connector`
     - Export of the chart of accounts, partners, companies, warehouses, journal entries, bills
       and payments to an external accounting system, mapped per state GSTIN, with an admin
       dashboard.

Workforce
=========

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_retail_incentives`
     - Sales incentive structures (regular, target, product ageing), flat or tiered, global or
       store-wise, with detailed and summary reports.
   * - `mtl_retail_recruitment`
     - CTC breakup, two-level offer and appointment approval, letters, employee creation from
       applicant, web interview form.
   * - `mtl_retail_attendance`
     - Attendance upload, late deduction, overtime, shifts, lunch bonus, state professional tax.
   * - `mtl_hr_payroll` *(built on Open HRMS)*
     - Payroll and payroll accounting, loans, salary advances, branch transfers, multi-company HR,
       documents and expiry, resignation, end-of-service settlement, announcements, HR dashboard.
   * - `mtl_retail_store_checklist`
     - Store opening and closing checklist with daily PDF record.

MetaLogic platform
==================

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Capabilities
   * - `mtl_live_sync`
     - Change-data-capture replication between HO and stores: rules, routing, identity mapping,
       idempotent ORM apply, loop prevention, retries, bootstrap. See :doc:`live_sync`.
   * - `mtl_sync_monitor`
     - Live sync dashboard, replication logs, scheduled-job history.
   * - `mtl_error_codes`
     - Coded errors, remediation and escalation registry, occurrence log, guarded data fixes.
   * - `mtl_background_jobs`
     - Background task queue with live progress for heavy actions.
   * - `mtl_global_search`
     - Cross-model number search with related-record panel.
   * - `mtl_entity_trace`
     - Record lineage capture, visualiser and replay.
   * - `mtl_release_manager`
     - Git-driven, change-aware module upgrades with status in Odoo.
   * - `mtl_access_governance`
     - Profile-based access, per-user menus, module audit trail, session timeout, automated
       backups, mass edit, advanced list search, report delivery options.
   * - `mtl_safe_staging`
     - Automatic neutralisation of non-production copies.
   * - `mtl_admin_toolkit`
     - Parameter, settings and record explorer for administrators.
   * - `mtl_retail_analytics`
     - Real-time feed into the analytics warehouse and the retail report pack. See
       :doc:`analytics`.
