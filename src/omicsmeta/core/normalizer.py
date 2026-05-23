"""String normalization and domain abbreviation expansion."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


ABBREVIATIONS: dict[str, str] = {
    "aml": "acute myeloid leukemia",
    "brca": "breast cancer",
    "bc": "breast cancer",
    "crc": "colorectal cancer",
    "dcis": "ductal carcinoma in situ",
    "er+": "estrogen receptor positive",
    "er-": "estrogen receptor negative",
    "gbm": "glioblastoma",
    "hcc": "hepatocellular carcinoma",
    "her2+": "human epidermal growth factor receptor 2 positive",
    "her2-": "human epidermal growth factor receptor 2 negative",
    "ipf": "idiopathic pulmonary fibrosis",
    "luad": "lung adenocarcinoma",
    "lusc": "lung squamous cell carcinoma",
    "mdd": "major depressive disorder",
    "mm": "multiple myeloma",
    "ms": "multiple sclerosis",
    "nsclc": "non-small cell lung cancer",
    "pbmc": "peripheral blood mononuclear cell",
    "pr+": "progesterone receptor positive",
    "pr-": "progesterone receptor negative",
    "ra": "rheumatoid arthritis",
    "sclc": "small cell lung cancer",
    "tnbc": "triple negative breast cancer",
    "uc": "ulcerative colitis",
}

COMMON_TYPOS: dict[str, str] = {
    "adenocarcenoma": "adenocarcinoma",
    "caner": "cancer",
    "carcenoma": "carcinoma",
    "carinoma": "carcinoma",
    "leukaemia": "leukemia",
    "melanona": "melanoma",
    "neoplasmns": "neoplasms",
}

MULTI_VALUE_SPLIT_RE = re.compile(r"\s*(?:;|\||,|\band\b)\s*", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class NormalizedTerm:
    """A normalized term plus the original input span."""

    original: str
    normalized: str


def normalize_text(value: object, *, expand_abbreviations: bool = True) -> str:
    """Normalize one metadata value to a stable lowercase representation."""

    if value is None:
        return ""

    text = unicodedata.normalize("NFKC", str(value))
    text = text.strip().strip("\"'")
    if not text:
        return ""

    text = text.replace("_", " ")
    text = text.replace("/", " / ")
    text = WHITESPACE_RE.sub(" ", text)
    text = text.lower()

    for typo, correction in COMMON_TYPOS.items():
        text = re.sub(rf"\b{re.escape(typo)}\b", correction, text)

    if expand_abbreviations:
        text = expand_domain_abbreviations(text)

    text = WHITESPACE_RE.sub(" ", text)
    return text.strip(" ;,")


def expand_domain_abbreviations(text: str) -> str:
    """Expand common biomedical abbreviations using whole-token matching."""

    expanded = text
    for short, long in sorted(ABBREVIATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = rf"(?<![a-z0-9]){re.escape(short)}(?![a-z0-9])"
        expanded = re.sub(pattern, long, expanded, flags=re.IGNORECASE)
    return expanded


def split_terms(value: object) -> list[NormalizedTerm]:
    """Split a multi-value metadata cell into normalized term candidates."""

    if value is None:
        return []

    raw = unicodedata.normalize("NFKC", str(value)).strip()
    if not raw:
        return []

    terms: list[NormalizedTerm] = []
    for part in MULTI_VALUE_SPLIT_RE.split(raw):
        part = part.strip()
        if not part:
            continue
        normalized = normalize_text(part)
        if normalized:
            terms.append(NormalizedTerm(original=part, normalized=normalized))
    return terms
