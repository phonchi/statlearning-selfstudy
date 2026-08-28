#!/usr/bin/env python3
"""00b_setup.html（課前準備 B · 環境安裝）完整自學充實。冪等。

內容依據：課程 lab 每一份的前幾格（%pip install ISLP、imports、掛 Drive）。
以 Colab 為主、本機 conda 為輔，因為第一次上手最重要的是「先能跑」。

版本清單一律引用 pages.ENV_NOTE，不要在內文自己抄一份。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pages as P  # noqa: E402
from lib import (apply, card, hl, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LAB1 = "Ch01-lab-zh.ipynb"
LAB2 = "Ch02-statlearn-lab-zh.ipynb"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB1 if ch == 1 else LAB2
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 先能跑 ───────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>環境這件事有一個常見的誤區：想先把最完整的設定弄好，再開始學。
  結果是花了一個下午裝東西，一行統計程式都還沒跑過。
  <strong>順序反過來</strong>——先用三分鐘在瀏覽器裡跑出第一張圖，
  等你確定要長期用了，再回來做本機安裝。</p>

{info("三分鐘版本", '① 開 <a href="https://colab.research.google.com/" target="_blank" '
      'rel="noopener">Colab</a>；② 新增一個 notebook；③ 第一格貼 ' 
      "<code>%pip install ISLP</code> 按執行；④ 第二格貼課程 lab 的 imports；"
      "⑤ 開始跑。就這樣。")}

{viz(svg("w13pathSvg", 320),
     [info_card("三條路，先選最上面那條",
                "按按鈕比較三種環境。第一次上手<strong>一律選 Colab</strong>，"
                "它零安裝而且跟課程 lab 的環境最接近。"),
      rows_card("這一條路",
                [("要花多久", "—", "w13paTime"),
                 ("好處", "—", "w13paPro"),
                 ("代價", "—", "w13paCon")]),
      info_card("為什麼不建議一開始就裝本機",
                "本機安裝會遇到的問題（權限、路徑、版本衝突）跟統計學習一點關係都沒有，"
                "但它們很會消耗你的耐心。"
                "<strong>把耐心留給真正的課程內容。</strong>")],
     "w13paStatus", "三條路，先看它們各自的代價。",
     '<button class="btn btn-toggle" onclick="w13paSet(0)">① Colab（推薦）</button>'
     '<button class="btn btn-toggle" onclick="w13paSet(1)">② 本機 conda</button>'
     '<button class="btn btn-toggle" onclick="w13paSet(2)">③ 本機 pip + venv</button>')}

{card("裝課程用的套件", C(1, 3), src=S(1, 3),
      note="<code>%pip</code> 開頭的百分比符號是 Jupyter 的魔術指令，"
           "意思是「裝到<strong>這個 notebook 正在用的</strong> Python 裡」——"
           "比在終端機打 <code>pip install</code> 保險。")}

{card("ISLP 會順便裝一整套相依", C(2, 8), O(2, 8), src=S(2, 8),
      note="輸出很長，因為 numpy、pandas、scikit-learn、statsmodels 都是它的相依。"
           "裝完 Colab 可能會叫你重啟執行階段，照做。")}

{quiz("qPath", "PART 00 · 自我檢測",
      "你第一次要跑課程的 lab，手邊只有一台學校的公用電腦。最合理的做法是？",
      [(True, "用 Colab，登入自己的 Google 帳號",
        "對。公用電腦多半沒有安裝權限，而且你也不會想把環境留在別人的機器上。"
        "Colab 把環境放在雲端，換一台電腦照樣接得上。"),
       (False, "在公用電腦上裝 Anaconda",
        "多半裝不了（沒有管理員權限），就算裝得了，下次換一台又要重來。"),
       (False, "先買一台自己的電腦",
        "在跑過第一張圖之前，你還不知道自己需要什麼規格。先用免費的把課上完。")])}
"""

