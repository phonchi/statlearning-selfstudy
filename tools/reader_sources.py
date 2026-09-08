"""Keep mutable source positions out of reader prose; retain build provenance.

Code and saved notebook outputs are never rewritten. Internal cell identifiers
are carried by data-lab-* attributes and checked against the extracted sources.
"""
import html
import re
from html.parser import HTMLParser

NUMBERS = r"\d+(?:\s*[–—\-、,，／/]\s*\d+)*"
CELL = rf"(?:儲存格|[Cc]ells?)\s*{NUMBERS}"
LECTURE = rf"(講義(?:\s*\d{{2}}(?:_\d{{2}})?)?)\s*(?:·\s*)?(?:[pP]\.\s*{NUMBERS}|第\s*{NUMBERS}\s*頁)"


def prose(text):
    """Normalize prose only, retaining actual dataset years and code values."""
    text = re.sub(rf"[（(](?:lab\s*(?:的\s*)?)?{CELL}[）)]", "", text)
    if "Seeing Theory 講義" in text:
        text = re.sub(rf"，推導續於\s*p\.\s*{NUMBERS}", "", text)
    text = re.sub(LECTURE, r"\1", text)
    text = re.sub(rf"(?:lab\s*(?:的\s*)?)?{CELL}", "lab 範例", text)
    text = re.sub(r"\s*·\s*(?=[，。；）]|$)", "", text)
    text = text.replace("課本節號或講義頁碼", "課本章節與講義主題")
    text = re.sub(r"標了儲存格編號，可以直接回去對。", "提供原始筆記本連結。", text)
    text = text.replace("各卡標有來源儲存格", "各卡附有來源筆記本連結")
    return text


def source_span(source):
    """A useful notebook link plus machine-readable, non-visible positions."""
    from pages import COURSE_REPO
    match = re.search(r"<code>(Ch(\d+)-[^<]+\.ipynb)</code>\s*·\s*儲存格\s*(.*)", source)
    if not match:
        raise ValueError(f"Unrecognized notebook citation: {source}")
    name, ch, positions = match.groups()
    # Source helpers enumerate cells. A range is expanded when encountered.
    cells = []
    for item in re.split(r"[、,，／/]", positions):
        nums = [int(x) for x in re.findall(r"\d+", item)]
        if len(nums) == 2 and re.search(r"[–—-]", item):
            cells.extend(range(nums[0], nums[1] + 1))
        else:
            cells.extend(nums)
    if not cells:
        raise ValueError(f"No cells in citation: {source}")
    repo = "intro-stat-learning/ISLP_labs" if int(ch) == 10 else COURSE_REPO
    path = "" if int(ch) == 10 else "static_files/presentations/"
    url = f"https://github.com/{repo}/blob/main/{path}{name}"
    return (f'<span class="dx-src" data-lab-ch="{int(ch)}" '
            f'data-lab-cells="{",".join(map(str, cells))}">來源：'
            f'<a href="{url}" target="_blank" rel="noopener"><code>{html.escape(name)}</code></a></span>')


class ReaderHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        if not self.protected:
            raw = re.sub(r'(href=")([^"]+)#page=(\d+)(")',
                         lambda m: m[1] + m[2] + m[4] + ' data-source-page="' + m[3] + '"', raw)
            # Feedback and accessible labels are reader-facing too.
            raw = re.sub(r'((?:data-fb|title|aria-label)=")([^"]*)(")',
                         lambda m: m[1] + html.escape(prose(html.unescape(m[2])), quote=True) + m[3], raw)
        self.output.append(raw)
        if tag in ('script', 'style', 'pre', 'code') or (tag == 'div' and dict(attrs).get('class') == 'pseudo-code'):
            self.protected.append(tag)

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')
        if self.protected and self.protected[-1] == tag:
            self.protected.pop()

    def handle_startendtag(self, tag, attrs):
        self.output.append(self.get_starttag_text())

    def handle_data(self, text):
        self.output.append(text if self.protected else prose(text))

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')

    def handle_comment(self, text):
        self.output.append(f'<!--{text}-->')

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')


def fragment(value):
    parser = ReaderHTML()
    parser.feed(value)
    parser.close()
    return ''.join(parser.output)
