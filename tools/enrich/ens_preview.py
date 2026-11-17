"""開發預覽：把某一個 ens_* 模組的新節與 JS 拼進目前的 tree_based_methods.html 副本，寫到指定路徑。

不改 repo 裡的任何檔案。用法：
  python3 tools/enrich/ens_preview.py ens_b /abs/path/preview_b.html
之後可用 puppeteer 開這個檔（MathJax、Chart.js 走 CDN）。
"""
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from lib import fragment, prose, splice_pagejs, splice_section  # noqa: E402

ROOT = HERE.parent.parent
snap = json.loads((HERE.parent / "verification/ensemble-deepen-20261117/consult/old_bodies.json").read_text(encoding="utf-8"))
mod = importlib.import_module(sys.argv[1])
old = snap["BODIES"]
new = mod.build(dict(old))
js = snap["PAGEJS"]
if hasattr(mod, "patch_js"):
    js = mod.patch_js(js)
js = js + "\n" + getattr(mod, "JS", "")
src = (ROOT / "tree_based_methods.html").read_text(encoding="utf-8")
for sid, body in {**old, **new}.items():
    if sid == "exercises":
        continue
    src = splice_section(src, sid, fragment(body))
frames = snap.get("FRAMES", "")
src = splice_pagejs(src, (frames + "\n\n" + prose(js)) if frames else prose(js))
Path(sys.argv[2]).write_text(src, encoding="utf-8")
print("寫入", sys.argv[2], "新節：", ", ".join(new))
