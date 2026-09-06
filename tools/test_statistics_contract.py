#!/usr/bin/env python3
"""Regression tests for concept-source checks and unchanged lab requirements."""
import unittest
from dataclasses import replace
from unittest.mock import patch
import pages as P
import sources as S
import validate as V
from paths import ROOT


class StatisticsContract(unittest.TestCase):
    def setUp(self):
        self.page = P.BY_STEM['s1_probability']
        self.html = (ROOT / self.page.file).read_text()

    def failures(self, html, page=None):
        with patch.object(V, 'fail') as fail:
            V.check_concept_grounding(page or self.page, 'fixture', html)
        return [call.args[2] for call in fail.call_args_list]

    def test_valid_concept_has_no_lab_requirement(self):
        self.assertEqual(self.failures(self.html), [])
        self.assertEqual(S.page_books(self.page), ['Seeing-Theory'])

    def test_missing_section_locator_fails(self):
        broken = self.html.replace('doc/seeing-theory.pdf#page=16', 'doc/seeing-theory.pdf')
        self.assertTrue(any('#population' in msg for msg in self.failures(broken)))

    def test_pdf_outside_document_fails(self):
        self.assertTrue(any('頁碼' in msg for msg in self.failures(
            self.html.replace('doc/seeing-theory.pdf#page=16', 'doc/seeing-theory.pdf#page=99'))))

    def test_valid_url_for_unrelated_chapter_fails(self):
        broken = self.html.replace('doc/seeing-theory.pdf#page=16', 'frequentist-inference/index.html')
        self.assertTrue(any('登記章節不符' in msg for msg in self.failures(broken)))

    def test_unverified_output_card_fails(self):
        self.assertTrue(self.failures(self.html + '<div class="expected-out">invented output</div>'))

    def test_concept_cannot_mask_lab_page(self):
        self.assertTrue(self.failures(self.html, replace(self.page, src_labs=(2,))))

    def test_existing_prep_still_requires_actual_lab_card(self):
        with patch.object(V, 'fail') as fail:
            V.check_prep_grounding(P.BY_STEM['p3_numpy'], 'fixture', '', '')
        self.assertTrue(any('沒有任何引用' in call.args[2] for call in fail.call_args_list))
        self.assertTrue(all(p.grounding_mode == 'lab' for p in P.PAGES if p.n <= 20))

    def test_index_ignores_earlier_shortcut_links(self):
        with patch.object(V, 'fail') as fail:
            V.check_index()
        self.assertEqual(fail.call_args_list, [])

    def test_statistics_navigation_is_optional_and_self_contained(self):
        six = [p for p in P.PAGES if p.grp == 'statistics']
        self.assertEqual([p.n for p in six], list(range(21, 27)))
        self.assertEqual(len({p.dkey for p in six}), 6)
        self.assertIsNone(P.neighbours(six[0])[0])
        self.assertIsNone(P.neighbours(six[-1])[1])
        for i in range(5):
            self.assertEqual(P.neighbours(six[i])[1], six[i+1])
        self.assertEqual(P.neighbours(P.BY_STEM['00c_ai_assisted'])[1].stem, 'introduction')
        self.assertIsNone(P.neighbours(P.BY_STEM['deep_learning'])[1])


if __name__ == '__main__':
    unittest.main()
