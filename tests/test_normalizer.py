import unittest
from rule_based_normalizer import SesothoRuleBasedNormalizer

class TestSesothoRuleBasedNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = SesothoRuleBasedNormalizer()

    def test_rule_1_copulative_ke_a(self):
        text = "Ke a bona"
        normalized_text, _ = self.normalizer.rule_1_copulative_ke_a(text)
        self.assertEqual(normalized_text, "Kea bona")

    def test_rule_2_copulative_o_a(self):
        text = "O a tsamaya"
        normalized_text, _ = self.normalizer.rule_2_copulative_o_a(text)
        self.assertEqual(normalized_text, "Oa tsamaya")

    def test_rule_3_noun_prefix_di_li(self):
        text = "dijo tse monate"
        normalized_text, _ = self.normalizer.rule_3_noun_prefix_di_li(text)
        self.assertEqual(normalized_text, "lijo tse monate")

    def test_rule_4_consonant_ngw_ngo(self):
        text = "ngwana o a lla"
        normalized_text, _ = self.normalizer.rule_4_consonant_ngw_ngo(text)
        self.assertEqual(normalized_text, "ngoana o a lla")

    def test_rule_5_possessive_ya_ea(self):
        text = "koloi ya hao"
        normalized_text, _ = self.normalizer.rule_5_possessive_ya_ea(text)
        self.assertEqual(normalized_text, "koloi ea hao")

    def test_normalization_pipeline(self):
        text = "Ke a ja dijo le ngwana ya hao"
        normalized_text, _ = self.normalizer.normalize(text)
        self.assertEqual(normalized_text, "Kea ja lijo le ngoana ea hao")

if __name__ == '__main__':
    unittest.main()
