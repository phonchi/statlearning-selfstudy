#!/usr/bin/env python3
"""產生 project/index.html：期末專題的真實資料來源與 AI agent（MCP）上手指南。冪等。

這頁不在 tools/pages.py 裡（不是教材章節，沒有 lab 出處、詞彙卡與題庫），
做法比照 island/：內容寫在本檔，樣式 inline base.css + stats.css + project.css，
validate.py 的 check_project() 會重建後逐 byte 比對、檢查用語與站內連結。
學期日期、配分等每年會變的規定不寫在這裡，以當學期的期末專題規範為準。
額度、方案與設定指令會變動，頁面標注查證日期；改內容時一併更新 CHECKED。
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, TEMPLATE  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "enrich"))
from lib import detail, info, table  # noqa: E402

OUT = ROOT / "project" / "index.html"
CHECKED = "2026-11-04"
TITLE = "期末專題：真實資料 × AI agent 上手指南"


def a(url, label=None):
    return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{label or url}</a>'


def code(text):
    return f'<div class="pseudo-code"><pre>{html.escape(text.strip())}</pre></div>'


SECTIONS = [
    ("flow", "P01", "先想問題，再找資料"),
    ("sources", "P02", "推薦的資料來源"),
    ("mcp", "P03", "把資料來源接進 AI agent"),
    ("prompts", "P04", "可以這樣問 agent"),
    ("repro", "P05", "讓別人跑得出同樣的結果"),
    ("disclose", "P06", "AI 使用聲明與資料出處"),
    ("reference", "速查", "連結與查證日期"),
]

# ── P01 ────────────────────────────────────────────────────────────────
FLOW = f"""
<p>期末專題鼓勵大家用<strong>開放政府資料或其他真實資料</strong>，避免選用已被大量分析過的公開資料集。
現在的 AI coding agent（例如 Claude Code、Codex CLI、OpenCode）可以幫你搜尋資料目錄、讀欄位說明、寫下載與清理程式，
找資料這一步比以前省力很多。分析的想法與判斷仍須由你自己負責，AI 協作的原則請先讀
<a href="../00c_ai_assisted.html">課前準備 C：用 AI 做統計分析</a>。</p>
<div class="project-steps">
  <div class="step"><b>① 先寫下問題</b>想回答什麼？結果要給誰看？一列資料代表什麼？</div>
  <div class="step"><b>② 讓 agent 幫你找</b>用自然語言描述需求，請它列出候選資料集、欄位、時間範圍與授權。</div>
  <div class="step"><b>③ 下載原始檔</b>回到資料的原始機關下載，存進 <code>data/raw/</code>，記下網址與取得日期。</div>
  <div class="step"><b>④ 在本機分析</b>之後的清理、EDA、建模都從本機的原始檔開始跑，不再依賴線上查詢。</div>
</div>
{info("為什麼要把原始檔存下來？",
      "線上查詢服務有額度限制，API 資料也會更新或修訂。只要原始檔存在本機，"
      "額度用完、服務改版或資料被更新，都不影響你的專題，助教也能重現你的結果。")}
