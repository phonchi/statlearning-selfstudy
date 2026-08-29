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
from lib import (apply, card, hl, hook, info, lab_code,  # noqa: E402
                 lab_output, qa, quiz, table, ver_note)

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

{table(["環境", "啟動成本", "適合情境", "主要代價"],
       [["<strong>Colab（第一次上手推薦）</strong>", "瀏覽器開啟即可使用",
         "第一次跑 lab、公用電腦、需要臨時 GPU", "執行階段會回收，套件需重裝"],
        ["本機 conda", "需安裝環境並註冊 kernel", "長期使用、需要固定版本",
         "要管理環境與 Jupyter kernel"],
        ["本機 pip + venv", "需自行準備 Python 與 venv", "磁碟空間有限、熟悉 Python 環境",
         "Python 與套件版本需自行管理"]])}

{card("裝課程用的套件", C(1, 3), src=S(1, 3),
      note="<code>%pip</code> 開頭的百分比符號是 Jupyter 的魔術指令，"
           "意思是「裝到<strong>這個 notebook 正在用的</strong> Python 裡」——"
           "比在終端機打 <code>pip install</code> 保險。")}

{card("ISLP 會順便安裝相依套件", C(2, 8), src=S(2, 8),
      note="安裝輸出通常很長，沒有必要逐行閱讀。確認最後沒有紅色錯誤；"
           "若 Colab 要求重啟執行階段，照做即可。")}

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

<div class="viz-layout" data-provenance="illustrative">
 <div><div class="viz-panel">
  <p><strong>自己決定三格的執行順序。</strong>每按一次，就等於在 notebook 執行那一格；
  左邊的 <code>[n]</code> 是執行次序，不是儲存格位置。</p>
  {table(["儲存格", "程式", "執行"],
         [["<code id=\"w13clN0\">[ ]</code>", "<code>x = 10</code>",
           '<button class="btn btn-step" onclick="w13clRun(0)">執行第 1 格</button>'],
          ["<code id=\"w13clN1\">[ ]</code>", "<code>x = x * 2</code>",
           '<button class="btn btn-step" onclick="w13clRun(1)">執行第 2 格</button>'],
          ["<code id=\"w13clN2\">[ ]</code>", "<code>print(x)</code>",
           '<button class="btn btn-step" onclick="w13clRun(2)">執行第 3 格</button>']])}
  <div class="status-banner" id="w13clStatus"><span class="status-icon">›</span>
    <span class="status-text">請自行選一格開始；也可以故意先按第 2 或第 3 格。</span></div>
  <div class="controls-bar">
    <button class="btn btn-play" onclick="w13clTopDown()">▶ 由上到下全部執行</button>
    <button class="btn btn-reset" onclick="w13clReset()">重啟執行階段</button>
  </div>
  <div class="viz-source"><span>自訂概念示意</span>三格程式用來呈現 notebook 的狀態與執行順序；數值不是課程資料。</div>
 </div></div>
 <div class="side-panel">
  <div class="info-card"><div class="ic-title">這個模擬器要看什麼</div>
   同一格可以重跑，也可以跳著跑；所以 notebook 的結果取決於<strong>目前記憶體狀態</strong>，
   不只取決於畫面上儲存格的位置。</div>
  <div class="info-card"><div class="ic-title">交作業前</div>
   重啟執行階段並由上到下全部執行，確認結果不依賴先前殘留的變數。</div>
 </div>
</div>

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

{table(["套件", "慣用簡稱", "負責什麼", "本站位置"],
       [["numpy", "<code>np</code>", "陣列與數值運算", "P3"],
        ["pandas", "<code>pd</code>", "資料表、選取與分組", "P4"],
        ["matplotlib", "<code>plt</code>", "Figure 與 Axes", "P5"],
        ["seaborn", "<code>sns</code>", "統計圖的高階介面", "P5"],
        ["statsmodels", "<code>sm</code>", "係數、標準誤與 p 值", "P6"],
        ["scikit-learn", "<code>sklearn</code>", "fit、predict 與交叉驗證", "P6"]])}

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

{table(["做法", "課程專案", "另一個專案", "結果"],
       [["全部裝在 base", "需要 pandas 2.3.2", "需要 pandas 1.5.3",
         "同一環境只能留下其中一版，容易互相影響"],
        ["各自建立環境", "m524：pandas 2.3.2", "other：pandas 1.5.3",
         "兩個版本可以共存"]])}

