"""第 9 章整節重寫（2026-11-22，HANDOFF §32）。

依講義 09（2026-11-22 版）、ISLP 第 9 章、課程中文 Lab 為正文來源，講義內嵌連結與其他補充一律放收合；
稽核與規格見 tools/verification/ch9-svm-deepen-20261122/consult/audit.md。
上游各層照常執行，這裡在最後整節覆寫七節；可重用的元件、Lab 卡、quiz 與收合從上游輸出取出，id 不變。
內容分在三個模組：svm_a（prologue、maxmargin）、svm_b（soft、hinge）、svm_c（kernel、multiclass、vslogit）。
"""
import svm_a
import svm_b
import svm_c
from ensemble_deepen import _drop_deck_pages

SECS = ["prologue", "maxmargin", "soft", "hinge", "kernel", "multiclass", "vslogit"]

# 舊版留下、這次決定移除或更正的字串；任何一節還出現就報錯。
STALE = ["無論 C 調成多少", "下面的元件看不到", "上面元件的 OVA", "元件裡的三條線",
         "係數烘焙進頁面", "&y;", "&w;", "O(n²)～O(n³) 的"]


# 沿用上游段落裡、經審閱確認要更正的字串（每個必須恰好出現一次）：(節, 舊, 新)。
FIXES = [
    ("soft", "這導出正文三類", "這導出上表三類"),
    ("hinge", "就得到正文的兩種 $\\lambda$", "就得到上面的兩種 $\\lambda$"),
    ("vslogit", "slack 項消失，得到正文對偶。", "slack 項消失，得到上面的對偶。"),
    ("multiclass", "ISLP 對 K 不大的情況建議 OVO。", "講義建議 K 不大時用 OVO。"),
    ("maxmargin", "使用「輸出減目標」卻仍加到權重上會往錯誤方向走；",
     "使用「輸出減目標」卻仍加到權重上會往錯誤方向走（講義附錄的感知器式子寫成 $\\alpha(o_i-y_i)x_i$，照字面方向正好相反，要改成目標減輸出）；"),
    ("prologue", "<p>講義附錄以回應／特徵的資料型態整理統計方法，那是選方法的起點。",
     "<p>講義附錄以回應 $Y$ 與特徵 $X$ 的資料型態整理統計方法：兩者都連續用迴歸分析；$Y$ 離散、$X$ 連續時，$X$ 為 Gaussian 用 LDA、非 Gaussian 用邏輯斯迴歸；兩者都離散用判別對應分析（discriminant correspondence analysis）；$Y$ 連續、$X$ 離散用 ANOVA。這張表是選方法的起點，但分界不是絕對的。"),
]


def augment(BODIES, PAGEJS):
    old = dict(BODIES)
    new = {}
    for mod in (svm_a, svm_b, svm_c):
        part = mod.build(dict(old))
        dup = set(part) & set(new)
        if dup:
            raise ValueError(f"{mod.__name__} 重複產生：{dup}")
        new.update(part)
    if set(new) != set(SECS):
        raise ValueError(f"第 9 章各節不齊：多 {set(new) - set(SECS)}，少 {set(SECS) - set(new)}")
    for sid, old_s, new_s in FIXES:
        if new[sid].count(old_s) != 1:
            raise ValueError(f"{sid} 找不到（或不只一次）要更正的字串：{old_s[:30]}")
        new[sid] = new[sid].replace(old_s, new_s)
    BODIES.update({k: _drop_deck_pages(v) for k, v in new.items()})
    for sid in SECS:
        for s in STALE:
            if s in BODIES[sid]:
                raise ValueError(f"{sid} 殘留舊句：{s}")
    return PAGEJS
