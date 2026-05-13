# trusted-brand-demand

> **How to prove product-market fit (and grow faster) with marketing.**

A web app for B2B SaaS founders. Drop in your website URL, answer three quick questions, and get back a complete go-to-market framework — generated in ~20 seconds by Claude AI.

---

## What it produces

| Section | What you get |
|---|---|
| **Positioning check** | April Dunford's framework applied to your product: competitive alternatives, unique attributes, the value they create, who cares, and the ownable market frame |
| **Positioning gap** | The single most important thing your messaging is missing |
| **Marketing impact map** | Buyer journey × marketing actions across four stages: Problem Aware → "You" Aware → Interested → Acting |
| **5 campaign premises** | Testable hypotheses pairing a segment, a message, and a channel mix — designed to run simultaneously |
| **RICE prioritisation** | Reach × Impact × Confidence ÷ Effort scores so you know which bet to place first |
| **Measurement guardrails** | Growth KPIs and B2B SaaS channel benchmarks calibrated to your stage |
| **Markdown export** | Download the full framework as a clean `.md` file to share with your team |

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/nickwassenberg/trusted-brand-demand.git
cd trusted-brand-demand
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add your Anthropic API key

```bash
cp .env.example .env
# Edit .env and paste your key — or enter it directly in the UI
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

---

## How it works

```
Founder inputs              Flask backend                  Claude API
─────────────────────       ──────────────────────         ──────────────────────
Website URL         ──────► Scrape homepage (BS4)  ──────► claude-sonnet-4-6
Company description          Clean text (≤3 000 ch)        System prompt encodes
Stage / ICP                  Parse PDF if uploaded          April Dunford framing,
Marketing challenge          Build context message          buyer journey model,
Optional pitch deck                                         RICE scoring logic
                    ◄─────── Structured JSON ◄──────────── Structured JSON output
                             Render in Alpine.js UI
```

The prompt instructs Claude to return **only** a structured JSON object covering all five framework sections. The frontend renders it into a polished report and allows Markdown export.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python / Flask | Lightweight, no boilerplate |
| AI | Anthropic Claude (`claude-sonnet-4-6`) | Best-in-class reasoning for strategic analysis |
| Frontend | Alpine.js + Tailwind CSS (CDN) | No build step, reactive, clean |
| Web scraping | requests + BeautifulSoup | Reliable, simple |
| PDF parsing | pdfplumber | Accurate text extraction from pitch decks |

---

## Project structure

```
trusted-brand-demand/
├── app.py                  # Flask app — routes, scraping, PDF parsing, Claude call
├── templates/
│   └── index.html          # Single-page UI (Alpine.js, Tailwind CDN)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Methodology

**April Dunford's positioning methodology** ([*Obviously Awesome*](https://www.aprildunford.com/obviously-awesome))
Positions a product by working backwards from competitive alternatives → unique attributes → value → who cares. Forces you to describe what you do in terms of the buyer's existing mental model, not your own.

**The buyer journey as a marketing impact map**
Separates buyers into four stages based on awareness. Each stage has different information needs, observable signals, and appropriate marketing interventions. Aligns spend with where buyers actually are, not where you want them to be.

**RICE prioritisation** ([Intercom](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/))
Reach × Impact × Confidence ÷ Effort. Forces explicit scoring of intuitive trade-offs and gives a clear rationale for which campaigns to run first.

---

## Limitations

- Analysis is grounded in publicly available information and your inputs. It does not replace customer interviews.
- Website scraping may be blocked by some sites — the tool degrades gracefully if the fetch fails.
- RICE scores are AI estimates — treat them as a starting framework, not ground truth.

---

## License

MIT
