# rule_based_normalizer.py

import re
from typing import Tuple, List

class SesothoRuleBasedNormalizer:
    """
    Basic rule-based normalizer for SA -> Lesotho Sesotho
    Implements a set of transformation rules. Replacements preserve capitalization.
    """

    def __init__(self):
        self.rules = [
            self.rule_1_copulative_ke_a,
            self.rule_2_copulative_o_a,
            self.rule_3_noun_prefix_dijo,
            self.rule_4_consonant_ngwana,
            self.rule_5_possessive_ya_ea,
        ]
        self.transformation_log: List[dict] = []

    # helper to preserve capitalization of replacement
    def _preserve_case_repl(self, replacement: str):
        def repl(match):
            matched_text = match.group(0)
            # If first char of the match is uppercase, capitalize replacement
            if matched_text and matched_text[0].isupper():
                return replacement[0].upper() + replacement[1:]
            else:
                return replacement
        return repl

    def rule_1_copulative_ke_a(self, text: str) -> Tuple[str, bool]:
        """Rule 1: Copulative consolidation 'Ke a' -> 'Kea' (and lowercase)"""
        pattern = re.compile(r'\b([Kk]e)\s+a\s+', flags=re.UNICODE)
        new_text, n = pattern.subn(r'\1a ', text)
        changed = n > 0
        if changed:
            self.transformation_log.append({'rule': 'copulative_ke_a', 'pattern': r'\b[Kk]e\s+a', 'replacement': r'\1a'})
        return new_text, changed

    def rule_2_copulative_o_a(self, text: str) -> Tuple[str, bool]:
        """Rule 2: Copulative consolidation 'o a' -> 'oa' (and uppercase)"""
        pattern = re.compile(r'\b([oO])\s+a\s+', flags=re.UNICODE)
        new_text, n = pattern.subn(r'\1a ', text)
        changed = n > 0
        if changed:
            self.transformation_log.append({'rule': 'copulative_o_a', 'pattern': r'\b[oO]\s+a', 'replacement': r'\1a'})
        return new_text, changed

    def rule_3_noun_prefix_dijo(self, text: str) -> Tuple[str, bool]:
        """
        Rule 3: Noun class prefix di- -> li- for common words and standalone 'di' concord.
        Implemented conservatively:
        - Specific safe-word mappings (dijo, diphoofolo, dibuka)
        - Standalone 'di' -> 'li'
        - Generic di([a-z]+) -> li\1 for longer tokens, excluding an exceptions set
        All replacements preserve capitalization.
        """
        new_text = text
        changed = False

        # Specific words mapping (case-preserving)
        specific = {
            'dijo': 'lijo',
            'diphoofolo': 'liphoofolo',
            'dibuka': 'libuka',
        }
        for sa_word, les_word in specific.items():
            # match with word boundaries and preserve capitalization
            pattern = re.compile(r'\b[' + sa_word[0].upper() + sa_word[0].lower() + r']' + sa_word[1:] + r'\b')
            def repl_spec(m, target=les_word):
                s = m.group(0)
                return target[0].upper() + target[1:] if s[0].isupper() else target
            new_text, n = pattern.subn(repl_spec, new_text)
            if n > 0:
                changed = True
                self.transformation_log.append({
                    'rule': 'noun_prefix_di_li',
                    'pattern': sa_word,
                    'replacement': les_word
                })

        # Standalone concord 'di' -> 'li' (safe)
        pattern_di_standalone = re.compile(r'\b[Dd]i\b')
        def repl_di(m):
            s = m.group(0)
            return 'Li' if s[0].isupper() else 'li'
        new_text, n = pattern_di_standalone.subn(repl_di, new_text)
        if n > 0:
            changed = True
            self.transformation_log.append({
                'rule': 'noun_prefix_di_li',
                'pattern': r'\bdi\b',
                'replacement': 'li'
            })

        # Generic diX -> liX for tokens like 'dipale' -> 'lipale' but exclude known exceptions
        exceptions = {'dipale', 'dimela', 'dinaha'}  # words to skip (lowercase)
        pattern_generic = re.compile(r'\b([Dd])i([a-z]+)\b')

        made_a_change = False
        def repl_generic(m):
            nonlocal made_a_change
            first = m.group(1)
            rest = m.group(2)
            full_lower = ('di' + rest).lower()
            if full_lower in exceptions:
                return m.group(0)

            made_a_change = True
            replacement = 'li' + rest
            return replacement[0].upper() + replacement[1:] if first.isupper() else replacement

        new_text = pattern_generic.sub(repl_generic, new_text)

        if made_a_change:
            self.transformation_log.append({
                'rule': 'noun_prefix_di_li_generic',
                'pattern': r'\b[dD]i([a-z]+)\b',
                'replacement': 'li\\1'
            })
            changed = True

        return new_text, changed

    def rule_4_consonant_ngwana(self, text: str) -> Tuple[str, bool]:
        """
        Rule 4: Consonant cluster transformations for 'ngwana' -> 'ngoana' and variants.
        Preserves capitalization.
        """
        transformations = {
            'ngwana': 'ngoana',
            'ngwaneso': 'ngoaneso',
            'ngwanaka': 'ngoanaka',
        }
        new_text = text
        changed = False
        for sa_form, les_form in transformations.items():
            pattern = re.compile(r'\b[' + sa_form[0].upper() + sa_form[0].lower() + ']' + sa_form[1:] + r'\b')
            def repl_ng(m, target=les_form):
                s = m.group(0)
                return target[0].upper() + target[1:] if s[0].isupper() else target
            new_text, n = pattern.subn(repl_ng, new_text)
            if n > 0:
                changed = True
                self.transformation_log.append({
                    'rule': 'consonant_ngw_ngo',
                    'pattern': sa_form,
                    'replacement': les_form
                })
        return new_text, changed

    def rule_5_possessive_ya_ea(self, text: str) -> Tuple[str, bool]:
        """Rule 5: Possessive marker 'ya <poss>' -> 'ea <poss>'"""
        pattern = re.compile(r'\b(ya)\s+(hao|rona|bona)\b', flags=re.IGNORECASE)
        def repl(m):
            # preserve capitalization of 'ya' -> 'ea' by checking the first character
            prefix = 'Ea' if m.group(1)[0].isupper() else 'ea'
            return f'{prefix} {m.group(2)}'
        new_text, n = pattern.subn(repl, text)
        changed = n > 0
        if changed:
            self.transformation_log.append({'rule': 'possessive_ya_ea', 'pattern': r'\bya (hao|rona|bona)\b', 'replacement': 'ea <possessive>'})
        return new_text, changed

    def normalize(self, text: str) -> Tuple[str, List[dict]]:
        self.transformation_log = []
        normalized = text
        for rule_func in self.rules:
            normalized, _ = rule_func(normalized)
        return normalized, self.transformation_log
