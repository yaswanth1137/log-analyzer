from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.preprocessor import clean_log_text

# Structural training anchors: Explicit definitions of what a class vector contains semantically.
FAILURE_TAXONOMY = {
    "FLAKY_INFRASTRUCTURE": (
        "network timeout socket connection refused reset by peer retry connection drop "
        "database connection dropped transient network error connection timed out internal error runner crashed"
    ),
    "SOURCE_CODE_BUG": (
        "syntaxerror indentationerror indexerror zero-division unexpected token nullpointerexception "
        "assertionerror check failed expected true got false referenceerror typeerror variable undefined"
    ),
    "DEPENDENCY_MISMATCH": (
        "modulenotfounderror no module named pip package install failure requirements conflict "
        "mismatched versions build target missing poetry lock out of sync dependency resolution failed"
    )
}

def analyze_log_payload(raw_unstructured_log: str) -> dict:
    """
    Parses unmapped workflow runs by computing semantic document distances against known failure taxonomies.
    """
    # 1. Ingest log into cleaning pipeline
    cleaned_target = clean_log_text(raw_unstructured_log)
    
    if not cleaned_target:
        return {
            "verdict": "UNCLASSIFIED",
            "confidence": 0.0,
            "insights": "No executable error logs or tracebacks could be structurally isolated from this build run."
        }
        
    # 2. Build corpus index for Vector space mapping
    categories = list(FAILURE_TAXONOMY.keys())
    corpus = list(FAILURE_TAXONOMY.values()) + [cleaned_target]
    
    # 3. Extract term weights utilizing a TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # 4. Measure Cosine Distance between our target vector (last item) and reference profiles
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    
    best_fit_index = similarities.argmax()
    confidence_score = similarities[best_fit_index]
    
    # Dynamic lower threshold to handle complete wildcards or edge cases cleanly
    if confidence_score < 0.12:
        return {
            "verdict": "UNKNOWN_ANOMALY",
            "confidence": round(float(confidence_score), 2),
            "insights": "Anomalous failure caught, but does not fit standard historical error profiles. Manual review advised."
        }
        
    predicted_verdict = categories[best_fit_index]
    
    verdict_metadata = {
        "FLAKY_INFRASTRUCTURE": {
            "insights": "Transient execution fluke detected. The crash stems from temporary ecosystem timeouts or socket breaks.",
            "actionable_tip": "This build signature points to infrastructure flakiness. Try triggering a clean re-run of this pipeline."
        },
        "SOURCE_CODE_BUG": {
            "insights": "Defective logic frame caught. The system isolated a programmatic exception directly within the application layer.",
            "actionable_tip": "Check the runtime stack traces posted on your branch review board to debug code parameters."
        },
        "DEPENDENCY_MISMATCH": {
            "insights": "Package matrix mismatch. The container engine failed during environment lock initialization or module discovery.",
            "actionable_tip": "Verify package config declarations (e.g., requirements.txt, package.json) for version lock drifts."
        }
    }
    
    return {
        "verdict": predicted_verdict,
        "confidence": round(float(confidence_score), 2),
        "insights": verdict_metadata[predicted_verdict]["insights"],
        "actionable_tip": verdict_metadata[predicted_verdict]["actionable_tip"]
    }