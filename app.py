"""
PMF Marketing Tool — Flask Backend
Analyzes a B2B SaaS startup and generates a complete
"Prove PMF with Marketing" framework using Claude AI.
"""

import os
import io
import json
import logging

import requests
from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
from bs4 import BeautifulSoup

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdfplumber not installed — PDF pitch deck parsing will be unavailable.")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_website_content(url: str) -> str:
    """Fetch a URL and return cleaned plain text (≤ 3 000 chars)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; PMFAnalyzer/1.0)"}
        resp = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.splitlines() if l.strip()]
        return "\n".join(lines)[:3000]
    except Exception as exc:
        logging.warning("Could not fetch %s: %s", url, exc)
        return f"[Website could not be fetched: {exc}]"


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from a PDF file (≤ 4 000 chars from first 10 pages)."""
    if not PDF_SUPPORT:
        return "[PDF parsing unavailable — install pdfplumber]"
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages = pdf.pages[:10]
            text = "\n\n".join(p.extract_text() or "" for p in pages)
        return text[:4000]
    except Exception as exc:
        logging.warning("Could not parse PDF: %s", exc)
        return f"[PDF could not be parsed: {exc}]"


# ---------------------------------------------------------------------------
# Claude prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert B2B SaaS growth strategist and positioning consultant.
Your job is to analyse a startup and produce a complete
"Prove PMF with Marketing" framework — the same strategic document
that a senior fractional CMO would hand to a seed-stage founder.

You will receive:
  • Company name and one-line description
  • Website content (scraped)
  • Founder context: stage, ICP, biggest marketing challenge
  • Optional pitch deck text

Produce the framework as **valid JSON only** — no markdown fencing,
no commentary outside the JSON object — using this exact schema:

{
  "company_name": "string",
  "positioning": {
    "product_description": "string — one tight sentence",
    "market_category": "string — category + subcategory",
    "market_frame": "string — ownable framing tagline",
    "competitive_alternatives": ["string", ...],
    "unique_attributes": ["string", ...],
    "value": "string — what those attributes actually get the customer",
    "who_cares": "string — the precise buyer segment",
    "trends": ["string", "string", "string"]
  },
  "positioning_gap": "string — the single most important gap/opportunity",
  "buyer_journey": [
    {
      "stage": "Problem Aware",
      "description": "string",
      "what_they_do": "string",
      "what_we_can_see": "string",
      "marketing_impact": "string"
    },
    { "stage": "\\"You\\" Aware", ... },
    { "stage": "Interested", ... },
    { "stage": "Acting", ... }
  ],
  "campaigns": [
    {
      "id": "A",
      "name": "string",
      "segment": "string",
      "message": "string",
      "channel_mix": "string",
      "rationale": "string"
    }
  ],
  "rice": [
    {
      "id": "A",
      "description": "string",
      "reach": 7,
      "impact": 2,
      "confidence": 6,
      "effort": 3,
      "score": 28.0
    }
  ],
  "measurement": {
    "growth_kpis": [
      {
        "metric": "string",
        "target": "string — recommended target for THIS company",
        "benchmark": "string — industry range"
      }
    ],
    "channel_benchmarks": [
      {
        "channel": "string",
        "metric": "string",
        "benchmark": "string",
        "context": "string"
      }
    ]
  }
}

Rules:
- Be specific to the company — do not use generic filler.
- Competitive alternatives = what the buyer actually uses today, not ideal-world alternatives.
- Campaign premises must be genuinely testable with a lean team in 30–60 days.
- RICE scores: Reach 1-10 (relative ICP reach); Impact: 0.25/0.5/1/2/3;
  Confidence 1-10; Effort 1-5. Score = R×I×C÷E rounded to 1 decimal.
- Output ONLY the JSON object. Do not wrap it in markdown code blocks.
"""


def build_user_message(form: dict, website: str, deck: str) -> str:
    return f"""\
COMPANY INFORMATION
Product name      : {form.get("product_name", "").strip()}
One-line desc     : {form.get("description", "").strip()}
Website URL       : {form.get("website_url", "").strip()}

FOUNDER CONTEXT
Stage             : {form.get("stage", "").strip()}
ICP               : {form.get("icp", "").strip()}
Biggest challenge : {form.get("challenge", "").strip()}

WEBSITE CONTENT
{website or "(not provided)"}

PITCH DECK / ADDITIONAL CONTEXT
{deck or "(not provided)"}

Generate the complete PMF Marketing framework for this company.
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    api_key = (request.form.get("api_key") or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"error": "No Anthropic API key provided. Add it in the form or set ANTHROPIC_API_KEY."}), 400

    form = request.form.to_dict()

    website_content = ""
    if form.get("website_url"):
        app.logger.info("Fetching website: %s", form["website_url"])
        website_content = fetch_website_content(form["website_url"])

    deck_content = ""
    deck_file = request.files.get("deck_file")
    if deck_file and deck_file.filename:
        app.logger.info("Parsing pitch deck: %s", deck_file.filename)
        deck_content = extract_pdf_text(deck_file.read())

    user_message = build_user_message(form, website_content, deck_content)

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0].strip()

        result = json.loads(raw)
        return jsonify({"success": True, "data": result})

    except json.JSONDecodeError as exc:
        app.logger.error("JSON parse error: %s\nRaw: %s", exc, raw[:500])
        return jsonify({"error": f"AI returned malformed JSON: {exc}", "raw": raw[:1000]}), 500
    except Exception as exc:
        app.logger.error("Analysis error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
