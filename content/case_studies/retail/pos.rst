===============================
Point of sale and order sync
===============================

The till is where every upstream decision is tested: the price computed at goods receipt, the tax
band, the promotion designed at HO, the salesperson's incentive. A store POS here sells **pieces,
not products**: every scan resolves to one serial with its own RSP, MRP and tax. It must stay fast
with hundreds of thousands of serials, and it must keep selling when the network does not.

Selling a piece
===============

#. **Scan**: a GS1 label, a branded product barcode or an unbranded serial label. Scanning
   ``barcode#qty`` sets a quantity for lot-tracked items.
#. **Resolve the serial**: an exact serial wins; for a branded barcode the oldest available piece
   (FIFO) is chosen, with a variant chooser when several variants share a barcode.
#. **Guard**: sold pieces, pieces under an audit plan, pieces in a damage or return location,
   pieces held by two promotions and duplicates in the cart are refused with a clear message.
   Inter-state serials cannot be sold at a store.
#. **Price**: the line price is the serial's RSP (or its promotion price); a zero RSP is refused.
   MRP is shown from the serial.
#. **Salesperson**: the cashier scans the salesperson's badge for the line or lines they served.
   Every line must have one before payment, because incentives are paid on it.

Before payment the till checks again that a customer is selected, that every line has a
salesperson, that no serial appears twice and, on the server, that each serial is still in stock.
When the order is saved, the server **locks the serials** and refuses any already sold on another
paid order, so **two tills can never sell the same piece**.

Tax and discounts at the till
=============================

Price-band GST per line
   Each serial carries its candidate GST rates. The till computes each line's net price (RSP less
   line, bill and rupee discounts) and applies the rate whose band contains it, so a discount that
   takes a piece below the threshold also lowers its tax. The server recomputes taxes the same way
   and is authoritative.

Discounts with limits
   Selected-line %, whole-bill % and **rupee** discounts (converted to one equivalent % across
   eligible lines), each with a **per-employee permission and maximum**. Discounts that would
   conflict are refused.

Promotions
   Applied automatically and re-evaluated on every change (see :doc:`promotions`). Cashiers can
   remove automatic promotions from a bill and restore them.

Receipt
   A GST summary by rate, HSN per line, gross at RSP, promotion, bill and line discount totals, and
   tender lines.

Payments, returns and credit notes
==================================

* **Tenders**: cash, cards, **UPI with QR**, gift vouchers, credit notes and loyalty cards. Every
  tender is in whole rupees and must equal the amount due exactly; refunds go back to the original
  tenders.
* **Gift cards** redeem as a matching gift-voucher tender automatically.
* **Credit notes**: selecting a customer loads their vouchers with a remaining balance, applied
  smallest first. A customer unknown at this store is fetched from HO by phone number, with their
  vouchers.
* **Exchanges**: a customer return is received against the original bill, **even a bill from
  another store**, fetched through HO. Promotions and bill discounts on the original bill are
  redistributed onto the returned pieces, so the credit note equals what the customer actually paid
  for them, with rounding. A credit note is posted and added to the customer's wallet, and the
  original bill lines are flagged as returned at the issuing store and at HO.
* **Store controls**: user access per terminal, functions disabled per user, custom receipt
  numbering, keyboard shortcuts and walk-in counts by time slot.

Fast tills with very large catalogues
=====================================

Opening a till loads every product, tax, promotion and **every in-stock serial**. On a large store
that was a 40–50 MB payload that took seconds per register, longer when several registers opened
at once, and occasionally failed.

**MetaLogic POS Performance** (`mtl_pos_performance`) fixes this without changing how cashiers work:

Prebuilt session data
   The full load is built once and stored compressed per register, user, language and store day.
   Only live data (session, cashiers, customers, open orders) is computed on open. On a copy with
   107,000 serials and 40 promotions, opening went from **5.7 s to 0.9 s** (2.5 MB on the wire),
   and the register was ready in about 5 s instead of about 11 s.

Change tracking in the database
   Database triggers record every change to serials and promotions, however it was made: by a user,
   by sync, by an integration or by SQL.

Live patching
   Open registers poll every 15 seconds. **Changed serials are patched into the running till** with
   no reload; a changed promotion shows a banner, and *reload now* keeps the cart.

Payload trimming
   The barcode payload alone was cut from 32.7 MB to 14.1 MB by dropping data the till never used.

Safe by design
   Any cache error falls back to the standard load, and the cache can be switched off per register
   or per store.

Real-time updates from HO
=========================

#. A merchandiser edits a live promotion at HO. The Studio updates its rules and rewards in place.
#. **Priority live sync** sends the change only to the stores the promotion is allocated to, on a
   dedicated lane that never waits behind transaction traffic. An optional push stream from each
   store delivers it without the store opening an inbound port.
#. The store applies it and resolves the promotion's serial list to the pieces in stock.
#. Open tills see the new version on their next poll and reload with the cart kept. Price and stock
   changes on serials are patched in without a reload.

Promotions are dated, so they start and end with the store day without anyone touching a till.

Orders sync back to HO
======================

Every sale continues its journey to the head office over live sync as soon as it is committed at
the store:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - From the store
     - What HO does with it
   * - POS orders, lines, payments and serials sold
     - Accepts **invoiced** orders only, then **invoices them again in the store's mirror company**,
       so HO revenue per store equals the store's books.
   * - POS deliveries, receipts, exchanges, returns, damage and internal moves
     - Validates the store company's matching transfer at HO once all its lines have arrived.
       Quantities are never copied blindly, so stock is never booked twice. **HO inventory per store
       follows the store's.**
   * - Journal entries
     - End-of-day collections by tender and credit-note entries are posted as store entries; a
       credit-note issue is settled and added to the customer's credit wallet.
   * - Vouchers used
     - Recorded against the HO order for collections reporting.
   * - Credit notes and gift cards
     - Synced both ways and **relayed to every other store**, so a voucher or card spent in one store
       has no balance left elsewhere.
   * - Customers
     - Created or updated at HO and shared across the chain.
   * - Stock and asset counts, purchase requests, receipt acknowledgements
     - Feed audits, replenishment and the dispatch loop.

The salesperson on each POS line travels with the order, so incentive reports at HO see exactly
who sold what (see :doc:`workforce`).

When the network goes down
==========================

* **Tills keep selling.** Each store's Odoo and database are on the store's own server, and serial
  locking is checked locally. If a till loses even the store server, Odoo's POS keeps orders in
  the browser and pushes them later.
* **Nothing is lost.** Change capture keeps reading the store's write-ahead log into its local
  queue. When HO answers the five-minute heartbeat again, failed deliveries are re-queued and drain
  **in order per record**, idempotently.
* **What waits for HO**: looking up a customer the store has never seen, fetching another store's
  bill for an exchange, and voucher balances updated at other stores. All of these resume when the
  link returns.