"""

# ── P02 ────────────────────────────────────────────────────────────────
SOURCES = f"""
<p>下表的來源都不強制使用，任何可靠的來源都可以。前五個是台灣政府機關的官方資料，都免費，授權條款請到各站確認；
Twinkle Hub 適合用中文描述需求、讓 agent 幫你找資料；做國際題目可以看 FRED 與 Our World in Data。</p>
{table(["來源", "適合的題目", "怎麼取得", "帳號／金鑰"], [
    [a("https://data.gov.tw/", "政府資料開放平臺"), "各部會資料，題材最廣",
     "網頁下載（CSV、JSON、XML）；也有不需金鑰的 REST API", "不需要"],
    [a("https://plvr.land.moi.gov.tw/DownloadOpenData", "內政部不動產實價登錄"), "房價、迴歸、空間差異",
     "下載 ZIP（本期與按季資料），檔案固定、容易重現", "不需要"],
    [a("https://nstatdb.dgbas.gov.tw/dgbasall/webMain.aspx?k=dgmain", "主計總處總體統計資料庫"), "總體經濟時間序列",
     "網頁查詢；也有匿名 API（回傳 JSON）", "不需要"],
    [a("https://cpx.cbc.gov.tw/", "中央銀行統計資料庫"), "匯率、利率、金融資料",
     "網頁查詢；API 回傳 JSON", "不需要"],
    [a("https://opendata.cwa.gov.tw/", "中央氣象署開放資料平臺"), "天氣、氣候、災害",
     "API 與檔案下載；API 多為近期資料，要自己存快照", "免費會員授權碼"],
    [a("https://hub.twinkleai.tw/zh-TW", "Twinkle Hub"), "用中文搜尋台灣約 5 萬筆政府資料",
     "MCP（見 P03）；只能查詢、沒有整包下載，找到後回原機關下載", "註冊取得金鑰；免費額度有限"],
    [a("https://fred.stlouisfed.org/", "FRED"), "美國與國際經濟指標",
     "網頁下載 CSV；也有官方 MCP", "下載不需要；MCP 需登入"],
    [a("https://ourworldindata.org/", "Our World in Data"), "跨國比較（健康、能源、人口…）",
     "每張圖都能下載 CSV，附資料說明", "不需要"],
    [a("https://www.kaggle.com/datasets", "Kaggle"), "各式整理好的資料集",
     "網頁、<code>kaggle</code> CLI 或官方 MCP", "需要帳號"],
])}
{info("Kaggle 與二手資料",
      "Kaggle 上很多資料是別人整理過的二手資料。使用前先追到原始出處，確認授權與收集方式；"
      "熱門資料集要另外找出新的問題，不要只是重做他人已完成的分析。", "purple")}
{detail("project-more-sources", "其他可以參考的來源",
        "<ul>"
        f"<li>{a('https://tdx.transportdata.tw/', '交通部 TDX 運輸資料流通服務')}：交通資料很完整，但要註冊並等管理員審核，多為即時資料，需要自己存快照。</li>"
        f"<li>{a('https://huggingface.co/docs/hub/en/hf-mcp-server', 'Hugging Face MCP')}：搜尋機器學習資料集；品質參差，授權要逐一確認。</li>"
        f"<li>{a('https://docs.datacommons.org/mcp/', 'Google Data Commons MCP')}：整合各國社經指標；需要免費 API key，只回傳數值、沒有原始檔。</li>"
        f"<li>{a('https://datahelpdesk.worldbank.org/knowledgebase/articles/889392', 'World Bank Indicators API')}：跨國發展指標，不需要金鑰。</li>"
        f"<li>{a('https://archive.ics.uci.edu/', 'UCI Machine Learning Repository')}、{a('https://www.openml.org/', 'OpenML')}：經典資料集，適合當方法比較的基準，不適合當應用型專題的主題資料。</li>"
        "</ul>")}
{info("台灣政府資料常見的坑",
      "檔案編碼可能是 Big5（<code>pd.read_csv(..., encoding='cp950')</code>）；日期常用民國年（加 1911 才是西元）；"
      "同一份資料不同年度的欄位名稱可能不一樣；數字欄位可能夾著千分位逗號；有些檔案有兩列表頭。"
      "讀進來之後先檢查欄位型態、缺值與單位，再開始分析。", "warm")}
"""

# ── P03 ────────────────────────────────────────────────────────────────
MCP = f"""
<p><strong>MCP</strong>（Model Context Protocol）是讓 AI agent 呼叫外部工具的標準介面。
資料平台有 MCP 端點，agent 就能自己搜尋資料目錄、查資料，不必手動逐頁瀏覽網站。
下面用 Twinkle Hub 示範；其他提供遠端 MCP 的服務接法相同，只需更換網址與登入方式。</p>

