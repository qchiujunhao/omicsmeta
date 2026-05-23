from omicsmeta.core.normalizer import normalize_text, split_terms


def test_normalize_text_expands_domain_abbreviations():
    assert normalize_text("NSCLC") == "non-small cell lung cancer"
    assert normalize_text("TNBC") == "triple negative breast cancer"


def test_normalize_text_fixes_common_typos():
    assert normalize_text("lung carcenoma") == "lung carcinoma"
    assert normalize_text("lung caner") == "lung cancer"


def test_split_terms_returns_original_and_normalized_terms():
    terms = split_terms("breast cancer, stage III; ER+")
    assert [term.original for term in terms] == ["breast cancer", "stage III", "ER+"]
    assert [term.normalized for term in terms] == [
        "breast cancer",
        "stage iii",
        "estrogen receptor positive",
    ]
