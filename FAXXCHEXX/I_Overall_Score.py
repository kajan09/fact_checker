# ——— your_data.py ———

# 1) Paste the JSON here as a Python dict literal:
data = {
    "transcript": "Smoking gives you cancer. Doing sport is super unhealthy. Sleeping well lets you die early.",
    "statements": [
        {
            "id": 1,
            "text": "Smoking gives you cancer",
            "verdict": "true",
            "rationale": "VERDICT: true\nFINALSCORE: 0.95",
            "confidence": 0.95,
            "query": "smoking cancer etiology neoplasm",
            "evidence": [
                {
                    "pubmed_id": "40375086",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/40375086/",
                    "summary": "This study investigated the cost-effectiveness of low-dose CT (LDCT) screening for lung cancer in non-smokers with a first-degree relative (FDR) history of the disease. ...",
                    "relevance": ""
                },
                {
                    "pubmed_id": "40372792",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/40372792/",
                    "summary": "This study analyzed data from two national surveys (NHIS & BRFSS) to examine breast cancer screening ...",
                    "relevance": ""
                },
                {
                    "pubmed_id": "40367394",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/40367394/",
                    "summary": "## Global Rise in Early-Onset Pancreatic Cancer: Key Results ...",
                    "relevance": ""
                }
            ]
        },
        {
            "id": 2,
            "text": "Doing sport is super unhealthy",
            "verdict": "uncertain",
            "rationale": "VERDICT: uncertain\nFINALSCORE: 0.05",
            "confidence": 0.05,
            "query": "exercise health risks adverse",
            "evidence": []
        },
        {
            "id": 3,
            "text": "Sleeping well lets you die early.",
            "verdict": "uncertain",
            "rationale": "VERDICT: uncertain\nFINALSCORE: 0.05",
            "confidence": 0.05,
            "query": "sleep mortality aging paradox",
            "evidence": []
        }
    ],
    "overall_truthiness": None,
    "generated_at": "2025-05-16T20:27:25Z"
}

# 2) Then define your function below:
def I_Overall_Score(data, threshold=0.35):
    """
    Computes the weighted average of statement confidences,
    giving triple weight to values below the threshold.
    Updates the data dict in-place by setting 'overall_truthiness'.
    """
    confidences = [stmt["confidence"] for stmt in data["statements"]]
    weights = [3 if conf < threshold else 1 for conf in confidences]
    
    weighted_sum = sum(conf * w for conf, w in zip(confidences, weights))
    total_weight = sum(weights)
    overall = weighted_sum / total_weight if total_weight else 0
    
    data["overall_truthiness"] = overall
    return data

output = I_Overall_Score(data)
print(output)
