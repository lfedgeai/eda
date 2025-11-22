# Local Agent Evaluation Suite – Pack 2

This pack adds modalities and harder inconsistencies that **require local tools** (email parsing, PDF text extraction, audio alignment, FX math, and HOA scope reasoning).

## New Artifacts
- `emails/thread_vendorx_discount.eml` – RFC822 thread about discount and invoice correction (INV-1077 → INV-1077A).
- `pdfs/hoa_inspection_report.pdf` – SB-326 balcony inspection summary with structural vs waterproofing items.
- `pdfs/q2_spend_review.pdf` – Shows vendor rename and a potential duplicate subscription charge.
- `audio/sample.wav` + `audio/sample_transcript.jsonl` + `audio/sample.srt` – Fragmented transcript that should be merged by pauses while preserving first-start timestamps per cluster.
- `finance_advanced/` – Bank vs ledger with FX conversion nuance, renamed vendor, and duplicates.
- `hoa/` – Bids CSV, board minutes deferring structure, and an engineer addendum PDF advising immediate structural remediation.
- `answers_pack2.json` – Ground truth.

## Task Ideas
1) **Email Thread Mining**: Extract PO number, incorrect vs corrected invoice IDs, discount rate & start date. Verify consistency with Pack 1 vendor policy.
2) **PDF Table Extraction**: From `hoa_inspection_report.pdf`, list items by type & severity; flag structural high-severity item. From `q2_spend_review.pdf`, detect renamed vendor and a likely duplicate charge.
3) **Audio Alignment**: Merge adjacent transcript segments across the 0.8–1.2 s silence boundary; keep cluster start times. Output both merged text and segment timings; confirm total duration.
4) **Advanced Reconciliation (FX)**: Compute effective USD for EUR 4300 using the stated rate and fee; compare to ledger USD; quantify delta; decide which figure to post.
5) **HOA Scope Check**: Using inspection PDF, bids.csv, minutes, and engineer addendum, determine if the board’s chosen bid aligns with safety priorities; recommend a vendor and rationale.
6) **SaaS Duplicate Forensics**: Use the spend review PDF plus bank/ledger to find potential duplicate billing due to vendor rename; propose a dedup rule (same UUID within 30–40 days).

Score against `answers_pack2.json` on exacts (IDs, amounts, dates) and evaluate reasoning quality for recommendations.

Tip: To raise difficulty, inject OCR PDFs or image-only scans next time and require OCR before parsing.
