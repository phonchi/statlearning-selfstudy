#!/usr/bin/env python3
"""Executable checks of reader-visible examples and frozen evidence.
Run with site Python; the PCA snippet uses the existing m524 environment.
All execution inputs are synthetic, not course lab data.
"""
import ast
import hashlib
import html
import json
import re
import os
import subprocess
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from rebuild_content import frame_declarations

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'tools/verification/reader-fixes-20260906/baseline.json'


def soup(stem):
    return BeautifulSoup((ROOT / (stem + '.html')).read_text(), 'html.parser',
                         preserve_whitespace_tags={'pre', 'textarea', 'span'})


class ReaderFixes(unittest.TestCase):
    def test_p1_visible_dictionary_example(self):
        page = soup('p1_python_basics')
        box = page.find(id='qDictOptions').find_parent(class_='quiz-box')
        code = box.find('p').find('code').get_text()
        ns = {}
        exec(code, ns)
        self.assertEqual(ns['scores'], {'R2': .54})
        with self.assertRaises(KeyError):
            _ = ns['scores']['MSE']

    def test_p1_visible_format_examples(self):
        page = soup('p1_python_basics')
        box = page.find(id='qStrOptions').find_parent(class_='quiz-box')
        code = box.find('p').find('code').get_text()
        self.assertEqual(eval(code), '16.54%')
        choice = page.find(id='qEx4Options').find(attrs={'data-correct':'true'})
        self.assertEqual(eval(choice.find('code').get_text(), {'mse':25.573878}), 'MSE = 25.57')
        for code in page.select('code'):
            self.assertNotIn('{{', code.get_text())

    def test_visible_pca_card_fits_before_transform(self):
        page = soup('unsupervised_learning')
        blocks = page.select('#pca .deck-extra')
        codes = ['\n'.join(x.get_text() for x in b.select('.pseudo-code .line')) for b in blocks]
        code = next(c for c in codes if 'pcaUS = PCA()' in c)
        self.assertLess(code.index('pcaUS.fit('), code.index('pcaUS.transform('))
        # Read the displayed snippet on fresh synthetic data with its stated imports.
        python = os.environ.get('M524_PYTHON', str(Path.home() / 'miniconda3/envs/m524/bin/python'))
        runner = '''import json,sys
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
ns = {'PCA':PCA, 'StandardScaler':StandardScaler,
      'USArrests':pd.DataFrame([[1,4,9,2],[3,2,8,6],[7,1,2,4],[2,8,3,9],[9,3,1,5]])}
exec(json.load(sys.stdin)['code'], ns)
print(json.dumps([list(ns['scores'].shape),list(ns['pcaUS'].components_.shape)]))
'''
        result = subprocess.run([python, '-B', '-c', runner], input=json.dumps({'code':code}),
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), [[5,4],[4,4]])

    def test_plain_text_flashcards(self):
        for path in (ROOT / 'data/flashcards_zh').glob('*.json'):
            for card in json.loads(path.read_text()):
                for side in ['front','back']:
                    text = card[side]
                    self.assertEqual(html.unescape(text), text, str(path))
                    self.assertIsNone(re.search(r'</?(?:b|strong|em|i|code|a|span|br|p)(?:\s[^>]*)?>', text), str(path))

    def test_visible_grid_search_fits_scaler_within_each_fold(self):
        page = soup('model_selection')
        codes = ['\n'.join(x.get_text() for x in block.select('.line'))
                 for block in page.select('#ridge .pseudo-code')]
        code = next(c for c in codes if 'grid = GridSearchCV(' in c)
        python = os.environ.get('M524_PYTHON', str(Path.home() / 'miniconda3/envs/m524/bin/python'))
        runner = '''import json,sys,numpy as np
from sklearn.preprocessing import StandardScaler
original = StandardScaler.fit
sizes = []
def record(self, X, y=None, **kwargs):
    sizes.append(len(X))
    return original(self, X, y, **kwargs)
StandardScaler.fit = record
ns = {'X_train':np.arange(30,dtype=float).reshape(10,3),
      'Y_train':np.array([2,0,1,4,3,6,5,8,7,9])}
exec(json.load(sys.stdin)['code'], ns)
print(json.dumps(sizes))
'''
        result = subprocess.run([python, '-B', '-c', runner], input=json.dumps({'code':code}),
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), [8]*15 + [10])

    def test_existing_sources_and_outputs_unchanged(self):
        before = json.loads(BASE.read_text())
        for name, digest in before['sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest, name)
        for name, outputs in before['outputs'].items():
            page = BeautifulSoup((ROOT/name).read_text(), 'html.parser')
            current = [hashlib.sha256(e.get_text().encode()).hexdigest() for e in page.select('.expected-out')]
            self.assertEqual(current, outputs, name)

    def test_baked_frames_byte_identical(self):
        before = json.loads(BASE.read_text())
        for name, hashes in before['frames'].items():
            text = (ROOT/name).read_text()
            current = {}
            for m in re.finditer(r'const\s+(FRAMES_\w+)\s*=\s*', text):
                _, length = json.JSONDecoder().raw_decode(text[m.end():])
                current[m.group(1)] = hashlib.sha256(text[m.end():m.end()+length].encode()).hexdigest()
            self.assertEqual(current, hashes, name)

    def test_frame_extractor_preserves_escaped_strings(self):
        text = 'const FRAMES_w99test = {"label":"brace } and \\\"quote\\\"","x":[1,2]};\nfunction next() {}'
        kept = frame_declarations(text)
        self.assertEqual(kept, text.split('\n')[0])

    def test_neural_lab_cell_separators_are_actual_newlines(self):
        blocks = soup('deep_learning').select('.deck-extra')
        self.assertTrue(blocks)
        for block in blocks:
            code = '\n'.join(x.get_text() for x in block.select('.pseudo-code .line'))
            ast.parse(code)


if __name__ == '__main__':
    unittest.main()
