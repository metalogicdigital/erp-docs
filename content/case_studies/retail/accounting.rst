==================================
Accounting journals and compliance
==================================

Every operational step in the chain leaves an accounting footprint, posted automatically by the
process that caused it. Finance teams do not re-key operations; they review, reconcile and close.

What is posted, and where
=========================

.. list-table::
   :header-rows: 1
   :widths: 28 42 30

   * - Event
     - Entry
     - Company
   * - GRC validated
     - Perpetual stock valuation entry from the receipt's valuation layers. Opening stock and data
       imports are valued at their imported cost.
     - Main company
   * - GRC with excess or shortage
     - **Draft vendor bill** for the LR quantity and **draft debit note** for the shortage, linked
       to the purchase order lines.
     - Main company
   * - Vendor bill from receipt
     - Bill lines built from the receipt's moves; bill, debit note or credit note typed and
       cross-referenced.
     - Main company
   * - Landed cost
     - Valuation adjustment; each serial's CP, RSP and MRP are recomputed.
     - Main company
   * - Goods return to vendor
     - **Posted debit note** per vendor at the serials' cost with purchase taxes.
     - Main company
   * - HO → store dispatch
     - Customer invoice to the store: no tax intra-state, IGST inter-state; e-invoice and e-way
       bill references.
     - Main company
   * - Store receives the dispatch
     - Vendor side of the inter-company purchase, and the receipt's valuation.
     - Store company
   * - Store pays HO
     - The HO receipt of payment creates the mirror outbound payment in the store company.
     - Both
   * - POS orders
     - Each store POS order arrives at HO already invoiced at the store and is **invoiced again in
       the store's mirror company**, so HO revenue by store equals the stores' own books.
     - Store company
   * - Store end-of-day entries
     - Collections by mode of payment and credit-note entries from the store, posted
       automatically on arrival.
     - Store company
   * - Credit note issued on a return
     - A refund on the credit-note journal, settled by a cash payment and added to the customer's
       **credit wallet** (voucher number, total, used, remaining). Redemption at any store reduces
       the wallet.
     - Store company
   * - Gift vouchers and cards
     - Issued and redeemed against their own journals; a card used in one store is zeroed in all
       the others the same day.
     - Store company
   * - Payroll
     - Payslip entries with debit and credit accounts per salary rule and an analytic account per
       contract, which puts payroll cost on each store.
     - Employing company
   * - Fleet and transport
     - Vehicle captured on journal entries and lines for transport cost analysis.
     - Any

Withholding and cess
====================

TDS, TCS and cess taxes are selected on the bill or invoice and applied to every line alongside
GST, so withholding never has to be added line by line.

GST compliance
==============

* **Price-band GST**, **intra/inter-state** logic and the **HSN master** are described in
  :doc:`master_data`.
* **E-invoices and e-way bills**: generated through a GST suvidha provider, with the references
  stored on the invoice and the batch.
* **GSTR returns**: GSTR-1 and GSTR-3B, GSTR-2B reconciliation, TDS and TCS reports, and the
  HSN-wise sales report from the analytics stack (see :doc:`analytics`).

The external accounting bridge
==============================

The group keeps its statutory books in an external accounting system with **one company per state
GSTIN**. The **accounting connector** (`mtl_accounting_connector`) exposes a key-protected API
from which that system pulls:

* account groups, the chart of accounts, customers and vendors;
* companies, warehouses and locations (as cost centres);
* journal entries, vendor bills, customer and vendor payments, and customer invoice items.

Every exported record is flagged once exported and flagged again if its reference or narration
changes, so nothing is sent twice and nothing is missed. Each document type is mapped to the right
state company, and an admin dashboard shows what is pending export by type.

Closing the loop
================

Because the head office holds a mirror company for every store (see :doc:`architecture`), the
consolidated P&L, stock valuation by store and inter-company balances all come from **one
database**. The standard Odoo reports (P&L, balance sheet, cash flow, general ledger, trial
balance, partner ledger, aged balances) therefore work per store or across the chain with a
company filter, and the COGS roll-forward in analytics proves that opening stock plus movements
equals closing stock.
