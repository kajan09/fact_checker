import argparse
import json
import requests
import subprocess
import sys
import re
from typing import Optional, List, Dict, Any
import datetime

# Base URL for NCBI E-utilities
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
# Regex to find PMID in PubMed URL
PUBMED_URL_RE = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?")
# Regex to remove trailing commas before } or ] in relaxed JSON
TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")


def extract_pmid(url: str) -> str:
    """Extract numeric PMID from a PubMed URL or accept raw PMIDs."""
    if url.isdigit():
        return url
    match = PUBMED_URL_RE.search(url)
    if match:
        return match.group(1)
    raise ValueError(f"Unable to extract PMID from URL: {url}")


def pubmed_fetch_abstract(pmid: str) -> Optional[str]:
    """Fetch abstract text for given PMID (returns None if none found)."""
    params = {"db": "pubmed", "id": pmid, "rettype": "abstract", "retmode": "text"}
    r = requests.get(f"{NCBI_EUTILS}/efetch.fcgi", params=params, timeout=20)
    r.raise_for_status()
    lines = [line.strip() for line in r.text.splitlines() if line.strip()]
    abstract = " ".join(line for line in lines if not line.isupper())
    return abstract or None


def summarize_with_gemma(text: str) -> str:
    """Use Ollama+Gemma3 to generate a concise summary."""
    prompt = (
        "Please provide a short summary of the following text that does not exceed 300 words and focuses on the results: \n\n" + text
    )
    proc = subprocess.run(
        ["ollama", "run", "gemma3:27b"],
        input=prompt,
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Ollama call failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def load_json_relaxed(path: str) -> Any:
    """Load JSON file, removing trailing commas to tolerate common mistakes."""
    raw = open(path, 'r', encoding='utf-8').read()
    cleaned = TRAILING_COMMAS_RE.sub('', raw)
    return json.loads(cleaned)


def process_file(input_path: str, output_path: str) -> None:
    try:
        data: Dict[str, Any] = load_json_relaxed(input_path)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine if evidence is nested or top-level
    statements = data.get('statements', [])
    # If top-level evidence list exists, process those as well
    top_evidence = data.get('evidence', [])

    def process_evidence_list(ev_list: List[Dict[str, Any]]):
        for ev in ev_list:
            url = ev.get('url')
            try:
                pmid = extract_pmid(url)
                ev['pubmed_id'] = pmid
                abstract = pubmed_fetch_abstract(pmid)
                ev['summary'] = summarize_with_gemma(abstract) if abstract else None
            except Exception as e:
                print(f"Warning: could not process evidence URL {url}: {e}", file=sys.stderr)
                ev.setdefault('pubmed_id', None)
                ev.setdefault('summary', None)

    # Process nested evidence under each statement
    for stmt in statements:
        ev_list = stmt.get('evidence', [])
        process_evidence_list(ev_list)

    # Process top-level evidence list if present
    if top_evidence:
        process_evidence_list(top_evidence)

    # Update generated timestamp
    data['generated_at'] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated JSON written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Enrich JSON with evidence items using PubMed and Gemma3 summaries.'
    )
    parser.add_argument('input_json', help='Path to input JSON file')
    parser.add_argument('output_json', help='Path to output JSON file')
    args = parser.parse_args()
    process_file(args.input_json, args.output_json)


if __name__ == '__main__':
    main()
