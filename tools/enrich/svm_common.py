"""第 9 章整節重寫（svm_deepen）共用的小工具。

`old` 一律是上游各層（enrich_svm 本體 → svm_completion → reading_flow → teaching_scope →
lecture_alignment_ch9）跑完後的 BODIES 快照；這裡只從裡面「取出」可重用的元件與段落，不修改它。
"""
import re

from ens_common import grab_details, grab_viz, _div_block  # noqa: F401
from lib import card, detail, info, info_card, lab_code, lab_output, proof, qa, quiz, table  # noqa: F401

LAB = "Ch09-svm-lab-zh.ipynb"


def chunk(cell, start=None, end=None):
    s = lab_code(9, cell)
    if start is not None:
        s = s[s.index(start):]
    if end is not None:
        s = s[:s.index(end)]
    return s.rstrip()


def lab(label, cell, out=None, start=None, end=None, note=None):
    """一張第 9 章 lab 程式卡：程式逐字取自儲存格 cell，輸出逐字取自儲存格 out。"""
    return card(label, chunk(cell, start, end), lab_output(9, out) if out else None,
                note=note, src=f"<code>{LAB}</code> · 儲存格 {cell}")


def links(items):
    """「本主題的講義來源與延伸閱讀」：items = [(url, 中文標籤), ...]。"""
    a = "、".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for u, t in items)
    return f'<p class="source-links">本主題的講義來源與延伸閱讀：{a}。</p>'


def grab_block(body, start_marker):
    """回傳從 start_marker（必須恰好出現一次）開始的整個 <div …>…</div>。"""
    if body.count(start_marker) != 1:
        raise ValueError(f"標記出現 {body.count(start_marker)} 次：{start_marker[:40]}")
    a = body.index(start_marker)
    return body[a:_div_block(body, a)]


def grab_quiz(body, qid):
    """回傳含 id={qid}Options 的整個 quiz-box。"""
    k = body.find(f'id="{qid}Options"')
    if k < 0:
        raise ValueError("找不到 quiz：" + qid)
    a = body.rfind('<div class="quiz-box">', 0, k)
    return body[a:_div_block(body, a)]


def grab_qa(body, question_start):
    """回傳以 question_start 開頭的那一則觀念釐清 <details class="qa-item"> … </details>（無 id）。"""
    k = body.find("<summary>" + question_start)
    if k < 0:
        raise ValueError("找不到 Q&A：" + question_start)
    a = body.rfind("<details", 0, k)
    depth = 0
    for t in re.finditer(r"<details\b|</details>", body[a:]):
        depth += -1 if t.group().startswith("</") else 1
        if depth == 0:
            return body[a:a + t.end()]
    raise ValueError("Q&A 沒有結束：" + question_start)


def qa_wrap(head, items_html):
    """把已組好的 <details class="qa-item"> 字串包成觀念釐清方框。"""
    return f'<div class="qa-box">\n  <div class="qa-head">{head}</div>\n' + "\n".join(items_html) + "\n</div>"


A = lambda u, t: f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'  # noqa: E731

URL = {
    "vidhya": "https://www.analyticsvidhya.com/blog/2021/07/deep-understanding-of-discriminative-and-generative-models-in-machine-learning/",
    "dist": "https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line",
    "proj": "https://en.wikipedia.org/wiki/Scalar_projection",
    "h202": "https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf",
    "duality": "https://en.wikipedia.org/wiki/Duality_(optimization)",
    "h204": "https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf",
    "cmu": "https://www.cs.cmu.edu/~epxing/Class/10701-08s/recitation/svm.pdf",
    "bourret": "https://xavierbourretsicotte.github.io/Kernel_feature_map.html",
    "cs229": "https://cs229.stanford.edu/notes2021fall/cs229-notes3.pdf",
    "cs229main": "https://cs229.stanford.edu/notes2022fall/main_notes.pdf",
    "so_rbf": "https://stackoverflow.com/questions/23581508/why-gaussian-radial-basis-function-maps-the-examples-into-an-infinite-dimensiona",
    "mercer": "https://en.wikipedia.org/wiki/Mercer%27s_theorem",
    "esl121": "https://yuhangzhou88.github.io/ESL_Solution/ESL-Solution/_12-Flexible-Discriminants/ex12-01/",
    "hinge1": "https://math.stackexchange.com/questions/3576111/hinge-loss-why-1",
    "logloss": "https://stats.stackexchange.com/questions/229645/why-there-are-two-different-logistic-loss-formulation-notations",
    "sgd": "https://scikit-learn.org/1.6/modules/sgd.html",
    "kapprox": "https://scikit-learn.org/1.6/modules/kernel_approximation.html",
    "h206": "https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf",
    "htlin": "https://www.csie.ntu.edu.tw/~htlin/mooc/",
    "sksvm": "https://scikit-learn.org/1.6/modules/svm.html",
    "perceptron": "https://scikit-learn.org/1.6/modules/linear_model.html#perceptron",
}
