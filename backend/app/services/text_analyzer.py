"""
Lightweight sentiment analysis that maps text → emotion score in [-1, 1].

Priority:
- Try a HuggingFace transformers pipeline (BERT/Roberta)。
- If transformers/model unavailable, gracefully fall back to a random score
  to avoid breaking the app during local testing.

Score mapping rule:
- If model provides class probabilities, map to [-1, 1] via: score = P(pos) - P(neg).
- When only a label+score is available, use score for the predicted label
  and infer the opposite as (1 - score).
"""

from typing import Optional, List, Dict

_pipeline = None  # lazy-initialized HF pipeline


def _load_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    try:
        # Import locally to avoid hard dependency if user didn't install it
        from transformers import pipeline  # type: ignore
        # A commonly used Chinese sentiment model (binary):
        #   uer/roberta-base-finetuned-jd-binary-chinese
        # This can be replaced by any compatible model.
        _pipeline = pipeline(
            "sentiment-analysis",
            model="uer/roberta-base-finetuned-jd-binary-chinese",
        )
    except Exception:
        _pipeline = None
    return _pipeline


def _extract_pos_neg_probs(outputs: List[Dict]) -> Optional[float]:
    """Given a list of label-score dicts, compute P(pos) - P(neg).
    Returns a float in [-1, 1] or None if cannot parse.
    """
    if not outputs:
        return None

    # Normalize labels to lowercase for matching
    pos_labels = {"pos", "positive", "label_1", "1"}
    neg_labels = {"neg", "negative", "label_0", "0"}

    p_pos = None
    p_neg = None
    for item in outputs:
        label = str(item.get("label", "")).lower()
        score = float(item.get("score", 0.0))
        if any(pl in label for pl in pos_labels):
            p_pos = score
        if any(nl in label for nl in neg_labels):
            p_neg = score

    # If model returns only one score with a single label (binary), infer the other side
    if p_pos is None and p_neg is None and len(outputs) == 1:
        label = str(outputs[0].get("label", "")).lower()
        score = float(outputs[0].get("score", 0.0))
        if any(pl in label for pl in pos_labels):
            p_pos, p_neg = score, 1.0 - score
        elif any(nl in label for nl in neg_labels):
            p_neg, p_pos = score, 1.0 - score

    if p_pos is None or p_neg is None:
        return None

    val = p_pos - p_neg
    # Ensure numerical safety and clamp to [-1, 1]
    return max(-1.0, min(1.0, float(val)))


def analyze_emotion(text: str) -> float:
    """
    Analyze sentiment and map to [-1, 1].
    -1: strong negative, 0: neutral, +1: strong positive
    """
    text = (text or "").strip()
    if not text:
        return 0

    nlp = _load_pipeline()
    if nlp is None:
        # Fallback for environments without transformers or network access
        return 0

    try:
        # Try to retrieve full probability distribution if supported
        results = nlp(text, return_all_scores=True)  # type: ignore
        # HF returns a list (batch) of lists (labels)
        if isinstance(results, list) and results and isinstance(results[0], list):
            score = _extract_pos_neg_probs(results[0])
            if score is not None:
                return score

        # Fallback: standard sentiment-analysis output {'label': 'POSITIVE', 'score': 0.99}
        single = nlp(text)  # type: ignore
        if isinstance(single, list) and single:
            out = single[0]
            mapped = _extract_pos_neg_probs([out])
            if mapped is not None:
                return mapped
    except Exception:
        # Any runtime failure should not break the app; fall back
        pass

    return 0
