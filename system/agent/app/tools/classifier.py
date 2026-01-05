import re
from typing import List, Tuple

from schemas.enums import Severity, LogCategory, SignalType
from schemas.classification import ClassificationResult
from schemas.log_ingest import LogEntry


def extract_keywords(text: str) -> List[str]:
    if not text:
        return []
    tokens = re.findall(r"[a-zA-Z_]+", text.lower())
    return list(set(tokens))

def classify_severity_and_category(
    message: str,
    level: str
) -> Tuple[Severity, LogCategory]:

    msg = (message or "").lower()
    lvl = level.upper()

    # Severity
    if "outofmemory" in msg or "panic" in msg:
        severity = Severity.CRITICAL
    elif lvl == "ERROR":
        severity = Severity.ERROR
    elif lvl == "WARN":
        severity = Severity.WARN
    else:
        severity = Severity.INFO

    # Category
    if any(x in msg for x in ["sql", "db", "connection pool"]):
        category = LogCategory.DATABASE
    elif any(x in msg for x in ["pod", "container", "kubernetes"]):
        category = LogCategory.INFRA
    elif any(x in msg for x in ["auth", "unauthorized", "token"]):
        category = LogCategory.SECURITY
    else:
        category = LogCategory.APPLICATION

    return severity, category

def determine_signal_type(severity: Severity) -> SignalType:
    if severity in {Severity.CRITICAL, Severity.ERROR}:
        return SignalType.FAILURE
    elif severity == Severity.WARN:
        return SignalType.DEGRADATION
    return SignalType.NOISE

def classify_log(log: LogEntry) -> ClassificationResult:
    text = f"{log.level} {log.message or ''}"
    keywords = extract_keywords(text)

    severity, category = classify_severity_and_category(
        message=log.message or "",
        level=log.level,
    )

    signal_type = determine_signal_type(severity)

    # Simple, explainable confidence heuristic
    confidence = min(0.9, 0.3 + 0.05 * len(keywords))

    return ClassificationResult(
        severity=severity,
        category=category,
        signal_type=signal_type,
        confidence=confidence,
        keywords=keywords[:10],
    )
