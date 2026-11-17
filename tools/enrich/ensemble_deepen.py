"""第 8 章集成各節整節重寫（2026-11-17，HANDOFF §31）。

依講義 08 p.30–80、講義連結（tools/verification/ensemble-deepen-20261117/sources/）與學生問答，
覆寫 why／bagging／rf／boosting／modern／stacking，新增 importance／splitsearch／categorical／successors。
上游各層（含 scope_trim）照常執行，這裡在最後整節覆寫；可重用的元件從上游輸出取出，id 不變。
內容分在三個模組：ens_a（why、bagging、rf、importance）、ens_b（boosting、modern、splitsearch）、
ens_c（categorical、successors、stacking）。
"""
import re

import ens_a
import ens_b
import ens_c

SECS = ["why", "bagging", "rf", "boosting", "importance", "modern",
        "splitsearch", "categorical", "successors", "stacking"]

# 舊版留下、這次決定移除或更正的字串；任何一節還出現就報錯。
STALE = ["第一輪讀可以整節略過", "各一句話", "定在 36.8% 附近", "又多賺一點", "反而變差",
         "實驗性支援（建議自己先編碼）", "每次排序全部資料"]


_DECK_PAGE = re.compile(r"講義(\s*\d{2})?\s*(?:·\s*)?[pP]\.\s*\d+(?:\s*[–—\-、,，／/]\s*\d+)*(\s*)")


def _drop_deck_pages(body):
    """讀者層會刪掉「講義 p.73」的頁碼卻留下後面的空格；這裡先整段處理，必要時保留與英數之間的空格。"""
    def sub(m):
        nxt = body[m.end():m.end() + 1]
        return "講義" + (" " if nxt and (nxt.isascii() and (nxt.isalnum() or nxt == "$")) else "")
    return _DECK_PAGE.sub(sub, body)


def augment(BODIES, PAGEJS):
    old = dict(BODIES)
    new = {}
    for mod in (ens_a, ens_b, ens_c):
        part = mod.build(dict(old))
        dup = set(part) & set(new)
        if dup:
            raise ValueError(f"{mod.__name__} 重複產生：{dup}")
        new.update(part)
    if set(new) != set(SECS):
        raise ValueError(f"集成各節不齊：多 {set(new) - set(SECS)}，少 {set(SECS) - set(new)}")
    BODIES.update({k: _drop_deck_pages(v) for k, v in new.items()})
    for sid in SECS:
        for s in STALE:
            if s in BODIES[sid]:
                raise ValueError(f"{sid} 殘留舊句：{s}")
    js = PAGEJS
    for mod in (ens_a, ens_b, ens_c):
        if hasattr(mod, "patch_js"):
            js = mod.patch_js(js)
    return js + "".join("\n" + getattr(mod, "JS", "") for mod in (ens_a, ens_b, ens_c))