# ── P01 Colab 工作流 ──────────────────────────────────────────────────
BODIES["colab"] = f"""
  <p>Colab 是跑在 Google 機器上的 Jupyter notebook。它的好處是零安裝、有免費 GPU；
  代價是<strong>執行階段（runtime）會被回收</strong>——閒置太久或關掉分頁之後，
  你裝的套件與記憶體裡的變數都會消失，程式碼本身則存在你的 Drive 裡不會掉。</p>

{info("最常見的一個誤會", "「我明明裝過 ISLP 了，怎麼又說找不到？」"
      "，因為那是<strong>上一個執行階段</strong>裝的。"
      "重新連線之後要再跑一次 <code>%pip install ISLP</code>。"
      "把它留在 notebook 的第一格，就不會忘。", "warm")}

{card("Colab 上的加速選項", C(1, 4), O(1, 4), src=S(1, 4),
      note="這兩行是課程 lab 拿來開 GPU 加速的（<code>cudf</code> 加速 pandas、"
           "<code>cuml</code> 加速 scikit-learn）。"
           "本機沒有 NVIDIA 顯卡的話會失敗，<strong>刪掉這兩行照樣能跑</strong>，只是慢一點。")}

{viz(svg("w13cellSvg", 340),
     [info_card("按亂序執行看看",
                "notebook 的儲存格<strong>可以照任何順序執行</strong>，"
                "而且左邊的編號記錄的是「第幾次執行」不是「第幾格」。"
                "按「亂序執行」，看變數變成什麼。"),
      rows_card("目前",
                [("執行順序", "—", "w13clOrder"),
                 ("x 的值", "—", "w13clX"),
                 ("結果對不對", "—", "w13clOk")]),
      info_card("怎麼避免",
                "定期<strong>重啟執行階段並全部重跑</strong>"
                "（Colab：執行階段 → 重新啟動並全部執行）。"
                "交作業之前一定要做一次。你不會想交出一份只有你自己那台機器跑得出來的東西。")],
     "w13clStatus", "先按「由上到下」，再按「亂序執行」。",
     '<button class="btn btn-play" onclick="w13clRun(0)">▶ 由上到下</button>'
     '<button class="btn btn-step" onclick="w13clRun(1)">亂序執行</button>'
     '<button class="btn btn-reset" onclick="w13clReset()">重啟並全部重跑</button>')}

{table(["Colab 的東西", "會不會留下"],
       [["程式碼與文字（notebook 本身）", "✓ 存在你的 Google Drive"],
        ["<code>%pip install</code> 裝的套件", "✗ 執行階段結束就沒了"],
        ["變數與載入的資料", "✗ 同上"],
        ["<code>/content/</code> 底下自己存的檔案", "✗ 同上"],
        ["掛載的 Google Drive 裡的檔案", "✓ 那是你的雲端硬碟"]])}

{quiz("qColab", "PART 01 · 自我檢測",
      "你昨天在 Colab 跑得好好的 notebook，今天打開第一格就報 "
      "<code>ModuleNotFoundError: No module named 'ISLP'</code>。為什麼？",
      [(True, "執行階段被回收了，套件要重裝",
        "對。Colab 的環境是暫時的。把 <code>%pip install ISLP</code> "
        "留在第一格，每次重新連線先跑它就好。"),
       (False, "notebook 檔案壞掉了",
        "notebook 存在 Drive 裡不會壞。報錯的是<strong>環境</strong>不是檔案。"),
       (False, "ISLP 這個套件被下架了",
        "在懷疑套件之前先懷疑環境，後者的機率高一萬倍。")])}
"""

# ── P02 imports 那一格 ────────────────────────────────────────────────
BODIES["imports"] = f"""
  <p>每一份課程 lab 的第一格都長得差不多：把要用的套件全部 import 進來。
  這一格<strong>一定要先跑</strong>，不然後面每一格都會報 <code>NameError</code>。</p>

{card("課程 lab 的 imports（第 2 章）", C(2, 3), src=S(2, 3),
      note="注意最後那段 <code>try / except</code>："
           "<code>google.colab</code> 只有在 Colab 上才有，"
           "本機跑的時候讓它安靜地把 <code>drive</code> 設成 None 就好。"
           "<strong>這是 try/except 的正確用法</strong>。你知道會發生什麼錯、也知道怎麼處理。")}

{card("第 1 章的 imports", C(1, 5), src=S(1, 5),
      note="每個 import 後面都有一句中文註解，說明那個套件負責什麼。"
           "先掃過一遍，之後看到 <code>sns.</code> 或 <code>sm.</code> 開頭就知道是誰。")}

{viz(svg("w13impSvg", 320),
     [info_card("點名字看它管什麼",
                "課程用到的六個主要套件。按按鈕看它負責什麼、"
                "以及本站哪一頁在講它。"),
      rows_card("這個套件",
                [("慣用簡稱", "—", "w13imAlias"),
                 ("負責什麼", "—", "w13imWhat"),
                 ("哪一頁在講", "—", "w13imWhere")]),
      info_card("為什麼都用同一個簡稱",
                "<code>np</code>、<code>pd</code>、<code>sns</code>、<code>sm</code> "
                "是整個社群的慣例。照著用，別人（跟 AI）才看得懂你的程式碼，"
                "你也看得懂網路上找到的範例。")],
     "w13imStatus", "六個套件，各管一塊。",
     '<button class="btn btn-toggle" onclick="w13imSet(0)">numpy</button>'
     '<button class="btn btn-toggle" onclick="w13imSet(1)">pandas</button>'
     '<button class="btn btn-toggle" onclick="w13imSet(2)">matplotlib</button>'
     '<button class="btn btn-toggle" onclick="w13imSet(3)">seaborn</button>'
     '<button class="btn btn-toggle" onclick="w13imSet(4)">statsmodels</button>'
     '<button class="btn btn-toggle" onclick="w13imSet(5)">scikit-learn</button>')}

{quiz("qImp", "PART 02 · 自我檢測",
      "你跳過第一格直接跑第三格，得到 <code>NameError: name 'np' is not defined</code>。該怎麼辦？",
      [(True, "回去把第一格跑一次",
        "對。<code>np</code> 是 <code>import numpy as np</code> 建立的名字，"
        "那一格沒跑，這個名字就不存在。"
        "NameError 十次有九次是「某一格沒跑」。"),
       (False, "重新安裝 numpy",
        "套件裝得好好的，只是<strong>還沒 import</strong>。"
        "重裝不會建立 <code>np</code> 這個名字。"),
       (False, "把 np 改成 numpy",
        "那要先 <code>import numpy</code>。而且改了之後跟課程 lab 的寫法就不一致了。")])}
"""

