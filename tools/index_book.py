#!/usr/bin/env python3
"""建立課本「印刷頁碼 ↔ PDF 頁碼」對映表與章節頁範圍。冪等。

為什麼必要：ISLP_website.pdf 的位移會漂移（前言、卷首頁會插入），
任何硬寫的加減法都會靜靜讀到錯的頁。有了這張表，
`pdftotext -f/-l` 才能讀到真正想要的章節。

版面事實（ISLP 與 ESL 相同，已實測）：印刷頁碼在頁首那一行——
  偶數（verso）頁：`70       3. Linear Regression`        ← 頁碼在行首
  奇數（recto）頁：`      3.1 Simple Linear Regression  71` ← 頁碼在行尾
全頁圖表與卷首頁沒有頁首，用位移內插補齊。

用法：python3 tools/index_book.py [islp|esl|all]
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ESL_PDF, ISLP_PDF, SRC_INDEX, require  # noqa: E402

VERSO = re.compile(r"^\s{0,6}(\d{1,3})\s{2,}(\S.*?)\s*$")   # 頁碼 + 章名
RECTO = re.compile(r"^\s{2,}(\S.*?)\s{2,}(\d{1,3})\s*$")     # 節名 + 頁碼
CHAP = re.compile(r"^(\d{1,2})\.\s+(.+)$")                   # "3. Linear Regression"


def parse(pdf):
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()

    rows = []          # (pdf_page, printed|None, running_head)
    for pdfno, page in enumerate(pages, start=1):
        head = next((ln for ln in page.splitlines() if ln.strip()), "")
        printed, running = None, ""
        m = VERSO.match(head)
        if m:
            printed, running = int(m.group(1)), " ".join(m.group(2).split())
        else:
            m = RECTO.match(head)
            if m:
                printed, running = int(m.group(2)), " ".join(m.group(1).split())
        # 只信位移合理的（頁碼不可能大於 PDF 頁碼，也不會差太遠）
        if printed is not None and not (0 <= pdfno - printed <= 60):
            printed, running = None, ""
        rows.append([pdfno, printed, running])
    return rows


def fill(rows):
    """用最近的前一個錨點的位移補齊沒有頁首的頁。"""
    offset = None
    for r in rows:
        if r[1] is not None:
            offset = r[0] - r[1]
        elif offset is not None:
            r[1] = r[0] - offset
            r.append("內插")
    return rows


def chapters(rows):
    """從 verso 頁首的 'N. Title' 推出各章的 PDF / 印刷頁範圍。"""
    seen = {}
    for pdfno, printed, running, *_ in rows:
        m = CHAP.match(running)
        if not m:
            continue
        n, title = int(m.group(1)), m.group(2)
        e = seen.setdefault(n, {"title": title, "pdf": [pdfno, pdfno],
                                "printed": [printed, printed]})
        e["pdf"][1] = pdfno
        if printed is not None:
            e["printed"][1] = printed
    return dict(sorted(seen.items()))


def write(pdf, tag):
    rows = fill(parse(pdf))
    hit = sum(1 for r in rows if len(r) == 3 and r[1] is not None)
    interp = sum(1 for r in rows if len(r) == 4)

    dest = SRC_INDEX / f"{tag}_pages.tsv"
    body = [f"# {pdf.name}\t{len(rows)} PDF 頁\t{hit} 頁直接讀到\t{interp} 頁內插",
            "# pdf_page\tprinted_page\trunning_head\tnote"]
    for r in rows:
        body.append("\t".join([str(r[0]), "" if r[1] is None else str(r[1]),
                               r[2], r[3] if len(r) == 4 else ""]))
    dest.write_text("\n".join(body) + "\n", encoding="utf-8")

    ch = chapters(rows)
    cdest = SRC_INDEX / f"{tag}_chapters.tsv"
    cbody = ["# chapter\ttitle\tpdf_from\tpdf_to\tprinted_from\tprinted_to"]
    for n, e in ch.items():
        cbody.append("\t".join([str(n), e["title"], str(e["pdf"][0]), str(e["pdf"][1]),
                                str(e["printed"][0]), str(e["printed"][1])]))
    cdest.write_text("\n".join(cbody) + "\n", encoding="utf-8")

    print(f"  {dest.name:18s} {len(rows)} 頁（{hit} 直讀 / {interp} 內插）")
    print(f"  {cdest.name:18s} {len(ch)} 章")
    for pdfno, printed, *_ in rows:
        if printed and pdfno in (20, 80, 150, 300, 400, 520, 600):
            print(f"      PDF {pdfno:4d} → 書上 p.{printed:<4d} (位移 {pdfno - printed})")
    return ch


def main(argv):
    which = (argv[0] if argv else "all").lower()
    SRC_INDEX.mkdir(parents=True, exist_ok=True)
    if which in ("islp", "all"):
        print("ISLP:")
        write(require(ISLP_PDF, "ISLP 課本 PDF"), "islp")
    if which in ("esl", "all"):
        print("ESL:")
        write(require(ESL_PDF, "ESL 課本 PDF"), "esl")


if __name__ == "__main__":
    main(sys.argv[1:])
