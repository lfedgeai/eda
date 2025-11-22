# Local Agent Evaluation Suite – Pack 5 (Signatures + Redactions + Recurrence + Delta Lake)

This pack emphasizes **signature/hash verification**, **true vs cosmetic redactions**, **calendar recurrence with exceptions**, and **Delta Lake-style snapshots**.

## Artifacts
- `pdfs/invoice_INV-4002_signed.pdf` + `.p7s` + `signature_manifest.json` — verify file hash; treat PKCS#7 as a placeholder.
- `pdfs/reimbursement_original.pdf` and `pdfs/reimbursement_redacted_overlay.pdf` — redactions are **overlays**, not content removal.
- `emails/finance_support.mbox` (+ `emails/att_statement.csv`) — message references a local attachment path stored separately.
- `calendar/vendorx_weekly.ics` — weekly RRULE with EXDATEs and a moved instance (RECURRENCE-ID).
- `delta_lake/` — partitions `date=YYYY-MM-DD/part-*.csv` and `_delta_log/000000.json`, `000001.json` showing a remove/add (late data).

## Tasks
1) **Signature Verification**: Compute SHA-256 of `invoice_INV-4002_signed.pdf` and compare to `signature_manifest.json`. Treat `.p7s` as untrusted placeholder unless you actually verify PKCS#7.
2) **Redaction Audit**: Determine if PII (EMP ID, card digits) is still extractable from `reimbursement_redacted_overlay.pdf` by reading the text layer. Flag as non-destructive redaction.
3) **Mbox Attachment Handling**: Parse `finance_support.mbox`, detect the attachment filename, and load it from the local path.
4) **ICS Recurrence Expansion**: Expand the series, drop EXDATEs, and apply the moved instance (`RECURRENCE-ID`). Output UTC instance list.
5) **Delta Lake Snapshotting**: Using `_delta_log`, compute the **current active files** and derive the up-to-date quantity for order `O-3003` (should be 4).

## Scoring
Compare answers to `answers_pack5.json`. For redactions: pass if you detect overlay-only masking. For signatures: pass if hash matches manifest and `.p7s` is not blindly trusted.