# ── P03 資料放哪裡 ────────────────────────────────────────────────────
BODIES["data"] = f"""
  <p>課程 lab 的資料放在你自己的 Google Drive 裡。流程是三步：
  掛載 Drive → 設一個 <code>DATA_PATH</code> → 用 <code>pd.read_csv</code> 讀。</p>

{card("掛載 Drive", C(2, 183), O(2, 183), src=S(2, 183),
      note="第一次會跳出授權視窗，選你的 Google 帳號按同意。"
           "掛好之後 Drive 就出現在 <code>/content/drive/MyDrive/</code> 底下。")}

{card("設一個路徑變數", C(2, 184), src=S(2, 184),
      note="<strong>這一行要改成你自己的路徑。</strong>"
           "把路徑存成變數而不是每次都打全長，換資料夾時只要改一個地方。")}

{card("讀進來", C(2, 185), O(2, 185), src=S(2, 185),
      note="<code>os.path.join</code> 幫你處理斜線，"
           "比自己用加號接字串保險（Windows 與 Linux 的斜線方向不同）。")}

{info("讀檔的參數決定你後面有多痛",
      "同一份 Auto 資料，<code>Auto.csv</code> 與 <code>Auto.data</code> 要用不同的參數讀，"
      "而且後者需要 <code>na_values=['?']</code>，不然 horsepower 整欄會變成字串。"
      "細節在 <a href=\"p4_pandas.html#na\">P4 的遺漏值那一節</a>。", "warm")}

{quiz("qData", "PART 03 · 自我檢測",
      "<code>FileNotFoundError: /content/drive/MyDrive/Lab/Data/Auto.csv</code>。"
      "最可能的原因是？",
      [(True, "DATA_PATH 沒改成你自己的資料夾位置",
        "對。lab 裡那一行是老師的路徑，你的 Drive 結構多半不一樣。"
        "在 Colab 左側的檔案窗格點開資料夾，右鍵可以複製正確的路徑。"),
       (False, "Drive 掛載失敗",
        "有可能，但掛載失敗會在 <code>drive.mount</code> 那一格就報錯，"
        "而不是等到讀檔。"),
       (False, "檔案格式不對",
        "格式不對是 <code>ParserError</code> 或讀出奇怪的欄，"
        "<code>FileNotFoundError</code> 講的是<strong>檔案不在那裡</strong>。")])}
"""

# ── P04 本機安裝 ──────────────────────────────────────────────────────
BODIES["local"] = f"""
  <p>確定要長期用了再做這一步。本機安裝的唯一理由是<strong>你想控制版本</strong>——
  讓自己跑出來的數字跟課程 lab 一致。做法是開一個獨立的 conda 環境，
  把版本釘在課程用的那一組。</p>

{info("本站的圖表就是這樣產生的",
      f"環境版本：{P.ENV_NOTE}。"
      "本站每一張自己算的圖都在這個環境下用固定種子跑出來，所以任何人都能重生同樣的數字。")}

{hl('''# 開一個獨立的環境，Python 版本也釘住
conda create -n m524 python=3.11 -y

# 裝課程用的套件（版本對齊課程的 packages.txt）
conda run -n m524 pip install numpy==1.24.4 pandas==2.3.2 \\
  scikit-learn==1.6.1 scipy==1.13.1 statsmodels==0.14.2 \\
  matplotlib==3.8.4 seaborn==0.13.2 ISLP==0.4.0

# 讓 Jupyter 看得到這個環境
conda run -n m524 pip install jupyterlab ipykernel
conda run -n m524 python -m ipykernel install --user --name m524''')}

{viz(svg("w13envSvg", 320),
     [info_card("為什麼要獨立的環境",
                "按按鈕看「全部裝在同一個環境」會發生什麼事。"
                "兩個專案要求不同版本的同一個套件時，後裝的會蓋掉先裝的。"),
      rows_card("目前",
                [("情境", "—", "w13enCase"),
                 ("課程專案", "—", "w13enA"),
                 ("另一個專案", "—", "w13enB")]),
      info_card("kernel 沒選對是最常見的假故障",
                "環境開好了、套件也裝了，但 Jupyter 左上角選的還是 base。"
                "症狀是「明明裝過了卻說找不到」。"
                "先看右上角顯示的 kernel 名稱是不是 m524。")],
     "w13enStatus", "先看「全部裝在一起」會怎樣。",
     '<button class="btn btn-toggle" onclick="w13enSet(0)">全部裝在 base</button>'
     '<button class="btn btn-toggle" onclick="w13enSet(1)">各自獨立的環境</button>')}

{viz(svg("w13cmdSvg", 300),
     [info_card("按選項組指令",
                "選你的情況，下面會組出該打的那一行。"
                "四個選項組合出來的指令都不一樣。這也是為什麼直接抄別人的指令常常不管用。"),
      rows_card("組出來的指令",
                [("步驟", "建立環境", "w13cmStep"),
                 ("指令", "conda create -n m524 python=3.11 -y", "w13cmCmd")]),
      info_card("順序有意義",
                "建立 → 裝套件 → 註冊 kernel → 每次使用前 activate。"
                "跳過第三步的話 Jupyter 看不到這個環境，"
                "你就會遇到「明明裝了卻找不到」。")],
     "w13cmStatus", "四個步驟，照順序做。",
     '<button class="btn btn-toggle" onclick="w13cmSet(0)">① 建立環境</button>'
     '<button class="btn btn-toggle" onclick="w13cmSet(1)">② 裝套件</button>'
     '<button class="btn btn-toggle" onclick="w13cmSet(2)">③ 註冊 kernel</button>'
     '<button class="btn btn-toggle" onclick="w13cmSet(3)">④ 每次使用</button>')}

{table(["情境", "建議"],
       [["第一次上手、只想跑 lab", "Colab"],
        ["想長期用、要跟課程數字一致", "conda 環境（上面那段指令）"],
        ["電腦空間很小", "pip + venv（不裝 Anaconda，省 3–5 GB）"],
        ["要用 GPU", "Colab（本機要 NVIDIA 顯卡加 CUDA，很麻煩）"],
        ["交作業前的最後檢查", "<b>重啟 kernel 並全部重跑一次</b>"]])}

{quiz("qLocal", "PART 04 · 自我檢測",
      "你在終端機 <code>pip install ISLP</code> 裝好了，但 Jupyter 裡還是 "
      "<code>ModuleNotFoundError</code>。最可能的原因？",
      [(True, "Jupyter 用的 kernel 不是你剛剛裝套件的那個環境",
        "對。這是最常見的假故障。"
        "在 notebook 裡跑 <code>%pip install ISLP</code>（前面加百分比符號），"
        "它會裝到<strong>當前 kernel</strong> 的 Python 裡，直接避開這個問題。"),
       (False, "要重開電腦",
        "重開沒有用——問題不是快取，是<strong>裝到了另一個 Python</strong>。"),
       (False, "ISLP 不支援你的作業系統",
        "ISLP 是純 Python 套件，跨平台。先檢查環境，再懷疑套件。")])}
"""