{info("四步驟的順序",
      "<strong>建立環境 → 安裝套件 → 註冊 kernel → 選擇／啟用環境。</strong>"
      "上面的命令區已給出可直接執行的精確指令；不需要另一個動畫重複播放。"
      "若 Jupyter 說找不到已安裝的套件，先用 <code>import sys; print(sys.executable)</code> "
      "確認當前 kernel 使用哪一個 Python。")}

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

{table(["症狀", "先收集的證據", "優先檢查"],
       [["<code>ModuleNotFoundError</code>", "<code>sys.executable</code> 與 kernel 名稱",
         "套件是否裝在當前 kernel"],
        ["<code>NameError</code>", "變數第一次出現在哪一格、執行編號",
         "imports 或建立變數的儲存格是否已執行"],
        ["<code>FileNotFoundError</code>", "錯誤中的完整路徑",
         "Drive 是否掛載、<code>DATA_PATH</code> 是否指向自己的資料夾"],
        ["數值結果不同", "資料版本、前處理、套件版本、seed、完整重跑結果",
         "先定位差異來源，不要只憑結果猜是 seed"]])}

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
      [(True, "先從乾淨 kernel 全部重跑，再比資料、前處理、版本與 seed",
        "對。相同文字不保證相同執行狀態，也不代表讀到同一份資料。"
        "先做可重現的完整重跑，再逐項比對；若流程含隨機切分或重抽樣，"
        "才進一步檢查 <code>random_state</code> 或 <code>seed</code>。"),
       (False, "一定是其中一邊沒有固定 seed",
        "seed 是常見原因，但不是唯一原因。資料版本、前處理、套件版本、"
        "kernel 與亂序執行都可能造成差異，不能只由兩個 MSE 反推原因。"),
       (False, "直接把兩人的 MSE 平均起來",
        "平均不會找出差異來源。先確認兩邊其實在執行同一個分析。")])}

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
        ["結果跟同學不同", "資料、前處理、版本、seed 或執行狀態不同",
         "乾淨重跑後逐項比對，不先武斷歸因"],
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

# ── 元件 JS：只保留 notebook 儲存格狀態模擬器 ─────────────────────────
PAGEJS = r"""
let w13clX;
let w13clHasX = false;
let w13clHistory = [];

function w13clShow(message) {
  ['w13clN0', 'w13clN1', 'w13clN2'].forEach((id, i) => {
    const runs = w13clHistory
      .map((cell, n) => cell === i ? n + 1 : null)
      .filter(n => n !== null);
    document.getElementById(id).textContent = runs.length ? '[' + runs[runs.length - 1] + ']' : '[ ]';
  });
  setStatus('w13clStatus', message + '<br><small>執行紀錄：' +
    (w13clHistory.length ? w13clHistory.map(i => '第 ' + (i + 1) + ' 格').join(' → ') : '尚未執行') +
    '；目前 x：' + (w13clHasX ? w13clX : '尚未定義') + '</small>');
}

function w13clRun(cell) {
  w13clHistory.push(cell);
  if (cell === 0) {
    w13clX = 10;
    w13clHasX = true;
    w13clShow('執行 <code>x = 10</code>：現在 x 是 10。');
  } else if (cell === 1) {
    if (!w13clHasX) {
      w13clShow('<code>NameError</code>：x 還不存在。這就是亂序執行時常見的狀態問題。');
    } else {
      w13clX *= 2;
      w13clShow('執行 <code>x = x * 2</code>：現在 x 是 ' + w13clX + '。');
    }
  } else if (!w13clHasX) {
    w13clShow('<code>NameError</code>：print 找不到 x。');
  } else {
    w13clShow('<code>print(x)</code> 輸出 <strong>' + w13clX + '</strong>。同一格重跑時，結果取決於先前狀態。');
  }
}

function w13clReset() {
  w13clX = undefined;
  w13clHasX = false;
  w13clHistory = [];
  w13clShow('執行階段已重啟：變數與執行編號都已清空。');
}

function w13clTopDown() {
  w13clReset();
  w13clRun(0);
  w13clRun(1);
  w13clRun(2);
}
"""

apply("00b_setup", BODIES, PAGEJS)
