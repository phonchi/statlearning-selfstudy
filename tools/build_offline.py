"""產生斷網可用的離線 zip（給期中考等斷網場合）。

線上版只依賴三個外部資源，離線版這樣處理：
  MathJax 3     → 從 npm 取 mathjax@3.2.2 的 es5/，放進 vendor/mathjax/
  Chart.js      → 從 npm 取 chart.js@4.5.1，核對與 HTML 相同的 sha384 後放進 vendor/
  Google Fonts  → 移除，改用 CSS 原有的 serif／sans-serif／monospace 系統字型

HTML 來源是 repo 根目錄已建好的頁面（先跑完 build_page.py／build_index.py 再打包）。
npm 套件快取在 ~/.cache/selfstudy-offline，zip 輸出到 dist/（不進 git）。

用法：python3 tools/build_offline.py
"""
import base64
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pages import PAGES  # noqa: E402
from paths import ROOT  # noqa: E402

CACHE = Path.home() / ".cache" / "selfstudy-offline"
DIST = ROOT / "dist"
NAME = "statlearning-selfstudy-offline"

MATHJAX = "mathjax@3.2.2"
CHARTJS = "chart.js@4.5.1"
CHARTJS_SHA384 = "jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ"

MATHJAX_TAG = '<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
CHARTJS_RE = re.compile(
    r'<script src="https://cdn\.jsdelivr\.net/npm/chart\.js@4\.5\.1/dist/chart\.umd\.min\.js"\s+'
    r'integrity="[^"]+" crossorigin="anonymous"></script>')
FONTS_RE = re.compile(r'<link href="https://fonts\.googleapis\.com/[^"]+" rel="stylesheet">\n?')


def npm_package(spec: str) -> Path:
    """npm pack 到快取並解開，回傳 package/ 目錄。"""
    dest = CACHE / spec.replace("/", "_")
    pkg = dest / "package"
    if pkg.exists():
        return pkg
    dest.mkdir(parents=True, exist_ok=True)
    out = subprocess.run(["npm", "pack", spec, "--silent"], cwd=dest,
                         check=True, capture_output=True, text=True).stdout.split()[-1]
    with tarfile.open(dest / out) as tf:
        tf.extractall(dest, filter="data")
    return pkg


def offline_html(html: str, stem: str, stamp: str) -> str:
    n_mj = html.count(MATHJAX_TAG)
    html = html.replace(MATHJAX_TAG,
                        '<script id="MathJax-script" async src="vendor/mathjax/tex-mml-chtml.js"></script>')
    html, n_cj = CHARTJS_RE.subn('<script src="vendor/chart.umd.min.js"></script>', html)
    html, n_ft = FONTS_RE.subn("", html)
    if stem == "index":
        html = html.replace(
            '<div class="scroll-hint">',
            f'<div class="subtitle">離線版 · {stamp} 產生 · 課程錄影、講義 PDF 等外部連結需要網路</div>\n'
            '    <div class="scroll-hint">', 1)
    # index 沒有公式與圖表；其他頁兩者都要換掉，否則斷網時會壞
    if n_ft != 1 or (stem != "index" and (n_mj, n_cj) != (1, 1)):
        raise SystemExit(f"{stem}.html：外部資源替換數量不符（MathJax {n_mj}、Chart.js {n_cj}、字型 {n_ft}）")
    left = re.findall(r'<(?:script|link)[^>]+(?:src|href)="https?://[^"]+', html)
    if left:
        raise SystemExit(f"{stem}.html 仍有外部資源：{left}")
    return html


def main():
    stamp = datetime.date.today().isoformat()
    stems = ["index"] + [p.stem for p in PAGES]
    on_disk = sorted(p.stem for p in ROOT.glob("*.html"))
    if sorted(stems) != on_disk:
        raise SystemExit(f"pages.py 與根目錄 HTML 不一致：{set(stems) ^ set(on_disk)}")

    mathjax = npm_package(MATHJAX) / "es5"
    chartjs = npm_package(CHARTJS) / "dist" / "chart.umd.min.js"
    digest = base64.b64encode(hashlib.sha384(chartjs.read_bytes()).digest()).decode()
    if digest != CHARTJS_SHA384:
        raise SystemExit(f"Chart.js sha384 不符：{digest}")

    site = DIST / NAME
    if site.exists():
        shutil.rmtree(site)
    (site / "vendor").mkdir(parents=True)
    # sre 是無障礙語音朗讀模組，只有手動打開 MathJax 選單的 a11y 選項才會載入
    shutil.copytree(mathjax, site / "vendor" / "mathjax", ignore=shutil.ignore_patterns("sre"))
    shutil.copy2(chartjs, site / "vendor" / "chart.umd.min.js")
    for stem in stems:
        html = (ROOT / f"{stem}.html").read_text(encoding="utf-8")
        (site / f"{stem}.html").write_text(offline_html(html, stem, stamp), encoding="utf-8")
    (site / "README.txt").write_text(
        "統計學習 × Python 互動自學網站（離線版）\n"
        f"產生日期：{stamp}\n\n"
        "解壓縮後用瀏覽器（Chrome／Edge／Firefox）開啟 index.html 即可，不需要網路。\n"
        "請保留整個資料夾結構（vendor/ 內是公式與圖表套件）。\n"
        "課程錄影、講義 PDF、GitHub Lab 等外部連結需要網路才能開啟。\n",
        encoding="utf-8")

    zpath = DIST / f"{NAME}-{stamp.replace('-', '')}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in sorted(site.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(DIST))
    print(f"{len(stems)} 頁 → {zpath}（{zpath.stat().st_size / 1e6:.1f} MB）")


if __name__ == "__main__":
    main()
