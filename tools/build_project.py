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
    ("check", "P05", "用 AI 分析時要核對的事"),
    ("repro", "P06", "讓別人跑得出同樣的結果"),
    ("disclose", "P07", "AI 使用聲明與資料出處"),
    ("reference", "速查", "連結與查證日期"),
]

# ── P01 ────────────────────────────────────────────────────────────────
FLOW = f"""
<p>期末專題鼓勵大家用<strong>開放政府資料或其他真實資料</strong>，避免選用已被大量分析過的公開資料集。
現在的 AI coding agent（例如 Claude Code、Codex CLI、OpenCode）可以幫你搜尋資料目錄、讀欄位說明、寫下載與清理程式，
找資料這一步比以前省力很多。分析的想法與判斷仍須由你自己負責。MCP 能做與不能做的事見 <a href="#mcp">P03</a>；
請 AI 協助分析之前，先看 <a href="#check">P05 的核對清單</a>，更完整的原則在
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
下面用 Twinkle Hub 示範。</p>

<h3>1. 先了解 MCP 能做什麼</h3>
<p>可以把 MCP 想成會查目錄、也會替你算摘要的圖書館員；整份資料還是要自己到原機關下載。下表依專題階段整理：</p>
{table(["階段", "適合交給 MCP", "不要用 MCP 做"], [
    ["選題", "用中文描述想法，請它列出候選資料集、欄位、年份範圍、授權與提供機關",
     "替你決定題目：它只知道有沒有資料，不知道問題值不值得做"],
    ["找資料", "讀欄位定義、更新頻率與出處標示，找出原始檔的下載位置",
     "當成下載工具：免費方案每次最多回 10 列、沒有翻頁，抓不完大多數資料集"],
    ["初探", "用聚合確認各組筆數、平均值範圍與時間涵蓋，判斷題目是否可行",
     "當成正式分析：沒有中位數與分位數，聚合結果最多也只回 10 組"],
    ["建模", "不使用", "用線上查詢結果建模：助教沒有金鑰就無法重現，額度用完分析也會中斷"],
    ["報告", "引用回應附的授權與出處標示句", "把 MCP 回傳的數字直接寫進報告：每個數字都要能從本機的原始檔重算"],
])}
<p>Twinkle Hub 免費方案的限制（{CHECKED} 實測）：每次資料查詢扣 1 點，最多回 10 列，沒有翻頁。
聚合（count、sum、avg、min、max）會對符合條件的全部資料計算，但結果同樣最多回 10 組；
例如查高雄市各行政區的交易件數，只會拿到 38 區中的 10 區，要用條件分批查。
這個列數上限和點數無關，點數還有剩也一樣只回 10 列。</p>

<h3>2. 取得金鑰，放進環境變數</h3>
<p>到 {a("https://hub.twinkleai.tw/zh-TW", "Twinkle Hub")} 註冊，在 Dashboard 取得以 <code>sk-</code> 開頭的金鑰。
<strong>金鑰不要寫進程式碼、筆記本、投影片或要 commit 的設定檔</strong>，一律放在環境變數：</p>
{code('''
# macOS／Linux：寫進 ~/.zshrc 或 ~/.bashrc，重開終端機
export TWINKLE_HUB_API_KEY=sk-你的金鑰

# Windows PowerShell：設定後重開終端機
setx TWINKLE_HUB_API_KEY "sk-你的金鑰"
''')}

<h3>3. 依你用的 agent 加入 MCP 伺服器</h3>
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
已在 OpenCode 1.18 用真實金鑰實測可以查詢）。在專案根目錄建立 <code>opencode.json</code>：</p>
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
<p>沒有付費的 AI 訂閱也能先試：OpenCode 內建幾個免費模型（名稱以 <code>-free</code> 結尾，用 <code>opencode models</code> 查看），例如
<code>opencode run -m opencode/deepseek-v4.1-flash-free "你的問題"</code>。免費模型的清單會變動，以 <code>opencode models</code> 的結果為準。</p>

{info(f"實測結果（{CHECKED}）",
      "依上面三種設定各接一次，請 agent 查高雄市苓雅區 2025 年起的 3 筆實價登錄交易："
      "Claude Code、Codex CLI、OpenCode（免費模型）都查詢成功，結果相同，每次都只執行一次資料查詢、扣 1 點。"
      "Twinkle Hub 的實價登錄有專用資料集 <code>lvr-trades</code>（預售屋 <code>lvr-presale</code>、租賃 <code>lvr-rentals</code>），"
      "日期另有西元欄位 <code>iso_trade_date</code>。回應會附授權與出處標示句，可直接用在報告。"
      "要注意兩件事：免費方案每次最多回 10 列（回應標示 <code>truncated</code>），沒指定排序時也不是最新的資料；"
      "完整資料仍請到內政部實價登錄下載。", "green")}

<h3>4. 額度與學術方案</h3>
<p>Twinkle Hub 免費方案每 5 小時 50 點、每週最多 200 點（{CHECKED} 查證，方案可能調整，以
{a("https://hub.twinkleai.tw/zh-TW/pricing", "官方定價頁")}為準）。每次資料查詢扣 1 點，回應的 <code>meta.usage.credit_price</code> 會寫明；查詢工具清單與參數說明不是資料查詢。剩餘點數請到 Dashboard 查看。
需要更多額度可以用學校信箱申請 Edu 學術方案（申請方式見定價頁）；使用 Edu 方案的成果須註記「本研究由 Twinkle Hub 贊助資料服務」。</p>
{info("其他官方 MCP（依官方文件整理，尚未實測）",
      "<ul>"
      f"<li>{a('https://fred.stlouisfed.org/help/data/connecting-fred-to-ai-services/FRED-MCP-Connector', 'FRED')}：查美國與國際經濟時間序列，可產生 CSV／JSON 下載連結，下載後一樣存進 <code>data/raw/</code>。</li>"
      f"<li>{a('https://www.kaggle.com/docs/mcp', 'Kaggle')}：可搜尋並下載整份資料集，但要追到原始出處並確認授權。</li>"
      f"<li>{a('https://huggingface.co/docs/hub/en/hf-mcp-server', 'Hugging Face')}：搜尋機器學習資料集、讀資料卡；品質參差，授權要逐一確認。</li>"
      f"<li>{a('https://docs.datacommons.org/mcp/', 'Google Data Commons')}：回傳整理過的跨國或地區指標數值，沒有原始檔，適合快速比較；需要免費 API key。</li>"
      "</ul>"
      "設定方式依各服務的說明；需要登入的服務用 OAuth 登入（Claude Code 在對話中輸入 <code>/mcp</code>，Codex 用 <code>codex mcp login</code>）。")}
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

<h3>免費額度內做得到的查詢</h3>
<p>下面每個提問大約只需要一次資料查詢（1 點），實際次數以 agent 的呼叫紀錄為準。</p>
<ul>
  <li><strong>確認樣本數</strong>：「用 twinkle-hub 的 lvr-trades，統計高雄市三民區、苓雅區、左營區 2024 年的交易件數與平均單價，只回傳聚合結果。」
  三個區在 10 組以內，一次就能完整回傳。</li>
  <li><strong>確認期間涵蓋</strong>：「篩選苓雅區，回傳交易日期的最小值、最大值與筆數。」可以確認起訖年份，但不能據此認定中間沒有缺期。</li>
  <li><strong>先看真實值長相</strong>：「回傳苓雅區 2025 年起 10 筆交易，依交易日期由新到舊排序，附欄位說明與單位。」
  看過日期格式、單位與欄位內容，再請 agent 寫下載與清理程式。</li>
  <li><strong>找可以合併的資料</strong>：「找出可以和實價登錄依行政區合併的人口或所得資料集，列出欄位、年份、授權與原始下載網址，先不要下載。」</li>
</ul>
{info("常見誤用",
      "最常見的誤用有兩種。一種是用條件切很多次，把明細拼成訓練資料：一週最多約 2,000 列，抓到的列可能重複，也無法重現。"
      "另一種是把聚合結果當成分析：房價是偏態分布，平均數容易誤導，只回 10 組也可能漏掉部分地區。"
      "分析程式（例如 <code>analysis.py</code>）裡不要呼叫 MCP，一律讀本機的原始檔。", "warm")}
"""

