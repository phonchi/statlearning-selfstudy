#!/usr/bin/env python3
"""把 data/flashcards_zh 與 data/questions_zh 注入各頁的 DATA 區段。冪等。

母檔是 JSON，頁面只是它的呈現。改內容請改 JSON 再跑這支，不要直接改 HTML。
每一節的標題徽章（「N 張」「N 題」）由 build_page.py 讀同一份 JSON 產生，
所以數字不可能跟母檔不一致。

用法：
  python3 tools/inject_data.py                     # 全部
  python3 tools/inject_data.py resampling_methods
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pages as P  # noqa: E402
from paths import FLASHCARDS, QUESTIONS, ROOT  # noqa: E402

BANKQUIZ_JS = r"""
/* ===== 題庫自我檢測引擎（資料在 BANKQUIZ） ===== */
(() => {
  const box = document.getElementById('bqBox');
  if (!box || typeof BANKQUIZ === 'undefined' || !BANKQUIZ.length) return;
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  box.innerHTML = BANKQUIZ.map((q, i) => {
    const opts = q.options.map((o, j) => {
      const letter = 'ABCDE'[j];
      return '<div class="quiz-opt" data-correct="' + (j === q.answer) + '" data-fb="'
        + String(q.why[j] || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;') + '" '
        + 'onclick="quizCheck(\'bq' + i + '\', this)">'
        + '<span class="opt-letter">(' + letter + ')</span> ' + q.options[j] + '</div>';
    }).join('');
    return '<div class="quiz-box"><div class="quiz-label">題庫 ' + (i + 1) + ' · '
      + esc(q.topic || '') + '</div><p>' + q.q + '</p>'
      + '<div class="quiz-options" id="bq' + i + 'Options">' + opts + '</div>'
      + '<div class="quiz-feedback" id="bq' + i + 'Feedback"></div></div>';
  }).join('\n');
  HC.retype(box);
})();
"""


def inject(p: P.Page) -> str:
    dest = ROOT / p.file
    src = dest.read_text(encoding="utf-8")
    blocks, msg = [], []

    fc = FLASHCARDS / f"ch{p.islp}.json"
    if fc.exists():
        cards = json.loads(fc.read_text(encoding="utf-8"))
        blocks.append("<script>\nconst FLASHCARDS = "
                      + json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
                      + ";\nHC.initFlashcards();\n</script>")
        msg.append(f"{len(cards)} 張詞彙卡")

    if p.bankquiz:
        qf = QUESTIONS / f"ch{p.islp}.json"
        if qf.exists():
            qs = json.loads(qf.read_text(encoding="utf-8"))
            blocks.append("<script>\nconst BANKQUIZ = "
                          + json.dumps(qs, ensure_ascii=False, separators=(",", ":"))
                          + ";" + BANKQUIZ_JS + "</script>")
            msg.append(f"{len(qs)} 題題庫")

    body = "\n".join(blocks)
    pat = re.compile(r"<!-- DATA:BEGIN -->.*?<!-- DATA:END -->", re.S)
    if not pat.search(src):
        raise SystemExit(f"{p.file} 找不到 DATA 區段（先跑 tools/build_page.py）")
    out = pat.sub(lambda _m: "<!-- DATA:BEGIN -->\n" + body + "\n<!-- DATA:END -->", src, count=1)
    if out != src:
        dest.write_text(out, encoding="utf-8")
    return "、".join(msg) or "（母檔尚未撰寫）"


def main(argv):
    targets = [P.BY_STEM[a] for a in argv] if argv else P.PAGES
    for p in targets:
        print(f"  {p.file:34s} {inject(p)}")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
