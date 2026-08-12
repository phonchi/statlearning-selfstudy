#!/usr/bin/env python3
"""把 lab notebook 攤成帶儲存格編號的 Markdown，供寫頁面時逐字引用。冪等。

紀律：頁面上的程式碼與「預期輸出」一律從這裡逐字抄，不重跑。
本機環境（numpy 2.x / 無 statsmodels / 無 ISLP）跟課程環境不同，重跑會跑出
不一樣的數字；而 notebook 裡已經是實跑過的輸出。

兩種來源：
1. `LABS`  — 課程的中文 lab notebook，在 `DECKS`（課程 repo）底下。
2. `OFFICIAL` — 課本官方的英文 lab notebook，從 GitHub 抓釘住的 commit。
   只有「課程沒教、但站上要補充」的章節才用它（目前只有第 10 章深度學習）。
   notebook 本身不進 repo（600 KB 且含 base64 圖），只 commit 這裡產生的 .md。

用法：python3 tools/extract_lab.py [notebook 檔名 ...]   （省略＝全部）
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import DECKS, SRC_INDEX, require  # noqa: E402

# lab 檔名 → ISLP 章號
LABS = {
    "Ch01-lab-zh.ipynb": 1,
    "Ch02-statlearn-lab-zh.ipynb": 2,
    "Ch03-linreg-lab-zh.ipynb": 3,
    "Ch04-classification-lab-zh.ipynb": 4,
    "Ch05-resample-lab-zh.ipynb": 5,
    "Ch06-varselect-lab-zh.ipynb": 6,
    "Ch07-nonlin-lab-zh.ipynb": 7,
    "Ch08-baggboost-lab-zh.ipynb": 8,
    "Ch09-svm-lab-zh.ipynb": 9,
    "Ch12-unsup-lab-zh.ipynb": 12,
}

# 官方 lab。**釘 commit**，否則上游一改，站上引用的儲存格編號就會錯位。
OFFICIAL_REPO = "intro-stat-learning/ISLP_labs"
OFFICIAL_REF = "6bf6160a3dd180c6651ba06655b453e81f91dc20"
OFFICIAL_LICENSE = "BSD 2-Clause"
OFFICIAL = {
    "Ch10-deeplearning-lab.ipynb": 10,
}
# 下載快取放 repo 外面（repo 不放 notebook）
LAB_CACHE = Path(os.environ.get("M524_LAB_CACHE", Path.home() / ".cache" / "selfstudy-labs"))

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

COURSE_NOTE = [
    "> 由 tools/extract_lab.py 產生。頁面上的程式碼與預期輸出一律從這裡逐字抄，",
    "> `.dx-src` 要標注這裡的儲存格編號。不要重跑：輸出是課程環境下的實跑結果。",
]

OFFICIAL_NOTE = [
    "> 由 tools/extract_lab.py 產生。頁面上的程式碼與預期輸出一律從這裡逐字抄，",
    "> `.dx-src` 要標注這裡的儲存格編號。不要重跑：輸出是課本作者存在 notebook 裡的實跑結果。",
    ">",
    f"> **來源**：https://github.com/{OFFICIAL_REPO}（{OFFICIAL_LICENSE}）",
    f"> · 分支 `main` · commit `{OFFICIAL_REF}`",
    ">",
    "> 本課（MATH524）沒有教這一章，所以沒有中文 lab；站上這一章是補充章，",
    "> 改用課本官方的英文 lab 當出處。程式碼逐字引用、註解保持英文，中文解說寫在卡片外面。",
]


def fetch_official(name: str) -> Path:
    """抓釘住 commit 的官方 notebook 到 repo 外的快取。已經有就不重抓。"""
    LAB_CACHE.mkdir(parents=True, exist_ok=True)
    dest = LAB_CACHE / f"{OFFICIAL_REF[:7]}-{name}"
    if dest.exists():
        return dest
    url = f"https://raw.githubusercontent.com/{OFFICIAL_REPO}/{OFFICIAL_REF}/{name}"
    print(f"  下載 {name} ← {OFFICIAL_REF[:7]}")
    with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310
        if r.status != 200:
            raise SystemExit(f"下載失敗（HTTP {r.status}）：{url}")
        dest.write_bytes(r.read())
    return dest


def flat(x):
    return "".join(x) if isinstance(x, list) else (x or "")


def outputs_text(cell):
    """把儲存格輸出攤平成純文字；圖片只記一行標記。"""
    parts = []
    for o in cell.get("outputs", []):
        t = o.get("output_type")
        if t == "stream":
            parts.append(ANSI.sub("", flat(o.get("text"))))
        elif t in ("execute_result", "display_data"):
            data = o.get("data", {})
            if "text/plain" in data:
                parts.append(ANSI.sub("", flat(data["text/plain"])))
            if "image/png" in data:
                parts.append("<figure omitted>")
        elif t == "error":
            parts.append(f"{o.get('ename')}: {o.get('evalue')}")
    return "".join(parts).rstrip()


def extract(nb_path, ch, note=None, name=None):
    """name 是要寫進標題與 .dx-src 的檔名（官方 lab 的快取檔名有 commit 前綴，要還原）。"""
    name = name or nb_path.name
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    lines = [
        f"# {name} — ISLP 第 {ch} 章",
        "",
        *(note or COURSE_NOTE),
        "",
    ]
    n_code = n_out = 0
    for i, cell in enumerate(nb["cells"]):
        src = flat(cell["source"]).rstrip()
        if not src and cell["cell_type"] != "code":
            continue
        if cell["cell_type"] == "markdown":
            lines += [f"## 儲存格 {i} [md]", "", src, ""]
        elif cell["cell_type"] == "code":
            n_code += 1
            lines += [f"## 儲存格 {i} [code]", "", "```python", src, "```", ""]
            out = outputs_text(cell)
            if out:
                n_out += 1
                lines += ["**輸出**", "", "```", out, "```", ""]
    dest = SRC_INDEX / f"lab_ch{ch}.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  {dest.name:16s} {len(nb['cells']):3d} 儲存格（{n_code} code，{n_out} 有輸出）"
          f"  ← {name}")
    return dest


def main(argv):
    SRC_INDEX.mkdir(parents=True, exist_ok=True)
    names = argv or list(LABS) + list(OFFICIAL)

    course = [n for n in names if n in LABS]
    if course:
        require(DECKS, "講義／lab 目錄")
        for name in course:
            p = DECKS / name
            if not p.exists():
                print(f"  跳過（不存在）：{name}")
                continue
            extract(p, LABS[name])

    for name in [n for n in names if n in OFFICIAL]:
        extract(fetch_official(name), OFFICIAL[name], note=OFFICIAL_NOTE, name=name)

    unknown = [n for n in names if n not in LABS and n not in OFFICIAL]
    for name in unknown:
        print(f"  跳過（不在 LABS／OFFICIAL 名單）：{name}")


if __name__ == "__main__":
    main(sys.argv[1:])
