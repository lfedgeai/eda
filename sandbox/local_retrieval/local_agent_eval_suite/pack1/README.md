# Local Agent Evaluation Suite

This suite is designed to test local agents on tasks **that require local data**. A pure LLM without access to these files should not be able to answer correctly.

## Data Map

- `finance/`
  - `bank_2025-06.csv`
  - `ledger_2025-06.csv`
  - `invoices/invoice_INV-1043.json`
- `hr/`
  - `employees.csv`
  - `badge_access.csv`
- `ops/`
  - `nginx.log`
  - `system.log`
  - `kpis.md`
- `product/`
  - `inventory.sqlite`
  - `orders_july.csv`
- `calendar/company.ics`
- `knowledge/handbook.md`
- `projects/ai-slides/manifest.yaml`, `notes.md`
- `vendors/vendor_x_thread.md`
- `security/.env`
- `transcripts/meeting_notes.md`
- `answers.json` (ground-truth for quick scoring)

## Tasks

1) **Bank ↔ Ledger Reconciliation**
   - Find expenses present in bank but **missing** in ledger.
   - Find entries in ledger that **do not** appear in bank.
   - Match invoices to bank transactions (exact date & amount).

2) **Post-Termination Access Detection**
   - Find any badge access events **after** an employee's termination date.

3) **Ops Incident Triage**
   - Detect any 5xx spike window in `nginx.log` and summarize endpoint(s) involved.
   - Correlate with `system.log` to infer a likely root-cause hint.

4) **Inventory Risk**
   - Using `product/inventory.sqlite` + `product/orders_july.csv`,
     determine which SKU goes negative, on what date, and when the next restock arrives.

5) **Calendar Lookup**
   - Extract the next Vendor X review date/time from `calendar/company.ics`.

6) **Vendor Terms Discovery**
   - Determine the Vendor X discount rate, start date, and applicable SKUs
     by reading `vendors/vendor_x_thread.md` and `knowledge/handbook.md`.

7) **Config/Secrets Awareness**
   - From `security/.env`, report the service URL and current mode.
     (Do **not** print secrets in logs—just confirm presence of an API key.)

8) **Cross-File Entity Graph**
   - List all files that reference "Vendor X" and build a small dependency map
     (invoice ↔ calendar ↔ emails ↔ notes).

## Scoring
Compare your agent's output to `answers.json`. For free-form explanations,
you can check that key fields match (dates, amounts, identifiers).

Good luck!
