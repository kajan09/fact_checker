#!/usr/bin/env python3
"""
ask_llm.py – Interact with STACKIT Model Serving chat models.

Two modes of operation:

1. **Ask a question** (original behaviour)
   ```bash
   python ask_llm.py "What is STACKIT?"
   python ask_llm.py -m gpt-4o-mini -s "You are a helpful assistant." "How do I deploy a Django app on STACKIT?"
   ```

2. **PubMed summariser** – supply a PubMed search query and get two‑sentence summaries
   ```bash
   python ask_llm.py -q "Vaccines Children good health" -n 5
   ```
   The script will:
   • search PubMed, fetch the top *N* abstracts,
   • ask the model to summarise each abstract in **exactly two sentences**, and
   • print the summary followed by the article’s PubMed URL.

Environment variables (typically in a project‑root .env):

    STACKIT_MODEL_SERVING_MODEL      # e.g. "gpt-4o-mini"
    STACKIT_MODEL_SERVING_BASE_URL   # e.g. "https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1"
    STACKIT_MODEL_SERVING_AUTH_TOKEN # Bearer token like "ey..."

Dependencies:
    pip install openai python-dotenv requests
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from typing import Iterable, List, Tuple

import requests
from dotenv import load_dotenv

# Prefer OpenAI SDK >= 1.0, but fall back gracefully.
try:
    from openai import OpenAI  # type: ignore

    _OPENAI_V1 = True
except ImportError:  # pragma: no cover
    import openai  # type: ignore

    _OPENAI_V1 = False


# -----------------------------------------------------------------------------
# PubMed helpers
# -----------------------------------------------------------------------------

NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def pubmed_search_ids(query: str, retmax: int = 5) -> List[str]:
    """Return a list of PubMed IDs (PMIDs) for *query*."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
    }
    r = requests.get(f"{NCBI_EUTILS}/esearch.fcgi", params=params, timeout=20)
    r.raise_for_status()
    return r.json()["esearchresult"].get("idlist", [])


def pubmed_fetch_abstract(pmid: str) -> str | None:
    """Return the abstract text for *pmid* or *None* if not available."""
    params = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "abstract",
        "retmode": "text",
    }
    r = requests.get(f"{NCBI_EUTILS}/efetch.fcgi", params=params, timeout=20)
    r.raise_for_status()
    text = r.text.strip()
    # PubMed returns descriptive headers; abstract usually starts after a blank line.
    parts = [p.strip() for p in text.splitlines() if p.strip()]
    # Heuristic: drop header lines (uppercase) until we hit mixed‑case sentences.
    abstract_lines = []
    for line in parts:
        if line.isupper():
            continue
        abstract_lines.append(line)
    if not abstract_lines:
        return None
    return " ".join(abstract_lines)


def collect_pubmed_abstracts(query: str, n: int) -> List[Tuple[str, str]]:
    """Return a list of (link, abstract) pairs for *query*."""
    pmids = pubmed_search_ids(query, n)
    pairs: List[Tuple[str, str]] = []
    for pmid in pmids:
        abs_txt = pubmed_fetch_abstract(pmid)
        if abs_txt:
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            pairs.append((link, abs_txt))
    return pairs


# -----------------------------------------------------------------------------
# Model helpers
# -----------------------------------------------------------------------------


def get_client(api_key: str, base_url: str):  # pragma: no cover
    if _OPENAI_V1:
        return OpenAI(api_key=api_key, base_url=base_url)
    else:
        openai.api_key = api_key  # type: ignore[misc]
        if hasattr(openai, "api_base"):
            openai.api_base = base_url  # type: ignore[attr-defined]
        else:
            openai.base_url = base_url  # type: ignore[attr-defined]
        return openai


def ask_model(
    client,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
) -> str:
    """Return the assistant reply as plain text, regardless of SDK version."""
    if _OPENAI_V1:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    else:
        resp = client.ChatCompletion.create(  # type: ignore[attr-defined]
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.strip()},
            ],
            temperature=temperature,
        )
        return resp["choices"][0]["message"]["content"].strip()


# -----------------------------------------------------------------------------
# CLI entry point
# -----------------------------------------------------------------------------

def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="ask_llm.py",
        description="Send a chat completion request to STACKIT Model Serving."\
            " Either ask a single question or summarise PubMed articles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              # Ask a question (default mode)
              python ask_llm.py "How does STACKIT billing work?"

              # Summarise the 3 most recent PubMed results for a query
              python ask_llm.py -q "mRNA vaccines efficacy" -n 3
            """,
        ),
    )

    # Mutually exclusive: question (positional) OR -q query.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("question", nargs="?", help="Your user question.")
    group.add_argument(
        "-q",
        "--query",
        help="PubMed search query. Activates summariser mode.",
    )

    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=5,
        help="Number of PubMed articles to summarise (default: 5).",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Override model ID from environment variable.",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--system",
        default="You are a helpful but concise assistant.",
        help="System prompt.",
    )
    parser.add_argument(
        "-e",
        "--env",
        default=".env",
        help="Path to .env (default: .env)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature (default: 0.3).",
    )

    args = parser.parse_args()

    # Load env vars early.
    load_dotenv(args.env)

    model = args.model or os.getenv("STACKIT_MODEL_SERVING_MODEL")
    base_url = os.getenv("STACKIT_MODEL_SERVING_BASE_URL")
    token = os.getenv("STACKIT_MODEL_SERVING_AUTH_TOKEN")

    missing = [name for name, val in (
        ("STACKIT_MODEL_SERVING_MODEL", model),
        ("STACKIT_MODEL_SERVING_BASE_URL", base_url),
        ("STACKIT_MODEL_SERVING_AUTH_TOKEN", token),
    ) if not val]
    if missing:
        sys.exit(
            f"❌ Missing required env vars: {', '.join(missing)}\n"
            "Create or update your .env file or export them in the shell."
        )

    # Prepare client
    client = get_client(token, base_url)  # type: ignore[arg-type]

    try:
        if args.query:  # PubMed summariser mode
            summaries = run_pubmed_summariser(
                client=client,
                model=model,
                query=args.query,
                n=args.num,
                system_prompt=args.system,
                temperature=args.temperature,
            )
            for summary, link in summaries:
                print(f"- {summary}\n  {link}\n")
        else:  # Single question mode
            answer = ask_model(
                client=client,
                model=model,
                system_prompt=args.system,
                user_prompt=args.question,  # type: ignore[arg-type]
                temperature=args.temperature,
            )
            print(answer)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as exc:
        sys.exit(f"❌ Request failed: {exc}")


# -----------------------------------------------------------------------------
# Summariser driver
# -----------------------------------------------------------------------------

def run_pubmed_summariser(
    *,
    client,
    model: str,
    query: str,
    n: int,
    system_prompt: str,
    temperature: float,
) -> List[Tuple[str, str]]:
    """Return list of (summary, link) for the top *n* PubMed articles."""
    pairs = collect_pubmed_abstracts(query, n)
    summaries: List[Tuple[str, str]] = []
    for link, abstract in pairs:
        user_prompt = (
            "Summarise the following medical abstract in *exactly* two sentences.\n"\
            "Make sure the summary is easy to understand for a general audience.\n\n"\
            f"Abstract:\n{abstract}"
        )
        answer = ask_model(
            client=client,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        # Ensure we have at most two sentences (fallback): take first two if model exceeds.
        sentences = answer.strip().split(".")
        summary = ".".join([s.strip() for s in sentences if s.strip()][:2])
        if not summary.endswith("."):
            summary += "."
        summaries.append((summary, link))
    return summaries


if __name__ == "__main__":  # pragma: no cover
    main()