# ── P05 跑不動的時候 ──────────────────────────────────────────────────
BODIES["trouble"] = f"""
  <p>環境的問題有八成是同樣的四種。這一節把它們列出來，
  每一種都給「症狀 → 原因 → 怎麼修」。學會這四種，你以後遇到的環境問題會少一大半。</p>

{viz(svg("w13fixSvg", 320),
     [info_card("點症狀看解法",
                "四種最常見的假故障。它們的共同點是：<strong>程式碼沒有錯</strong>，"
                "錯的是環境或執行順序。"),
      rows_card("這一種",
                [("症狀", "—", "w13fxSym"),
                 ("真正的原因", "—", "w13fxWhy"),
                 ("怎麼修", "—", "w13fxFix")]),
      info_card("一個萬用的第一步",
                "<strong>重啟 kernel 並從第一格全部重跑。</strong>"
                "這一步能解掉的問題比你想像的多，因為它同時消除了"
                "「亂序執行」與「殘留變數」這兩個最常見的干擾。")],
     "w13fxStatus", "四種症狀，各自的解法。",
     '<button class="btn btn-toggle" onclick="w13fxSet(0)">ModuleNotFoundError</button>'
     '<button class="btn btn-toggle" onclick="w13fxSet(1)">NameError</button>'
     '<button class="btn btn-toggle" onclick="w13fxSet(2)">FileNotFoundError</button>'
     '<button class="btn btn-toggle" onclick="w13fxSet(3)">結果跟同學不一樣</button>')}

{qa("還是跑不動的話", [
    ("問人之前先做這三件事",
     "① <strong>重啟並全部重跑</strong>；② 把<strong>完整的錯誤訊息最後一行</strong>複製起來；"
     "③ 確認是哪一格出錯、那一格用到哪些變數。"
     "做完這三件事，八成的問題你自己就解掉了；剩下的兩成，別人也才幫得上忙。"),
    ("可以直接把錯誤訊息丟給 AI 嗎？",
     "可以，而且通常很有用——環境問題正是 AI 最擅長的那一類（有標準答案、可驗證）。"
     "但要把<strong>完整的錯誤訊息</strong>與<strong>你實際跑的那一格</strong>都給它，"
     "不要只說「我的程式跑不動」。"
     "為什麼統計結果就不能這樣信它，見 "
     "<a href=\"00a_why_code.html\">00A</a>。"),
])}

{info("交作業之前一定要做的一件事",
      "<strong>重啟執行階段 → 從第一格全部重跑 → 確認每一格都有輸出而且沒有紅色錯誤。</strong>"
      "你不會想交出一份「只有我這台機器、而且只有照某個特定順序跑才對」的作業。")}

{quiz("qFix", "PART 05 · 自我檢測",
      "同一份 notebook，你跑出來的 MSE 是 25.57，同學是 23.80。程式碼一模一樣。為什麼？",
      [(True, "切分或重抽樣的隨機性，其中一邊沒有固定種子",
        "對。<code>train_test_split</code> 與自助法都有隨機性，"
        "沒有固定 <code>random_state</code> 或 <code>seed</code> 就會每次不同。"
        "細節見 <a href=\"p3_numpy.html#rand\">P3 的亂數那一節</a>。"),
       (False, "你們的套件版本不同",
        "有可能造成小數點後幾位的差異，但 25.57 對 23.80 差太多了，"
        "這種量級的差異幾乎一定是隨機性。"),
       (False, "其中一個人算錯了",
        "程式碼一樣的話，「算錯」的機率遠低於「隨機性」。"
        "先查最可能的原因。")])}

{hook("接下來讀什麼",
      '環境好了就可以開始了。沒寫過程式的話從 '
      '<a href="p1_python_basics.html">P1 Python 基礎</a> 開始；'
      '寫過但沒碰過資料科學套件的，直接跳到 '
      '<a href="p3_numpy.html">P3 NumPy</a>。'
      '想先知道「AI 都會了為什麼還要學」，看 '
      '<a href="00a_why_code.html">00A</a>。')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 裝套件",
      "在 Colab 的儲存格裡裝套件，該用哪一個？",
      [(True, "<code>%pip install ISLP</code>",
        "對。百分比開頭的魔術指令會裝到<strong>當前 kernel</strong> 的 Python 裡，"
        "不會裝錯環境。課程 lab 用的就是這個寫法。"),
       (False, "<code>!pip install ISLP</code>",
        "驚嘆號是「丟給系統的 shell 跑」，在 Colab 上多半也會成功，"
        "但在本機的多環境情況下可能裝到別的 Python 去。<code>%pip</code> 比較保險。"),
       (False, "<code>import ISLP</code>",
        "import 是「使用已經裝好的套件」，它不會去下載任何東西。")])}

{quiz("qEx2", "EXERCISE 2 · 執行順序",
      "notebook 左邊的 <code>[7]</code> 代表什麼？",
      [(False, "這是第 7 個儲存格",
        "不是。編號跟位置無關。你可以把第 20 格拉到最上面，它的編號不會變。"),
       (True, "這一格是這個 kernel 的第 7 次執行",
        "對。所以編號如果不是由上到下遞增，就代表你曾經亂序執行過，"
        "此時的變數狀態可能跟「從頭跑一次」不一樣。"),
       (False, "這一格跑了 7 秒",
        "執行時間會顯示在儲存格下方，不是那個中括號。")])}

{quiz("qEx3", "EXERCISE 3 · 版本",
      "為什麼本站要把套件版本釘死（numpy 1.24.4、pandas 2.3.2…）？",
      [(True, "讓任何人重跑都能得到同一組數字",
        "對。版本一改，某些預設值與演算法細節就可能不同，"
        "數字就對不上課程 lab 了。可重現性是這門課的基本紀律。"),
       (False, "新版本有 bug",
        "沒有這個假設。釘版本是為了<strong>一致</strong>，不是因為新版不好。"),
       (False, "舊版本比較快",
        "跟速度無關。")])}

{quiz("qEx4", "EXERCISE 4 · 假故障",
      "你在本機的 conda 環境裝好了全部套件，但 Jupyter 裡 import 還是失敗。"
      "第一件要檢查的事是？",
      [(True, "Jupyter 右上角顯示的 kernel 是不是那個環境",
        "對。kernel 選錯是最常見的假故障：你裝在 m524，Jupyter 卻用 base 在跑。"
        "在 notebook 裡跑 <code>import sys; print(sys.executable)</code> 就知道"
        "當前用的是哪一個 Python。"),
       (False, "重裝 Anaconda",
        "最貴的一步，而且多半沒用。先看便宜的證據。"),
       (False, "改用 Colab",
        "可以繞過問題，但你不會學到怎麼修，而且下次還會遇到。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張速查表。跑不動的時候回來看第二張。</p>

{table(["環境", "花多久", "適合誰", "注意"],
       [["Colab", "3 分鐘", "第一次上手、公用電腦", "執行階段會回收，套件要重裝"],
        ["conda 環境", "20 分鐘", "長期使用、要跟課程數字一致", "記得選對 kernel"],
        ["pip + venv", "10 分鐘", "電腦空間小", "自己管 Python 版本"],
        ["本機 base 環境", "—", "<b>不建議</b>", "遲早會版本衝突"]])}

{table(["症狀", "真正的原因", "怎麼修"],
       [["<code>ModuleNotFoundError</code>", "沒裝，或裝到別的環境",
         "<code>%pip install X</code>；檢查 kernel"],
        ["<code>NameError</code>", "某一格沒跑（多半是 imports）", "從第一格重跑"],
        ["<code>FileNotFoundError</code>", "路徑不對或 Drive 沒掛",
         "在檔案窗格複製正確路徑"],
        ["結果跟同學不同", "沒固定種子", "<code>random_state=0</code>、<code>seed=0</code>"],
        ["改了程式卻沒變", "改完沒重跑那一格", "重啟並全部重跑"]])}

{table(["交作業前的檢查", "為什麼"],
       [["重啟 kernel", "清掉殘留的變數"],
        ["從第一格全部重跑", "確認不依賴亂序執行"],
        ["每一格都有輸出、沒有紅色錯誤", "確認別人打開也跑得動"],
        ["固定所有種子", "確認別人跑得出同樣的數字"],
        ["DATA_PATH 有註明要改", "別人的 Drive 結構跟你不同"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 先能跑，再談其他。</strong>第一次上手用 Colab，"
      "把耐心留給課程內容而不是安裝問題。<br>"
      "<strong>2. 八成的「壞掉」其實是環境或執行順序。</strong>"
      "萬用第一步：重啟 kernel 並全部重跑。<br>"
      "<strong>3. 交作業前一定要從頭重跑一次。</strong>"
      "不然你交的是「只有你那台機器跑得出來」的東西。")}

{ver_note((1, 2))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* ═══ w13pa 三條路 ═══ */
const w13paS = HC.svg('w13pathSvg', {h: 320});
const w13paCases = [
  {t: '3 分鐘', pro: '零安裝、有免費 GPU、換電腦也接得上',
   con: '執行階段會回收，套件要重裝', note: '第一次上手一律選這條。'},
  {t: '20 分鐘', pro: '版本可以釘死，數字跟課程 lab 一致',
   con: '要下載 1 GB、佔 5 GB 空間', note: '確定要長期用了再做。'},
  {t: '10 分鐘', pro: '不用裝 Anaconda，省 3–5 GB',
   con: 'Python 版本要自己管', note: '電腦空間小的時候的折衷。'}
];
let w13paI = 0;
function w13paDraw() {
  const g = w13paS.clearLayer('main');
  const names = ['① Colab', '② 本機 conda', '③ pip + venv'];
  names.forEach((nm, i) => {
    const on = i === w13paI;
    const y = 66 + i * 78;
    w13paS.add('rect', {x: 40, y: y, width: 540, height: 62, rx: 9,
                        fill: on ? (i === 0 ? HC.tok.accent2 : HC.tok.accent) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.6,
                        opacity: on ? 0.95 : 0.45}, g);
    const t = w13paS.add('text', {x: 62, y: y + 27, cls: 'axtitle',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = nm;
    const u = w13paS.add('text', {x: 62, y: y + 49, cls: 'axlab',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = w13paCases[i].t + '　·　' + w13paCases[i].pro;
    if (i === 0) {
      const b = w13paS.add('text', {x: 556, y: y + 27, 'text-anchor': 'end', cls: 'axlab',
                                    fill: on ? HC.tok.paper : HC.tok.accent2}, g);
      b.textContent = '推薦';
    }
  });
  const c = w13paCases[w13paI];
  document.getElementById('w13paTime').textContent = c.t;
  document.getElementById('w13paPro').textContent = c.pro;
  document.getElementById('w13paCon').textContent = c.con;
  setStatus('w13paStatus', c.note);
}
function w13paSet(i) { w13paI = i; w13paDraw(); }
if (w13paS) w13paDraw();

/* ═══ w13cl 儲存格執行順序 ═══ */
const w13clS = HC.svg('w13cellSvg', {h: 340});
const w13clCells = [
  {code: 'x = 10', eff: 10},
  {code: 'x = x * 2', eff: null},
  {code: 'print(x)', eff: null}
];
let w13clOrder = [], w13clMode = -1;
function w13clDraw() {
  const g = w13clS.clearLayer('main');
  let x = null;
  const seen = [];
  w13clOrder.forEach(i => {
    seen.push(i);
    if (i === 0) x = 10;
    else if (i === 1) x = (x === null ? null : x * 2);
  });
  w13clCells.forEach((c, i) => {
    const pos = w13clOrder.indexOf(i);
    const on = pos >= 0;
    w13clS.add('rect', {x: 96, y: 78 + i * 62, width: 340, height: 46, rx: 6,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 0.95 : 0.45}, g);
    const t = w13clS.add('text', {x: 116, y: 107 + i * 62, cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = c.code;
    const n = w13clS.add('text', {x: 82, y: 107 + i * 62, 'text-anchor': 'end', cls: 'axlab',
                                  'font-family': HC.MONO}, g);
    n.textContent = on ? '[' + (pos + 1) + ']' : '[ ]';
  });
  const ok = w13clMode === 0;
  w13clS.txtPx(310, 296, w13clMode < 0 ? '還沒執行'
               : (ok ? 'print 印出 20 ✓' : (x === null ? 'NameError：x 還不存在 ✗'
                                                       : 'print 印出 ' + x + '（跟預期不同）✗')),
               {cls: 'axtitle', anchor: 'middle',
                fill: w13clMode < 0 ? HC.tok.muted : (ok ? HC.tok.accent2 : HC.tok.resid)}, g);
  document.getElementById('w13clOrder').textContent = w13clOrder.length
    ? w13clOrder.map(i => i + 1).join(' → ') : '—';
  document.getElementById('w13clX').textContent = x === null ? '（不存在）' : String(x);
  document.getElementById('w13clOk').textContent = w13clMode < 0 ? '—' : (ok ? '對 ✓' : '錯 ✗');
  setStatus('w13clStatus', w13clMode < 0 ? '先按「由上到下」。'
            : (ok ? '由上到下跑，結果是 20 —— 這才是你寫程式時心裡想的順序。'
                  : '亂序執行之後，同樣三格給出<b>不同的結果</b>。左邊的編號會出賣你。'));
}
function w13clRun(m) {
  w13clMode = m;
  w13clOrder = m === 0 ? [0, 1, 2] : [1, 0, 2];
  w13clDraw();
}
function w13clReset() { w13clMode = -1; w13clOrder = []; w13clDraw(); }
if (w13clS) w13clDraw();

/* ═══ w13im 六個套件 ═══ */
const w13imS = HC.svg('w13impSvg', {h: 320});
const w13imCases = [
  {n: 'numpy', a: 'np', w: '陣列與數值運算', p: 'P3'},
  {n: 'pandas', a: 'pd', w: '資料表：讀檔、選取、分組', p: 'P4'},
  {n: 'matplotlib', a: 'plt', w: '畫圖的底層：Figure 與 Axes', p: 'P5'},
  {n: 'seaborn', a: 'sns', w: '統計圖的高階介面', p: 'P5'},
  {n: 'statsmodels', a: 'sm', w: '係數、標準誤、p 值', p: 'P6'},
  {n: 'scikit-learn', a: 'sklearn', w: 'fit / predict / 交叉驗證', p: 'P6'}
];
let w13imI = 0;
function w13imDraw() {
  const g = w13imS.clearLayer('main');
  w13imCases.forEach((c, i) => {
    const on = i === w13imI;
    const col = i % 2, row = Math.floor(i / 2);
    const x = 52 + col * 272, y = 74 + row * 74;
    w13imS.add('rect', {x: x, y: y, width: 250, height: 58, rx: 8,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.5,
                        opacity: on ? 0.95 : 0.5}, g);
    const t = w13imS.add('text', {x: x + 16, y: y + 26, cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = c.n;
    const u = w13imS.add('text', {x: x + 16, y: y + 46, cls: 'axlab',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = 'as ' + c.a + '　·　' + c.w;
  });
  const c = w13imCases[w13imI];
  document.getElementById('w13imAlias').textContent = c.a;
  document.getElementById('w13imWhat').textContent = c.w;
  document.getElementById('w13imWhere').textContent = '先備 ' + c.p;
  setStatus('w13imStatus', c.n + ' 負責' + c.w + '，本站在 <b>' + c.p + '</b> 講它。');
}
function w13imSet(i) { w13imI = i; w13imDraw(); }
if (w13imS) w13imDraw();

/* ═══ w13en 環境隔離 ═══ */
const w13enS = HC.svg('w13envSvg', {h: 320});
let w13enI = 0;
function w13enDraw() {
  const g = w13enS.clearLayer('main');
  const shared = w13enI === 0;
  if (shared) {
    w13enS.add('rect', {x: 150, y: 86, width: 320, height: 130, rx: 10,
                        fill: HC.tok.resid, opacity: 0.18,
                        stroke: HC.tok.resid, 'stroke-width': 2}, g);
    w13enS.txtPx(310, 112, 'base 環境（大家共用）',
                 {cls: 'axtitle', anchor: 'middle', fill: HC.tok.resid}, g);
    w13enS.add('rect', {x: 186, y: 130, width: 248, height: 44, rx: 6,
                        fill: HC.tok.resid, opacity: 0.9}, g);
    const t = w13enS.add('text', {x: 310, y: 158, 'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = 'pandas 2.3.2';
    w13enS.txtPx(310, 246, '另一個專案裝了 pandas 1.5，就把它蓋掉了',
                 {cls: 'axtitle', anchor: 'middle', fill: HC.tok.resid}, g);
  } else {
    [['m524（課程）', 'pandas 2.3.2', HC.tok.accent2, 40],
     ['other（別的專案）', 'pandas 1.5.3', HC.tok.accent, 330]].forEach(e => {
      w13enS.add('rect', {x: e[3], y: 86, width: 250, height: 130, rx: 10,
                          fill: e[2], opacity: 0.16, stroke: e[2], 'stroke-width': 2}, g);
      const t = w13enS.add('text', {x: e[3] + 125, y: 112, 'text-anchor': 'middle',
                                    cls: 'axtitle', fill: e[2]}, g);
      t.textContent = e[0];
      w13enS.add('rect', {x: e[3] + 24, y: 130, width: 202, height: 44, rx: 6,
                          fill: e[2], opacity: 0.9}, g);
      const u = w13enS.add('text', {x: e[3] + 125, y: 158, 'text-anchor': 'middle',
                                    cls: 'vlab', 'font-family': HC.MONO,
                                    fill: HC.tok.paper}, g);
      u.textContent = e[1];
    });
    w13enS.txtPx(310, 246, '兩個版本共存，互不干擾',
                 {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent2}, g);
  }
  document.getElementById('w13enCase').textContent = shared ? '全部裝在 base' : '各自獨立';
  document.getElementById('w13enA').textContent = shared ? 'pandas 被蓋成 1.5.3' : 'pandas 2.3.2 ✓';
  document.getElementById('w13enB').textContent = shared ? 'pandas 1.5.3' : 'pandas 1.5.3 ✓';
  setStatus('w13enStatus', shared
    ? '後裝的蓋掉先裝的 —— 於是課程 lab 的數字就對不上了。'
    : '每個專案一個環境，版本各自釘死。<b>這就是 conda 環境的全部意義。</b>');
}
function w13enSet(i) { w13enI = i; w13enDraw(); }
if (w13enS) w13enDraw();

/* ═══ w13cm conda 指令組裝器 ═══ */
const w13cmS = HC.svg('w13cmdSvg', {h: 300});
const w13cmCases = [
  {s: '建立環境', c: 'conda create -n m524 python=3.11 -y',
   note: '<code>-n</code> 是環境名字，<code>python=3.11</code> 連 Python 版本一起釘住。'},
  {s: '裝套件', c: 'conda run -n m524 pip install numpy==1.24.4 pandas==2.3.2 ISLP==0.4.0',
   note: '用 <code>==</code> 釘版本。完整清單見上面那段程式碼。'},
  {s: '註冊 kernel', c: 'conda run -n m524 python -m ipykernel install --user --name m524',
   note: '<b>這一步最常被跳過</b>，跳過的話 Jupyter 的 kernel 選單裡看不到它。'},
  {s: '每次使用', c: 'conda activate m524',
   note: '開新的終端機都要做一次。Jupyter 那邊則是在右上角選 kernel。'}
];
let w13cmI = 0;
function w13cmDraw() {
  const g = w13cmS.clearLayer('main');
  w13cmCases.forEach((c, i) => {
    const on = i === w13cmI;
    const x = 40 + i * 138;
    w13cmS.add('rect', {x: x, y: 62, width: 124, height: 46, rx: 7,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 0.95 : 0.5}, g);
    const t = w13cmS.add('text', {x: x + 62, y: 90, 'text-anchor': 'middle', cls: 'axlab',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = (i + 1) + '. ' + c.s;
    if (i < 3) {
      w13cmS.add('path', {d: 'M' + (x + 128) + ' 85 H ' + (x + 172),
                          stroke: HC.tok.cardBorder, 'stroke-width': 2}, g);
      w13cmS.add('path', {d: 'M' + (x + 176) + ' 85 l -8 -5 v 10 z',
                          fill: HC.tok.cardBorder}, g);
    }
  });
  const c = w13cmCases[w13cmI];
  w13cmS.add('rect', {x: 40, y: 140, width: 540, height: 62, rx: 8,
                      fill: HC.tok.ink, opacity: 0.92}, g);
  const parts = c.c.match(/.{1,62}(\s|$)/g) || [c.c];
  parts.slice(0, 2).forEach((ln, i) => {
    const t = w13cmS.add('text', {x: 58, y: 168 + i * 22, cls: 'vlab',
                                  'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = ln.trim();
  });
  w13cmS.txtPx(310, 240, '在終端機打這一行', {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w13cmStep').textContent = c.s;
  document.getElementById('w13cmCmd').textContent = c.c;
  setStatus('w13cmStatus', c.note);
}
function w13cmSet(i) { w13cmI = i; w13cmDraw(); }
if (w13cmS) w13cmDraw();

/* ═══ w13fx 四種假故障 ═══ */
const w13fxS = HC.svg('w13fixSvg', {h: 320});
const w13fxCases = [
  {s: 'ModuleNotFoundError', w: '沒裝，或裝到了另一個環境',
   f: '%pip install X；檢查 kernel 是哪一個'},
  {s: 'NameError', w: '某一格沒跑（十次有九次是 imports 那一格）', f: '從第一格重跑'},
  {s: 'FileNotFoundError', w: '路徑不對，或 Drive 沒掛', f: '在檔案窗格複製正確的路徑'},
  {s: '結果跟同學不一樣', w: '切分或重抽樣沒有固定種子',
   f: 'random_state=0、seed=0，然後兩邊都重跑'}
];
let w13fxI = 0;
function w13fxDraw() {
  const g = w13fxS.clearLayer('main');
  w13fxCases.forEach((c, i) => {
    const on = i === w13fxI;
    const y = 68 + i * 58;
    w13fxS.add('rect', {x: 40, y: y, width: 540, height: 46, rx: 7,
                        fill: on ? HC.tok.accent : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 0.95 : 0.45}, g);
    const t = w13fxS.add('text', {x: 60, y: y + 21, cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = c.s;
    const u = w13fxS.add('text', {x: 60, y: y + 38, cls: 'axlab',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = on ? '→ ' + c.f : c.w;
  });
  w13fxS.txtPx(310, 300, '萬用第一步：重啟 kernel 並從第一格全部重跑',
               {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent2}, g);
  const c = w13fxCases[w13fxI];
  document.getElementById('w13fxSym').textContent = c.s;
  document.getElementById('w13fxWhy').textContent = c.w;
  document.getElementById('w13fxFix').textContent = c.f;
  setStatus('w13fxStatus', c.s + '：' + c.w + '。');
}
function w13fxSet(i) { w13fxI = i; w13fxDraw(); }
if (w13fxS) w13fxDraw();
"""

apply("00b_setup", BODIES, PAGEJS)
