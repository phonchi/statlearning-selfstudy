"""Seeing Theory statistics prerequisite metadata; IDs remain stable."""
WEB = "https://seeing-theory.brown.edu/"
PDF = WEB + "doc/seeing-theory.pdf"

# PDF page numbers are one-based PDF viewer pages, matching printed numbers here.
SPECS = [
    ("s1_probability", "機率、平均與變異", "Probability, Expectation and Variance", "basic-probability", 5,
     [("population", "母體與樣本"), ("chance", "事件與機率"),
      ("expectation", "隨機變數與期望值"), ("variation", "變異數與長期平均")]),
    ("s2_conditional", "條件機率與獨立", "Conditional Probability", "compound-probability", 19,
     [("events", "集合與事件"), ("conditional", "條件機率"), ("independence", "獨立與互斥"),
      ("bayes", "Bayes 公式"), ("counting", "計數〔選讀〕")]),
    ("s3_distributions", "分布與抽樣", "Distributions and Sampling", "probability-distributions", 31,
     [("variables", "隨機變數與分布"), ("density", "離散與連續"), ("families", "常用分布"),
      ("sampling", "抽樣分布"), ("clt", "大數法則與中央極限定理")]),
    ("s4_inference", "從樣本推論母體", "Frequentist Inference", "frequentist-inference", 41,
     [("estimation", "點估計與偏差"), ("standard_error", "標準差與標準誤"),
      ("intervals", "信賴區間"), ("testing", "假設檢定與 p 值"),
      ("errors", "兩類錯誤"), ("bootstrap", "Bootstrap 入門")]),
    ("s5_bayesian", "貝氏推論〔選讀〕", "Bayesian Inference", "bayesian-inference", 49,
     [("review", "Bayes 公式回顧"), ("likelihood", "概似與最大概似"),
      ("posterior", "先驗到後驗"), ("influence", "資料量與先驗影響")]),
    ("s6_regression", "相關與迴歸〔選讀〕", "Correlation and Regression", "regression-analysis", 55,
     [("covariance", "共變異數與相關"), ("least_squares", "最小平方法"),
      ("residuals", "殘差與解讀限制"), ("anova", "ANOVA 入門〔延伸〕")]),
]

SOURCE_CHAPTERS = {
    i+1: (WEB + spec[3] + "/index.html", spec[4],
          SPECS[i+1][4]-1 if i+1 < len(SPECS) else 66)
    for i, spec in enumerate(SPECS)
}


def make_pages(Page, Sec):
    pages = []
    for i, (stem, title, en, web, pdf, sections) in enumerate(SPECS, 1):
        pages.append(Page(
            n=20+i, stem=stem, slug=f"S{i} · STATISTICS", title_en=en,
            h1=title.replace("〔選讀〕", "") + '<br><span class="blue">統計先備知識</span>',
            plain=title, subtitle="選讀，不列入評分。用算例與互動理解統計，不需要 Python 或微積分基礎。",
            formula="觀察｜機率模型｜抽樣變動｜推論",
            deck="", deck_pages=0, lab="", islp=0,
            islp_label=f"先備 · S{i} 統計" + ("〔選讀〕" if i >= 5 else "〔核心路徑〕"),
            esl_label="", playlist="", hero_svg="",
            kind="prep", group="statistics", grounding_mode="concept", data_key="stats_"+stem,
            secs=[Sec(sid, label, label, f"Seeing-Theory Ch.{i}") for sid, label in sections],
            extra_pills=[("🔗 Seeing Theory 互動原站", WEB+web+"/index.html"),
                         ("📖 Seeing Theory 講義", PDF+f"#page={pdf}"),
                         ("🔗 直接進入正課", "introduction.html")],
            ex_links=[("🔗 本章原站延伸", WEB+web+"/index.html")],
            nav_next="introduction" if i == 6 else "",
        ))
    return pages
