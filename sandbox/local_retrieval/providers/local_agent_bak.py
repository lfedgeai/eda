# Implement `run(pack_dir: str, prompt: str) -> dict | str`
# - pack_dir: path to the located pack folder (so your agent can read files)
# - prompt: same text as given to general LLM
# Return JSON-compatible Python object, or a JSON string.
#
# TIP: You can route on task intent by reading files under `pack_dir`.
#  e.g., if 'answers.json' exists -> Pack1; 'answers_pack2.json' -> Pack2; etc.

import os, json

def run(pack_dir: str, prompt: str):
    # TODO: Wire your local tools. Below is a tiny heuristic demo:
    # This demo simply returns {}. Replace with real logic.
    # You can detect files under pack_dir and parse:
    # - CSVs in finance/, hr/, ops/
    # - .ics in calendar/
    # - PDFs in pdfs/ or pdf_scans/ (via OCR)
    # - PBM images in scans/ (Pack 3) -> OCR
    # - .eml and .mbox
    # - SQLite in product/ or sql/
    # - TAR/ZIP nested archives in archives/
    return {}
