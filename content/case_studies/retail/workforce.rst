===========================================
Workforce, payroll and sales incentives
===========================================

A store chain's largest controllable cost after stock is people: floor staff on shifts,
cashiers, security, warehouse and dispatch teams, and a head office. Sales staff are paid
partly on what they sell. The customer needed recruitment, attendance, payroll and incentives
in the same system as the sales they depend on, across one legal entity per store.

Odoo 17 Community has employees, contracts, time off and attendance, but no payroll. We built
the HR layer on the open-source Open HRMS payroll suite and extended it for multi-store retail.

.. _workforce-incentives:

Advanced sales incentive programs
=================================

Floor staff in fashion retail are motivated by what they earn on the floor, and the business wants
to steer that effort: towards higher-value pieces, towards ageing stock that needs to move, and
towards the store's target. **MetaLogic Sales Incentives** (`mtl_retail_incentives`) makes the
incentive scheme a configurable master, defined at HO and pushed to the stores.

Structure
   A validity period, a state (draft, confirmed, closed), the incentive account and the
   **incentive type**: regular, target, product ageing, days ageing or store target. A structure
   is **global** (every store) or **store-wise** (selected stores only).

Lines
   Each line names the **role** it rewards (a job position, such as sales associate or floor
   manager), the calculation (**percentage** or **fixed amount**), optional minimum and maximum
   values that create tiers, and for ageing types the ageing bucket or days-ageing slab
   (0–30 up to 330–360 days).

Attribution
   Every POS line carries the **salesperson** scanned at the till, by badge. A bill served by two
   people pays each of them for their own lines. At HO, the employee and their job position must
   match the line's role.

Reports
   Detailed, summary, employee-wise and designation-wise incentive reports, plus an ageing view,
   per store and period.

.. example:: **Regular, all stores: 1% for sales associates**

   A line of ₹1,999.20 including tax earns its salesperson **₹19.99**. The next line on the same
   bill, served by a colleague, earns for the colleague.

.. example:: **Target tiers, selected stores**

   Three lines on one structure: line value ₹0–999 → 0.5%, ₹1,000–2,999 → 1%, ₹3,000 and above →
   fixed ₹50. A ₹2,499 line pays **₹24.99**; a ₹3,499 line pays **₹50**. Tiers are evaluated per
   line, so selling up to the next price band is rewarded on every bill.

.. example:: **Move ageing stock**

   *Product ageing*: a fixed ₹20 for every piece sold from a chosen ageing bucket. *Days ageing*:
   2% on pieces received 90–120 days before the sale, so a ₹1,000 piece received 100 days ago pays
   **₹20**. Fresh stock earns nothing extra, and the floor team naturally shows the older stock
   first.

.. example:: **Store target for the floor managers**

   0.1% of the store's POS sales value for the month goes to **every** floor manager in the store:
   a store selling ₹10,00,000 pays each of them **₹1,000**. This rewards the team for the store's
   result rather than individual bills.

Structures are replicated to the stores, so the same rules are visible to store managers, and
the salesperson link on every POS line reaches HO with the order.

Incentive engine in the Promotion Studio
========================================

Structures like the above are fixed by role and bill line. Merchandisers also want incentives
that follow **the offer being pushed**: *2% on any piece of last season's ethnic wear, but only in
these twelve stores, only this month, capped at ₹5,000 a person.* **Promotion Incentives**
(`mtl_promo_incentive`) therefore lives in the :doc:`Promotion Studio <promotions>`, next to the
offers it supports, and reuses its building blocks instead of inventing a second set.

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Studio building block
     - Role in an incentive
   * - Item pool
     - The **scope**: serials, categories, families, brands, attributes, ageing, or any
       combination. Unlike a promotion, the pool matches the piece **as it was sold**, not what
       is in stock today.
   * - Definition
     - The **scheme**: a percentage of sale value (with or without tax), RSP, gross margin or
       quantity, or a fixed amount per item or once; slabs on item value, product ageing code or
       days in stock; a per-person cap; exclusion pools; and a **store target** type that pays on
       the share of target achieved or on sales value, either on the whole total or band by band.
       Days in stock count from the HO receipt or from the arrival at the store.
   * - Allocation
     - **Where and when**: stores and a period, so one scheme can run in a few stores for a week
       and a different one elsewhere.
   * - Sample testing
     - **Incentive testing**: replay a scheme over past sales to see who would have earned what
       before anyone is promised anything.

How a month is calculated
   The engine takes a snapshot of each sold line (salesperson, serial, price, cost, discount) as
   a *fact*, matches the facts against the scheme and writes a **ledger** entry per employee. A
   run is idempotent, so running it twice never pays twice, and it executes as a background job
   with progress. A month of roughly 79,000 sale lines for two stores turns into facts in about a
   minute.

