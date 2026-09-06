"""Reader-facing book names and links; metadata keeps its existing source keys."""
import html
import re

BOOKS = {
    "Seeing-Theory": ("統計入門參考", "Seeing Theory",
                      "Tyler Dae Devlin、Jingru Guo、Daniel Kunin、Daniel Xiang，2018 年講義草稿",
                      "https://seeing-theory.brown.edu/"),
    "ISLP": ("教科書", "An Introduction to Statistical Learning with Applications in Python",
             "James、Witten、Hastie、Tibshirani、Taylor，2023",
             "https://www.statlearning.com/"),
    "ESL": ("進階參考", "The Elements of Statistical Learning",
            "Hastie、Tibshirani、Friedman，第二版",
            "https://hastie.su.domains/ElemStatLearn/"),
    "AI-Stats": ("AI 協作參考書", "AI-Assisted Statistics for Data Scientists",
                 "Peter Bruce、Andrew Bruce、Peter Gedeck，第三版，2026",
                 "https://github.com/gedeck/ai-assisted-statistics-for-data-scientists"),
}
AI_TOPICS = {
    "Preface": "AI 協作的責任界線（前言）",
    "10": "生成式 AI 與提示設計（第 10 章）",
    "11": "AI 分析的限制與責任（第 11 章）",
}


def source_key(label):
    return next((k for k in BOOKS if label.startswith(k + " ")), None)


def source_id(page, key):
    return f"w{page.n:02d}-source-{key.lower()}"


def label_text(label):
    """Translate a source locator without changing chapter/section numbers."""
    key = source_key(label)
    if key == "AI-Stats":
        loc = label.removeprefix("AI-Stats §")
        return "參考：" + AI_TOPICS[loc]
    if key:
        loc = label[len(key):].strip()
        loc = re.sub(r"§(\d+) 開頭", r"第 \1 章開頭", loc)
        loc = re.sub(r"§([\d.]+(?:[–-][\d.]+)?)", r"第 \1 節", loc)
        loc = re.sub(r"Ch\.([\d]+)", r"第 \1 章", loc)
        return BOOKS[key][0] + " · " + loc
    return label


def badge(page, label):
    key = source_key(label)
    text = html.escape(label_text(label))
    if key:
        text = f'<a href="#{source_id(page, key)}">{text}</a>'
    return f'<span class="sec-badge">{text}</span>'


def page_books(page):
    if page.grounding_mode == "concept":
        return list(dict.fromkeys(source_key(b.strip()) for s in page.secs
                                 for b in s.badge.split("|") if source_key(b.strip())))
    keys = ["ISLP"]
    if page.esl_label or any("ESL " in s.badge for s in page.secs):
        keys.append("ESL")
    if any("AI-Stats " in s.badge for s in page.secs):
        keys.append("AI-Stats")
    return keys


def introduction(page):
    items = []
    for key in page_books(page):
        role, title, authors, _ = BOOKS[key]
        suffix = "" if key == "Seeing-Theory" else (f"（{key}）" if key != "AI-Stats" else "（第三版）")
        items.append(f'{role}：<cite>{title}</cite>{suffix}')
    return '<p class="source-intro">' + "；<br>".join(items) + "。章節旁的來源標記可點到本頁書目。</p>"


def bibliography(page):
    items = []
    for key in page_books(page):
        role, title, authors, url = BOOKS[key]
        locs = list(dict.fromkeys(label_text(b.strip()) for s in page.secs
                                 for b in s.badge.split("|") if source_key(b.strip()) == key))
        loc_text = "；".join(locs)
        link_label = "作者提供的程式與資料" if key == "AI-Stats" else "原書與下載資訊"
        items.append(f'<li id="{source_id(page, key)}"><strong>{role}</strong>：'
                     f'<cite>{title}</cite>。{authors}。'
                     f'<a href="{url}" target="_blank" rel="noopener">{link_label}</a>'
                     + (f'<br>本頁對應：{loc_text}。' if loc_text else "") + '</li>')
    return '<div class="source-list"><h3>本頁書目與章節定位</h3><ul>' + "\n".join(items) + '</ul></div>'
