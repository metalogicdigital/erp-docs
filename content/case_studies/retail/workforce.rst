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
