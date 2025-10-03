import re
PAT = re.compile(r"(password|token|api key|exfiltrate|bypass)", re.I)
def suspicious_score(text: str) -> float:
    return 1.0 if PAT.search(text) else 0.0
