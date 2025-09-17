# Local Agent Evaluation Suite – Pack 3 (OCR + Joins + Archives)

This pack stresses **OCR on image-only scans (PBM)**, **multi-table SQL joins**, **mbox parsing**,
**nested archives**, and **overlap-aware audio summarization**. All tasks require local tools.

## Artifacts
- `scans/*.pbm` — Image-only "scans" (no embedded text): Vendor X invoice INV-2091 (shows "12% APPLIED" and PO-8821),
  bank deposit slip EU-818, and delivery note for O-2007 with SKU-B qty 6.
- `sql/sales.db` — Customers, orders, lines, payments, shipments (+ partial), refunds (partial) with
  a pricing discrepancy on O-2007 (line price 170 vs agreed 150).
- `emails/support.mbox` — Two threads: chargeback on PMT-5001 (O-2007); shipment delay on O-2008.
- `archives/audit_bundle.tar` — Contains a **ZIP** with `audit/audit.csv` asserting the agreed unit price (150.00) for SKU-B on O-2007.
- `audio/dialog.wav` + `audio/dialog.jsonl` — Overlapping speakers referencing invoice/price/refund; test diarization/merge.
- `cross_artifact_hints.md` — Optional evaluator hints.
- `answers_pack3.json` — Ground truth targets.

## Task Ideas
1) **OCR the Scans**: Extract invoice ID, discount rate, PO number, wire reference, and delivery details from PBM images.
2) **SQL Reconciliation**: Compare `order_lines.unit_price` for O-2007 to the agreed price in `audit/audit.csv`; compute the total
   overcharge and compare with recorded refund(s). Output additional refund required.
3) **Mbox Parsing**: Identify which payment is under dispute and why (link to SKU-B discount expectation).
4) **Nested Archive Handling**: Open the TAR, then the inner ZIP, and read `audit/audit.csv` to support (2).
5) **Diarization-Aware Summary**: Merge claims from `audio/dialog.jsonl` in timeline order; note overlaps and deduplicate facts.
6) **Cross-Artifact Decision**: Given all evidence, recommend a resolution plan for O-2007 (price adjust remaining 5 units, notify AP, close chargeback).

## Scoring
Match `answers_pack3.json` for exacts (IDs, amounts) and assert that your final decision references at least
three distinct artifacts (scan+SQL+archive or mbox).

Tip: If you want *true* OCR PDFs next time, we can embed raster images into PDFs or supply image-only PNG/JPG scans;
PBM was chosen here to avoid external libraries.