# ── P05 ────────────────────────────────────────────────────────────────
CHECK = f"""
<p>AI 很會寫 scikit-learn 程式，也很會把結果講得頭頭是道，但統計學習專題最常出錯的地方，AI 預設不會替你檢查。
每次請 agent 分析的前後，都逐項核對下列事項：</p>
<ol>
  <li><strong>資料洩漏</strong>：標準化、補值、特徵選擇與調參只能用訓練資料估計（例如放進 <code>Pipeline</code> 再做交叉驗證）；
  有時間順序的資料按時間切分，同一地區或個體重複出現時要分組切分；測試集只在最後用一次。AI 產生的程式若只有一行 <code>train_test_split</code>，就要特別檢查這幾點。</li>
  <li><strong>資料本身</strong>：確認每一列代表什麼，以及欄位定義與單位（民國年或西元年、總價或單價、坪或平方公尺）；
  合併、篩選、刪除缺值前後都印出列數，看樣本有沒有悄悄變少或變偏。</li>
  <li><strong>評估方式</strong>：先建立基準模型（例如線性或邏輯斯迴歸），依任務選擇驗證方式與指標，回報交叉驗證的平均與變異，不要只挑表現最好的一次。</li>
  <li><strong>解讀結果</strong>：不只看 p 值或 accuracy，也要說明效果大小、不確定性與限制；類別不平衡時改看 precision、recall 或 AUC；相關不等於因果。</li>
  <li><strong>查證 AI 的說法</strong>：AI 會自信地解釋欄位，甚至編出不存在的欄位或論文。欄位意義回原機關的說明核對，文獻要自己找到原文，報告裡的數字都要由你的程式重算。</li>
  <li><strong>保護資料</strong>：個資、未公開資料與金鑰不要貼進雲端 AI 服務。</li>
</ol>
<p>怎麼把分析拆成小任務、要留哪些協作紀錄、哪些資料不能上傳，見
<a href="../00c_ai_assisted.html">課前準備 C：用 AI 做統計分析</a>。</p>
"""

# ── P06 ────────────────────────────────────────────────────────────────
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

# ── P07 ────────────────────────────────────────────────────────────────
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

BODIES = {"flow": FLOW, "sources": SOURCES, "mcp": MCP, "prompts": PROMPTS, "check": CHECK,
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
