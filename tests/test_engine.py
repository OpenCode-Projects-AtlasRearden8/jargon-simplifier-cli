"""Tests for the offline rewrite engine."""

from jargon_simplifier.engine import Edit, rewrite_offline, split_long_sentences


def test_basic_swaps():
    result = rewrite_offline("We will commence the project.", tone="friend")
    assert result.plain == "We will start the project."
    terms = {e.term for e in result.edits}
    assert "commence" in terms
    assert result.source == "offline"


def test_case_is_preserved_when_swapping():
    result = rewrite_offline("Commence the project at once.")
    assert result.plain == "Start the project at once."


def test_stiff_opener_removed_all_breaking_terms_join_cleanly():
    result = rewrite_offline("Please be advised that the bill is due and owing.")
    assert result.plain.strip() == "The bill is still owed." or "," not in result.plain
    assert "please be advised that" not in result.plain.lower()


def test_no_jargon_means_no_edits():
    result = rewrite_offline("The cat sat on the mat.")
    assert result.plain == "The cat sat on the mat."
    assert result.edits == []


def test_legal_tone_keeps_term_in_parentheses_once():
    text = "Liability applies; liability ends after two years."
    result = rewrite_offline(text, tone="legal")
    assert "(liability)" in result.plain
    # Only the first use kept the original term.
    assert result.plain.count("(liability)") == 1
    assert "legal responsibility" in result.plain
    assert "legal responsibility (liability)" in result.plain.lower()


def test_medical_tone_keeps_medical_term_in_parentheses():
    result = rewrite_offline(
        "Take the tablet bid. The scan is benign.", tone="medical"
    )
    assert "(bid)" in result.plain
    assert "(benign)" in result.plain


def test_neutral_tone_does_not_add_parentheticals():
    result = rewrite_offline("The parties shall arbitrate.")
    assert "(shall)" not in result.plain


def test_grade6_splits_long_sentences():
    long_sentence = (
        "The vendor will ship the goods, and the buyer will accept delivery, "
        "and the buyer will inspect the goods, and payment will fall due "
        "thirty days after delivery, and late payment will incur penalties."
    )
    out = split_long_sentences(long_sentence)
    assert out != long_sentence
    for piece in out.split(". "):
        assert piece.strip(" .") == "" or len(piece.split()) <= 26

    # grade-8 does not split.
    assert rewrite_offline(long_sentence).plain == long_sentence


def test_invalid_tone_and_level_rejected():
    import pytest

    with pytest.raises(ValueError):
        rewrite_offline("x", tone="shouty")
    with pytest.raises(ValueError):
        rewrite_offline("x", reading_level="grade-2")


def test_glossary_edits_are_sorted_and_counted():
    text = "Utilize the form. Utilize it again. Pursuant to policy, stop."
    result = rewrite_offline(text)
    edit = next(e for e in result.edits if e.term == "utilize")
    assert edit.count == 2
    assert edit.plain == "use"
    assert [e.term.lower() for e in result.edits] == sorted(
        e.term.lower() for e in result.edits
    )


def test_removal_edit_reports_removed_marker():
    result = rewrite_offline("Please be advised that the bill is due.")
    edit = next(e for e in result.edits if e.term == "please be advised that")
    assert ["plain", "count", "definition"] and edit.count == 1
