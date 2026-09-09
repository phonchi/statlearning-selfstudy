"""Regression tests for removing and restoring optional vocabulary sections."""
import unittest
from unittest.mock import patch
import pages as P
import build_page as B

class OptionalVocabulary(unittest.TestCase):
    def setUp(self):self.page=P.BY_STEM['00c_ai_assisted']
    def test_empty_cards_do_not_generate_ui_or_links(self):
        with patch.object(P,'flashcard_count',return_value=0):
            html=B.render_new(self.page)
            self.assertNotIn('id="cards"',html)
            self.assertNotIn('href="#cards"',html)
            self.assertNotIn('id="fcGrid"',html)
            self.assertIn('id="exercises"',html)
    def test_removing_last_card_removes_old_section_and_nav(self):
        with patch.object(P,'flashcard_count',return_value=1):old=B.render_new(self.page)
        with patch.object(P,'flashcard_count',return_value=0):
            new,changed,missing=B.refresh(self.page,old)
            self.assertEqual(missing,[])
            self.assertIn('remove-empty-cards',changed)
            self.assertNotIn('id="cards"',new)
            self.assertNotIn('#cards',new)
    def test_adding_first_real_term_restores_cards(self):
        with patch.object(P,'flashcard_count',return_value=0):old=B.render_new(self.page)
        with patch.object(P,'flashcard_count',return_value=1):
            new,changed,missing=B.refresh(self.page,old)
            self.assertEqual(missing,[])
            self.assertIn('add-cards',changed)
            self.assertEqual(new.count('id="cards"'),1)
            self.assertIn('href="#cards"',new)
    def test_few_real_terms_are_enough(self):
        with patch.object(P,'flashcard_count',return_value=1):
            tokens=P.tokens(self.page)
            self.assertEqual(tokens[-1][0].id,'cards')
            self.assertIn('id="fcGrid"',B.cards_block(self.page))
if __name__=='__main__':unittest.main()