<h3>1. 取得金鑰，放進環境變數</h3>
<p>到 {a("https://hub.twinkleai.tw/zh-TW", "Twinkle Hub")} 註冊，在 Dashboard 取得以 <code>sk-</code> 開頭的金鑰。
<strong>金鑰不要寫進程式碼、筆記本、投影片或要 commit 的設定檔</strong>，一律放在環境變數：</p>
{code('''
# macOS／Linux：寫進 ~/.zshrc 或 ~/.bashrc，重開終端機
export TWINKLE_HUB_API_KEY=sk-你的金鑰

# Windows PowerShell：設定後重開終端機
setx TWINKLE_HUB_API_KEY "sk-你的金鑰"
''')}

<h3>2. 依你用的 agent 加入 MCP 伺服器</h3>
<p><strong>Claude Code</strong>（Twinkle Hub 官方文件提供的指令，金鑰改從環境變數帶入）：</p>
{code('''
claude mcp add --transport http twinkle-hub https://api.twinkleai.tw/mcp/ \\
  --header "Authorization: Bearer $TWINKLE_HUB_API_KEY"
claude mcp list        # 確認狀態
''')}
<p>這個設定預設存在你自己的使用者設定裡，不會進入專案。請不要加 <code>--scope project</code>，否則金鑰會寫進專案的 <code>.mcp.json</code>，commit 後就會外流。</p>

<p><strong>Codex CLI</strong>（Twinkle Hub 官方文件）：</p>
{code('''
codex mcp add twinkle-hub --url https://api.twinkleai.tw/mcp/ \\
  --bearer-token-env-var TWINKLE_HUB_API_KEY
codex mcp list
''')}
<p>如果啟動時出現 30 秒逾時，在 <code>~/.codex/config.toml</code> 的 <code>[mcp_servers.twinkle-hub]</code> 底下加一行 <code>startup_timeout_sec = 60</code>。</p>

<p><strong>OpenCode</strong>（Twinkle Hub 文件沒寫，下面照 {a("https://opencode.ai/docs/mcp-servers/", "OpenCode 官方 MCP 說明")} 寫成，
在 OpenCode 1.18 試過：設定讀得到，也連得上端點）。在專案根目錄建立 <code>opencode.json</code>：</p>
{code('''
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "twinkle-hub": {
      "type": "remote",
      "url": "https://api.twinkleai.tw/mcp/",
      "oauth": false,
      "headers": { "Authorization": "Bearer {env:TWINKLE_HUB_API_KEY}" }
    }
  }
}
''')}
<p><code>{{env:...}}</code> 會在執行時讀環境變數，所以這個檔案裡沒有金鑰，可以放進 Git。用 <code>opencode mcp list</code> 確認狀態。</p>

<h3>3. 額度與學術方案</h3>
<p>Twinkle Hub 免費方案每 5 小時 50 點、每週最多 200 點，多數查詢扣 1 點（{CHECKED} 查證，方案可能調整，以
{a("https://hub.twinkleai.tw/zh-TW/pricing", "官方定價頁")}為準）。這個額度拿來找資料夠用，
拿來反覆抓大量資料就不夠，所以才要照 P01 的流程，找到後回原機關下載。
需要更多額度可以用學校信箱申請 Edu 學術方案（申請方式見定價頁）；使用 Edu 方案的成果須註記「本研究由 Twinkle Hub 贊助資料服務」。</p>
{info("其他官方 MCP",
      f"{a('https://fred.stlouisfed.org/help/data/connecting-fred-to-ai-services/FRED-MCP-Connector', 'FRED')}、"
      f"{a('https://www.kaggle.com/docs/mcp', 'Kaggle')}、"
      f"{a('https://huggingface.co/docs/hub/en/hf-mcp-server', 'Hugging Face')} 也提供官方遠端 MCP。"
      "接法同上：換成各自的網址；需要登入的服務，依各家說明用 OAuth 登入（Claude Code 在對話中輸入 <code>/mcp</code>，Codex 用 <code>codex mcp login</code>）。")}
