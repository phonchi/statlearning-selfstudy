"""Regression checks: readable citations must not weaken source verification."""
import unittest
from unittest.mock import patch

import pages as P
import validate as V
from reader_sources import fragment, prose, source_span


class ReaderSources(unittest.TestCase):
    def test_positions_removed_but_numbers_and_code_preserved(self):
        value = ('<p>講義 01 · p.7、16–19；lab 儲存格 152；薪資 3000 筆。</p>'
                 '<pre>lab 儲存格 152\n2025-09-04</pre>'
                 '<code>x[152]</code><div class="pseudo-code"><span class="line"># lab 儲存格 152</span></div>')
        got = fragment(value)
        self.assertIn('講義 01；lab 範例；薪資 3000 筆。', got)
        self.assertIn('<pre>lab 儲存格 152\n2025-09-04</pre>', got)
        self.assertIn('<code>x[152]</code>', got)
        self.assertIn('# lab 儲存格 152</span>', got)
        self.assertEqual(fragment(got), got)

    def test_feedback_and_pdf_links(self):
        got = fragment('<a href="a.pdf#page=16" title="講義第 16 頁">講義 p.16</a>'
                       '<div data-fb="請看 lab 儲存格 23。"></div>')
        self.assertNotIn('#page=', got)
        self.assertIn('data-source-page="16"', got)
        self.assertIn('data-fb="請看 lab 範例。"', got)
        self.assertEqual(fragment(got), got)

    def test_hidden_source_still_rejects_wrong_output_and_missing_cells(self):
        from enrich.lib import lab_output
        page = P.BY_STEM['p1_python_basics']
        cite = source_span('<code>Ch02-statlearn-lab-zh.ipynb</code> · 儲存格 12')
        self.assertNotIn('2025', cite)
        self.assertNotIn('儲存格', cite)
        import html
        value = ('<div class="deck-extra">' + cite + '<div class="expected-out"><pre>'
                 + html.escape(lab_output(2, 12)) + '</pre></div></div>')
        with patch.object(V, 'fail') as fail:
            V.check_prep_grounding(page, 'fixture', value, '')
            self.assertEqual(fail.call_args_list, [])
            V.check_prep_grounding(page, 'fixture', value.replace('<pre>', '<pre>WRONG'), '')
            self.assertTrue(any('不逐字相同' in c.args[2] for c in fail.call_args_list))
        with patch.object(V, 'fail') as fail:
            V.check_prep_grounding(page, 'fixture', value.replace('cells="12"', 'cells="99999"'), '')
            self.assertTrue(any('不存在' in c.args[2] for c in fail.call_args_list))

    def test_notebook_teaching_terminology_retained(self):
        self.assertEqual(prose('儲存格還沒執行；資料年份是 2025。'), '儲存格還沒執行；資料年份是 2025。')


if __name__ == '__main__':
    unittest.main()
