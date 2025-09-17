# Cross-Artifact Clues (for evaluator design)
- PBM scans include: invoice INV-2091 (with '12% applied'), bank deposit EU-818, delivery note for O-2007 (SKU-B qty 6).
- SQL shows O-2007 line price 170.00 and a later partial refund 170.00.
- Nested archive `audit_bundle.tar` contains a ZIP with `audit/audit.csv` asserting agreed unit price 150.00 for SKU-B on O-2007.
- mbox mentions chargeback on PMT-5001 due to expected 12% discount on SKU-B.
- Audio dialog connects INV-2091 discount vs audit unit price, and suggests issuing a 1-unit refund.