"""

# ── P04 ────────────────────────────────────────────────────────────────
PROMPTS = f"""
<p>提問時把問題、限制和你要的輸出講清楚，agent 給的東西會好用很多。三個例子：</p>
{code('''
找資料：
我想研究高雄市近十年住宅交易價格和屋齡、捷運距離的關係。
請用 twinkle-hub 找出相關的政府資料集，列出資料集名稱、提供機關、
時間範圍、主要欄位、更新頻率、授權，以及原始檔的下載網址。先不要下載。
''')}
{code('''
下載並記錄出處：
請寫 src/fetch_data.py，從上面選定的原始網址下載 2016–2025 年的檔案到 data/raw/，
不要修改原始檔。同時在 data/SOURCES.md 記下每個檔案的網址、提供機關、
授權、下載日期與篩選條件。需要金鑰的話從環境變數讀取。
''')}
{code('''
先檢查資料：
讀 data/raw/ 的檔案，回報每個欄位的型態、缺值比例、單位與可疑的值
（例如負的面積、民國年未轉換）。只回報，不要自動刪資料。
''')}
<p>agent 回報的欄位意義、單位與資料筆數，都要自己對照原始資料說明再確認一次。</p>
"""

# ── P05 ────────────────────────────────────────────────────────────────
REPRO = f"""
<p>期末專題要求<strong>繳交的程式能從頭跑完，重現報告裡的數字與圖</strong>。專案可以照這個結構整理：</p>
{code('''
my-project/
├── README.md          # 怎麼跑：環境、執行指令、會產生哪些圖表
├── requirements.txt   # 套件與版本（pip freeze > requirements.txt）
├── data/
│   ├── raw/           # 原始檔，下載後不手改
│   └── SOURCES.md     # 來源網址、授權、取得日期、查詢條件
├── src/
│   ├── fetch_data.py  # 下載資料（金鑰從環境變數讀）
│   └── analysis.py    # 從 data/raw 一路跑到報告裡的數字與圖
├── .env               # 金鑰只放本機
└── .gitignore         # 列入 .env；太大的資料檔也排除
''')}
<ul>
  <li>切分資料、交叉驗證、隨機森林這類有隨機性的步驟，都要設 <code>random_state</code>。</li>
  <li>小檔案直接附上；大檔案附下載連結或 <code>fetch_data.py</code>，寫明取得日期。
  經 API 或 MCP 查到的資料，要存成檔案一起附上，助教重現時不應該需要任何金鑰。</li>
  <li>交件前找個乾淨的環境（新的 Colab 或新的虛擬環境），照 README 從頭跑一次，確認數字和圖跟報告一樣。</li>
</ul>
<p>AI 協作的過程要記哪些東西，可以參考 <a href="../00c_ai_assisted.html#record">課前準備 C 的紀錄表</a>；
同一節也講了哪些資料（例如個資、未公開的研究資料）不該貼進雲端 AI 服務。</p>
"""

# ── P06 ────────────────────────────────────────────────────────────────
DISCLOSE = f"""
<p>歡迎使用 AI 工具，但<strong>書面報告與簡報都要簡短說明</strong>用了哪些工具、用在哪裡，
不需要附對話紀錄。報告放在 Acknowledgements 裡，簡報放一張投影片或某頁的角落即可。例如：</p>
{code('''
AI use: We used Claude Code to search Taiwan open-data catalogs and to draft
the data-cleaning code, and ChatGPT to polish the English in Sections 1–2.
All code was run and checked by the team, and every number in this report
comes from our own code.
''')}
<p>資料出處也要寫清楚。政府資料開放授權條款要求標示來源，例如：</p>
{code('''
資料來源：內政部不動產實價登錄開放資料（政府資料開放授權條款第 1 版），
2026-11-04 下載。
''')}
{info("你仍然要為結果負責",
      "AI 產生的統計量、圖表與參考文獻都可能出錯，甚至編出不存在的論文。"
      "放進報告前，每個數字都要能從你的程式重算出來，每篇引用都要自己查證過。", "warm")}
