#!/usr/bin/env python3
"""Report reader-visible English prose so it can be rewritten in Chinese.

This site is written for Chinese readers: slide and textbook sentences are
paraphrased in Chinese rather than quoted in English (STYLE_CONTRACT §6).
English *terms*, book titles, code and library names stay as they are, so
this script reports rather than fails — read the output and judge each hit.

    python3 tools/check_english_prose.py            # every page
    python3 tools/check_english_prose.py statistical_learning
"""
import json
import re
import sys
from pathlib import Path

import pages as P
import sources as S
from check_reader_contract import Visible
from rebuild_content import frame_declarations
from validate import js_strings, pagejs

ROOT = Path(__file__).resolve().parent.parent

# A run of this many English words in reader copy is prose, not a term.
WORDS = 5
RUN = re.compile(r"(?:[A-Za-z][A-Za-z'’\-]*(?:\s+|$)){%d,}" % WORDS)

# Term glosses are written 中文（English），and parenthesised English is a
# gloss by construction. Drop those spans before looking for prose.
PARENS = re.compile(r"[（(][^（()）]*[)）]")

# Names that legitimately appear as English in reader copy. Read them from the
# registries rather than keeping a copy here, so the list cannot go stale.
ALLOW = tuple(title for _, title, *_ in S.BOOKS.values()) + tuple(
    authors for _, _, authors, _ in S.BOOKS.values()) + tuple(
    p.title_en for p in P.PAGES if p.title_en) + (
    # Verbatim interpreter messages quoted as teaching material.
    "Traceback (most recent call last)",
    "The truth value of a Series is ambiguous",
    "could not be broadcast together",
    "shape mismatch: indexing arrays could not be",
)


def prose_runs(text):
    # Titles wrap across lines in the rendered page; match them on one line.
    text = re.sub(r"\s+", " ", text)
    text = PARENS.sub(" ", text)
    for allowed in ALLOW:
        text = text.replace(allowed, " ")
    return [m.group(0).strip() for m in RUN.finditer(text)]


def reader_copy(source):
    """Reader-visible text: page copy, quiz feedback, dynamic status, cards."""
    visible = Visible()
    visible.feed(source)
    parts = list(visible.text)
    for m in re.finditer(r"const (?:FLASHCARDS|BANKQUIZ) = ", source):
        payload, _ = json.JSONDecoder().raw_decode(source[m.end():])
        parts.append(json.dumps(payload, ensure_ascii=False))
    js = pagejs(source)
    for declaration in frame_declarations(js).splitlines():
        js = js.replace(declaration, "")
    parts.extend(s for s, _ in js_strings(js))
    return parts


def main(argv):
    names = [a.removesuffix(".html") for a in argv]
    paths = ([ROOT / f"{n}.html" for n in names] if names
             else sorted(ROOT.glob("*.html")))
    total = 0
    for path in paths:
        hits = sorted({h for part in reader_copy(path.read_text(encoding="utf-8"))
                       for h in prose_runs(part)})
        if hits:
            total += len(hits)
            print(f"\n{path.name}")
            for h in hits:
                print(f"  · {h}")
    print(f"\n{total} 處讀者可見的英文散文（{WORDS} 個以上連續英文單字）"
          f"，檢查了 {len(paths)} 頁。")
    print("這是報告，不是檢查失敗；術語、書名、程式輸出本來就該留英文。")


if __name__ == "__main__":
    main(sys.argv[1:])
