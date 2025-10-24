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

def test_possessive_ya_hao_capitalized(normalizer):
    out, log = normalizer.normalize("Ke ya hao")
    assert out == "Ke ea hao"
    assert any(entry['rule'] == 'possessive_ya_ea' for entry in log)

def test_no_midword_change(normalizer):
    s = "nodiyahoX"
    out, log = normalizer.normalize(s)
    assert out == s
    assert all(entry['rule'] != 'possessive_ya_ea' for entry in log)

def test_noun_prefix_specific_words(normalizer):
    out, log = normalizer.normalize("Dijo di monate haholo")
    # Expect Dijo -> Lijo and standalone di -> li
    assert out == "Lijo li monate haholo"
    assert any('noun_prefix_di_li' in entry['rule'] for entry in log)

def test_noun_prefix_generic(normalizer):
    out, log = normalizer.normalize("Diphoofolo di a tsamaea")
    assert out == "Liphoofolo li a tsamaea"
    assert any('noun_prefix_di_li' in entry['rule'] or 'noun_prefix_di_li_generic' in entry['rule'] for entry in log)

def test_ngwana_variants(normalizer):
    out, log = normalizer.normalize("Ngwana o a bapala")
    assert out == "Ngoana oa bapala"
    assert any(entry['rule'] == 'consonant_ngw_ngo' for entry in log)

def test_ngwaneso_lower(normalizer):
    out, log = normalizer.normalize("ngwaneso ke nama ya rona")
    assert out == "ngoaneso ke nama ea rona"
    assert any(entry['rule'] == 'consonant_ngw_ngo' for entry in log)
