"""Tests for concise model field signatures."""

from ontolutils import Thing
from ontolutils.typing import AnyIri


class SignatureModel(Thing):
    target: AnyIri
    count: int
    note: str | None = None


def test_model_signature_shows_declared_fields_and_defaults():
    assert SignatureModel.model_signature() == (
        "SignatureModel(target: AnyIri, count: int, note: str | None = None)"
    )


def test_model_signature_can_include_common_thing_fields():
    signature = SignatureModel.model_signature(include_inherited=True)

    assert signature.startswith("SignatureModel(\n")
    assert "    id: " in signature
    assert "    label: " in signature
    assert "target: AnyIri" in signature


def test_model_signature_wraps_long_signatures():
    signature = SignatureModel.model_signature(width=24)

    assert signature == (
        "SignatureModel(\n"
        "    target: AnyIri,\n"
        "    count: int,\n"
        "    note: str | None = None,\n"
        ")"
    )
