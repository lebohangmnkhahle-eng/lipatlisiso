# rules.py - Basic Orthographic Transformation Rules

import re
from typing import Tuple, List

class SesothoRuleBasedNormalizer:
    """
    Basic rule-based normalizer for SA -> Lesotho Sesotho
    Implements 5 fundamental transformation rules
    """

    def __init__(self):
        self.rules = [
            self.rule_1_copulative_ke_a,
            self.rule_2_copulative_o_a,
            self.rule_3_noun_prefix_dijo,
            self.rule_4_consonant_ngwana,
            self.rule_5_possessive_ya_hao,
        ]
        self.transformation_log = []

    def rule_1_copulative_ke_a(self, text: str) -> Tuple[str, bool]:
        """
        Rule 1: Copulative consolidation "Ke a" -> "Kea"

        Pattern: Subject pronoun "Ke" + auxiliary "a" + verb
        Example: "Ke a sebetsa" -> "Kea sebetsa" (I am working)

        Linguistic note: This is the progressive/continuous marker
        """
        pattern = r'\bKe\s+a\s+'
        replacement = 'Kea '

        new_text = re.sub(pattern, replacement, text)
        changed = (new_text != text)

        if changed:
            self.transformation_log.append({
                'rule': 'copulative_ke_a',
                'pattern': 'Ke a',
                'replacement': 'Kea'
            })

        return new_text, changed

    def rule_2_copulative_o_a(self, text: str) -> Tuple[str, bool]:
        """
        Rule 2: Copulative consolidation "o a" -> "oa"

        Pattern: Subject concord "o" + auxiliary "a" + verb
        Example: "o a bapala" -> "oa bapala" (he/she plays)

        Note: Lowercase only to avoid false positives at sentence start
        """
        pattern = r'\bo\s+a\s+'
        replacement = 'oa '

        new_text = re.sub(pattern, replacement, text)
        changed = (new_text != text)

        if changed:
            self.transformation_log.append({
                'rule': 'copulative_o_a',
                'pattern': 'o a',
                'replacement': 'oa'
            })

        return new_text, changed

    def rule_3_noun_prefix_dijo(self, text: str) -> Tuple[str, bool]:
        """
        Rule 3: Noun class prefix "dijo" -> "lijo"

        Pattern: Class 5/6 plural prefix di- -> li-
        Example: "dijo" -> "lijo" (food items)

        Note: Starting with specific common word to avoid overgeneralization
        """
        # Specific words first (safer)
        words = {
            'dijo': 'lijo',      # food
            'diphoofolo': 'liphoofolo',  # animals
            'dibuka': 'libuka',  # books
        }

        new_text = text
        changed = False

        for sa_word, les_word in words.items():
            pattern = r'\b' + sa_word + r'\b'
            if re.search(pattern, new_text):
                new_text = re.sub(pattern, les_word, new_text)
                changed = True
                self.transformation_log.append({
                    'rule': 'noun_prefix_di_li',
                    'pattern': sa_word,
                    'replacement': les_word
                })

        return new_text, changed

    def rule_4_consonant_ngwana(self, text: str) -> Tuple[str, bool]:
        """
        Rule 4: Consonant cluster "ngwana" -> "ngoana"

        Pattern: ngw- -> ngo- (nasal + glide + vowel sequence)
        Example: "ngwana" -> "ngoana" (child)

        Common in: ngwana (child), ngwaneso (our child)
        """
        transformations = {
            'ngwana': 'ngoana',
            'ngwaneso': 'ngoaneso',
            'ngwanaka': 'ngoanaka',
        }

        new_text = text
        changed = False

        for sa_form, les_form in transformations.items():
            pattern = r'\b' + sa_form + r'\b'
            if re.search(pattern, new_text):
                new_text = re.sub(pattern, les_form, new_text)
                changed = True
                self.transformation_log.append({
                    'rule': 'consonant_ngw_ngo',
                    'pattern': sa_form,
                    'replacement': les_form
                })

        return new_text, changed

    def rule_5_possessive_ya_hao(self, text: str) -> Tuple[str, bool]:
        """
        Rule 5: Possessive marker "ya hao" -> "ea hao"

        Pattern: Possessive concord "ya" -> "ea"
        Example: "ya hao" -> "ea hao" (your/yours)

        Note: Context-dependent (noun class agreement),
        starting with common possessives
        """
        possessives = [
            ('ya hao', 'ea hao'),   # your (singular)
            ('ya rona', 'ea rona'), # our
            ('ya bona', 'ea bona'), # their
        ]

        new_text = text
        changed = False

        for sa_poss, les_poss in possessives:
            if sa_poss in new_text:
                new_text = new_text.replace(sa_poss, les_poss)
                changed = True
                self.transformation_log.append({
                    'rule': 'possessive_ya_ea',
                    'pattern': sa_poss,
                    'replacement': les_poss
                })

        return new_text, changed

    def normalize(self, text: str) -> Tuple[str, List[dict]]:
        """
        Apply all transformation rules in sequence

        Args:
            text: SA Sesotho input text

        Returns:
            normalized_text: Lesotho Sesotho output
            log: List of transformations applied
        """
        self.transformation_log = []
        normalized = text

        # Apply each rule
        for rule_func in self.rules:
            normalized, changed = rule_func(normalized)

        return normalized, self.transformation_log

    def get_statistics(self):
        """Get statistics on rule applications"""
        from collections import Counter

        rule_counts = Counter(log['rule'] for log in self.transformation_log)
        return dict(rule_counts)

# Test the normalizer
if __name__ == "__main__":
    normalizer = SesothoRuleBasedNormalizer()

    # Test cases
    test_sentences = [
        "Ke a sebetsa kajeno",
        "Ngwana o a bapala ka ntle",
        "Dijo di monate haholo",
        "Ke a rata dijo tsa hao",
        "Ba a kena sekolong",
    ]

    print("="*60)
    print("SESOTHO RULE-BASED NORMALIZER - TEST RESULTS")
    print("="*60)

    for i, sentence in enumerate(test_sentences, 1):
        normalized, log = normalizer.normalize(sentence)

        print(f"\n{i}. SA Sesotho:  {sentence}")
        print(f"   Lesotho:     {normalized}")

        if log:
            print(f"   Rules applied: {len(log)}")
            for entry in log:
                print(f"     - {entry['rule']}: '{entry['pattern']}' -> '{entry['replacement']}'")
        else:
            print(f"   Rules applied: None (no changes needed)")

    print("\n" + "="*60)
    print("✅ Rule-based normalizer implemented successfully!")
    print("="*60)
