import requests

# Step 1: Search for article IDs
query = "Vaccines Children good health"
search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "pubmed",
    "term": query,
    "retmax": 5,
    "retmode": "json"
}
search_response = requests.get(search_url, params=params)
id_list = search_response.json()["esearchresult"]["idlist"]

# Step 2: Build article URLs
article_links = [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" for pmid in id_list]

print(article_links)