People are matched by job position
   Each store has its own job-position master, so the scheme names the role (*sales associate*)
   and the engine finds it in each company by name. Sales by counters, promoters or anyone without
   a position are listed separately instead of silently dropped.

Bill-level discounts are spread
   A promotion applied to the whole bill arrives as a negative line. The engine spreads it over
   the bill's items, so incentives follow the net price and not the gross.

Exchanges reverse earnings
   When a piece comes back through an exchange, the engine reverses what it earned, if it
   earned anything, in the period that follows.

Statements and locking
   A statement per employee and store shows each line that contributed. When payroll has
   accepted a period it is **locked**; a period can be locked only after HO holds the bills dated
   after it, so late-arriving bills cannot change a number already paid.

.. example::
   A *Move old season* scheme gives sales associates 1% on pieces of ageing codes G1–G12 and 2% on
   older codes, capped at ₹5,000 each, in two stores for July. Run over a month of real sales it
   computes the amounts for 282 employees on ₹6.74 crore of sales, a payout of 0.29% of sales,
   and shows that none of the 183 exchanges had earned anything, so nothing needed reversing. The
   top earner hits the cap. Only after reading that result does the business activate the scheme.

Incentives are calculated at head office from the sales that live sync delivers, so every store
that is on live sync is included from its go-live date.

Recruitment to appointment
==========================

**MetaLogic Retail Recruitment** (`mtl_retail_recruitment`) extends Odoo Recruitment for
high-volume store hiring:

* **CTC breakup** on the applicant (basic, HRA, PF, professional tax, net), so the offer is
  computed, not typed.
* **Two-level approval** of the offer and of the appointment letter, with stage remarks and an
  on-hold state.
* **Offer and appointment letters** generated as PDFs, including direct-appointment variants.
* **Employee creation from the applicant**, carrying grade, education, family, previous
  employment, nominee and references, plus company assets issued to the employee.
* A **tokenised web interview form** that candidates fill in themselves, feeding the interview
  record.

Attendance, shifts and statutory deductions
===========================================

**MetaLogic Store Attendance** (`mtl_retail_attendance`) handles the realities of store shifts:

* **Attendance upload** from biometric or register exports, with check-in, check-out, lunch and
  break sessions.
* **Late-coming deduction** and **overtime** slabs, **shift** masters with shift moves and
  approval, and **lunch-bonus** rules.
* **State-wise professional tax** slabs, because each store's state sets its own.
* Lunch and break summaries and a non-CTC payslip report, behind a salary-approver role.

Payroll, loans and advances
===========================

Payroll engine
   Salary structures, rules (fixed, percentage or formula, with conditions) and categories;
   payslips and payslip batches with worked days taken from the attendance calendar and leave;
   refunds; payslip and contribution-register reports.

Payroll accounting
   Each payslip posts its journal entry on confirmation, with debit and credit accounts per rule
   and an **analytic account per contract**, which is how payroll cost lands on each store's
   P&L.

Loans and salary advances
   Employee loans with an instalment schedule repaid automatically through payroll, optional
   second approval and accounting entries on payout and repayment. Mid-month salary advances
   with manager-then-accounts approval, a ceiling per salary structure, one advance per month
   and automatic deduction in the next payslip.

Multi-store workforce
=====================

Each store is its own company, so HR data is separated per company with multi-company rules on
attendance, leave, payslip batches and rule categories.

Branch transfer
   Moving an employee between stores is a two-step flow: the sending store transfers, the
   receiving store accepts. On acceptance the employee is created in the new company, the old
   contracts are closed, the old record is archived and a new contract is opened. Transfers can be
   approved at the head office and are replicated to the stores involved.

Employee lifecycle
   Joining date, ID and passport attachments with expiry reminders, family details and notice
   periods; resignation and termination with approvals and automatic archiving on the last day;
   end-of-service settlement including gratuity; HR announcements, rewards and warnings to chosen
   employees, departments or job positions.

Floor staff without a login
   Leave can be requested by email, matched to the sender, so staff without an ERP user still use
   the same process. Every new ERP user automatically gets an employee record.

Store routines
   A **store opening and closing checklist** (managers and security on duty, parking, signage,
   lighting and air-conditioning, shelf and expiry checks, same-day dispatch of goods returns,
   billing counters, trial rooms) with a PDF record per day, plus a birthday and work-anniversary
   board and configurable HR reminders.

HR dashboard
   Leave by department and trend, joining and resignation trend, **attrition rate**, and the
   **Bradford Factor** absence score.
