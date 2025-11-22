"""
Gemini provider for the "general LLM" (no local file access).

Setup:
  pip install google-generativeai requests
  export GEMINI_API_KEY="..."

Usage:
  from providers import general_llm
  out = general_llm.run("Return JSON with keys a,b,c ...")
  # returns a Python object (dict/list) parsed from model output

Notes:
- We strongly encourage you to prompt Gemini to return STRICT JSON.
- If the model replies with text, we attempt to extract the first {...} JSON block.
"""

import os, json, re, logging
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
API_KEY_ENV = "GEMINI_API_KEY"

def _extract_json(text: str) -> Union[dict, list, str]:
    """Try to parse JSON; if mixed text, extract the first {...} or [...] block."""
    text = text.strip()
    # Direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Greedy search for first balanced JSON-looking block
    # Simple heuristic: find first '{' or '[' and last matching '}' or ']'
    start = None
    for i, ch in enumerate(text):
        if ch in '{[':
            start = i
            break
    if start is not None:
        # Try progressively shrinking the end to the last brace/bracket
        for j in range(len(text), start, -1):
            chunk = text[start:j]
            try:
                return json.loads(chunk)
            except Exception:
                continue

    # As a last resort, return raw text
    return {"_raw": text}

def _call_gemini_with_sdk(prompt: str, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(DEFAULT_MODEL)
    # Use a JSON-focused prompt to improve structure
    sys_inst = (
        "You are a data extraction engine. "
        "Always respond with STRICT JSON only, no markdown or prose."
    )
    # SDK supports system_instruction in newer versions; fall back if not present
    try:
        resp = model.generate_content([{"role":"user","parts":[sys_inst + "\n\n" + prompt]}])
    except TypeError:
        # older SDKs
        resp = model.generate_content(sys_inst + "\n\n" + prompt)
    # Handle candidates
    if hasattr(resp, "text") and resp.text:
        return resp.text
    # Some SDK versions expose candidates[0].content.parts[0].text
    try:
        cand = resp.candidates[0]
        parts = getattr(cand, "content", getattr(cand, "content", None)).parts
        texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", "")]
        return "\n".join(texts).strip()
    except Exception as e:
        return ""

def _call_gemini_rest(prompt: str, api_key: str) -> str:
    import requests
    # Using the "generateContent" endpoint for 1.5 models.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_MODEL}:generateContent?key={api_key}"
    sys_inst = (
        "You are a data extraction engine. "
        "Always respond with STRICT JSON only, no markdown or prose."
    )
    payload = {
        "contents": [
            {"parts": [{"text": sys_inst + "\n\n" + prompt}]}  # single user message
        ]
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Parse the first text part
    try:
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0]["content"].get("parts", [])
            texts = [p.get("text","") for p in parts if "text" in p]
            return "\n".join(texts).strip()
    except Exception:
        pass
    return json.dumps({"_raw_api_response": data})

def run(prompt: str) -> Any:
    """Call Gemini WITHOUT local file access and return a Python object (dict/list/scalars)."""
    api_key = os.environ.get(API_KEY_ENV, "").strip()
    if not api_key:
        # Return a helpful error as JSON
        return {"_error": f"Missing {API_KEY_ENV}. Please export your Gemini API key."}

    # Try SDK first, then REST fallback
    text = ""
    try:
        text = _call_gemini_with_sdk(prompt, api_key)
    except Exception as e:
        logger.warning("Gemini SDK call failed, falling back to REST: %s", e)
        try:
            text = _call_gemini_rest(prompt, api_key)
        except Exception as e2:
            return {"_error": f"REST call failed: {e2.__class__.__name__}: {e2}"}

    if not text:
        return {"_error": "Gemini returned empty response."}

    return _extract_json(text)