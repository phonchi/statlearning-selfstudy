#!/usr/bin/env python3
"""把課程講義 PDF 抽成「頁碼 → 投影片標題」的 TSV 大綱。冪等。

每頁的第一個非空行就是投影片標題，這份大綱直接決定各章頁面的 PART 清單，
也提供「講義 08 · p.43」這種可引用的錨點。

用法：python3 tools/index_deck.py [deck 檔名 ...]     （省略＝全部）
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import DECKS, SRC_INDEX, require  # noqa: E402

# 講義編號 → 站內章節序號（授課順序，見 tools/pages.py）
DECK_ORDER = [
    "01_Introduction.pdf",
    "02_Statistical_Learning.pdf",
    "03_Regression.pdf",
    "04_Classification.pdf",
    "05_Resampling_Methods.pdf",
    "06_Linear_Model_Selection.pdf",
    "12_Unsupervised_learning.pdf",
    "07_Moving_Beyond_Linearity.pdf",
    "08_Tree-Based_Methods.pdf",
    "09_Support_Vector_Machines.pdf",
    "01-06_Recap.pdf",
]

# RISE 投影片的頁首/頁尾雜訊，不能當標題
NOISE = re.compile(
    r"^(\d+\s*/\s*\d+|\d{1,3}|https?://|MATH\s*524|Statistical Learning and Data Mining"
    r"|NSYSU|National Sun Yat-Sen|鍾思齊|\W{0,3})$",
    re.I,
)


def slide_titles(pdf):
    """回傳 [(頁碼, 標題), ...]。以換頁字元切頁，取每頁第一個像標題的行。"""
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = []
    for pageno, page in enumerate(out.split("\f"), start=1):
        title = ""
        for line in page.splitlines():
            line = " ".join(line.split())          # 收掉 -layout 產生的多重空白
            if not line or NOISE.match(line):
                continue
            title = line
            break
        rows.append((pageno, title))
    # 尾端 pdftotext 常多切一個空頁
    while rows and not rows[-1][1]:
        rows.pop()
    return rows


def main(argv):
    require(DECKS, "講義目錄")
    SRC_INDEX.mkdir(parents=True, exist_ok=True)
    targets = argv or DECK_ORDER
    for name in targets:
        pdf = DECKS / name
        if not pdf.exists():
            print(f"  跳過（不存在）：{name}")
            continue
        rows = slide_titles(pdf)
        stem = name.split("_")[0].replace("-", "_")      # 01 / 12 / 01_06
        dest = SRC_INDEX / f"deck_{stem}.tsv"
        body = [f"# {name}\t{len(rows)} 頁", "# page\ttitle"]
        body += [f"{p}\t{t}" for p, t in rows]
        dest.write_text("\n".join(body) + "\n", encoding="utf-8")
        print(f"  {dest.name:18s} {len(rows):3d} 頁  ← {name}")


if __name__ == "__main__":
    main(sys.argv[1:])
