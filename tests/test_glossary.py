"""Integrity check for the built-in glossaries."""

from jargon_simplifier.glossary import GLOSSARY, LEGAL_TERMS, MEDICAL_TERMS, PHRASING_TERMS


def test_every_entry_is_term_plain_definition():
    for term, value in GLOSSARY.items():
        assert isinstance(term, str) and term.strip() == term and term
        assert isinstance(value, tuple) and len(value) == 2
        swap, definition = value
        assert isinstance(swap, str)
        assert isinstance(definition, str) and definition.strip()


def test_domain_sets_are_known_terms():
    for term in LEGAL_TERMS + MEDICAL_TERMS + PHRASING_TERMS:
        assert term in GLOSSARY, term


def test_no_term_rewrites_to_an_invented_fact():
    # Swaps must be short rewordings, never long invented boilerplate.
    for term, (swap, _) in GLOSSARY.items():
        assert len(swap.split()) <= len(term.split()) + 6
