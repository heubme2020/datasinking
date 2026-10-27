"""
Community example: score DataSinking reports for AI-generated text using
`finbert-ai-detector` by Marcelo Perlin.

This is a *community integration* — it combines two independent tools. It is
not part of the core DataSinking product, and `finbert-ai-detector` is
maintained by its own author.

Dependencies
------------
    pip install datasinking finbert-ai-detector

`finbert-ai-detector` pulls in torch + transformers and downloads the
Hugging Face model `msperlin/finbert-ai-detector` on first use (several
hundred MB).

What it does
------------
Pulls a company's latest annual report from DataSinking, takes one section
(the MD&A), chops it into pieces that fit the model's 512-token input limit,
and scores each piece for the probability that it was AI-written.
"""
from datasinking import DataSinking
from finbert_ai_detector import FinbertAIDetector

API_KEY = "YOUR_KEY"
SYMBOL = "600519.SS"      # Kweichow Moutai
SECTION = "MD&A"          # fuzzy section match; None = whole report

# finbert-ai-detector caps each input at 512 tokens. A conservative character
# estimate (~1 char/token for CJK, ~4 chars/token for Latin) keeps us under it.
CHUNK_CHARS = 400


def chunk(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)]


def main():
    ds = DataSinking(API_KEY)
    detector = FinbertAIDetector()          # auto-selects cuda/cpu, downloads model once

    reports = ds.get_stock_reports(SYMBOL, doc_type="annual", limit=1)
    if not reports:
        raise SystemExit(f"no annual reports found for {SYMBOL}")

    doc = reports[0]
    if SECTION:
        section = ds.get_section(doc["id"], SECTION)
        text = section.get("content", "") or doc.get("content", "")
    else:
        text = doc.get("content", "")

    pieces = chunk(text, CHUNK_CHARS)
    if not pieces:
        raise SystemExit("empty section")

    results = detector.predict_batch(pieces)
    avg_ai = sum(r["ai_probability"] for r in results) / len(results)

    print(f"{SYMBOL} — {doc['title']}")
    print(f"section: {SECTION or 'full report'}  pieces: {len(pieces)}")
    print(f"average AI probability: {avg_ai:.3f}")
    print()
    for r in results[:5]:
        print(f"  [{r['label']:>13}] ai={r['ai_probability']:.3f}  {r['text'][:50]!r}")


if __name__ == "__main__":
    main()
