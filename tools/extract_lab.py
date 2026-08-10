#!/usr/bin/env python3
"""把中文 lab notebook 攤成帶儲存格編號的 Markdown，供寫頁面時逐字引用。冪等。

紀律：頁面上的程式碼與「預期輸出」一律從這裡逐字抄，不重跑。
本機環境（numpy 2.x / 無 statsmodels / 無 ISLP）跟課程環境不同，重跑會跑出
不一樣的數字；而 notebook 裡已經是老師本人跑出來的輸出。

用法：python3 tools/extract_lab.py [notebook 檔名 ...]   （省略＝全部）
"""
import json
import re
import sys
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

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


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


def extract(nb_path, ch):
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    lines = [
        f"# {nb_path.name} — ISLP 第 {ch} 章",
        "",
        "> 由 tools/extract_lab.py 產生。頁面上的程式碼與預期輸出一律從這裡逐字抄，",
        "> `.dx-src` 要標注這裡的儲存格編號。不要重跑：輸出是課程環境下的實跑結果。",
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
          f"  ← {nb_path.name}")
    return dest


def main(argv):
    require(DECKS, "講義／lab 目錄")
    SRC_INDEX.mkdir(parents=True, exist_ok=True)
    names = argv or list(LABS)
    for name in names:
        p = DECKS / name
        if not p.exists():
            print(f"  跳過（不存在）：{name}")
            continue
        extract(p, LABS.get(name, 0))


if __name__ == "__main__":
    main(sys.argv[1:])
