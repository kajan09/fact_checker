from typing import Dict, Any

threshold=0.35
def statement_to_score(data: Dict[str, Any]) -> Dict[str, Any]:
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