"""

# ── 速查 ───────────────────────────────────────────────────────────────
REFERENCE = f"""
{table(["項目", "連結"], [
    ["Twinkle Hub 設定說明（Claude）", a("https://hub.twinkleai.tw/zh-TW/docs?aud=claude")],
    ["Twinkle Hub 設定說明（Codex）", a("https://hub.twinkleai.tw/zh-TW/docs?aud=codex")],
    ["Twinkle Hub 方案與額度", a("https://hub.twinkleai.tw/zh-TW/pricing")],
    ["Claude Code MCP 說明", a("https://code.claude.com/docs/en/mcp")],
    ["OpenCode MCP 說明", a("https://opencode.ai/docs/mcp-servers/")],
    ["政府資料開放授權條款", a("https://data.gov.tw/license")],
    ["AI 協作原則與紀錄表", '<a href="../00c_ai_assisted.html">課前準備 C：用 AI 做統計分析</a>'],
    ["找資料與開始 EDA", '<a href="../introduction.html#datasets">第 1 章：資料集入口</a>'],
])}
<p class="project-checked">本頁的額度、方案與指令於 {CHECKED} 查證，服務可能調整，請以各官方頁面為準。
學期日期、繳交方式與評分重點以當學期的期末專題規範為準。</p>
"""

BODIES = {"flow": FLOW, "sources": SOURCES, "mcp": MCP, "prompts": PROMPTS,
          "repro": REPRO, "disclose": DISCLOSE, "reference": REFERENCE}


def build():
    css = "\n\n".join((TEMPLATE / n).read_text(encoding="utf-8").rstrip()
                      for n in ("base.css", "stats.css", "project.css"))
    toc = "\n".join(f'<a href="#{sid}"><span class="toc-num">{num}</span>{name}</a>'
                    for sid, num, name in SECTIONS)
    secs = []
    for sid, num, name in SECTIONS:
        label = "QUICK REFERENCE · 速查" if sid == "reference" else f"PART {num[1:]} · 第 {int(num[1:])} 節"
        secs.append(f'<section id="{sid}">\n<div class="section-number">{label}</div>\n'
                    f'<h2>{name}</h2>\n{BODIES[sid].strip()}\n</section>')
    sections = "\n\n".join(secs)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="統計學習期末專題指南：推薦的開放政府與真實資料來源、用 MCP 把資料來源接進 Claude Code／Codex／OpenCode、可重現的專題結構與 AI 使用聲明。">
<title>{TITLE} — NSYSU MATH524</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="hero" id="top">
  <div class="hero-grid"></div>
  <div class="hero-content">
    <h1>期末專題：<span class="green">真實資料</span> × <span class="blue">AI agent</span></h1>
    <div class="subtitle">找資料、接上 Claude Code／Codex／OpenCode、留下能重現的分析</div>
    <div class="big-formula">先寫問題｜讓 agent 找資料｜下載原始檔｜本機分析｜記錄出處</div>
  </div>
</div>

<div class="container">
<div class="study-guide">
  <div class="sg-title">📌 這頁給誰看</div>
  <p>準備期末專題、想用開放政府資料或其他真實資料的同學。這頁介紹推薦的資料來源，
  示範怎麼用 MCP 把資料來源接進 AI agent，以及交件時怎麼讓結果可以重現。
  使用哪個來源、哪個 AI 工具都不強制。</p>
  <div class="sg-links"><a href="../index.html">🏠 回到首頁</a><a href="../00c_ai_assisted.html">🤖 課前準備 C：用 AI 做統計分析</a></div>
</div>

<div class="toc">
  <div class="toc-title">CONTENTS · 內容目錄</div>
  <div class="toc-grid">
{toc}
  </div>
</div>

{sections}
</div>

<footer>
  統計學習 × Python 互動自學網站 · 期末專題指南 · 查證日期 {CHECKED}<br>
  <a href="../index.html">回到首頁</a>
</footer>
</body></html>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
