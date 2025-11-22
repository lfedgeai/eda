# Local Agent Evaluation Suite – Pack 4 (Image-PDF + EML attachments + XLSX formulas + Parquet)

Focus areas:
- **Image-only PDFs**: embedded 1-bit raster images inside PDFs (no text layer) → require OCR.
- **.eml with attachments**: CSV + scanned invoice PDF.
- **Multi-sheet XLSX**: formulas across sheets (`Summary` references `Inputs` totals).
- **Parquet shard**: small sales dataset (falls back to CSV if Parquet libs unavailable).

## Artifacts
- `pdf_scans/expense_report_scan.pdf` (image-only): JUL 2025 totals and EMP ID E002.
- `pdf_scans/invoice_inv3001_scan.pdf` (image-only): INV-3001 with 12% discount on SKU-B qty 4 @ 150.00.
- `emails/inv3001_with_attachments.eml`: multipart/mixed; contains `inv3001_lines.csv` and the invoice scan PDF.
- `xlsx/ops_finance.xlsx`: `Inputs` (SKU rows) + `Summary` (cross-sheet SUM formulas).
- `data_lake/sales_2025-07.parquet` or `sales_2025-07.csv` (+ `PARQUET_FALLBACK.txt` if needed).
- `answers_pack4.json`: ground truth for spot-checking exacts.

## Tasks
1) **OCR the PDFs**: Extract numeric fields from both scans; verify the invoice CSV matches the scan.
2) **EML Parsing**: Enumerate attachments, decode the CSV, and cross-check against the OCR’d invoice.
3) **XLSX Formula Eval**: Compute `Summary!B1` and `Summary!B2` (total vs discounted total) without Excel—your agent should evaluate formulas or use a library.
4) **Lake Query**: Read the Parquet shard (or CSV fallback) and produce totals by SKU/date; reconcile with `Inputs` sheet.
5) **Cross-Check**: Confirm that INV-3001 (SKU-B qty 4 @ 150, 12%) is consistent across PDF scan, CSV attachment, and your XLSX totals.

Scoring: Compare your results to `answers_pack4.json` for exact numbers and attachment presence.
