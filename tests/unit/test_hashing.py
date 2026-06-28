"""US4: variable_hash hashes names, not values (T032)."""

from __future__ import annotations

from tokenhelm_prompt.lib import hashing


def test_variable_names_extracted_and_sorted():
    assert hashing.variable_names("Hi {b} and {a} and {a}") == ["a", "b"]


def test_variable_hash_independent_of_values():
    # Same variable NAMES, different values → identical hash.
    h1 = hashing.variable_hash_from_template("Pay {amount} to {payee}")
    h2 = hashing.variable_hash(["payee", "amount"])
    assert h1 == h2


def test_variable_hash_changes_when_names_change():
    h1 = hashing.variable_hash_from_template("Pay {amount}")
    h2 = hashing.variable_hash_from_template("Pay {total}")
    assert h1 != h2


def test_template_hash_is_sha256_hex():
    digest = hashing.template_hash("hello")
    assert len(digest) == 64
    assert digest == hashing.template_hash("hello")


def test_template_hash_changes_with_content():
    assert hashing.template_hash("a") != hashing.template_hash("b")
