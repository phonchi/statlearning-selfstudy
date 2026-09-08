"""Check published prose, links and interactive data, excluding quoted code."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from reader_sources import CELL, LECTURE

ROOT = Path(__file__).resolve().parent.parent


class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = []
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style', 'pre', 'code') or (tag == 'div' and attrs.get('class') == 'pseudo-code'):
            self.skip.append(tag)
        if attrs.get('href'):
            self.links.append(attrs['href'])
        for key in ('title', 'aria-label', 'data-fb', 'content'):
            if key in attrs:
                self.text.append(attrs[key])

    def handle_endtag(self, tag):
        if self.skip and self.skip[-1] == tag:
            self.skip.pop()

    def handle_data(self, value):
        if not self.skip:
            self.text.append(value)


def main():
    failures = []
    for path in sorted(ROOT.glob('*.html')):
        source = path.read_text()
        parser = Visible()
        parser.feed(source)
        # Flashcard/question payloads become visible after the JavaScript runs.
        for match in re.finditer(r'const (?:FLASHCARDS|BANKQUIZ) = ', source):
            obj, _ = json.JSONDecoder().raw_decode(source[match.end():])
            parser.text.append(json.dumps(obj, ensure_ascii=False))
        text = '\n'.join(parser.text)
        for pattern in (LECTURE, CELL, r'每節自測|\d+\s*(?:張詞彙卡|個視覺區塊)',
                        r'(?:lab\s*的?\s*)第\s*\d+\s*格', r'標了儲存格編號', r'講義[^。\n]{0,25}有\s*\d+\s*頁'):
            match = re.search(pattern, text)
            if match:
                failures.append(f'{path.name}: visible locator/marketing text: {match[0]}')
        for link in parser.links:
            if 'nsysu-math524-2025' in link or '#page=' in link:
                failures.append(f'{path.name}: stale/positional link: {link}')
        if path.name != 'index.html':
            for required in ('id="fcGrid"', 'class="quiz-box"', 'const FLASHCARDS = '):
                if required not in source:
                    failures.append(f'{path.name}: missing preserved learning feature {required}')
    readme = (ROOT / 'README.md').read_text()
    if re.search(r'nsysu-math524-2025|內容量|\d+\s*張卡|每節自測', readme):
        failures.append('README.md: stale link or count metadata')
    if failures:
        raise SystemExit('\n'.join(failures))
    print('Reader contract: all pages and README pass; links, prose and learning features checked.')


if __name__ == '__main__':
    main()
