import pytest
from rule_based_normalizer import SesothoRuleBasedNormalizer

@pytest.fixture
def normalizer():
    return SesothoRuleBasedNormalizer()

def test_ke_a_capitalized(normalizer):
    out, log = normalizer.normalize("Ke a sebetsa kajeno")
    assert out == "Kea sebetsa kajeno"
    assert any(entry['rule'] == 'copulative_ke_a' for entry in log)

def test_ke_a_lowercase(normalizer):
    out, log = normalizer.normalize("ke a sebetsa kajeno")
    assert out == "kea sebetsa kajeno"
    assert any(entry['rule'] == 'copulative_ke_a' for entry in log)

def test_o_a_lowercase(normalizer):
    out, log = normalizer.normalize("o a bapala")
    assert out == "oa bapala"
    assert any(entry['rule'] == 'copulative_o_a' for entry in log)

def test_possessive_ya_hao_lowercase(normalizer):
    out, log = normalizer.normalize("ke ya hao")
    assert out == "ke ea hao"
    assert any(entry['rule'] == 'possessive_ya_ea' for entry in log)

def test_possessive_ya_hao_in_capitalized_sentence(normalizer):
    out, log = normalizer.normalize("Ke ya hao")
    # 'ya' is lowercase, so 'ea' should be too, regardless of sentence capitalization.
    assert out == "Ke ea hao"
    assert any(entry['rule'] == 'possessive_ya_ea' for entry in log)

def test_possessive_Ya_hao_capitalized(normalizer):
    out, log = normalizer.normalize("Ya hao ke yona")
    # 'Ya' is capitalized, so 'Ea' should be too.
    assert out == "Ea hao ke yona"
    assert any(entry['rule'] == 'possessive_ya_ea' for entry in log)

def test_no_midword_change(normalizer):
    # ensure substring inside a token is not replaced
    s = "nodiyahoX"
    out, log = normalizer.normalize(s)
    assert out == s
    assert all(entry['rule'] != 'possessive_ya_ea' for entry in log)
