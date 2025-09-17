# Local Agent Eval Harness

This harness runs the same tasks against:
1) A **General LLM** (no local file access)
2) A **Local Agent** (allowed to read local files & use tools)

and scores them against the ground truth shipped with the data packs.

## Quick Start
1. Unzip the evaluation packs into a folder, e.g.
   - `/data/LocalAgentEvalSuite/` (Pack 1)
   - `/data/LocalAgentEvalSuite_Pack2/`
   - `/data/LocalAgentEvalSuite_Pack3/`
   - `/data/LocalAgentEvalSuite_Pack4/`
2. Implement the providers:
   - `providers/general_llm.py`: call your hosted model (no local file access).
   - `providers/local_agent.py`: call your local agent with file access.
3. Run the harness:
```bash
python harness.py --packs "/data" --out "report.json"
```
4. Inspect `report.json` and the per-task logs in `runs/`.

## Scoring
- Each task expects a **JSON** answer with specific keys. We compare to `answers*.json`.
- Score = exact match (% of keys matching expected values). Non-scalars are compared as sets/lists where sensible.
- We log both the model's raw text and parsed JSON for debugging.

## Adding/Removing Tasks
- Edit `tasks.py`. Each task defines:
  - `pack_glob` (directory name pattern)
  - `prompt` (input string sent to both providers)
  - `answer_path` (relative path to ground-truth answers file)
  - `answer_key_path` (JSON pointer list to the sub-answer we compare against)
  - `extractor` (optional) to post-process model JSON to a comparable shape.


### Evaluation Results

| Task                         | General LLM | Local Agent | Δ (Agent − LLM) |
|-----------------------------|------------:|------------:|----------------:|
| p1_finance_invoice_match    | 0.33        | 1.00        | 0.67            |
| p1_hr_post_termination      | 0.00        | 1.00        | 1.00            |
| p1_ops_spike                | 0.00        | 1.00        | 1.00            |
| p2_emails_discount_thread   | 0.00        | 1.00        | 1.00            |
| p2_audio_merge              | 0.17        | 1.00        | 0.83            |
| p2_finance_fx               | 0.00        | 0.40        | 0.40            |
| p3_ocr_invoice              | 0.00        | 1.00        | 1.00            |
| p3_sql_recon                | 0.00        | 1.00        | 1.00            |
| p4_eml_attachments          | 0.00        | 1.00        | 1.00            |
| p4_xlsx_summary             | 0.00        | 0.00        | 0.00            |
| **Averages**                | **0.05**    | **0.84**    | **0.79**        |


## Pack 1 — LocalAgentEvalSuite

- **p1_finance_invoice_match**  
  Return JSON with invoice_id, bank_date (YYYY-MM-DD), and amount for Vendor X INV-1043 by reading local files.

- **p1_hr_post_termination**  
  Return JSON with employee_id, name, and a list of 'timestamp door result' strings for any badge events after termination.

- **p1_ops_spike**  
  Return JSON with keys: 500_spike_window (human-readable), top_endpoint, root_cause_hint by correlating nginx.log and system.log.


## Pack 2 — LocalAgentEvalSuite_Pack2

- **p2_emails_discount_thread**  
  Parse emails to return JSON with po, issue_invoice, corrected_invoice, discount, start, skus.

- **p2_audio_merge**  
  Merge transcript segments across silence. Return a list of {start, end, text} segments preserving cluster start times.

- **p2_finance_fx**  
  Compute effective USD for EUR 4300 on 2025-06-20 per fx_notes.md and compare vs ledger USD; return JSON with fx_effective_usd and delta_vs_ledger_usd.


## Pack 3 — LocalAgentEvalSuite_Pack3

- **p3_ocr_invoice**  
  OCR PBM scans to extract inv_id, discount, po, bank_wire_ref, delivery_order and delivery_sku_qty (with date). Return JSON.

- **p3_sql_recon**  
  From sql/sales.db and archives/audit_bundle.tar (zip inside), compute o2007_unit_price_db, agreed_unit_price_zip, qty, total_difference_usd, refund_recorded_usd, refund_needed_additional_usd. Return JSON.


## Pack 4 — LocalAgentEvalSuite_Pack4

- **p4_eml_attachments**  
  Parse inv3001_with_attachments.eml. Return JSON with csv_rows (as list of dicts) and attached_pdf filename.

- **p4_xlsx_summary**  
  Evaluate ops_finance.xlsx formulas and return JSON with expected_values for Inputs!D2, Inputs!D3, Summary!B1, Summary!B2.
