#!/usr/bin/env python3
"""tree_based_methods.html（ISLP 第 8 章 · 站內第 09 章）完整自學充實。冪等。

內容依據：講義 08_Tree-Based_Methods.pdf（80 頁，集成學習那一週折進這一頁）、
Ch08-baggboost-lab-zh.ipynb、ISLP 第 8 章（書上 p.332–366）。
所有「預期輸出」逐字取自 lab 的實跑結果，圖表資料由 tools/frames/gen_trees.py
在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 8
LAB = "Ch08-baggboost-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def code(*cells):
    """把幾格 lab 程式碼接起來（逐字，只去掉首尾空行）。"""
    return "\n\n".join(lab_code(CH, c).strip("\n") for c in cells)


def slider(sid, label, lo, hi, step, val, valtext, oninput, basis="230px"):
    """.controls-bar 裡的滑桿。用 .slider-row 當殼，才吃得到 base.css 的滑桿樣式。"""
    return (f'<span class="slider-row" style="margin-bottom:0;flex:1 1 {basis};min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" value="{val}" '
            f'oninput="{oninput}" aria-label="{label}">'
            f'<span class="slider-val" id="{sid}Val">{valtext}</span></span>')


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_trees.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_trees.py 失敗：\n" + r.stderr[-2000:])
    return "/* ===== 烘焙資料（tools/frames/gen_trees.py，固定種子）===== */\n" + r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>前面幾章的模型都在配一個<strong>式子</strong>：線性迴歸配一條線、樣條配一條彎的曲線、
  邏輯斯迴歸配一個機率。這一章換一個完全不同的想法——<strong>不配式子，直接把特徵空間切成方塊</strong>，
  每個方塊裡的所有點都給同一個預測值。</p>

  <p>ISLP §8.1 的例子是棒球員薪水（<code>Hitters</code>）：用 <code>Years</code>（打了幾年）
  和 <code>Hits</code>（去年幾支安打）預測 log 薪水。整棵樹只有兩刀，就把球員切成三塊：</p>

  $$R_1 = \\{{X \\mid \\texttt{{Years}} < 4.5\\}}, \\quad
    R_2 = \\{{X \\mid \\texttt{{Years}} \\ge 4.5,\\ \\texttt{{Hits}} < 117.5\\}}, \\quad
    R_3 = \\{{X \\mid \\texttt{{Years}} \\ge 4.5,\\ \\texttt{{Hits}} \\ge 117.5\\}}$$

  <p>三塊的預測值就是各塊訓練資料的<strong>平均</strong>：$e^{{5.107}}$、$e^{{5.999}}$、$e^{{6.740}}$
  千美元，也就是約 16.5 萬、40.3 萬、84.5 萬。整個模型可以用一句話講完：
  <strong>資淺的便宜；資深的看安打數</strong>。這種「一句話講得完」的能力，是樹最大的賣點。</p>

{info("先把四個詞釘住", '''<strong>終端節點／葉（terminal node / leaf）：</strong>樹最底下那些不再分裂的節點，
  每一個對應特徵空間的一塊方塊 $R_m$。<br>
  <strong>內部節點（internal node）：</strong>寫著分裂規則（例如 <code>Years &lt; 4.5</code>）的節點。<br>
  <strong>分支（branch）：</strong>連接節點的線段。慣例是<strong>左邊＝條件成立</strong>。<br>
  <strong>樹是倒著畫的：</strong>根在上、葉在下。這件事第一次看都會愣一下。''')}

  <p>樹的整體形狀就是一個<strong>階梯函數</strong>：</p>

  $$f(X) = \\sum_{{m=1}}^{{M}} c_m \\cdot \\mathbf{{1}}(X \\in R_m)$$

  <p>對照線性迴歸的 $f(X) = \\beta_0 + \\sum_j X_j \\beta_j$——一個是連續的斜面，
  一個是一格一格的台階。哪個對？看真實關係長什麼樣，這是 PART 05 的主題。</p>

{table(["", "線性迴歸", "決策樹"],
       [["模型長相", "一個斜面（連續、光滑）", "一堆方塊（階梯、有稜角）"],
        ["外插能力", "有（可以往定義域外推）", "沒有（葉的值是常數，出界就給邊界值）"],
        ["類別變數", "要做虛擬變數編碼", "天生就會處理（把水準分兩堆）"],
        ["變數尺度", "要小心（正則化時必須標準化）", "完全不受影響（只看大小順序）"],
        ["交互作用", "要自己乘出來", "自動有（連續兩刀就是一個交互作用）"],
        ["最大弱點", "真實關係非線性時失手", "<strong>不穩定</strong>：資料動一點，樹就長成另一棵"]])}

  <p>最後那一列是這一整章後半的動機。單一棵樹的<strong>變異</strong>大得離譜。把訓練資料隨機切成兩半、
  各配一棵樹，兩棵樹可能完全不像。所以真正實用的做法從來不是「一棵樹」，
  而是<strong>種很多棵再合起來</strong>：bagging、random forest、boosting。
  這一頁的後六節就在講這件事。</p>

  <h3 id="dx-high">講義完整實作：把 <code>Sales</code> 變成二元的 <code>High</code></h3>
{card("講義 08 · Carseats 與 High（lab 的起點）", code(12, 13), lab_output(CH, 13),
      src=src("12、13"),
      note="lab 前半用 <code>Carseats</code> 練分類樹（<code>Sales &gt; 8</code> 記為 "
           "<code>High = Yes</code>），後半用 <code>Boston</code> 練迴歸樹與集成。"
           "注意 <code>ShelveLoc</code>、<code>Urban</code>、<code>US</code> 是類別變數——"
           "理論上樹不必編碼，但 <code>scikit-learn</code> 的實作不支援，所以 lab 還是做了 one-hot。")}

{quiz("qWhat", "QUIZ · 樹在幹什麼",
      "一棵迴歸樹對落在同一個葉節點裡的兩個觀測值，會給出什麼預測？",
      [(True, "完全相同的預測值，也就是該葉節點內訓練資料的平均",
        "對。這正是「階梯函數」的意思：同一塊方塊內部完全平坦。所以樹的預測值只有 M 種（M ＝ 葉子數），不管特徵怎麼變。"),
       (False, "不同的預測值，因為兩點的特徵值不同",
        "不對。這是<strong>線性模型</strong>的直覺：特徵動一點，預測就跟著動一點。樹不是這樣，只要沒有跨過任何一個切點，預測完全不動。"),
       (False, "先落在同一葉，再用該葉內的線性迴歸算出各自的預測",
        "這描述的是 <em>model tree</em>／MARS 那一類混合模型，不是 CART。標準的迴歸樹葉節點只放一個常數。")])}
"""

# ── P01 grow ──────────────────────────────────────────────────────────
BODIES["grow"] = f"""
  <p>方塊要怎麼切？理想上我們想找到讓下面這個 RSS 最小的一組方塊 $R_1, \\dots, R_J$：</p>

  $$\\sum_{{j=1}}^{{J}} \\sum_{{i \\in R_j}} \\left(y_i - \\hat y_{{R_j}}\\right)^2$$

  <p>問題是——<strong>所有可能的切法多到算不完</strong>。所以實務上用一個貪婪的近似：
  <strong>遞迴二元分裂</strong>（recursive binary splitting）。</p>

  <p>做法只有一句話：<strong>每一步，在所有變數 $X_j$ 與所有切點 $s$ 裡面，
  選讓 RSS 掉最多的那一刀</strong>。切完之後，對切出來的兩塊各自再問同樣的問題，一直遞迴下去。
  數學上就是找 $(j, s)$ 最小化</p>

  $$\\sum_{{i:\\, x_i \\in R_1(j,s)}} \\left(y_i - \\hat y_{{R_1}}\\right)^2
    + \\sum_{{i:\\, x_i \\in R_2(j,s)}} \\left(y_i - \\hat y_{{R_2}}\\right)^2$$

  <p>其中 $R_1(j,s) = \\{{X \\mid X_j < s\\}}$、$R_2(j,s) = \\{{X \\mid X_j \\ge s\\}}$。</p>

{info("「貪婪」是什麼意思，為什麼要在意", '''貪婪＝<strong>每一步只看這一步最好</strong>，
  不往前看。所以第一刀是「單獨看只切一刀時最好的那一刀」，
  <strong>不保證</strong>是「最終要切五刀時，第一刀該切哪裡」。<br>
  代價是可能錯過「這一刀本身沒什麼用，但切完之後下一刀超好」的組合。
  好處是快到可以在幾毫秒內算完。這是能夠實用的唯一理由。
  下一節的剪枝，正是為了補救貪婪的短視。''')}

{viz(svg("w09growSvg", 380),
     [info_card("虛擬碼", '<div class="pseudo-code" id="w09growCode" style="font-size:.72rem;">'
                '<span class="line" data-l="1">葉子 = [整個特徵空間]</span>\n'
                '<span class="line" data-l="2"><span class="kw">while</span> 還可以切：</span>\n'
                '<span class="line" data-l="3">    對每個葉子、每個變數 j、每個切點 s：</span>\n'
                '<span class="line" data-l="4">        算 RSS 下降量</span>\n'
                '<span class="line" data-l="5">    切下降最多的那一刀</span>\n'
                '<span class="line" data-l="6">葉子的預測值 = 該葉子內的 y 平均</span></div>', "CODE"),
      rows_card("這一刀",
                [("切在哪個變數", "—", "w09growVar"), ("切點 s", "—", "w09growThr"),
                 ("RSS 下降量", "—", "w09growGain"),
                 ("目前葉子數 |T|", "1", "w09growLeaves"),
                 ("目前訓練 RSS", "—", "w09growRss")]),
      info_card("兩邊在看同一件事",
                '左邊是<strong>特徵空間</strong>：每塊方塊填該塊 y 平均值的顏色'
                '（藍＝低、橘紅＝高），點也照 y 上色。右邊是<strong>同一刀一刀長出來的樹</strong>，'
                'R1、R2… 的編號兩邊對得上。<br>資料是固定種子的合成資料，'
                '真值有四塊；<strong>分裂搜尋是在瀏覽器裡即時算的</strong>，不是預錄的動畫。')],
     "w09growStatus",
     "按「單步」切一刀：程式會掃過兩個變數的每個候選切點，挑 RSS 下降最多的那一個。",
     '<button class="btn btn-play" onclick="w09growStart()">▶ 自動長</button>'
     '<button class="btn btn-step" onclick="w09growPlayer &amp;&amp; w09growPlayer.step()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w09growReset()">重置</button>')}

  <p>玩過上面的元件之後有三件事應該很明顯：</p>

  <ul>
    <li><strong>每一刀都是軸平行的。</strong>切出來一定是長方形方塊，
    不可能是斜的一刀。這是樹的表達能力上限，也是 PART 05 要比較的重點。</li>
    <li><strong>RSS 下降量一路遞減。</strong>前幾刀掉很多，後面愈切愈沒用。
    這條遞減曲線就是下一節「該切幾刀」的依據。</li>
    <li><strong>只要切得夠多，訓練 RSS 可以壓到 0。</strong>每個葉子只剩一個點時，
    每個預測都完全命中——然後這個模型什麼都沒學到。</li>
  </ul>

  <h3 id="dx-reg">講義完整實作：Boston 上的迴歸樹</h3>
{card("講義 08 · Boston 迴歸樹（max_depth=3）", code(50, 52, 54), None, src=src("50、52、54"),
      note="這一格畫出的樹，ISLP 書上的解讀是："
           "<code>lstat</code>（低社經地位人口比例）愈低、房價愈高；"
           "而對於 <code>lstat &gt; 14.4</code>、<code>crim &gt; 5.8</code>、<code>rm &lt; 6.8</code> "
           "的郊區小房子，樹預測房價中位數 <strong>12,042 美元</strong>。"
           "<code>max_depth=3</code> 是手動限制——下一節改成用 CV 學出來。")}

{quiz("qGrow", "QUIZ · 遞迴二元分裂",
      "找第一刀時，演算法實際上比較了多少種可能？（p 個變數、n 筆資料）",
      [(True, "大約 p × (n−1) 種：每個變數都試過所有相鄰觀測值之間的切點",
        "對。切點只要試「排序後相鄰兩個值的中間」就夠了，因為切在同一個間隔內的任何位置，分組結果完全一樣。所以候選數是變數數乘上間隔數，算得非常快。"),
       (False, "所有可能的 J 塊分割，因為目標函數就是定義在整組方塊上的",
        "這是<strong>理想</strong>的目標，但它的組合數隨 J 爆炸，算不完。這正是要退而求其次用貪婪法的原因。第一刀只考慮「切成兩塊」。"),
       (False, "只有 p 種：每個變數用它的中位數當切點",
        "不對。切點是被<strong>搜尋</strong>出來的，不是預先指定的。用中位數切是另一種演算法（例如某些 kd-tree），不是 CART。")])}
"""

# ── P02 prune ─────────────────────────────────────────────────────────
BODIES["prune"] = f"""
  <p>上一節的過程如果不管它，樹會一直長到每個葉子只剩幾個點。訓練誤差很漂亮，
  測試誤差很難看——<strong>典型的過度配適</strong>。</p>

  <p>直覺的解法是「RSS 下降量小於某個門檻就停」。<strong>這個解法是錯的</strong>，
  而且錯得很有教育意義：它太短視。一刀本身看起來沒用，
  但切完之後下一刀可能超級有用；提早停就永遠看不到那一刀。</p>

  <p>正確的做法是<strong>先長太大，再剪回來</strong>。剪的依據是
  <strong>成本複雜度剪枝</strong>（cost complexity pruning，也叫 weakest link pruning）：
  對每個 $\\alpha \\ge 0$，找讓下式最小的子樹 $T \\subset T_0$</p>

  $$\\sum_{{m=1}}^{{|T|}} \\sum_{{i:\\, x_i \\in R_m}} \\left(y_i - \\hat y_{{R_m}}\\right)^2
    + \\alpha |T|$$

  <p>$|T|$ 是葉子數。左邊是配適程度，右邊是複雜度的罰款——
  <strong>形式跟第 6 章的 lasso 一模一樣</strong>：一個要小的目標加上一個乘了調整參數的罰項。
  $\\alpha = 0$ 時罰款是零，最小化的就是訓練誤差，答案是完整的 $T_0$；
  $\\alpha$ 愈大，多留一個葉子愈貴，樹就愈小。</p>

{info("為什麼這招可行：α 一動，樹是「一層一層剝」的", '''關鍵的技術事實是：
  $\\alpha$ 從 0 慢慢調大時，分支是以<strong>巢狀而且可預測的方式</strong>被剪掉——
  $\\alpha_1 < \\alpha_2$ 對應的子樹一定滿足 $T(\\alpha_2) \\subset T(\\alpha_1)$。<br>
  所以整條「子樹序列」只有 $O(|T_0|)$ 條，一次算完就好，
  不必去枚舉指數多的子樹。<code>scikit-learn</code> 的
  <code>cost_complexity_pruning_path()</code> 回傳的就是這條序列的斷點。''')}

  <p>剩下的問題是 α 該取多少。這是第 5 章的老題目：<strong>用交叉驗證選</strong>。
  ISLP 演算法 8.1 把整套流程寫成四步：</p>

  <ol>
    <li>用遞迴二元分裂在訓練資料上長一棵很大的樹。</li>
    <li>對它做成本複雜度剪枝，得到一整條「子樹 vs α」的序列。</li>
    <li>用 K 折交叉驗證選 α：每一折都<strong>重跑步驟 1 與 2</strong>，
    在留出的那折上算誤差，然後對每個 α 平均，挑誤差最小的 α̂。</li>
    <li>回到完整訓練資料，交出對應 α̂ 的那棵子樹。</li>
  </ol>

{viz(chart("w09pruneChart", "tall",
           "。此圖的重點：訓練 MSE 隨葉子數單調下降，但 CV 與測試 MSE 先降後平——"
           "曲線拉平的位置就是該停的地方。"),
     [rows_card("目前的剪枝強度",
                [("α", "—", "w09pruneA"), ("葉子數 |T|", "—", "w09pruneL"),
                 ("訓練 MSE", "—", "w09pruneTr"), ("CV MSE（六折）", "—", "w09pruneCv"),
                 ("測試 MSE", "—", "w09pruneTe")]),
      info_card("怎麼看這張圖",
                'x 軸是剪完之後的葉子數（α 從右往左遞增），三條線分別是訓練、六折 CV、'
                '與測試 MSE。<strong>訓練那條一定單調下降</strong>。它不能當選擇依據。'
                'CV 那條才是可以拿來選的，虛線標的是 CV 選出來的葉子數。', "圖 8.5"),
      info_card("跟課本比",
                '課本圖 8.5 的 CV 最低點在 <strong>3 個葉子</strong>，我們這個分割是 '
                '<strong id="w09pruneBest">—</strong> 個。'
                '數字不會一樣（132/131 的隨機切分不同），但<strong>形狀一樣</strong>：'
                '從 1 到 3 個葉子誤差雪崩式下降，之後就在雜訊裡晃。')],
     "w09pruneStatus", "拖動 α：α 愈大，樹被剪得愈小。看三條誤差線怎麼反應。",
     slider("w09pruneAlpha", "α", 0, 10, 1, 3, "—", "w09pruneSet()", "300px")
     + '<button class="btn btn-toggle" onclick="w09pruneJumpCv()">跳到 CV 選出的 α</button>')}

  <h3 id="dx-ccp">講義完整實作：Boston 上的成本複雜度剪枝</h3>
{card("講義 08 · cost_complexity_pruning_path ＋ GridSearchCV（迴歸）",
      code(57, 59), lab_output(CH, 59), src=src("57、59"),
      note="流程完全照演算法 8.1：先拿 <code>ccp_path.ccp_alphas</code> 當候選格點，"
           "再用 <code>GridSearchCV</code> 在五折上挑，最後 <code>refit=True</code> "
           "用全部訓練資料重配。測試 MSE <strong>28.07</strong>，開根號約 5.30，"
           "也就是預測誤差大約在 5,300 美元的量級。")}

  <h3 id="dx-cv">講義完整實作：分類樹的剪枝（Carseats）</h3>
{card("講義 08 · 用 CV 挑 ccp_alpha（分類）", code(37, 39), lab_output(CH, 39),
      src=src("37、39"),
      note="被選中的樹有 <strong>30 個葉子</strong>（儲存格 43），"
           "在測試集上的正確率 <strong>0.72</strong>（儲存格 45），"
           "比未剪枝的 0.735 還<em>略差</em>。lab 的原話是：「交叉驗證在這裡對我們的幫助不大」。"
           "<strong>這很正常也很重要</strong>——CV 是無偏的選擇工具，但它自己有變異，"
           "換個種子結果就會動。剪枝不是保證變好的魔法。")}

{quiz("qPrune", "QUIZ · 剪枝",
      "為什麼不直接「RSS 下降量小於門檻就停止分裂」，而要先長大再剪？",
      [(True, "因為那樣太短視：一刀本身沒什麼用，但它之後可能接著一刀非常有用",
        "對。ISLP §8.1.1 用的字是 <em>too short-sighted</em>。先長大再剪，等於讓演算法「看過後面」再決定要不要留這一刀。"),
       (False, "因為 RSS 下降量無法計算，只有剪枝時才算得出來",
        "不對，RSS 下降量在每一步都算得出來（上一節的元件就在顯示它）。問題不是算不出來，是<strong>不該用它當停止條件</strong>。"),
       (False, "因為門檻法會讓樹變得太大，剪枝法才會讓樹變小",
        "方向剛好講反了。門檻法產生的樹<strong>更小</strong>（提早停就停了），剪枝法是先刻意長超大再修回來。問題出在門檻法剪掉的可能是錯的分支。")])}
"""

# ── P03 classtree ─────────────────────────────────────────────────────
BODIES["classtree"] = f"""
  <p>分類樹跟迴歸樹幾乎一樣：一樣遞迴二元分裂、一樣剪枝。只有兩件事要換。</p>

  <p><strong>第一，預測值換成多數類別。</strong>落在某個葉子的觀測，
  預測為該葉子內訓練資料<strong>最常出現的那一類</strong>。
  但別忘了同時看類別比例——「90% 是 Yes」跟「51% 是 Yes」的可信度完全不同。</p>

  <p><strong>第二，RSS 換掉。</strong>類別沒有平方誤差可算。最直覺的替代品是
  <strong>錯誤率</strong>（classification error rate）：</p>

  $$E = 1 - \\max_k \\hat p_{{mk}}$$

  <p>$\\hat p_{{mk}}$ 是第 $m$ 個節點裡屬於第 $k$ 類的比例。看起來很合理，
  <strong>但它不夠敏感，不適合當分裂準則</strong>。實務上用另外兩個：</p>

  $$G = \\sum_{{k=1}}^{{K}} \\hat p_{{mk}} (1 - \\hat p_{{mk}}) \\qquad\\text{{（Gini 指數）}}$$

  $$D = -\\sum_{{k=1}}^{{K}} \\hat p_{{mk}} \\log \\hat p_{{mk}} \\qquad\\text{{（交叉熵 / entropy）}}$$

  <p>兩個都在量<strong>節點純度</strong>（node purity）：所有 $\\hat p_{{mk}}$ 都靠近 0 或 1 時值很小。
  兩者數值上非常接近，實務上選哪個幾乎沒差。</p>

{viz(svg("w09impSvg", 330),
     [rows_card("目前的節點組成",
                [("p̂（第一類的比例）", "0.50", "w09impP"),
                 ("錯誤率 E", "—", "w09impErr"),
                 ("Gini 指數 G", "—", "w09impGini"),
                 ("交叉熵 D", "—", "w09impEnt")]),
      info_card("三條線的關鍵差別",
                '<strong>錯誤率是兩段直線</strong>，在 p̂ = 0.5 折一下。'
                '直線代表「斜率是常數」：從 0.5 移到 0.4 跟從 0.2 移到 0.1，它給的獎勵一樣多。'
                '<br>Gini 與交叉熵是<strong>凹的曲線</strong>，兩端特別陡——'
                '「把 0.2 推到 0.1」拿到的獎勵比「把 0.5 推到 0.4」多得多。'
                '<strong>這就是「對純度更敏感」的意思。</strong>', "ISLP 8.4 第 3 題"),
      info_card("為什麼折線會出事",
                '因為錯誤率是<strong>線性</strong>的，'
                '「切完之後兩塊的加權錯誤率」常常剛好等於「不切」的錯誤率——'
                '演算法看到下降量 0，就以為這一刀沒用。下面那張表是最經典的例子。')],
     "w09impStatus", "拖動 p̂ 看三個不純度指標的值。注意錯誤率是折線、另兩個是曲線。",
     slider("w09impSl", "p̂", 0, 100, 1, 50, "0.50", "w09impSet()", "280px")
     + '<button class="btn btn-toggle" onclick="w09impToggle()">縮放交叉熵</button>')}

  <p>下面這個例子把問題講得最清楚。父節點有 800 筆、兩類各 400 筆。兩種切法：</p>

{table(["", "左邊（Yes / No）", "右邊（Yes / No）", "加權錯誤率", "加權 Gini", "加權交叉熵"],
       [["切法 A", "300 / 100", "100 / 300", "<strong>0.250</strong>", "0.375", "0.562"],
        ["切法 B", "200 / 400", "<strong>200 / 0</strong>", "<strong>0.250</strong>",
         "<strong>0.333</strong>", "<strong>0.477</strong>"]])}
  <p style="font-size:.82rem;color:var(--muted);">兩種切法都是 200 筆被分錯，
  <strong>錯誤率完全一樣</strong>，所以用錯誤率當準則的話，這兩刀「一樣好」。
  但切法 B 生出了一個<strong>完全純的葉子</strong>（200 筆全是 Yes），
  Gini 與交叉熵都認得出這件事比較有價值。交叉熵用自然對數。</p>

  <p>ISLP 圖 8.6 的 <code>Heart</code> 例子有同一個現象的實例：
  未剪枝樹右下角那一刀 <code>RestECG &lt; 1</code>，兩邊的預測都是 <code>Yes</code>——
  <strong>錯誤率完全沒降</strong>，可是右邊那 9 筆全是 <code>Yes</code>、左邊只有 7/11，
  純度差很多。這一刀之所以被切，就是因為 Gini 與交叉熵看得到差別。</p>

{info("剪枝的時候可以換回錯誤率", '''分裂用 Gini／交叉熵，
  <strong>剪枝時三個都可以用</strong>；如果你最終在意的是預測正確率，
  剪枝階段用錯誤率反而更對題。<code>scikit-learn</code> 的
  <code>DecisionTreeClassifier(criterion=...)</code> 只管分裂準則；
  剪枝用的是 <code>ccp_alpha</code>，而 <code>GridSearchCV(scoring='accuracy')</code>
  那一步就等於「用錯誤率挑 α」。lab 正是這樣寫的。''')}

  <h3 id="dx-ent">講義完整實作：用交叉熵長分類樹，再把樹印成文字</h3>
{card("講義 08 · DecisionTreeClassifier(criterion='entropy') ＋ export_text",
      code(17, 29), lab_output(CH, 29), src=src("15、17、29"),
      note="訓練正確率 0.79（儲存格 19），對應偏差 "
           "<code>log_loss</code> = <strong>0.4711</strong>（儲存格 21）。"
           "那正是 (8.7) 式的交叉熵。<code>show_weights=True</code> 印出的 "
           "<code>weights: [7.00, 3.00]</code> 就是該葉子裡 No／Yes 的筆數，"
           "拿它算 $\\hat p_{{mk}}$ 就能自己驗算 Gini 與交叉熵。"
           "第一刀切在 <code>ShelveLoc[Good]</code>——貨架位置好不好最重要。")}

{qa("觀念釐清", [
    ("Q：為什麼分裂準則用 Gini 或交叉熵，而不用我們真正在意的錯誤率？",
     "<p>因為錯誤率<strong>對純度的變化不敏感</strong>，常常給出「下降量 0」的假訊號，"
     "讓貪婪演算法以為這一刀沒用而不切。</p>"
     "<p>根本原因是形狀。兩類的情況下錯誤率是 $\\min(\\hat p, 1-\\hat p)$，"
     "這是<strong>兩段直線</strong>；Gini 是 $2\\hat p(1-\\hat p)$、交叉熵是 "
     "$-\\hat p \\log \\hat p - (1-\\hat p)\\log(1-\\hat p)$，兩者都<strong>嚴格凹</strong>。"
     "而「切一刀的不純度下降量」等於父節點的不純度減掉兩個子節點不純度的加權平均。"
     "對嚴格凹的函數，這個下降量<strong>永遠大於 0</strong>（除非兩邊的 $\\hat p$ 剛好相同）；"
     "對線性的函數，只要兩邊的 $\\hat p$ 落在 0.5 的同一側，加權平均就剛好等於父節點的值，"
     "下降量是 0。</p>"
     "<p>上面那張 800 筆的表就是這件事的實例：切法 B 生出一個完全純的葉子，"
     "錯誤率卻報「跟切法 A 一樣」。而且純度不只是美學問題——"
     "落在純葉子裡的測試點，我們對它的預測有信心；落在 7/11 那個葉子裡的，我們沒有。"
     "這個差別在需要輸出<strong>機率</strong>時尤其要緊，而集成方法（bagging 的多數投票、"
     "boosting 的加權和）全都靠葉子的機率估計吃飯。</p>"
     "<p>最後補一句實務規則：<strong>分裂用 Gini／交叉熵，剪枝與最終評估用錯誤率</strong>（或 AUC）。"
     "兩者的角色不同，不必統一。</p>"),
])}

{quiz("qImp", "QUIZ · 不純度",
      "兩類問題中，某節點有 50 筆 Yes、50 筆 No。它的 Gini 指數是多少？",
      [(True, "0.5",
        "對。$G = \\hat p(1-\\hat p) + (1-\\hat p)\\hat p = 2 \\times 0.5 \\times 0.5 = 0.5$。這是兩類情況下 Gini 的<strong>最大值</strong>，也就是最不純的狀態。"),
       (False, "0.25",
        "這是 $\\hat p (1-\\hat p) = 0.25$，只算了一項。Gini 的定義是<strong>對所有 K 個類別加總</strong>，兩類的時候要算兩次，所以是 0.5。"),
       (False, "1.0",
        "不對。兩類的 Gini 上限是 0.5（在 $\\hat p = 0.5$ 時），下限是 0（完全純）。要拿到接近 1 的 Gini，得有很多個類別（K 類的上限是 $1 - 1/K$）。")])}
"""

# ── P04 vslinear ──────────────────────────────────────────────────────
BODIES["vslinear"] = f"""
  <p>兩個模型形式擺在一起：</p>

  $$f(X) = \\beta_0 + \\sum_{{j=1}}^{{p}} X_j \\beta_j
    \\qquad\\text{{對上}}\\qquad
    f(X) = \\sum_{{m=1}}^{{M}} c_m \\cdot \\mathbf{{1}}(X \\in R_m)$$

  <p>哪一個好？<strong>沒有普遍答案，看真實的邊界長什麼樣。</strong>
  ISLP 圖 8.7 用兩排圖把這件事講完：</p>

{table(["真實邊界", "線性模型（左欄）", "樹（右欄）", "誰贏"],
       [["<strong>線性</strong>（斜的一刀）", "一刀就完美切開",
         "要用很多階梯去逼近那條斜線，邊界呈鋸齒狀", "<strong>線性模型</strong>"],
        ["<strong>非線性</strong>（方塊狀）", "怎麼轉都切不對，一定有一大塊錯的",
         "幾刀就切得漂亮", "<strong>樹</strong>"]])}

  <p>關鍵在於<strong>樹的每一刀都是軸平行的</strong>。要表現「$X_1 + X_2 > 1$」這種斜邊界，
  樹只能用一堆小台階去爬那條斜線——能逼近，但要很多刀，
  而每一刀都花掉自由度、都增加變異。反過來，
  「$X_1 < 3$ 且 $X_2 > 5$ 的那一塊特別高」這種方塊狀結構，
  線性模型除非你手動把交互作用項乘出來，否則永遠抓不到。</p>

{info("怎麼決定用哪個：別猜，用第 5 章的工具", '''這不是靠肉眼看散佈圖決定的事。
  <strong>把兩個都配一次，用交叉驗證比測試誤差</strong>，就這樣。<br>
  但誤差不是唯一考量：有時候你選樹是因為<strong>要能畫給人看</strong>
  （醫療、法規、風控場景），這時候即使樹的誤差稍差一點也值得。
  反過來，如果只追求準確率，本章後半的集成方法幾乎一定打得贏兩者，
  代價是失去那張可以貼在牆上的圖。''')}

  <p>ISLP §8.1.4 把樹的優缺點列成清單，值得整段記下來：</p>

{table(["", "內容"],
       [["✔ 好解釋", "比線性迴歸還好解釋。可以畫出來給非專業的人看懂"],
        ["✔ 像人在想事情", "「先看這個、再看那個」的層層判斷，貼近人的決策過程"],
        ["✔ 類別變數免編碼", "一刀就是「把某些水準分到左邊」，不需要虛擬變數"],
        ["✔ 尺度無關", "只看大小順序，不必標準化，也不怕離群的 x"],
        ["✘ 準確率不夠好", "單一棵樹通常打不過本書其他方法"],
        ["✘ <strong>非常不穩定</strong>", "資料動一點點，整棵樹的結構可能完全改變"]])}

  <p>最後那一項是後半章的引擎。「不穩定」用統計的話講就是<strong>變異很大</strong>，
  而降變異最古典的手段就是<strong>平均</strong>。這正好是下三節的主題。</p>

{quiz("qVsLin", "QUIZ · 樹 vs 線性模型",
      "真實的決策邊界是一條斜線 $X_1 + X_2 = 1$。用決策樹去配會發生什麼事？",
      [(True, "樹會用許多軸平行的小台階去逼近那條斜線，能逼近但需要很多刀",
        "對。這是 ISLP 圖 8.7 上排的情境。樹不是「配不出來」，是「要花很多刀才配得像」——刀愈多變異愈大，所以在這種資料上輸給一刀就完事的線性模型。"),
       (False, "樹完全配不出來，因為它只能表示水平或垂直的邊界",
        "說得太重了。單一刀確實只能軸平行，但<strong>很多刀疊起來</strong>可以逼近任何邊界（樹是萬用近似器）。問題是效率，不是能力。"),
       (False, "樹會自動找到 X₁ + X₂ 這個組合當新的分裂變數",
        "不會。標準的 CART 每一刀只看<strong>單一個</strong>原始變數。會去找線性組合的是 oblique tree／斜樹那一類變體，不是本章講的樹。")])}
"""

# ── P05 why ───────────────────────────────────────────────────────────
BODIES["why"] = f"""
  <p>先講一個跟樹無關的事實，因為整個集成學習都建在它上面。</p>

  <p>你把一個難題丟給幾千個隨機的路人，把他們的答案彙總起來——
  彙總的答案常常比一個專家還準。這叫<strong>群眾智慧</strong>（wisdom of the crowd）。
  機器學習版本的說法是：<strong>一群預測器合起來，常常比裡面最好的那一個還準</strong>。
  這一群叫做<strong>集成</strong>（ensemble），做法叫集成方法（ensemble method）。</p>

  <p>最簡單的集成是<strong>多數投票</strong>（hard voting）：M 個分類器各投一票，
  票多的那一類就是答案。假設每個分類器<strong>各自獨立</strong>、正確率都是 $p$，
  那麼多數投票的正確率就是二項分佈的尾機率：</p>

  $$P(\\text{{投票正確}}) = \\sum_{{k > M/2}} \\binom{{M}}{{k}} p^k (1-p)^{{M-k}}$$

  <p>講義第 31 頁舉的例子：<strong>1000 個只有 51% 正確率的弱學習器</strong>，
  多數投票之後可望達到 75% 的正確率。這個數字大得不像真的。下面自己算一次。</p>

{viz(svg("w09voteSvg", 250) + "\n" + chart("w09voteChart", "",
        "。此圖的重點：只要 p > 0.5，多數投票的正確率隨分類器數量單調上升並趨近 1；"
        "但 p < 0.5 時它反而趨近 0——投票會放大偏誤，不會修正它。"),
     [rows_card("目前設定",
                [("單一分類器正確率 p", "0.55", "w09voteP"),
                 ("分類器個數 M", "15", "w09voteM"),
                 ("多數投票正確率", "—", "w09voteAcc"),
                 ("比單一個高多少", "—", "w09voteGain")]),
      rows_card("講義第 31 頁的例子",
                [("p = 0.51, M = 1000", "—", "w09voteDeck"),
                 ("p = 0.49, M = 1000", "—", "w09voteBad")]),
      info_card("上面那排方塊",
                '每個方塊是一個分類器在某一筆資料上的表現：'
                '<span style="color:var(--accent3);font-weight:700;">綠＝答對</span>、'
                '<span style="color:var(--accent);font-weight:700;">紅＝答錯</span>'
                '（固定種子的模擬，所以你重載頁面看到的是同一組）。'
                '下面那條線是多數投票的結果。<strong>拖 p 到 0.45 看看</strong>——'
                '紅色一多，投票就開始穩定地答錯。')],
     "w09voteStatus", "拖動 p 與 M：看多數投票的正確率怎麼變。p 拖到 0.5 以下會發生有趣的事。",
     slider("w09voteSlP", "p", 30, 80, 1, 55, "0.55", "w09voteSet()", "220px")
     + slider("w09voteSlM", "M", 1, 201, 2, 15, "15", "w09voteSet()", "200px"))}

{info("「各自獨立」是整件事的命門", '''上面那條公式只有在
  <strong>分類器彼此完全獨立、錯的地方互不相關</strong>時才成立。<br>
  真實世界裡沒這種好事：同一份資料訓練出來的模型，錯的地方通常也一樣，
  這時候投一百票跟投一票差不多。所以集成方法真正在解的問題不是「怎麼投票」，
  而是<strong>「怎麼弄出一群不一樣的預測器」</strong>：<br>
  ① 用<strong>不同的演算法</strong>（voting／stacking，PART 11）<br>
  ② 用<strong>不同的資料</strong>（bagging，下一節）<br>
  ③ 用<strong>不同的變數</strong>（random forest，PART 08）<br>
  ④ 讓後面的人<strong>專門修前面的錯</strong>（boosting，PART 09）''', "warm")}

  <h3 id="dx-vote">講義完整實作：VotingClassifier</h3>
{card("講義 08 · 三個不同演算法的多數投票（Carseats）",
      code(238), lab_output(CH, 238), src=src("237、238"),
      note="KNN 0.78、決策樹 0.73、樸素貝氏 0.79，投票之後 <strong>0.82</strong>——"
           "比裡面<strong>任何一個</strong>都好，而且標準差還從 0.06/0.07 掉到 0.04。"
           "這裡三個成員是<strong>完全不同的演算法</strong>，所以它們錯的地方不一樣，"
           "投票才有效。（標籤印成 <code>StackingClassifier</code> 是 lab 裡的筆誤，"
           "這一格用的是 <code>VotingClassifier(voting='hard')</code>。）")}

{quiz("qVote", "QUIZ · 投票與大數法則",
      "1000 個分類器各自的正確率都是 <strong>0.48</strong>，且彼此獨立。多數投票的正確率大約是多少？",
      [(True, "接近 0，比單一個分類器差得多",
        "對。大數法則對兩個方向一樣有效：p > 0.5 時投票趨近 1，p < 0.5 時趨近 0。0.48 × 1000 的期望是 480 票，過半要 501 票，機率極小。<strong>投票放大多數的傾向，不管那個傾向對不對。</strong>"),
       (False, "還是 0.48 左右，投票不會改變平均正確率",
        "不對。投票不是在平均正確率，是在算「過半」的機率。$\\mathrm{Bin}(1000, 0.48)$ 超過 500 的機率遠低於 0.48。"),
       (False, "接近 0.52，因為投票會把錯誤的方向反轉過來",
        "不對。集成方法沒有「反轉」機制。如果你知道分類器系統性地答錯，把它的輸出取反就變成 0.52，但那是你自己動手，不是投票幫你做的。")])}
"""

# ── P06 bagging ───────────────────────────────────────────────────────
BODIES["bagging"] = f"""
  <p>回到樹。單一棵樹的問題是<strong>變異太大</strong>。而降變異最古典的手段，
  第 5 章就講過了：<strong>平均</strong>。給定 $n$ 個獨立的觀測值、每個變異數都是 $\\sigma^2$，
  它們的平均 $\\bar Z$ 的變異數是 $\\sigma^2 / n$。</p>

  <p>所以理想的做法是：蒐集 $B$ 份獨立的訓練資料、各配一棵樹、把預測平均起來。
  問題是我們只有一份資料。<strong>那就用 bootstrap 假造出 $B$ 份</strong>。
  這就是 <strong>bootstrap aggregation</strong>，簡稱 <strong>bagging</strong>：</p>

  $$\\hat f_{{\\text{{bag}}}}(x) = \\frac{{1}}{{B}} \\sum_{{b=1}}^{{B}} \\hat f^{{*b}}(x)$$

  <p>分類問題就把平均換成<strong>多數投票</strong>：B 棵樹各投一票，票多的那一類就是答案。</p>

{info("bagging 的樹要長很深，而且不要剪枝", '''這一點跟前兩節的直覺剛好相反，
  但完全講得通：<br>
  每棵樹都<strong>長到很深、不剪枝</strong>，所以每棵樹的<strong>偏差很小、變異很大</strong>。
  然後平均 B 棵樹，把變異壓下來。<strong>偏差在平均的過程裡不會變</strong>
  （B 個無偏估計的平均還是無偏），所以我們用「降變異」換到了「保留低偏差」。<br>
  反過來如果每棵樹都剪成三個葉子，偏差大，平均一百棵之後偏差還是那麼大——
  白費工。<strong>bagging 只治變異，不治偏差。</strong>''')}

  <p>還有一個副產品，好用到有點不像話。有放回抽 $n$ 次，某一筆<strong>始終沒被抽到</strong>的機率是</p>

  $$\\left(1 - \\frac{{1}}{{n}}\\right)^n \\;\\xrightarrow[n \\to \\infty]{{}}\\; e^{{-1}} \\approx 0.368$$

  <p>所以每棵樹平均只用到約 <strong>2/3</strong> 的資料，剩下那 <strong>1/3</strong> 沒被用到的叫做
  <strong>袋外樣本</strong>（out-of-bag, OOB）。它們對這棵樹來說是天然的驗證集——
  <strong>完全免費的測試誤差估計</strong>，不必再做交叉驗證。
  （這個 0.632／0.368 在<a href="resampling_methods.html#bootstrap">第 5 章 bootstrap</a>
  那一節推導過，回去對一下。）</p>

{viz(svg("w09bagSvg", 220),
     [rows_card("這一棵樹的抽樣",
                [("被抽中幾筆（去重）", "—", "w09bagIn"), ("OOB 幾筆", "—", "w09bagOob"),
                 ("這次的 OOB 比例", "—", "w09bagPct"),
                 ("累計樹的棵數 B", "0", "w09bagB"),
                 ("累計 OOB 比例", "—", "w09bagAvg"),
                 ("理論值 1/e", "36.79%", "w09bagTheory")]),
      info_card("怎麼看",
                '20 顆球＝20 筆訓練資料。每按一次就是「長一棵樹」：'
                '有放回抽 20 次，<strong>實心＝被抽到</strong>（右上角的 ×k 是被抽到幾次），'
                '<strong>虛線空框＝這棵樹沒看過它</strong>。'
                '按幾十次，右邊的累計 OOB 比例就會定在 36.8% 附近。'),
      info_card("OOB 誤差怎麼算",
                '對第 i 筆資料，把「所有沒用到它的那些樹」找出來（大約 B/3 棵），'
                '用它們預測第 i 筆再平均（或投票），得到一個 OOB 預測。'
                'n 筆各做一次，就得到 OOB 誤差。<strong>B 夠大時它幾乎等於 LOOCV 誤差</strong>，'
                '但成本只有一次配適。', "ISLP §8.2.1")],
     "w09bagStatus", "按「長一棵樹」看一次有放回重抽：虛線框的球就是這棵樹的袋外樣本。",
     '<button class="btn btn-step" onclick="w09bagOne()">→ 長一棵樹</button>'
     '<button class="btn btn-play" onclick="w09bagMany()">▶ 連長 200 棵</button>'
     '<button class="btn btn-reset" onclick="w09bagReset()">重置</button>')}

  <p>還有一件實務上很重要的事：<strong>B 不是需要調的參數</strong>。
  ISLP 圖 8.8 顯示誤差隨 B 上升而下降、然後平掉就不動了——
  <strong>B 太大不會過度配適</strong>（只是浪費算力），B 太小才會欠配適。
  所以做法是「挑一個大到誤差已經平掉的 B」，通常 100 到 500 就夠。</p>

  <h3 id="dx-bag">講義完整實作：Boston 上的 bagging</h3>
{card("講義 08 · bagging ＝ max_features = p 的 random forest",
      code(64, 68), lab_output(CH, 68), src=src("64、66、68"),
      note="<code>max_features=X_train.shape[1]</code>（＝12）就是「每次分裂都考慮全部變數」，"
           "也就是 bagging。B = 100 時測試 MSE 是 <strong>14.6347</strong>（儲存格 66），"
           "B = 500 時 14.6057——<strong>幾乎沒動</strong>，正是「B 大不會過度配適也不會再變好」。"
           "對照單一棵剪枝樹的 28.07：<strong>誤差直接砍半</strong>。")}

{qa("觀念釐清", [
    ("Q：Bagging 為什麼能降變異，卻幾乎不降偏差？",
     "<p>從公式看最清楚。設每棵樹的預測 $\\hat f^{*b}(x)$ 期望值都是 $\\mu(x)$、變異數都是 "
     "$\\sigma^2(x)$、兩兩相關係數是 $\\rho$。那麼平均的期望與變異是</p>"
     "<p>$$\\mathbb{E}\\left[\\hat f_{\\text{bag}}(x)\\right] = \\mu(x), \\qquad "
     "\\mathrm{Var}\\left[\\hat f_{\\text{bag}}(x)\\right] = "
     "\\frac{1-\\rho}{B}\\sigma^2(x) + \\rho\\, \\sigma^2(x)$$</p>"
     "<p><strong>期望值完全沒變</strong>——平均一堆同分佈的東西，期望還是那個期望，"
     "所以偏差 $\\mu(x) - f(x)$ 一動也不動。變異數則被壓成兩項：第一項隨 B 變大而消失，"
     "第二項 $\\rho \\sigma^2$ <strong>不隨 B 消失</strong>。這第二項就是下一節 random forest 要對付的東西。</p>"
     "<p>所以 bagging 的正確用法是：<strong>拿變異很大、偏差很小的東西去平均</strong>。"
     "長很深不剪枝的樹剛好就是這種東西。它把訓練資料配到幾乎完美（低偏差），"
     "但資料換一點就長成另一棵（高變異）。反過來，"
     "拿 bagging 去平均一堆線性迴歸幾乎沒有用：線性迴歸本來變異就小，沒什麼可壓的。</p>"),
    ("Q：既然有 OOB 誤差，還需要交叉驗證嗎？",
     "<p>估 bagging／random forest 本身的測試誤差時，OOB 就夠了，而且便宜太多："
     "配一次模型就順手拿到，不必像 k-fold 那樣配 k 次。ISLP 說 B 夠大時 OOB 誤差"
     "<strong>幾乎等於 LOOCV 誤差</strong>。</p>"
     "<p>要小心的是兩件事。第一，如果你用 OOB 誤差去<strong>挑超參數</strong>"
     "（例如挑 m、挑樹的深度），那被挑中的那組的 OOB 誤差就跟第 5 章講的一樣會偏低，"
     "不能再當誠實的測試誤差報出來。第二，OOB 只有在<strong>有 bootstrap 抽樣</strong>時才存在——"
     "boosting 沒有 bootstrap，所以沒有 OOB，只能用驗證集或 CV。</p>"),
])}

{quiz("qBag", "QUIZ · Bagging 與 OOB",
      "做 bagging 時，每一棵樹該長多深？",
      [(True, "長到很深、不剪枝——刻意讓每棵樹低偏差高變異，再靠平均壓變異",
        "對。ISLP §8.2.1 的原話是 <em>These trees are grown deep, and are not pruned</em>。平均能治變異但治不了偏差，所以偏差要在單棵樹的階段就先壓低。"),
       (False, "用交叉驗證幫每一棵樹各自挑最佳的 ccp_alpha，才不會過度配適",
        "不對，而且是雙重浪費：算力花在 B 次 CV 上，換來的是一堆偏差偏大的樹，平均之後偏差還是偏大。單棵樹要剪枝是因為它<em>自己</em>就是最終模型；在 bagging 裡它不是。"),
       (False, "全部剪成單一分裂的 stump，這樣集成才穩定",
        "這是 <strong>boosting</strong> 的做法，不是 bagging。boosting 是序列式地降偏差，所以每棵樹可以很弱；bagging 是並行地降變異，弱樹平均起來還是弱。")])}
"""

# ── P07 rf ────────────────────────────────────────────────────────────
BODIES["rf"] = f"""
  <p>上一節的公式留了一個尾巴：</p>

  $$\\mathrm{{Var}}\\left[\\hat f_{{\\text{{bag}}}}(x)\\right]
    = \\frac{{1-\\rho}}{{B}}\\sigma^2(x) + \\rho\\, \\sigma^2(x)$$

  <p>第二項 $\\rho \\sigma^2$ <strong>不管 B 多大都不會消失</strong>。
  $\\rho$ 是樹跟樹之間預測的相關係數，而 bagging 的樹相關得很嚴重。原因很具體：</p>

  <p><strong>如果資料裡有一個特別強的變數</strong>，那麼幾乎每一棵 bagged 樹都會拿它當根節點的分裂變數。
  根一樣，接下來的結構也就大同小異——B 棵樹長得像複製品，$\\rho$ 接近 1，
  平均一百棵跟平均一棵差不多。</p>

  <p><strong>Random forest</strong> 的解法簡單到有點粗暴：<strong>每一次分裂，
  只准從隨機挑出的 $m$ 個變數裡選</strong>（$m < p$，而且每一刀都重新抽一次）。
  典型取 $m \\approx \\sqrt{{p}}$（分類）或 $m = p/3$（迴歸）。</p>

  <p>於是平均有 $(p-m)/p$ 比例的分裂<strong>根本看不到那個強變數</strong>，
  其他變數就有機會出頭。樹跟樹長得不一樣了，$\\rho$ 掉下來，
  第二項跟著縮小。這叫<strong>去相關</strong>（decorrelate）。
  注意 $m = p$ 時 random forest 就<strong>退化成 bagging</strong>，
  所以 bagging 只是 random forest 的一個特例。</p>

{viz(chart("w09rfChart", "tall",
           "。此圖的重點：m 愈小，樹與樹之間的相關 ρ 愈低（右側面板），"
           "但單棵樹也愈弱——m 是一個要調的參數，不是愈小愈好。"),
     [rows_card("每個 m 的表現（B = 300）",
                [("m = p（bagging）", "—", "w09rfR0"), ("m = p/2", "—", "w09rfR1"),
                 ("m ≈ √p", "—", "w09rfR2"), ("m = 2", "—", "w09rfR3"),
                 ("單一棵樹", "—", "w09rfSingle")]),
      info_card("怎麼看這張圖",
                'x 軸是樹的棵數 B（前 B 棵的平均預測），y 軸是測試 MSE。'
                '右邊面板每一列同時列出<strong>該 m 的測試 MSE 與樹間平均相關 ρ</strong>。'
                '<strong>ρ 一定隨 m 變小而下降</strong>。那是去相關的直接證據；'
                '但誤差會不會跟著下降，要看資料。', "圖 8.8／8.10"),
      info_card("兩份資料為什麼結論不同",
                '<strong>Boston</strong>：只有 12 個變數、<code>lstat</code> 與 <code>rm</code> '
                '真的最有用，硬是不給樹看它們只是自找麻煩，所以 m = p 最好。'
                'lab 的原話就是「隨機森林比 bagging 表現稍差」。<br>'
                '<strong>模擬資料</strong>：30 個彼此相關的變數、其中 20 個都帶訊號，'
                '一個特別強。這正是 ISLP §8.2.2 描述的情境，這時 m ≈ √p 明顯贏。')],
     "w09rfStatus", "換資料集看 m 的效果。注意兩份資料給出相反的結論。",
     '<label class="slider-label" style="margin-right:.4rem;">資料</label>'
     '<select id="w09rfSel" class="mono" onchange="w09rfDraw()">'
     '<option value="boston" selected>Boston（p = 12，lab 的同一份切分）</option>'
     '<option value="sim">模擬：1 強 ＋ 20 中，30 個變數彼此相關</option>'
     '</select>')}

  <h3 id="dx-imp">講義完整實作：random forest 與變數重要度</h3>
{card("講義 08 · max_features = 6 的 random forest ＋ feature_importances_",
      code(70, 72), lab_output(CH, 72), src=src("70、72"),
      note="測試 MSE <strong>20.0428</strong>（儲存格 70），比 bagging 的 14.63 差——"
           "在 Boston 上限制 m 沒有幫助，這一點 lab 講得很直白。"
           "下面那張表是<strong>變數重要度</strong>：每個變數造成的不純度下降總量，在所有樹上平均。"
           "<code>lstat</code>（0.356）與 <code>rm</code>（0.332）合起來就佔了近 70%——"
           "社區的財富水準與房子大小最重要。這張表怎麼讀、有什麼陷阱，放在 PART 11 講。")}

{qa("觀念釐清", [
    ("Q：Random Forest 的 m 為什麼要小於 p？「去相關」在數學上到底降低了什麼？",
     "<p>降低的是變異數公式裡<strong>那個不隨 B 消失的項</strong>。</p>"
     "<p>$$\\mathrm{Var}\\left[\\hat f_{\\text{avg}}\\right] = "
     "\\frac{1-\\rho}{B}\\sigma^2 + \\rho\\,\\sigma^2$$</p>"
     "<p>把 B 開到一萬，第一項趨近 0，剩下的是 $\\rho \\sigma^2$。"
     "所以「多種幾棵樹」有一個天花板，而天花板的高度由 $\\rho$ 決定。"
     "bagging 沒有任何機制去壓 $\\rho$——每棵樹都看得到全部變數，"
     "貪婪法就會一再選中同一個最強的變數，$\\rho$ 因此很高（本頁 Boston 上實測 m = p 時 ρ ≈ 0.82）。"
     "限制 m 之後，不同的樹被迫用不同的變數，ρ 掉到 0.68。</p>"
     "<p>但這裡有一個取捨，而且非常實在：<strong>m 變小同時讓每棵樹變差</strong>，"
     "也就是上式的 $\\sigma^2$ 變大（元件的側欄有列出每棵樹預測的變異，m 愈小它愈大）。"
     "所以 $\\rho \\sigma^2$ 是「$\\rho$ 下降 × $\\sigma^2$ 上升」的乘積，不保證變小。"
     "$m$ 太小的時候，樹弱到連訊號都找不到，整體反而變糟。</p>"
     "<p>什麼時候壓 $\\rho$ 划算？<strong>變數多、而且彼此相關</strong>的時候。"
     "此時「不給樹看變數 A」的損失很小（相關的變數 B 幾乎能代替它），"
     "但換到的多樣性很大。反過來像 Boston 這種只有 12 個變數、"
     "其中兩個明顯不可替代的資料，遮住它們的代價就付不起。"
     "<strong>結論：$m$ 是超參數，$\\sqrt{p}$ 只是好用的預設值，該調就調。</strong></p>"),
])}

{quiz("qRf", "QUIZ · Random Forest",
      "Random forest 每次分裂只從 m 個隨機挑出的變數裡選。這個 m 是怎麼抽的？",
      [(True, "每一次分裂都重新隨機抽 m 個變數，不是整棵樹共用一組",
        "對。ISLP 的原話是 <em>A fresh sample of m predictors is taken at each split</em>。如果整棵樹共用一組變數，那叫 random subspace（隨機子空間）法，多樣性來源不同、效果也不同。"),
       (False, "每棵樹開始前抽一次 m 個變數，整棵樹都只用這 m 個",
        "這是 <strong>random subspace</strong>／隨機子空間法，講義第 34 頁提過（跟 bagging 合用時叫 random patches）。它跟 random forest 是不同的東西——RF 的重抽發生在<strong>每一刀</strong>。"),
       (False, "抽出重要度最高的 m 個變數，這樣樹才不會浪費分裂",
        "剛好相反。如果每次都用最重要的 m 個，每棵樹又會長得一模一樣，$\\rho$ 降不下來。那就白做了。<strong>隨機</strong>才是重點。")])}
"""

# ── P08 boosting ──────────────────────────────────────────────────────
BODIES["boosting"] = f"""
  <p>Bagging 與 random forest 是<strong>並行</strong>的：B 棵樹互不相干，
  誰先誰後無所謂，可以開 B 個執行緒一起長。<strong>Boosting 完全相反——樹是序列長出來的，
  每一棵都靠前面那些樹的資訊決定自己要做什麼。</strong>而且沒有 bootstrap，
  每棵樹都看全部資料，只是看的<strong>目標</strong>被改過。</p>

  <p>ISLP 演算法 8.2 是整章最值得背下來的十行：</p>

{info("梯度提升（regression 版），ISLP 演算法 8.2", '''<strong>1.</strong> 令 $\\hat f(x) = 0$，
  殘差 $r_i = y_i$。<br>
  <strong>2.</strong> 對 $b = 1, 2, \\dots, B$：<br>
  &nbsp;&nbsp;&nbsp;(a) 用 $(X, r)$ 配一棵只有 $d$ 刀（$d+1$ 個葉子）的<strong>小樹</strong> $\\hat f^b$；<br>
  &nbsp;&nbsp;&nbsp;(b) 把收縮後的它加進去：$\\hat f(x) \\leftarrow \\hat f(x) + \\lambda \\hat f^b(x)$；<br>
  &nbsp;&nbsp;&nbsp;(c) 更新殘差：$r_i \\leftarrow r_i - \\lambda \\hat f^b(x_i)$。<br>
  <strong>3.</strong> 輸出 $\\hat f(x) = \\sum_{b=1}^{B} \\lambda \\hat f^b(x)$。''')}

  <p>注意 (a)：<strong>配的目標是殘差 $r$，不是 $y$</strong>。這就是整個把戲。
  第一棵樹抓走一部分結構，剩下沒解釋掉的變成新的目標，第二棵樹去抓它，以此類推。
  ISLP 的說法是 <strong>boosting 學得很慢</strong>（learns slowly）——
  而在統計學習裡，學得慢的方法往往表現得好。</p>

{viz(svg("w09gbSvg", 400),
     [info_card("虛擬碼", '<div class="pseudo-code" id="w09gbCode" style="font-size:.72rem;">'
                '<span class="line" data-l="1">f = 0；r = y</span>\n'
                '<span class="line" data-l="2"><span class="kw">for</span> b <span class="kw">in</span> <span class="kw">range</span>(B):</span>\n'
                '<span class="line" data-l="3">    tree = 配一棵淺樹(X, r)</span>\n'
                '<span class="line" data-l="4">    f += λ * tree(X)</span>\n'
                '<span class="line" data-l="5">    r -= λ * tree(X)</span></div>', "CODE"),
      rows_card("目前狀態",
                [("已加入的樹 b", "0", "w09gbB"), ("學習率 λ", "0.35", "w09gbLamV"),
                 ("每棵樹的葉子數", "2", "w09gbLeaf"),
                 ("訓練 MSE", "—", "w09gbMse"),
                 ("殘差的標準差", "—", "w09gbSd")]),
      info_card("兩個面板",
                '<strong>上面</strong>是目前的配適 $\\hat f$（橘線）疊在資料上。'
                '<strong>下面</strong>是目前的殘差 $r$，以及下一棵樹準備加上去的那個階梯（虛線）。'
                '注意它總是往殘差最偏的地方去。<br>'
                '<strong>λ 調小</strong>：每一步只走一點點，需要更多棵樹，但配出來的曲線更平滑；'
                '<strong>λ 調到 1</strong>：幾步就衝過去，然後開始抖。')],
     "w09gbStatus", "按「單步」加一棵淺樹：它配的是目前的殘差，然後乘上 λ 加進配適裡。",
     slider("w09gbSlLam", "λ", 5, 100, 5, 35, "0.35", "w09gbSetLam()", "200px")
     + '<label class="slider-label" style="margin:0 .3rem;">深度 d</label>'
     '<select id="w09gbSel" class="mono" onchange="w09gbSetDepth()">'
     '<option value="1" selected>1（stump）</option><option value="2">2</option></select>'
     '<button class="btn btn-play" onclick="w09gbStart()">▶ 開始</button>'
     '<button class="btn btn-step" onclick="w09gbPlayer &amp;&amp; w09gbPlayer.step()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w09gbReset()">重置</button>')}

  <p>Boosting 有<strong>三個</strong>要調的參數，而且跟 bagging 不同，
  <strong>它真的會過度配適</strong>：</p>

{table(["參數", "意思", "典型值", "調錯會怎樣"],
       [["<strong>B</strong>（樹的棵數）", "跑幾輪", "由 CV 決定",
         "<strong>太大會過度配適</strong>（只是通常發生得很慢）。bagging 沒有這個問題"],
        ["<strong>λ</strong>（學習率／收縮）", "每棵樹只採用 λ 倍", "0.01 或 0.001",
         "太小 → 需要非常大的 B；太大 → 幾步就衝過頭，開始配雜訊"],
        ["<strong>d</strong>（每棵樹幾刀）", "交互作用深度", "常常 1 就夠",
         "d = 1（stump）的集成是<strong>加法模型</strong>；d 愈大能抓愈高階的交互作用，也愈容易過度配適"]])}

  <p>$B$ 與 $\\lambda$ 是綁在一起的：<strong>λ 砍十倍，B 大約要放大十倍</strong>。
  lab 用的是 <code>n_estimators=5000, learning_rate=0.001</code>，
  換成 <code>learning_rate=0.2</code> 之後測試 MSE 幾乎一樣（14.48 vs 14.50）——
  在這份資料上兩組設定都落在「已經收斂」的區域裡。</p>

  <h4 id="dx-ada">AdaBoost：不改目標，改權重</h4>

  <p>Boosting 還有另一種更早的版本。<strong>AdaBoost</strong> 不去配殘差，
  而是<strong>調整每一筆資料的權重</strong>：這一輪答錯的點，下一輪權重變大，
  於是下一個分類器會特別在意它們。講義第 44 頁的式子是</p>

  $$\\alpha_j = \\eta \\log \\frac{{1 - e_j}}{{e_j}}, \\qquad
    w_{{j+1}}(i) = \\begin{{cases}}
      w_j(i) \\cdot e^{{-\\alpha_j}} & \\text{{答對}} \\\\
      w_j(i) \\cdot e^{{+\\alpha_j}} & \\text{{答錯}}
    \\end{{cases}}$$

  <p>$e_j$ 是第 $j$ 個分類器的<strong>加權</strong>錯誤率，$\\alpha_j$ 同時是它在最終投票裡的份量：
  錯誤率愈低、$\\alpha$ 愈大、票愈重。最終預測是 $\\hat y = \\arg\\max_k \\sum_{{j:\\, h_j(x) = k}} \\alpha_j$。
  下面的元件取 $\\eta = \\tfrac{{1}}{{2}}$，那正是 Freund–Schapire 原版的 AdaBoost；
  $\\eta = 1$（<code>scikit-learn</code> 的 SAMME）重新加權更兇，在小樣本上容易讓權重
  幾輪就集中到少數幾點上。</p>

{viz(svg("w09adaSvg", 320),
     [rows_card("這一輪",
                [("第幾輪 j", "0 / 10", "w09adaRound"),
                 ("這一輪的切點", "—", "w09adaThr"),
                 ("加權錯誤率 e", "—", "w09adaErr"),
                 ("這一輪的權重 α", "—", "w09adaAlpha"),
                 ("集成的訓練錯誤率", "—", "w09adaEns")]),
      info_card("怎麼看",
                '每個圈是一筆資料，<strong>圈的大小＝它現在的權重</strong>；'
                '上排是 A 類、下排是 B 類。灰色虛線是這一輪 stump 的切點，'
                '答錯的點畫成粗黑框。<strong>按單步幾次</strong>就會看到：'
                '答錯的圈一輪一輪變大，逼得後面的 stump 改切在別的地方。'),
      info_card("集成錯誤率為什麼會來回跳",
                '每一輪都在<strong>換一份加權後的資料</strong>，所以新加進來的 stump 是為了'
                '那份加權資料而選的，對「未加權的訓練錯誤率」不保證每一輪都更好。'
                '這個例子在第 6 輪第一次歸零、第 7 輪又跳回 1 個錯，之後穩定在 0——'
                '<strong>看趨勢，不要看單一輪。</strong>'),
      info_card("為什麼 boosting 的樹要很淺",
                '因為它<strong>降的是偏差不是變異</strong>。序列裡的每一棵只需要修掉一小塊誤差，'
                '所以 stump 就夠；樹長深了反而一步就把殘差配光，'
                '後面的樹只能開始配雜訊。<br>這跟 bagging 剛好互補——'
                'bagging 要深樹低偏差，boosting 要淺樹低變異。', "ISLP §8.2.3")],
     "w09adaStatus", "按「單步」跑一輪 AdaBoost：看答錯的點怎麼變大，切點怎麼被逼著移動。",
     '<button class="btn btn-play" onclick="w09adaStart()">▶ 開始</button>'
     '<button class="btn btn-step" onclick="w09adaPlayer &amp;&amp; w09adaPlayer.step()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w09adaReset()">重置</button>')}

  <h3 id="dx-gbr">講義完整實作：Boston 上的梯度提升</h3>
{card("講義 08 · GradientBoostingRegressor（5000 棵樹，λ = 0.001）",
      code(76, 80), lab_output(CH, 80), src=src("76、78、80、82"),
      note="測試 MSE <strong>14.4814</strong>，跟 bagging 的 14.63 差不多，比 RF 的 20.04 好。"
           "把 <code>learning_rate</code> 換成 0.2（儲存格 82）得到 14.5015——幾乎一樣。"
           "儲存格 78 用 <code>staged_predict()</code> 畫出訓練與測試誤差隨棵數變化的曲線，"
           "那是判斷「B 是不是太大」唯一可靠的辦法。")}

{qa("觀念釐清", [
    ("Q：Bagging 與 Boosting 的根本差別是什麼？",
     "<p>三句話：<strong>並行 vs 序列、降變異 vs 降偏差、深樹 vs 淺樹。</strong>"
     "而第三點是前兩點的必然結果。</p>"
     "<p><strong>Bagging 降變異。</strong>它平均一堆同分佈的估計，期望值不變（偏差不變）、"
     "變異被 $1/B$ 壓下去。既然偏差不會被改善，就必須讓每棵樹的偏差一開始就很低，"
     "所以樹要<strong>長很深、不剪枝</strong>。樹的高變異不是問題，那正是要被平均掉的東西。</p>"
     "<p><strong>Boosting 降偏差。</strong>它把「還沒解釋掉的部分」（殘差／被放大權重的難樣本）"
     "交給下一棵樹，是一個逐步把偏差咬掉的過程。每一步只需要修一小塊，"
     "所以每棵樹<strong>只要很淺</strong>（ISLP 說 $d = 1$ 常常就夠）。"
     "反過來，如果第一棵樹就長很深，它會把殘差一次配光——包括雜訊；"
     "後面 4999 棵就只剩雜訊可配，而每一棵都在增加整體的變異。</p>"
     "<p>由此還推得幾個實務差別：<strong>bagging／RF 的 B 不會過度配適</strong>"
     "（平均更多同分佈的東西只會更穩），所以 B 挑大一點就好；"
     "<strong>boosting 的 B 會過度配適</strong>，必須用 CV 或 early stopping 挑。"
     "而且 bagging 可以完全平行、boosting 天生序列（這正是 XGBoost 要花那麼多力氣"
     "在工程上加速的原因）。最後：bagging 有 bootstrap 所以有免費的 OOB 誤差，"
     "boosting 沒有 bootstrap，所以沒有 OOB。</p>"),
])}

{quiz("qBoost", "QUIZ · Boosting",
      "梯度提升的第 b 棵樹，配的目標（response）是什麼？",
      [(True, "目前模型的殘差 r，不是原始的 y",
        "對，這是演算法 8.2 步驟 (a)。所以每棵樹只負責「前面還沒解釋掉的部分」，整體是一路把偏差咬掉。"),
       (False, "原始的 y，但只用 bootstrap 抽出來的那份資料",
        "這是 <strong>bagging</strong>。boosting 完全不做 bootstrap，每棵樹都看全部資料——被改掉的是<strong>目標</strong>（或權重），不是資料。"),
       (False, "原始的 y，但只用前一棵樹預測錯的那些觀測值",
        "方向對了一半：AdaBoost 確實會<strong>加重</strong>答錯的樣本，但也沒有把答對的丟掉（它們的權重只是變小）。而梯度提升根本不動權重，它動的是目標值。")])}
"""

# ── P09 modern ────────────────────────────────────────────────────────
BODIES["modern"] = f"""
  <p class="skip-note">這一節是課堂沒細講的延伸（講義 p.52–61）：三個現代 GBDT 套件與該調的超參數。
  第一輪讀可以整節略過，回頭要用套件時再看。</p>

  <p>上一節的梯度提升在概念上已經完整了，剩下的全是<strong>工程</strong>與<strong>正則化</strong>。
  三個套件把這件事推到了工業級：</p>

{table(["", "全名／來源", "核心賣點", "在 lab 的實測"],
       [["<strong>XGBoost</strong>", "Extreme Gradient Boosting",
         "目標函數<strong>內建正則化</strong>（葉子數與葉值的 L1/L2 罰項）；"
         "用類似<strong>牛頓法</strong>的二階近似而非單純梯度；分位數草圖做近似分裂搜尋、"
         "稀疏感知、快取友善", "24.3 秒（儲存格 114）"],
        ["<strong>LightGBM</strong>", "Microsoft",
         "<strong>直方圖分箱</strong>（預設 255 箱）把排序的 $O(n \\log n)$ 降成 $O(n)$；"
         "GOSS 只對小梯度的樣本抽樣；<strong>leaf-wise</strong> 而非 level-wise 長樹；"
         "互斥特徵綁定（EFB）", "13.1 秒（儲存格 185）"],
        ["<strong>CatBoost</strong>", "Yandex",
         "<strong>對稱樹</strong>（同一層用同一個分裂條件，本身就是正則化，預測極快）；"
         "<strong>ordered boosting</strong> 用另一份子集算殘差以防過度配適；"
         "類別變數原生支援", "15.1 秒（儲存格 210）"],
        ["對照組", "<code>sklearn</code> 的 <code>GradientBoostingClassifier</code>",
         "純 Python 迴圈的參考實作", "<strong>624.8 秒</strong>（儲存格 113）"]])}

  <p style="font-size:.82rem;color:var(--muted);">同一份系外行星資料（3197 個特徵）、同樣 100 棵樹、
  <code>max_depth=2</code>。<strong>625 秒 vs 13 秒，差了快 50 倍</strong>，而正確率還略微更好
  （0.9874 → 0.9914）。資料一大，這種差距就是「跑得完」與「跑不完」的差別。</p>

{info("XGBoost 的正則化到底加了什麼", '''原本的梯度提升只最小化損失。
  XGBoost 的目標函數多了一項對每棵樹本身的懲罰：<br>
  $$\\text{Obj} = \\sum_i L(y_i, \\hat y_i) + \\sum_b \\Omega(f_b), \\qquad
    \\Omega(f) = \\gamma |T| + \\tfrac{1}{2}\\lambda \\sum_{m} w_m^2$$
  $|T|$ 是葉子數、$w_m$ 是葉子的輸出值。<strong>$\\gamma$ 就是「多開一個葉子要付的錢」</strong>——
  形式上跟本頁 PART 03 的成本複雜度剪枝一模一樣，只是這次直接寫進目標函數，
  分裂增益算出來小於 $\\gamma$ 就不切。這也是為什麼 XGBoost 常被稱為
  「a regularized version of gradient boosting」。''')}

  <p>該調哪些超參數？講義第 60–61 頁把三個套件的參數名對照起來，
  分成「求快」「求準」「防過度配適」三組：</p>

{table(["目的", "XGBoost", "LightGBM", "CatBoost"],
       [["<strong>求快</strong>（抽樣列／欄、少幾棵）",
         "<code>subsample</code> · <code>colsample_bytree</code> · <code>n_estimators</code>",
         "<code>bagging_fraction</code> · <code>feature_fraction</code> · <code>num_iterations</code>",
         "<code>subsample</code> · <code>rsm</code> · <code>iterations</code>"],
        ["<strong>控制過度配適／求準</strong>",
         "<code>learning_rate</code>（0.01–0.2）· <code>max_depth</code> · "
         "<code>min_child_weight</code> · <code>gamma</code>",
         "<code>learning_rate</code> · <code>max_depth</code> · <code>num_leaves</code> · "
         "<code>min_data_in_leaf</code>",
         "<code>learning_rate</code> · <code>depth</code> · <code>l2-leaf-reg</code>"],
        ["<strong>類別變數</strong>", "實驗性支援（建議自己先編碼）",
         "<code>categorical_feature</code>", "<code>cat_features</code> · <code>one_hot_max_size</code>"]])}

  <p>lab 在 <code>heart_disease.csv</code>（303 筆、13 個特徵，用 <code>!wget</code> 抓 Packt 的那份）
  上一個一個網格搜過去，基準是 0.79：</p>

{table(["調的參數", "搜尋範圍", "最佳值", "最佳 CV 正確率", "lab 儲存格"],
       [["（基準）", "全部預設", "—", "0.79", "124"],
        ["<code>learning_rate</code>", "0.01 – 0.5", "0.5", "0.79557", "130"],
        ["<code>max_depth</code>", "2, 3, 5, 6, 8", "<strong>3</strong>", "<strong>0.81197</strong>", "134"],
        ["<code>gamma</code>", "0 – 2", "0.1", "0.81197", "138"],
        ["<code>min_child_weight</code>", "1 – 5", "4", "0.81197", "142"],
        ["<code>subsample</code>", "0.5 – 1", "0.5", "<strong>0.81536</strong>", "145"],
        ["<code>colsample_bytree</code>", "0.5 – 1", "0.7", "0.80552", "149"],
        ["<code>n_estimators</code>", "100 – 800", "400", "0.79541", "153"]])}
  <p style="font-size:.82rem;color:var(--muted);">最大的一筆進步來自把 <code>max_depth</code>
  從預設的 6 降到 3（0.79 → 0.812）——<strong>「把模型調簡單一點」</strong>。
  <code>subsample</code> 降到 0.5 又多賺一點，同樣是在減少變異。
  而把樹加到 800 棵反而變差：這份資料只有 303 筆，B 大不會有幫助。</p>

  <h3 id="dx-xgb">講義完整實作：XGBoost ＋ StratifiedKFold 的基準分數</h3>
{card("講義 08 · XGBClassifier 在 heart_disease 上的 5 折基準",
      code(123, 124), lab_output(CH, 124), src=src("119、123、124"),
      note="兩個細節值得學。① <strong>用 <code>StratifiedKFold</code> 而不是 "
           "<code>KFold</code></strong>：分類問題要保住每折的類別比例。"
           "② <strong>把 <code>kfold</code> 物件存下來重複用</strong>："
           "後面所有 <code>GridSearchCV</code> 都吃同一組折，"
           "這樣「調參前 vs 調參後」的分數才可比。這正是第 5 章 PART 03 的規矩。")}

  <h3 id="dx-early">講義完整實作：early stopping</h3>
{card("講義 08 · early_stopping_rounds 取代「調 n_estimators」",
      code(162), lab_output(CH, 162), src=src("162、164"),
      note="<code>early_stopping_rounds</code> <strong>不是超參數，是策略</strong>："
           "設 <code>n_estimators=5000</code> 加上 <code>early_stopping_rounds=100</code>，"
           "連續 100 輪沒進步就停，等於讓演算法自己決定 B。"
           "這裡 10 輪就停了，測試正確率 84.21%。"
           "<strong>注意 <code>eval_set</code> 用的是測試集</strong>。"
           "這在教學程式碼裡很常見，但正式做法要另外切一份驗證集，"
           "否則 B 是照測試集挑的，報出來的 84.21% 就偏樂觀了。")}

{quiz("qModern", "QUIZ · XGBoost 與後繼者",
      "XGBoost 相對於課本演算法 8.2 的梯度提升，最主要的<strong>統計</strong>差別是什麼？（不算工程加速）",
      [(True, "目標函數裡多了對樹本身的正則化項（葉子數 γ|T| 與葉值的 L2 罰項）",
        "對。所以 XGBoost 常被說成 <em>a regularized version of gradient boosting</em>。它另外還用了二階（牛頓法式）近似，比單純用一階梯度更精準。"),
       (False, "它改用 bootstrap 抽樣，所以每棵樹只看部分資料",
        "把 boosting 跟 bagging 搞混了。<code>subsample &lt; 1</code> 確實可以隨機抽列（那叫 stochastic gradient boosting），但那是選項，不是 XGBoost 的核心差異，而且也不是有放回的 bootstrap。"),
       (False, "它把序列改成並行，B 棵樹可以同時長",
        "不對。boosting 的第 b 棵樹必須等第 b−1 棵算完殘差，這個相依性沒辦法拿掉。XGBoost 平行化的是<strong>單一次分裂搜尋</strong>（掃各個特徵的候選切點），不是樹與樹之間。")])}
"""

# ── P10 stacking ──────────────────────────────────────────────────────
BODIES["stacking"] = f"""
  <p class="skip-note">這一節是課堂沒細講的延伸（講義 p.66–79、ISLP §8.2.4）：變數重要度的讀法、
  stacking，以及貝氏版的加法樹 BART。第一輪讀可以整節略過。</p>

  <h4 id="dx-vi">變數重要度：把可解釋性買回來一點</h4>

  <p>單一棵樹最大的優點是可以畫出來給人看。集成之後這個優點就沒了。
  你不可能把 500 棵樹貼在牆上。<strong>變數重要度</strong>（variable importance）
  是把可解釋性買回來一點點的標準做法：</p>

  <ul>
    <li><strong>迴歸樹：</strong>把每個變數造成的 <strong>RSS 下降總量</strong>加起來，在 B 棵樹上平均。</li>
    <li><strong>分類樹：</strong>把每個變數造成的 <strong>Gini 下降總量</strong>加起來，在 B 棵樹上平均。</li>
  </ul>

  <p>ISLP 圖 8.9 就是 <code>Heart</code> 資料上的這張圖（相對於最大值標準化），
  最重要的三個是 <code>Thal</code>、<code>Ca</code>、<code>ChestPain</code>。
  下面用 lab 的 Boston 例子重畫（<code>Heart</code> 不在 <code>ISLP 0.4.0</code> 裡）：</p>

{viz(chart("w09vimpChart", "tall",
           "。此圖的重點：lstat 與 rm 兩個變數就吃掉近 70% 的不純度下降總量，"
           "其餘十個變數加起來還不到三分之一。"),
     [rows_card("排行",
                [("第一名", "—", "w09vimpTop1"), ("第二名", "—", "w09vimpTop2"),
                 ("前兩名合計佔比", "—", "w09vimpShare"),
                 ("這個模型的測試 MSE", "—", "w09vimpMse")]),
      info_card("兩種重要度差在哪",
                '<strong>不純度下降</strong>（impurity / Gini importance）：'
                '直接從訓練好的樹裡加總，<strong>零成本</strong>，但它是在<strong>訓練資料</strong>上算的，'
                '而且會系統性偏袒「取值很多的變數」（連續變數、高基數的類別變數）。<br>'
                '<strong>Permutation importance</strong>：把某一欄<strong>隨機打亂</strong>，'
                '看測試誤差變差多少。定義在<strong>測試資料</strong>上，'
                '直接對應「這個變數對預測的貢獻」，但要多跑很多次預測。', "ISLP 圖 8.9"),
      info_card("最大的陷阱：相關的變數會互相稀釋",
                '如果兩個變數幾乎一樣（例如身高（公分）與身高（英吋）），'
                '樹會隨機挑一個來切，兩個的重要度<strong>各自被砍半</strong>，'
                '看起來都「不太重要」。<strong>重要度低不等於沒用</strong>，'
                '只等於「在有其他變數陪著的情況下，這個變數沒有被用到」。')],
     "w09vimpStatus", "換一種重要度的定義，看排名會不會變。",
     '<label class="slider-label" style="margin-right:.4rem;">重要度</label>'
     '<select id="w09vimpSel" class="mono" onchange="w09vimpDraw()">'
     '<option value="impurity" selected>不純度下降（feature_importances_）</option>'
     '<option value="permutation">Permutation（測試集上打亂）</option>'
     '</select>')}

{info("變數重要度不是因果，也不是「拿掉它會怎樣」", '''三件常見的誤讀，每一件都會出事：<br>
  <strong>① 它不是因果效應。</strong>重要度高只表示「樹很愛用它來切」，
  跟「改變它會改變 y」是兩件事。<br>
  <strong>② 它不帶方向。</strong>線性迴歸的係數有正負，重要度永遠是正的。
  你不知道它是往上推還是往下壓（要方向請用 partial dependence 或 SHAP）。<br>
  <strong>③ 相關變數會互相稀釋。</strong>上面那張側欄卡講的就是這件事。
  所以「重要度排最後 → 可以刪掉」是危險的推論。''', "warm")}

  <h4 id="dx-stk2">Stacking：不用投票，訓練一個模型來合併</h4>

  <p>PART 06 的 voting 是用一個<strong>固定</strong>的規則（多數票、平均）去合併。
  <strong>Stacking</strong> 問了一個很自然的問題：<em>為什麼不訓練一個模型來做這件合併？</em></p>

  <p>做法的關鍵在<strong>怎麼造合併器的訓練資料</strong>。這裡有一個必須避開的洩漏：</p>

  <ol>
    <li>對集成裡的每個成員模型，用<strong>交叉驗證</strong>產生
    <strong>out-of-sample 的預測</strong>（每一筆的預測，都來自沒看過它的那個折）。</li>
    <li>把這些預測當成新的特徵，原始的 y 照抄，訓練一個<strong>合併器</strong>
    （blender／meta-learner，常用邏輯斯迴歸這種簡單模型）。</li>
    <li>預測時：成員各給一個預測，合併器把它們吃進去輸出最終答案。</li>
  </ol>

  <p>第 1 步為什麼一定要用 CV？因為如果拿成員模型在<strong>訓練資料上</strong>的預測去餵合併器，
  那些預測好得不真實（成員在訓練資料上本來就準），合併器會學到「完全相信最會過度配適的那個成員」。
  這就是第 5 章那個「所有用到 y 的步驟都要關在折裡面」的老規矩。</p>

  <h3 id="dx-stk">講義完整實作：StackingClassifier</h3>
{card("講義 08 · Stacking（KNN ＋ 決策樹 ＋ 樸素貝氏，合併器是邏輯斯迴歸）",
      code(240), lab_output(CH, 240), src=src("240"),
      note="0.81，跟同一組成員的 hard voting（0.82，儲存格 238）幾乎一樣。"
           "<strong>這很典型</strong>：成員只有三個、資料只有 200 筆訓練樣本時，"
           "合併器沒什麼可學的，複雜的做法不會贏過簡單的平均。"
           "stacking 真正發威是在成員很多、而且強弱差很多的時候"
           "（Kaggle 的解法動輒疊十幾個模型）。")}

  <h4 id="dx-bart2">BART：貝氏版的加法樹</h4>

  <p><strong>BART</strong>（Bayesian additive regression trees）站在 bagging 與 boosting 中間：</p>

  <ul>
    <li>像 bagging／RF：每棵樹都帶著<strong>隨機性</strong>建出來。</li>
    <li>像 boosting：每棵樹都在抓<strong>目前還沒被解釋掉</strong>的訊號（偏殘差）。</li>
    <li><strong>它的新意在「怎麼生新樹」</strong>：不是重新配一棵，而是拿上一輪那棵樹
    <strong>微調</strong>——① 加或剪一根分支、② 改某個葉子的預測值。整套流程是一個 MCMC。</li>
  </ul>

  <p>因為每一輪只是微調，BART <strong>沒辦法一次把資料配得太狠</strong>，
  這本身就是防過度配適的機制。要選三個數字：樹的棵數 $K$、迭代次數 $B$、
  丟掉的暖機輪數 $L$。講義的建議是 $K = 200$、$B = 1000$、$L = 100$，
  最終預測是暖機後的平均</p>

  $$\\hat f(x) = \\frac{{1}}{{B - L}} \\sum_{{b = L+1}}^{{B}} \\hat f^b(x)$$

  <p>BART 出名的地方是<strong>幾乎不用調參就能跑出好結果</strong>（out-of-box performance）。</p>

  <h3 id="dx-bart">講義完整實作：BART</h3>
{card("講義 08 · ISLP.bart 在 Boston 上", code(86, 88), lab_output(CH, 88),
      src=src("86、88"),
      note="測試 MSE <strong>22.15</strong>，跟 random forest 的 20.04 同一個量級。"
           "<strong>注意 <code>burnin=5, ndraw=15</code> 小得離譜</strong>。"
           "那是為了讓課堂上跑得完，正式用要拉到 $L = 100$、$B = 1000$。"
           "儲存格 90 的 <code>variable_inclusion_</code> 是 BART 版的變數重要度："
           "算每個變數在整組樹裡出現幾次，<code>lstat</code> 31.0、<code>rm</code> 29.8 最高，"
           "跟上面 random forest 的排名一致。")}

{quiz("qStack", "QUIZ · Stacking 與變數重要度",
      "訓練 stacking 的合併器時，成員模型的預測值一定要用<strong>交叉驗證</strong>產生。為什麼？",
      [(True, "否則成員在訓練資料上的預測好得不真實，合併器會學成「相信最會過度配適的那個成員」",
        "對。這就是第 5 章的老規矩：任何用到 y 的步驟都要關在折裡面。<code>StackingClassifier</code> 預設就幫你做了（<code>cv=5</code>）。"),
       (False, "因為 scikit-learn 的 StackingClassifier API 規定必須傳入 cv 參數",
        "因果講反了。API 這樣設計，是因為統計上必須這樣做；不是因為 API 規定，統計才變成這樣。"),
       (False, "因為合併器需要比成員模型更多的訓練資料，CV 可以把資料量放大",
        "不對。CV 不會增加資料量（每一筆還是只出現一次），它做的是讓每一筆的預測都來自<strong>沒看過它</strong>的模型。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 8.4 第 3 題",
      "課本第 3 題要你把 Gini 指數、錯誤率、交叉熵都畫成 $\\hat p_{{m1}}$ 的函數（兩類）。"
      "畫出來之後，哪一句話最能說明「為什麼分裂準則不用錯誤率」？",
      [(True, "錯誤率是兩段直線，Gini 與交叉熵是嚴格凹的曲線；只有凹的函數才保證「切一刀」的不純度下降量嚴格大於 0",
        "對。這正是本頁 PART 04 那個 800 筆例子的數學根源：對線性的錯誤率，兩個子節點的加權平均可能剛好等於父節點的值，下降量報 0；對嚴格凹的 Gini／交叉熵不會。"),
       (False, "三條曲線的最大值都在 p̂ = 0.5，所以錯誤率沒有辦法分辨純與不純",
        "前半句對（三者都在 0.5 最大、在 0 與 1 為 0），但後半句錯得離譜：錯誤率<strong>當然</strong>分辨得出純與不純（純的時候它是 0）。問題不是「分不出來」，是「對純度的變化不夠敏感」。"),
       (False, "交叉熵的最大值是 log 2 ≈ 0.693，跟另外兩個不同，所以三者不能一起比較",
        "尺度不同是真的（錯誤率上限 0.5、Gini 上限 0.5、交叉熵上限 ln 2），這也是很多人畫圖時把熵除以 2 的原因。但尺度不影響「該選哪一刀」——選的是<strong>下降量最大</strong>的那一刀，任何正的縮放都不改變排序。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 8.4 第 5 題",
      "十個 bootstrap 樣本各配一棵分類樹，對同一個 X 給出 $P(\\text{{紅}} \\mid X)$ 的十個估計："
      "0.1, 0.15, 0.2, 0.2, 0.55, 0.6, 0.6, 0.65, 0.7, 0.75。"
      "用<strong>多數投票</strong>與用<strong>平均機率</strong>，分別會判成哪一類？",
      [(True, "多數投票 → 紅；平均機率 → 綠",
        "對。超過 0.5 的有六個（0.55、0.6、0.6、0.65、0.7、0.75），六比四，多數投票判紅。但十個數字的平均是 4.50 / 10 = <strong>0.45</strong>，小於 0.5，所以平均機率判綠。<strong>同一組數字，兩種彙總法給出相反答案。</strong>"),
       (False, "兩種方法都判紅",
        "多數投票確實判紅，但平均沒有。把十個數加起來是 4.50，除以 10 得 0.45 < 0.5。原因是「紅方」那六票都只勉強過半（0.55–0.75），而「綠方」那四票非常堅決（0.1–0.2）。"),
       (False, "兩種方法都判綠，因為十個估計的中位數是 0.375",
        "中位數算錯了：排序後第 5、6 個是 0.55 與 0.6，中位數是 0.575。而且題目問的是多數投票與平均機率，不是中位數——多數投票的答案是紅。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 8.4 第 2 題",
      "課本第 2 題要你說明：用<strong>深度 1 的樹（stump）</strong>做 boosting，"
      "為什麼結果是一個加法模型 $f(X) = \\sum_{{j=1}}^{{p}} f_j(X_j)$？",
      [(True, "每個 stump 只切一個變數，所以它是「只含那一個變數的函數」；把所有 stump 依變數分組加總，就得到每個變數各一個函數的加法形式",
        "對。演算法 8.2 的輸出是 $\\hat f(x) = \\sum_b \\lambda \\hat f^b(x)$；每個 $\\hat f^b$ 只依賴一個 $X_j$，把用到同一個 $X_j$ 的那些項收在一起就是 $f_j(X_j)$。反過來說，<strong>d 就是交互作用深度</strong>：d 刀最多能牽涉 d 個變數。"),
       (False, "因為 stump 的葉子只有兩個，所以每個 stump 都是線性函數，線性函數相加還是線性",
        "兩處都錯。stump 是<strong>階梯</strong>函數（兩段常數），不是線性函數。而「加法模型」指的是「每個變數各有一個任意形狀的函數再相加」（第 7 章的 GAM），不是「線性」。"),
       (False, "因為 boosting 的收縮參數 λ 讓每棵樹的貢獻很小，小貢獻疊起來近似可加",
        "λ 跟可加性完全無關。就算 λ = 1，stump 的集成照樣是加法模型；反過來就算 λ 很小，d = 2 的樹集成也<strong>不是</strong>加法模型（它含兩變數的交互作用）。決定可加性的是 <strong>d</strong>。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 8.4 第 7 題",
      "課本第 7 題要你在 <code>Boston</code> 上掃過一整片 <code>max_features</code>（m）與 "
      "<code>n_estimators</code>（B）的組合，畫成圖 8.10 那樣。預期會看到什麼？",
      [(True, "每條曲線都隨 B 上升而下降、然後平掉；不同 m 的曲線收斂到不同高度，而在 Boston 上 m = p 那條最低",
        "對，本頁 PART 08 的元件就是這張圖。兩個重點：① <strong>B 大不會過度配適</strong>，只會收斂；② 在 Boston 上限制 m 沒有幫助（lab 儲存格 70 的 20.04 比 bagging 的 14.63 差）。m 是超參數，$\\sqrt{p}$ 只是預設值。"),
       (False, "曲線會先下降、到某個 B 之後又上升，所以要用 CV 挑最佳的 B",
        "那是 <strong>boosting</strong> 的形狀。random forest 是在平均一堆同分佈的樹，B 變大只會讓平均更穩。ISLP 的原話是 <em>random forests will not overfit if we increase B</em>。"),
       (False, "m 愈小曲線一定愈低，因為去相關永遠讓變異更小",
        "去相關確實會降低 ρ（本頁元件的側欄實測 0.82 → 0.68），但 m 變小同時讓<strong>每棵樹變差</strong>。變異數是 $\\rho\\sigma^2$ 的形式，兩個因子一降一升，不保證淨變小——Boston 就是反例。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>五種方法對照</h3>
{table(["方法", "樹怎麼來", "樹的深度", "主要降的是", "B 會過度配適嗎", "免費驗證集"],
       [["<strong>單一棵樹</strong>", "一棵，貪婪長 + 剪枝", "由 CV 選 α",
         "—（偏差與變異都要自己顧）", "—", "沒有（要 CV）"],
        ["<strong>Bagging</strong>", "B 個 bootstrap，<strong>並行</strong>",
         "很深、不剪枝", "<strong>變異</strong>", "不會（B 大只是浪費算力）",
         "<strong>有（OOB）</strong>"],
        ["<strong>Random Forest</strong>", "同上 ＋ 每刀只看 m 個變數",
         "很深、不剪枝", "<strong>變異</strong>（多壓了 ρ）", "不會",
         "<strong>有（OOB）</strong>"],
        ["<strong>Boosting</strong>", "配殘差／調權重，<strong>序列</strong>",
         "<strong>很淺</strong>（d 常常 = 1）", "<strong>偏差</strong>",
         "<strong>會</strong>（要用 CV 或 early stopping）", "沒有（沒 bootstrap）"],
        ["<strong>BART</strong>", "微調上一輪的樹，MCMC", "小樹",
         "兩者（貝氏平均）", "不會（B 是 MCMC 迭代數）", "沒有"]])}

  <h3>lab 在 Boston 上的實測數字（同一份 70/30 切分）</h3>
{table(["模型", "設定", "測試 MSE", "lab 儲存格"],
       [["剪枝後的單一棵樹", "<code>ccp_alpha</code> 由五折 CV 選", "<strong>28.07</strong>", "59"],
        ["Bagging", "<code>max_features=12</code>, B = 100", "<strong>14.63</strong>", "66"],
        ["Bagging", "<code>max_features=12</code>, B = 500", "14.61", "68"],
        ["Random Forest", "<code>max_features=6</code>, B = 100", "20.04", "70"],
        ["Gradient Boosting", "B = 5000, λ = 0.001, d = 3", "<strong>14.48</strong>", "80"],
        ["Gradient Boosting", "B = 5000, λ = 0.2, d = 3", "14.50", "82"],
        ["BART", "<code>burnin=5, ndraw=15</code>（刻意調小）", "22.15", "88"]])}
  <p style="font-size:.82rem;color:var(--muted);">兩個結論：①<strong>集成把單一棵樹的誤差砍了一半</strong>
  （28.07 → 14.5 左右）。②<strong>在這份資料上 bagging 與 boosting 打平，random forest 反而較差</strong>——
  m 不是愈小愈好，別把 $\\sqrt{{p}}$ 當定律。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["樹的模型形式", "$f(X) = \\sum_{m=1}^{M} c_m \\mathbf{1}(X \\in R_m)$", "式 8.9"],
        ["要最小化的 RSS", "$\\sum_{j=1}^{J} \\sum_{i \\in R_j} (y_i - \\hat y_{R_j})^2$", "式 8.1"],
        ["一刀的目標",
         "$\\sum_{i \\in R_1(j,s)} (y_i - \\hat y_{R_1})^2 + \\sum_{i \\in R_2(j,s)} (y_i - \\hat y_{R_2})^2$",
         "式 8.3，掃過所有 (j, s)"],
        ["成本複雜度剪枝",
         "$\\sum_{m=1}^{|T|} \\sum_{i \\in R_m} (y_i - \\hat y_{R_m})^2 + \\alpha|T|$",
         "式 8.4，形式同 lasso"],
        ["錯誤率", "$E = 1 - \\max_k \\hat p_{mk}$", "式 8.5，<strong>不</strong>當分裂準則"],
        ["Gini 指數", "$G = \\sum_{k} \\hat p_{mk}(1 - \\hat p_{mk})$", "式 8.6"],
        ["交叉熵", "$D = -\\sum_{k} \\hat p_{mk} \\log \\hat p_{mk}$", "式 8.7"],
        ["Bagging", "$\\hat f_{\\text{bag}}(x) = \\frac1B \\sum_{b} \\hat f^{*b}(x)$", "分類版改多數投票"],
        ["平均的變異",
         "$\\frac{1-\\rho}{B}\\sigma^2 + \\rho\\sigma^2$",
         "第二項不隨 B 消失 → random forest 要壓 ρ"],
        ["OOB 比例", "$(1 - 1/n)^n \\to e^{-1} \\approx 0.368$", "第 5 章的 0.632 反面"],
        ["Boosting 更新", "$\\hat f(x) \\leftarrow \\hat f(x) + \\lambda \\hat f^b(x)$", "式 8.10"],
        ["Boosting 殘差", "$r_i \\leftarrow r_i - \\lambda \\hat f^b(x_i)$", "式 8.11"],
        ["Boosting 輸出", "$\\hat f(x) = \\sum_{b=1}^{B} \\lambda \\hat f^b(x)$", "式 8.12，d = 1 時是加法模型"],
        ["AdaBoost 的權重",
         "$\\alpha_j = \\eta \\log\\frac{1-e_j}{e_j}$", "講義 p.44，$e_j$ 是加權錯誤率"]])}

  <h3>三個 GBDT 套件怎麼選（講義 p.62）</h3>
{table(["套件", "什麼時候選它"],
       [["<strong>XGBoost</strong>", "社群最大、生產環境的支援最完整。不確定就先用它"],
        ["<strong>LightGBM</strong>", "資料很大、同時要速度與準確率時的較好選擇"],
        ["<strong>CatBoost</strong>", "資料量小，或<strong>類別變數很重要</strong>的時候"]])}

{info("三個一定要記住的觀念", '''<strong>1. 樹的分裂用 Gini／交叉熵，不用錯誤率。</strong>
  因為錯誤率是折線、對純度的變化不敏感，會把「生出一個純葉子」的好刀報成「下降量 0」。<br>
  <strong>2. Bagging 降變異、Boosting 降偏差，所以 bagging 的樹要很深，boosting 的樹要很淺。</strong>
  平均不會改變偏差，序列修正不需要深樹。順帶：bagging 的 B 不會過度配適，boosting 的會。<br>
  <strong>3. Random Forest 的 m 在壓 $\\rho\\sigma^2$ 裡的 $\\rho$，代價是 $\\sigma^2$ 變大。</strong>
  變數多又彼此相關時這筆交易划算；變數少又不可替代時（例如 Boston）就不划算。
  $\\sqrt{p}$ 是預設值，不是定律。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
# 本頁元件（id 與全域一律 w09 前綴）
# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== tree_based_methods 本頁元件（id 與全域一律 w09 前綴）===== */

/* 手寫 SVG 的小工具：這一頁有好幾個雙面板元件，不走 HC.svg 的單一座標系 */
function w09mk(host, tag, attrs, text) {
  const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k of Object.keys(attrs || {})) {
    if (attrs[k] === null || attrs[k] === undefined) continue;
    n.setAttribute(k === 'cls' ? 'class' : k, String(attrs[k]));
  }
  if (text !== undefined) n.textContent = text;
  host.appendChild(n);
  return n;
}
/* viewBox 寬度一律 620，否則 SVG 被拉寬時字會等比放大 */
function w09frame(id, h) {
  const host = document.getElementById(id);
  if (!host) return null;
  host.setAttribute('viewBox', '0 0 620 ' + h);
  host.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  while (host.firstChild) host.removeChild(host.firstChild);
  return host;
}
/* 低（藍）→ 高（橘紅）的連續色標，樹的葉子與資料點共用 */
function w09heat(t) {
  const u = Math.max(0, Math.min(1, t));
  return 'hsl(' + Math.round(214 - 196 * u) + ',62%,' + Math.round(74 - 20 * u) + '%)';
}
const w09MONO = "font-family:'JetBrains Mono',monospace;";

/* ---------- P02 grow：樹的生長器（分裂搜尋在瀏覽器裡即時算） ---------- */
const w09growN = 96;
const w09growMaxSplit = 7;
const w09growData = (() => {
  const rand = HC.stat.lcg(80924), x1 = [], x2 = [], y = [];
  for (let i = 0; i < w09growN; i++) {
    const a = 0.3 + 9.4 * rand(), b = 0.3 + 9.4 * rand();
    const mu = a < 4 ? (b < 5 ? 4.2 : 6.6) : (b < 7 ? 12.4 : 8.6);
    x1.push(a); x2.push(b); y.push(mu + 1.0 * HC.stat.normal(rand));
  }
  return { x1, x2, y };
})();

function w09growStat(idx) {
  const y = w09growData.y;
  let s = 0;
  for (const i of idx) s += y[i];
  const m = s / idx.length;
  let r = 0;
  for (const i of idx) r += (y[i] - m) ** 2;
  return { mean: m, rss: r };
}
function w09growBest(idx) {
  if (idx.length < 12) return null;
  const D = w09growData, base = w09growStat(idx).rss;
  let best = null;
  for (let v = 0; v < 2; v++) {
    const col = v === 0 ? D.x1 : D.x2;
    const vals = idx.map(i => col[i]).sort((a, b) => a - b);
    for (let k = 4; k < vals.length - 5; k++) {
      if (vals[k] === vals[k + 1]) continue;
      const thr = (vals[k] + vals[k + 1]) / 2;
      const L = [], R = [];
      for (const i of idx) (col[i] < thr ? L : R).push(i);
      const gain = base - w09growStat(L).rss - w09growStat(R).rss;
      if (!best || gain > best.gain) best = { v, thr, gain, left: L, right: R };
    }
  }
  return best;
}
const w09growSteps = (() => {
  const all = Array.from({ length: w09growN }, (_, i) => i);
  const root = { id: 0, parent: -1, idx: all, lo1: 0, hi1: 10, lo2: 0, hi2: 10,
                 leaf: true, depth: 0 };
  const st0 = w09growStat(all);
  root.mean = st0.mean; root.rss = st0.rss;
  const nodes = [root];
  const snap = () => nodes.map(n => ({
    id: n.id, parent: n.parent, lo1: n.lo1, hi1: n.hi1, lo2: n.lo2, hi2: n.hi2,
    leaf: n.leaf, depth: n.depth, mean: n.mean, cnt: n.idx.length,
    v: n.v, thr: n.thr, L: n.L, R: n.R }));
  const tot = () => nodes.filter(n => n.leaf).reduce((s, n) => s + n.rss, 0);
  const out = [{ step: 0, nodes: snap(), split: null, rss: tot() }];
  for (let s = 1; s <= w09growMaxSplit; s++) {
    let pick = null;
    for (const n of nodes) {
      if (!n.leaf) continue;
      if (n.cand === undefined) n.cand = w09growBest(n.idx);
      if (n.cand && (!pick || n.cand.gain > pick.b.gain)) pick = { n: n, b: n.cand };
    }
    if (!pick) break;
    const n = pick.n, b = pick.b;
    n.leaf = false; n.v = b.v; n.thr = b.thr;
    const mk = (idx, lo1, hi1, lo2, hi2) => {
      const st = w09growStat(idx);
      nodes.push({ id: nodes.length, parent: n.id, idx: idx, lo1: lo1, hi1: hi1,
                   lo2: lo2, hi2: hi2, leaf: true, depth: n.depth + 1,
                   mean: st.mean, rss: st.rss });
      return nodes.length - 1;
    };
    if (b.v === 0) {
      n.L = mk(b.left, n.lo1, b.thr, n.lo2, n.hi2);
      n.R = mk(b.right, b.thr, n.hi1, n.lo2, n.hi2);
    } else {
      n.L = mk(b.left, n.lo1, n.hi1, n.lo2, b.thr);
      n.R = mk(b.right, n.lo1, n.hi1, b.thr, n.hi2);
    }
    out.push({ step: s, nodes: snap(), rss: tot(),
               split: { v: b.v, thr: b.thr, gain: b.gain, cnt: n.idx.length } });
  }
  return out;
})();
let w09growPlayer = null;

function w09growApply(f) {
  const host = w09frame('w09growSvg', 380);
  if (!host) return;
  const D = w09growData;
  const by = {};
  f.nodes.forEach(n => { by[n.id] = n; });
  const order = [];
  (function walk(id) {
    const n = by[id];
    if (!n) return;
    if (n.leaf) { order.push(id); return; }
    walk(n.L); walk(n.R);
  })(0);
  const rank = {};
  order.forEach((id, i) => { rank[id] = i; });

  const ys = D.y, ylo = Math.min.apply(null, ys), yhi = Math.max.apply(null, ys);
  const heat = v => w09heat((v - ylo) / (yhi - ylo));

  /* ── 左：特徵空間 ── */
  const P = { x: 46, y: 44, w: 234, h: 234 };
  const px = v => P.x + v / 10 * P.w;
  const py = v => P.y + P.h - v / 10 * P.h;
  w09mk(host, 'text', { x: P.x, y: 24, cls: 'axtitle' }, '特徵空間：每塊填該塊的 y 平均');
  order.forEach(id => {
    const n = by[id];
    w09mk(host, 'rect', { x: px(n.lo1), y: py(n.hi2),
                          width: px(n.hi1) - px(n.lo1), height: py(n.lo2) - py(n.hi2),
                          fill: heat(n.mean), opacity: 0.5, stroke: '#fff', 'stroke-width': 1.5 });
    if (px(n.hi1) - px(n.lo1) > 26 && py(n.lo2) - py(n.hi2) > 20) {
      w09mk(host, 'text', { x: (px(n.lo1) + px(n.hi1)) / 2, y: (py(n.lo2) + py(n.hi2)) / 2 + 4,
                            'text-anchor': 'middle', fill: 'var(--ink)',
                            style: w09MONO + 'font-size:10px;font-weight:700' },
            'R' + (rank[id] + 1));
    }
  });
  for (let i = 0; i < w09growN; i++) {
    w09mk(host, 'circle', { cx: px(D.x1[i]), cy: py(D.x2[i]), r: 3.4, fill: heat(ys[i]),
                            stroke: '#fff', 'stroke-width': 0.9 });
  }
  w09mk(host, 'rect', { x: P.x, y: P.y, width: P.w, height: P.h, fill: 'none',
                        stroke: 'var(--muted)', 'stroke-width': 1 });
  w09mk(host, 'text', { x: P.x + P.w / 2, y: P.y + P.h + 20, 'text-anchor': 'middle',
                        cls: 'axtitle' }, 'x1');
  w09mk(host, 'text', { x: 0, y: 0, cls: 'axtitle', 'text-anchor': 'middle',
                        transform: 'translate(16,' + (P.y + P.h / 2) + ') rotate(-90)' }, 'x2');
  if (f.split) {
    const n = f.nodes.filter(q => !q.leaf && q.v === f.split.v
                                  && Math.abs(q.thr - f.split.thr) < 1e-9).pop();
    if (n) {
      const a = f.split.v === 0
        ? [px(n.thr), py(n.lo2), px(n.thr), py(n.hi2)]
        : [px(n.lo1), py(n.thr), px(n.hi1), py(n.thr)];
      w09mk(host, 'line', { x1: a[0], y1: a[1], x2: a[2], y2: a[3],
                            stroke: 'var(--accent)', 'stroke-width': 3.2 });
    }
  }

  /* ── 右：樹 ── */
  const T = { x: 306, w: 300, y: 46 };
  const maxD = Math.max.apply(null, f.nodes.map(n => n.depth));
  const dy = maxD > 0 ? Math.min(52, 262 / maxD) : 52;
  const xp = {};
  (function place(id) {
    const n = by[id];
    if (n.leaf) { xp[id] = T.x + (rank[id] + 0.5) / order.length * T.w; return; }
    place(n.L); place(n.R);
    xp[id] = (xp[n.L] + xp[n.R]) / 2;
  })(0);
  w09mk(host, 'text', { x: T.x, y: 24, cls: 'axtitle' }, '同一刀一刀長出來的樹');
  f.nodes.forEach(n => {
    if (n.leaf) return;
    [n.L, n.R].forEach(c => {
      w09mk(host, 'line', { x1: xp[n.id], y1: T.y + n.depth * dy + 9,
                            x2: xp[c], y2: T.y + by[c].depth * dy - 9,
                            stroke: 'var(--card-border)', 'stroke-width': 1.6 });
    });
  });
  f.nodes.forEach(n => {
    const cx = xp[n.id], cy = T.y + n.depth * dy;
    if (n.leaf) {
      w09mk(host, 'rect', { x: cx - 18, y: cy - 9, width: 36, height: 18, rx: 4,
                            fill: heat(n.mean), stroke: '#fff', 'stroke-width': 1.2 });
      w09mk(host, 'text', { x: cx, y: cy + 4, 'text-anchor': 'middle', fill: '#fff',
                            style: w09MONO + 'font-size:9.5px;font-weight:700' },
            HC.fmt(n.mean, 1));
      w09mk(host, 'text', { x: cx, y: cy + 20, 'text-anchor': 'middle', fill: 'var(--muted)',
                            style: w09MONO + 'font-size:8.5px' },
            'R' + (rank[n.id] + 1) + ' n=' + n.cnt);
    } else {
      const lab = 'x' + (n.v + 1) + ' < ' + HC.fmt(n.thr, 1);
      w09mk(host, 'rect', { x: cx - 30, y: cy - 9, width: 60, height: 18, rx: 4,
                            fill: 'var(--card)', stroke: 'var(--accent2)', 'stroke-width': 1.3 });
      w09mk(host, 'text', { x: cx, y: cy + 4, 'text-anchor': 'middle', fill: 'var(--accent2)',
                            style: w09MONO + 'font-size:9.5px;font-weight:700' }, lab);
    }
  });

  /* ── 側欄與旁白 ── */
  const nLeaf = order.length;
  document.getElementById('w09growLeaves').textContent = String(nLeaf);
  document.getElementById('w09growRss').textContent = HC.fmt(f.rss, 1);
  if (!f.split) {
    document.getElementById('w09growVar').textContent = '—';
    document.getElementById('w09growThr').textContent = '—';
    document.getElementById('w09growGain').textContent = '—';
    hlLine('w09growCode', 1);
    setStatus('w09growStatus', '還沒切任何一刀：整個特徵空間是一塊，'
      + '預測值就是全部 96 筆的平均 ' + HC.fmt(f.nodes[0].mean, 2)
      + '，訓練 RSS = ' + HC.fmt(f.rss, 1) + '。按「單步」切第一刀。');
    return;
  }
  const vn = 'x' + (f.split.v + 1);
  document.getElementById('w09growVar').textContent = vn;
  document.getElementById('w09growThr').textContent = HC.fmt(f.split.thr, 2);
  document.getElementById('w09growGain').textContent = HC.fmt(f.split.gain, 1);
  hlLine('w09growCode', 5);
  setStatus('w09growStatus', '第 ' + f.step + ' 刀：在 ' + vn + ' = '
    + HC.fmt(f.split.thr, 2) + ' 切開一塊有 ' + f.split.cnt + ' 筆的區域（左圖橘線），'
    + 'RSS 掉了 <strong>' + HC.fmt(f.split.gain, 1) + '</strong>，'
    + '剩下 ' + HC.fmt(f.rss, 1) + '。現在有 ' + nLeaf + ' 個葉子。');
}
function w09growStart() {
  w09growPlayer = new Player({ frames: w09growSteps, apply: w09growApply, delayInput: null });
  w09growPlayer.reset();
  w09growPlayer.play();
}
function w09growReset() {
  if (w09growPlayer) w09growPlayer.stop();
  w09growPlayer = new Player({ frames: w09growSteps, apply: w09growApply });
  w09growPlayer.reset();
}
"""

PAGEJS += r"""

/* 參考線一律用共用的 HC.refs()：Chart.js 4 的 Config.prototype.plugins 只有 getter，
   建構之後寫 c.config.plugins = [...] 是靜默失效的（不報錯、線也畫不出來）。
   HC.refs 把 markers 掛在 chart 實例上，由 shared.js 註冊的全域 plugin 繪製。
   HC.vline / HC.hline 的第 4 個參數 row 可以把靠得近的標籤錯開一列。 */

/* ---------- P03 prune：α 滑桿（烘焙 Hitters 的剪枝路徑） ---------- */
let w09pruneIdx = 3;
function w09pruneSet() {
  const el = document.getElementById('w09pruneAlpha');
  if (el) w09pruneIdx = parseInt(el.value, 10);
  w09pruneDraw();
}
function w09pruneJumpCv() {
  const F = FRAMES_w09prune, j = F.leaves.indexOf(F.cvBest);
  w09pruneIdx = j < 0 ? 0 : j;
  const el = document.getElementById('w09pruneAlpha');
  if (el) el.value = String(w09pruneIdx);
  w09pruneDraw();
}
function w09pruneDraw() {
  const F = FRAMES_w09prune;
  const i = Math.max(0, Math.min(w09pruneIdx, F.leaves.length - 1));
  const w09pruneRefs = [HC.vline(i, '目前的 α'),
    HC.vline(F.leaves.indexOf(F.cvBest), 'CV 選這裡', HC.tok.accent3, 1)];
  HC.line('w09pruneChart', {
    labels: F.leaves,
    datasets: [
      { label: '訓練 MSE', data: F.train, borderColor: HC.tok.ink,
        backgroundColor: HC.tok.ink, borderWidth: 2, pointRadius: 2.5, fill: false },
      { label: 'CV MSE（六折）', data: F.cv, borderColor: HC.tok.accent3,
        backgroundColor: HC.tok.accent3, borderWidth: 2.8, pointRadius: 3.5, fill: false },
      { label: '測試 MSE', data: F.test, borderColor: HC.tok.accent,
        backgroundColor: HC.tok.accent, borderWidth: 2.4, pointRadius: 3,
        borderDash: [6, 4], fill: false },
    ],
  }, {
    scales: { x: { title: { display: true, text: '剪完之後的葉子數 |T|（α 由右往左遞增）' } },
              y: { title: { display: true, text: 'log 薪水的 MSE' } } },
  });
  HC.refs('w09pruneChart', w09pruneRefs);
  const sv = document.getElementById('w09pruneAlphaVal');
  if (sv) sv.textContent = HC.fmt(F.alpha[i], 3);
  document.getElementById('w09pruneA').textContent = HC.fmt(F.alpha[i], 4);
  document.getElementById('w09pruneL').textContent = String(F.leaves[i]);
  document.getElementById('w09pruneTr').textContent = HC.fmt(F.train[i], 3);
  document.getElementById('w09pruneCv').textContent = HC.fmt(F.cv[i], 3);
  document.getElementById('w09pruneTe').textContent = HC.fmt(F.test[i], 3);
  document.getElementById('w09pruneBest').textContent = String(F.cvBest);
  setStatus('w09pruneStatus', 'α = ' + HC.fmt(F.alpha[i], 4) + ' 剪出 '
    + F.leaves[i] + ' 個葉子：訓練 MSE ' + HC.fmt(F.train[i], 3)
    + '、CV ' + HC.fmt(F.cv[i], 3) + '、測試 ' + HC.fmt(F.test[i], 3)
    + '。訓練那條一路往下，CV 在 ' + F.cvBest + ' 個葉子最低——'
    + '只有 CV 那條可以拿來選。');
}

/* ---------- P04 imp：Gini／交叉熵／錯誤率（閉式解，完全即時） ---------- */
let w09impPv = 0.5, w09impScale = false, w09impSvc = null;
function w09impErrF(p) { return Math.min(p, 1 - p); }
function w09impGiniF(p) { return 2 * p * (1 - p); }
function w09impEntF(p) {
  if (p <= 0 || p >= 1) return 0;
  return -(p * Math.log(p) + (1 - p) * Math.log(1 - p));
}
function w09impEntShow(p) {
  return w09impScale ? w09impEntF(p) / (2 * Math.LN2) : w09impEntF(p);
}
function w09impSetup() {
  w09impSvc = HC.svg('w09impSvg', { xd: [0, 1], yd: [0, 0.75], h: 330 });
}
function w09impToggle() { w09impScale = !w09impScale; w09impDraw(); }
function w09impSet() {
  const el = document.getElementById('w09impSl');
  if (el) w09impPv = parseInt(el.value, 10) / 100;
  w09impDraw();
}
function w09impDraw() {
  const s = w09impSvc;
  if (!s) return;
  s.grid(5, 5, { xtitle: 'p̂ ── 第一類在這個節點裡的比例', ytitle: '不純度',
                 xdec: 1, ydec: 2 });
  const g = s.clearLayer('curves');
  const ps = HC.stat.seq(0.0005, 0.9995, 201);
  const draw = (fn, colr, w, dash) =>
    s.poly(ps.map(p => [p, fn(p)]), { stroke: colr, sw: w, dash: dash, cls: 'w09impc' }, g);
  draw(w09impErrF, HC.tok.muted, 2.6, '7 4');
  draw(w09impGiniF, HC.tok.accent2, 2.8, null);
  draw(w09impEntShow, HC.tok.accent, 2.8, null);
  const lg = [['錯誤率 E', HC.tok.muted], ['Gini 指數 G', HC.tok.accent2],
              [w09impScale ? '交叉熵 D（已縮放）' : '交叉熵 D', HC.tok.accent]];
  lg.forEach((it, k) => {
    s.add('line', { x1: 380, y1: 26 + k * 15, x2: 402, y2: 26 + k * 15,
                    stroke: it[1], 'stroke-width': 2.8 }, g);
    s.txtPx(408, 30 + k * 15, it[0], { fill: it[1] }, g);
  });
  const p = w09impPv;
  s.seg(p, 0, p, 0.75, { stroke: HC.tok.accent, sw: 1.4, dash: '4 3', cls: 'w09impc' }, g);
  [[w09impErrF(p), HC.tok.muted], [w09impGiniF(p), HC.tok.accent2],
   [w09impEntShow(p), HC.tok.accent]].forEach(it => {
    s.dot(p, it[0], { r: 5, fill: it[1], stroke: '#fff', sw: 1.4 }, g);
  });
  const sv = document.getElementById('w09impSlVal');
  if (sv) sv.textContent = HC.fmt(p, 2);
  document.getElementById('w09impP').textContent = HC.fmt(p, 2);
  document.getElementById('w09impErr').textContent = HC.fmt(w09impErrF(p), 4);
  document.getElementById('w09impGini').textContent = HC.fmt(w09impGiniF(p), 4);
  document.getElementById('w09impEnt').textContent = HC.fmt(w09impEntShow(p), 4)
    + (w09impScale ? '（縮放後）' : '');
  setStatus('w09impStatus', 'p̂ = ' + HC.fmt(p, 2) + ' 時：錯誤率 '
    + HC.fmt(w09impErrF(p), 3) + '、Gini ' + HC.fmt(w09impGiniF(p), 3)
    + '、交叉熵 ' + HC.fmt(w09impEntShow(p), 3)
    + '。把 p̂ 從 0.5 拖到 0.4，再從 0.2 拖到 0.1，比較兩次錯誤率各掉多少'
    + '——會發現一樣多。Gini 與交叉熵不是這樣。');
}

/* ---------- P06 vote：多數投票與大數法則 ---------- */
const w09voteLF = (() => {
  const a = [0];
  for (let k = 1; k <= 1201; k++) a.push(a[k - 1] + Math.log(k));
  return a;
})();
function w09voteMaj(p, M) {
  if (p <= 0) return 0;
  if (p >= 1) return 1;
  const lp = Math.log(p), lq = Math.log(1 - p);
  let s = 0;
  for (let k = Math.floor(M / 2) + 1; k <= M; k++) {
    s += Math.exp(w09voteLF[M] - w09voteLF[k] - w09voteLF[M - k] + k * lp + (M - k) * lq);
  }
  return Math.max(0, Math.min(1, s));
}
const w09voteMs = (() => {
  const a = [];
  for (let m = 1; m <= 101; m += 2) a.push(m);
  for (let m = 111; m <= 301; m += 10) a.push(m);
  return a;
})();
let w09voteP = 0.55, w09voteM = 15;
function w09voteSet() {
  const ep = document.getElementById('w09voteSlP'), em = document.getElementById('w09voteSlM');
  if (ep) w09voteP = parseInt(ep.value, 10) / 100;
  if (em) w09voteM = parseInt(em.value, 10);
  w09voteRender();
  w09voteChartDraw();
}
function w09voteRender() {
  const host = w09frame('w09voteSvg', 250);
  if (!host) return;
  const p = w09voteP, M = w09voteM;
  const rand = HC.stat.lcg(90831);
  let right = 0;
  const flags = [];
  for (let i = 0; i < M; i++) { const ok = rand() < p; flags.push(ok); if (ok) right++; }
  const per = 25, cell = 16, gap = 4, x0 = 46;
  w09mk(host, 'text', { x: x0, y: 22, cls: 'axtitle' },
        M + ' 個分類器在同一筆資料上：綠＝答對、紅＝答錯（固定種子的模擬）');
  flags.forEach((ok, i) => {
    const r = Math.floor(i / per), c = i % per;
    w09mk(host, 'rect', { x: x0 + c * (cell + gap), y: 34 + r * (cell + gap),
                          width: cell, height: cell, rx: 3,
                          fill: ok ? 'var(--accent3)' : 'var(--accent)', opacity: 0.88 });
  });
  const rows = Math.ceil(M / per);
  const yb = 34 + rows * (cell + gap) + 16;
  const win = right * 2 > M;
  w09mk(host, 'text', { x: x0, y: yb, fill: 'var(--ink)',
                        style: w09MONO + 'font-size:11.5px;font-weight:700' },
        '答對 ' + right + ' / ' + M + ' → 多數投票這一次'
        + (win ? '答對 ✓' : '答錯 ✗'));
  const bw = 400;
  w09mk(host, 'rect', { x: x0, y: yb + 10, width: bw, height: 12, rx: 6,
                        fill: 'var(--card-border)' });
  w09mk(host, 'rect', { x: x0, y: yb + 10, width: bw * right / M, height: 12, rx: 6,
                        fill: win ? 'var(--accent3)' : 'var(--accent)' });
  w09mk(host, 'line', { x1: x0 + bw / 2, y1: yb + 6, x2: x0 + bw / 2, y2: yb + 26,
                        stroke: 'var(--ink)', 'stroke-width': 2 });
  w09mk(host, 'text', { x: x0 + bw / 2 + 6, y: yb + 34, fill: 'var(--muted)',
                        style: w09MONO + 'font-size:9.5px' }, '過半的門檻');
  const acc = w09voteMaj(p, M);
  document.getElementById('w09voteP').textContent = HC.fmt(p, 2);
  document.getElementById('w09voteM').textContent = String(M);
  document.getElementById('w09voteAcc').textContent = HC.pct(acc, 2);
  document.getElementById('w09voteGain').textContent =
    (acc >= p ? '+' : '') + HC.fmt((acc - p) * 100, 2) + ' 百分點';
  document.getElementById('w09voteDeck').textContent = HC.pct(w09voteMaj(0.51, 1000), 1);
  document.getElementById('w09voteBad').textContent = HC.pct(w09voteMaj(0.49, 1000), 1);
  setStatus('w09voteStatus', 'p = ' + HC.fmt(p, 2) + '、M = ' + M
    + ' 時，多數投票的正確率是 <strong>' + HC.pct(acc, 2) + '</strong>'
    + (p > 0.5 ? '，比單一個分類器高 ' + HC.fmt((acc - p) * 100, 2) + ' 個百分點。'
               : '，比單一個分類器<strong>還低</strong>——p ≤ 0.5 時投票愈投愈糟。'));
}
function w09voteChartDraw() {
  const mk = pp => w09voteMs.map(m => w09voteMaj(pp, m));
  HC.line('w09voteChart', {
    labels: w09voteMs,
    datasets: [
      { label: '目前的 p = ' + HC.fmt(w09voteP, 2), data: mk(w09voteP),
        borderColor: HC.tok.accent, borderWidth: 3, pointRadius: 0, fill: false },
      { label: 'p = 0.55', data: mk(0.55), borderColor: HC.tok.accent3,
        borderWidth: 1.8, pointRadius: 0, borderDash: [6, 4], fill: false },
      { label: 'p = 0.45', data: mk(0.45), borderColor: HC.tok.muted,
        borderWidth: 1.8, pointRadius: 0, borderDash: [3, 3], fill: false },
    ],
  }, {
    scales: { x: { title: { display: true, text: '分類器個數 M' } },
              y: { min: 0, max: 1, title: { display: true, text: '多數投票的正確率' } } },
  });
  HC.refs('w09voteChart', HC.hline(0.5, '瞎猜的水準 0.5'));
}
"""

PAGEJS += r"""

/* ---------- P07 bag：bootstrap 與 OOB ---------- */
const w09bagN = 20;
let w09bagB = 0, w09bagOobSum = 0, w09bagSeed = 0;
function w09bagDraw(counts) {
  const host = w09frame('w09bagSvg', 220);
  if (!host) return;
  const cell = 26, gap = 6, per = 10, x0 = (620 - (per * cell + (per - 1) * gap)) / 2;
  w09mk(host, 'text', { x: x0, y: 22, cls: 'axtitle' },
        '20 筆訓練資料 · 實心＝這棵樹抽到（×k 是抽到幾次）· 虛線框＝袋外（OOB）');
  for (let i = 0; i < w09bagN; i++) {
    const r = Math.floor(i / per), c = i % per;
    const x = x0 + c * (cell + gap), y = 36 + r * (cell + gap + 10);
    const k = counts ? counts[i] : -1;
    const oob = k === 0;
    w09mk(host, 'rect', { x: x, y: y, width: cell, height: cell, rx: 6,
                          fill: k < 0 ? 'var(--card)' : (oob ? 'none' : 'var(--accent3)'),
                          stroke: oob ? 'var(--accent)' : 'var(--card-border)',
                          'stroke-width': oob ? 2.4 : 1,
                          'stroke-dasharray': oob ? '4 3' : null });
    w09mk(host, 'text', { x: x + cell / 2, y: y + cell / 2 + 4, 'text-anchor': 'middle',
                          fill: (k > 0) ? '#fff' : 'var(--ink)',
                          style: w09MONO + 'font-size:10.5px;font-weight:700' }, String(i + 1));
    if (k > 1) {
      w09mk(host, 'text', { x: x + cell / 2, y: y - 3, 'text-anchor': 'middle',
                            fill: 'var(--accent)',
                            style: w09MONO + 'font-size:9.5px;font-weight:700' }, '×' + k);
    }
  }
  const yb = 36 + 2 * (cell + gap + 10) + 14;
  if (counts) {
    const nOob = counts.filter(k => k === 0).length;
    w09mk(host, 'text', { x: x0, y: yb, fill: 'var(--ink)',
                          style: w09MONO + 'font-size:11px;font-weight:600' },
          '這棵樹：用到 ' + (w09bagN - nOob) + ' 筆、袋外 ' + nOob + ' 筆（'
          + HC.pct(nOob / w09bagN, 0) + '）');
    w09mk(host, 'text', { x: x0, y: yb + 18, fill: 'var(--muted)',
                          style: w09MONO + 'font-size:10.5px' },
          '累計 ' + w09bagB + ' 棵樹的平均 OOB 比例 = '
          + HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) + '  ·  理論值 36.79%');
  } else {
    w09mk(host, 'text', { x: x0, y: yb, fill: 'var(--muted)',
                          style: w09MONO + 'font-size:11px' },
          '按「長一棵樹」開始有放回重抽');
  }
}
function w09bagSample() {
  w09bagSeed += 1;
  const rand = HC.stat.lcg(20260811 + w09bagSeed * 6151);
  const counts = new Array(w09bagN).fill(0);
  for (let i = 0; i < w09bagN; i++) counts[Math.floor(rand() * w09bagN)] += 1;
  return counts;
}
function w09bagUpdate(counts) {
  const nOob = counts.filter(k => k === 0).length;
  document.getElementById('w09bagIn').textContent = (w09bagN - nOob) + ' / 20';
  document.getElementById('w09bagOob').textContent = nOob + ' / 20';
  document.getElementById('w09bagPct').textContent = HC.pct(nOob / w09bagN, 1);
  document.getElementById('w09bagB').textContent = String(w09bagB);
  document.getElementById('w09bagAvg').textContent =
    w09bagB ? HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) : '—';
  setStatus('w09bagStatus', '第 ' + w09bagB + ' 棵樹：' + nOob
    + ' 筆完全沒被抽到（虛線框），它們就是這棵樹的免費驗證集。累計平均 OOB 比例 = '
    + HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) + '，理論值 1/e ≈ 36.79%。');
}
function w09bagOne() {
  const c = w09bagSample();
  w09bagB += 1;
  w09bagOobSum += c.filter(k => k === 0).length;
  w09bagDraw(c);
  w09bagUpdate(c);
}
function w09bagMany() {
  let last = null;
  for (let t = 0; t < 200; t++) {
    last = w09bagSample();
    w09bagB += 1;
    w09bagOobSum += last.filter(k => k === 0).length;
  }
  w09bagDraw(last);
  w09bagUpdate(last);
}
function w09bagReset() {
  w09bagB = 0; w09bagOobSum = 0; w09bagSeed = 0;
  w09bagDraw(null);
  ['w09bagIn', 'w09bagOob', 'w09bagPct', 'w09bagAvg'].forEach(i => {
    const e = document.getElementById(i);
    if (e) e.textContent = '—';
  });
  const b = document.getElementById('w09bagB');
  if (b) b.textContent = '0';
  setStatus('w09bagStatus', '按「長一棵樹」看一次有放回重抽：虛線框的球就是這棵樹的袋外樣本。');
}

/* ---------- P08 rf：m 的效果（烘焙） ---------- */
function w09rfDraw() {
  const F = FRAMES_w09rf;
  const el = document.getElementById('w09rfSel');
  const key = el ? el.value : 'boston';
  const S = F[key];
  const cols = [HC.tok.ink, HC.tok.accent2, HC.tok.accent3, HC.tok.accent];
  HC.line('w09rfChart', {
    labels: F.B,
    datasets: S.ms.map((m, j) => ({
      label: 'm = ' + m + (m === S.p ? '（bagging）' : ''),
      data: S.curves[j], borderColor: cols[j], backgroundColor: cols[j],
      borderWidth: j === 0 ? 3 : 2.2, pointRadius: 0, fill: false,
      borderDash: j === 0 ? [] : [7 - j, 3],
    })),
  }, {
    scales: { x: { title: { display: true, text: '樹的棵數 B（取前 B 棵的平均預測）' } },
              y: { title: { display: true, text: '測試 MSE' } } },
  });
  HC.refs('w09rfChart', HC.hline(S.singleTree, '單一棵樹 ' + HC.fmt(S.singleTree, 2)));
  const last = F.B.length - 1;
  const best = S.curves.reduce((bi, cur, j) =>
    cur[last] < S.curves[bi][last] ? j : bi, 0);
  for (let j = 0; j < 4; j++) {
    const e = document.getElementById('w09rfR' + j);
    if (!e) continue;
    e.textContent = (j === best ? '★ ' : '') + 'MSE ' + HC.fmt(S.curves[j][last], 2)
      + ' · ρ ' + HC.fmt(S.rho[j], 3);
  }
  document.getElementById('w09rfSingle').textContent = HC.fmt(S.singleTree, 2);
  setStatus('w09rfStatus', (key === 'boston'
    ? 'Boston（p = 12，' + S.n + ' 筆訓練／' + S.nTest + ' 筆測試）：'
    : '模擬資料（p = 30，特徵之間平均 |相關| = ' + S.xCorr + '）：')
    + 'B = 300 時最好的是 <strong>m = ' + S.ms[best] + '</strong>（MSE '
    + HC.fmt(S.curves[best][last], 2) + '）。ρ 從 m = ' + S.ms[0] + ' 的 '
    + HC.fmt(S.rho[0], 3) + ' 一路降到 m = 2 的 '
    + HC.fmt(S.rho[3], 3) + '——去相關是真的，但誤差降不降要看資料。');
}

/* ---------- P11 vimp：變數重要度（烘焙） ---------- */
function w09vimpDraw() {
  const F = FRAMES_w09vimp;
  const el = document.getElementById('w09vimpSel');
  const mode = el ? el.value : 'impurity';
  const vals = mode === 'impurity' ? F.impurity : F.permutation;
  HC.bar('w09vimpChart', {
    labels: F.names,
    datasets: [{
      label: mode === 'impurity' ? '不純度（RSS）下降總量' : 'Permutation 重要度（測試 MSE 增加量）',
      data: vals,
      backgroundColor: vals.map((v, i) => i < 2 ? HC.tok.accent : 'rgba(44,62,122,.62)'),
      borderRadius: 4,
    }],
  }, {
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: { x: { title: { display: true,
                            text: mode === 'impurity' ? '不純度下降的相對佔比'
                                                      : '打亂該欄後測試 MSE 增加多少' } },
              y: { title: { display: true, text: 'Boston 的 12 個變數' } } },
  });
  const tot = vals.reduce((s, v) => s + Math.max(0, v), 0);
  document.getElementById('w09vimpTop1').textContent = F.names[0] + '（' + HC.fmt(vals[0], 3) + '）';
  document.getElementById('w09vimpTop2').textContent = F.names[1] + '（' + HC.fmt(vals[1], 3) + '）';
  document.getElementById('w09vimpShare').textContent =
    tot > 0 ? HC.pct((vals[0] + vals[1]) / tot, 1) : '—';
  document.getElementById('w09vimpMse').textContent = HC.fmt(F.testMse, 2);
  setStatus('w09vimpStatus', (mode === 'impurity'
    ? '不純度下降（<code>feature_importances_</code>，訓練資料上、零成本）：'
    : 'Permutation 重要度（測試資料上打亂該欄，重複 30 次取平均）：')
    + '前兩名都是 <strong>' + F.names[0] + '</strong> 與 <strong>' + F.names[1]
    + '</strong>，合計佔 ' + (tot > 0 ? HC.pct((vals[0] + vals[1]) / tot, 1) : '—')
    + '。兩種定義的排名在這份資料上幾乎一致——但這不保證，換一份資料就可能不同。');
}
"""

PAGEJS += r"""

/* ---------- P09 gb：梯度提升逐步器（淺樹在瀏覽器裡即時配殘差） ---------- */
const w09gbN = 70;
const w09gbSteps = 40;
const w09gbData = (() => {
  const rand = HC.stat.lcg(52408), x = [], y = [];
  for (let i = 0; i < w09gbN; i++) {
    const a = 10 * (i + 0.5) / w09gbN + 0.1 * (rand() - 0.5);
    x.push(a);
    y.push(3 * Math.sin(0.85 * a) + 0.42 * a + 0.55 * HC.stat.normal(rand));
  }
  return { x: x, y: y };
})();
const w09gbGrid = HC.stat.seq(0, 10, 161);
let w09gbLam = 0.35, w09gbDepth = 1, w09gbPlayer = null, w09gbFrames = [];

function w09gbSplit(idx, r) {
  const X = w09gbData.x;
  const vals = idx.map(i => X[i]).sort((a, b) => a - b);
  let best = null;
  for (let k = 2; k < vals.length - 3; k++) {
    const thr = (vals[k] + vals[k + 1]) / 2;
    let sl = 0, nl = 0, sr = 0, nr = 0;
    for (const i of idx) {
      if (X[i] < thr) { sl += r[i]; nl += 1; } else { sr += r[i]; nr += 1; }
    }
    if (nl < 3 || nr < 3) continue;
    const gain = sl * sl / nl + sr * sr / nr;
    if (!best || gain > best.gain) best = { thr: thr, gain: gain };
  }
  return best;
}
function w09gbFit(r) {
  const X = w09gbData.x;
  const mean = idx => {
    let s = 0;
    for (const i of idx) s += r[i];
    return idx.length ? s / idx.length : 0;
  };
  const build = (idx, lo, hi, d) => {
    if (d >= w09gbDepth || idx.length < 8) return [{ lo: lo, hi: hi, val: mean(idx) }];
    const b = w09gbSplit(idx, r);
    if (!b) return [{ lo: lo, hi: hi, val: mean(idx) }];
    const L = [], R = [];
    for (const i of idx) (X[i] < b.thr ? L : R).push(i);
    return build(L, lo, b.thr, d + 1).concat(build(R, b.thr, hi, d + 1));
  };
  return build(Array.from({ length: w09gbN }, (_, i) => i), 0, 10, 0);
}
function w09gbBuild() {
  const D = w09gbData;
  const r = D.y.slice();
  const G = new Array(w09gbGrid.length).fill(0);
  const out = [{ b: 0, fit: G.slice(), resid: r.slice(), next: null,
                 mse: HC.stat.mean(r.map(v => v * v)), sd: HC.stat.sd(r) }];
  for (let b = 1; b <= w09gbSteps; b++) {
    const segs = w09gbFit(r);
    const at = x => {
      for (const s of segs) if (x >= s.lo && x < s.hi) return s.val;
      return segs[segs.length - 1].val;
    };
    const scaled = segs.map(s => ({ lo: s.lo, hi: s.hi, val: w09gbLam * s.val }));
    out[b - 1].next = scaled;
    for (let i = 0; i < w09gbN; i++) {
      const d = w09gbLam * at(D.x[i]);
      r[i] -= d;
    }
    for (let k = 0; k < G.length; k++) G[k] += w09gbLam * at(w09gbGrid[k]);
    out.push({ b: b, fit: G.slice(), resid: r.slice(), next: null,
               mse: HC.stat.mean(r.map(v => v * v)), sd: HC.stat.sd(r) });
  }
  return out;
}
function w09gbApply(f) {
  const host = w09frame('w09gbSvg', 400);
  if (!host) return;
  const D = w09gbData;
  const X0 = 48, W = 552;
  const gx = v => X0 + v / 10 * W;
  const top = { y: 34, h: 172, lo: -5.5, hi: 8.5 };
  const bot = { y: 244, h: 118, lo: -5.0, hi: 5.0 };
  const ty = v => top.y + top.h - (v - top.lo) / (top.hi - top.lo) * top.h;
  const byy = v => bot.y + bot.h - (v - bot.lo) / (bot.hi - bot.lo) * bot.h;
  const box = (p, label) => {
    w09mk(host, 'rect', { x: X0, y: p.y, width: W, height: p.h, fill: '#fff',
                          stroke: 'var(--card-border)', 'stroke-width': 1 });
    w09mk(host, 'text', { x: X0, y: p.y - 8, cls: 'axtitle' }, label);
  };
  box(top, '目前的配適 f（橘線）');
  box(bot, '目前的殘差 r（灰點）與下一棵樹（虛線階梯）');
  w09mk(host, 'line', { x1: X0, y1: byy(0), x2: X0 + W, y2: byy(0),
                        stroke: 'var(--muted)', 'stroke-width': 1, 'stroke-dasharray': '4 3' });
  for (let i = 0; i < w09gbN; i++) {
    w09mk(host, 'circle', { cx: gx(D.x[i]), cy: ty(D.y[i]), r: 3, fill: 'var(--pt-train)',
                            stroke: '#fff', 'stroke-width': 0.8 });
    w09mk(host, 'circle', { cx: gx(D.x[i]), cy: byy(Math.max(bot.lo, Math.min(bot.hi, f.resid[i]))),
                            r: 2.6, fill: 'var(--muted)', opacity: 0.85 });
  }
  const pts = w09gbGrid.map((x, k) => gx(x) + ',' + ty(f.fit[k])).join(' ');
  w09mk(host, 'polyline', { points: pts, fill: 'none', stroke: 'var(--accent)',
                            'stroke-width': 2.8 });
  if (f.next) {
    const seg = [];
    f.next.forEach(s => {
      seg.push(gx(s.lo) + ',' + byy(Math.max(bot.lo, Math.min(bot.hi, s.val))));
      seg.push(gx(s.hi) + ',' + byy(Math.max(bot.lo, Math.min(bot.hi, s.val))));
    });
    w09mk(host, 'polyline', { points: seg.join(' '), fill: 'none', stroke: 'var(--accent3)',
                              'stroke-width': 2.4, 'stroke-dasharray': '6 4' });
  }
  w09mk(host, 'text', { x: X0 + W / 2, y: 392, 'text-anchor': 'middle', cls: 'axtitle' }, 'x');
  document.getElementById('w09gbB').textContent = f.b + ' / ' + w09gbSteps;
  document.getElementById('w09gbMse').textContent = HC.fmt(f.mse, 4);
  document.getElementById('w09gbSd').textContent = HC.fmt(f.sd, 4);
  document.getElementById('w09gbLeaf').textContent = String(Math.pow(2, w09gbDepth));
  hlLine('w09gbCode', f.b === 0 ? 1 : 4);
  setStatus('w09gbStatus', f.b === 0
    ? 'f 還是 0，所以殘差就是 y 本身（下面那排灰點）。虛線階梯是第一棵樹準備加上去的東西。'
    : '加了 ' + f.b + ' 棵樹（λ = ' + HC.fmt(w09gbLam, 2) + '，每棵 '
      + Math.pow(2, w09gbDepth) + ' 個葉子）：訓練 MSE = <strong>'
      + HC.fmt(f.mse, 4) + '</strong>，殘差的標準差降到 ' + HC.fmt(f.sd, 3)
      + '。注意下一棵樹（虛線）總是往殘差還偏得最多的地方去。');
}
function w09gbRebuild() {
  if (w09gbPlayer) w09gbPlayer.stop();
  w09gbFrames = w09gbBuild();
  w09gbPlayer = new Player({ frames: w09gbFrames, apply: w09gbApply });
  w09gbPlayer.reset();
}
function w09gbSetLam() {
  const el = document.getElementById('w09gbSlLam');
  if (el) w09gbLam = parseInt(el.value, 10) / 100;
  const sv = document.getElementById('w09gbSlLamVal');
  if (sv) sv.textContent = HC.fmt(w09gbLam, 2);
  const lv = document.getElementById('w09gbLamV');
  if (lv) lv.textContent = HC.fmt(w09gbLam, 2);
  w09gbRebuild();
}
function w09gbSetDepth() {
  const el = document.getElementById('w09gbSel');
  if (el) w09gbDepth = parseInt(el.value, 10);
  w09gbRebuild();
}
function w09gbStart() { w09gbRebuild(); w09gbPlayer.play(); }
function w09gbReset() { w09gbRebuild(); }

/* ---------- P09 ada：AdaBoost 的權重重分配 ---------- */
const w09adaPts = [[0.4, 1], [1.0, 1], [1.6, 1], [2.3, 1], [2.9, -1], [3.5, -1],
                   [4.2, 1], [4.8, 1], [5.4, -1], [6.0, -1], [6.6, -1], [7.2, 1],
                   [7.8, -1], [8.4, -1], [9.0, -1], [9.5, -1]];
const w09adaRounds = 10;
const w09adaEta = 0.5;        /* 講義式子裡的 η；η = ½ 就是經典的 AdaBoost */
let w09adaPlayer = null;
const w09adaFrames = (() => {
  const n = w09adaPts.length;
  let w = new Array(n).fill(1 / n);
  const score = new Array(n).fill(0);
  const out = [{ j: 0, w: w.slice(), thr: null, sign: 1, wrong: [], err: NaN,
                 alpha: NaN, ens: NaN }];
  for (let j = 1; j <= w09adaRounds; j++) {
    let best = null;
    for (let k = 0; k < n - 1; k++) {
      const thr = (w09adaPts[k][0] + w09adaPts[k + 1][0]) / 2;
      [1, -1].forEach(sg => {
        let e = 0;
        const wr = [];
        for (let i = 0; i < n; i++) {
          const h = (w09adaPts[i][0] < thr ? 1 : -1) * sg;
          if (h !== w09adaPts[i][1]) { e += w[i]; wr.push(i); }
        }
        if (!best || e < best.err) best = { thr: thr, sign: sg, err: e, wrong: wr };
      });
    }
    const e = Math.min(0.499, Math.max(0.001, best.err));
    const alpha = w09adaEta * Math.log((1 - e) / e);
    for (let i = 0; i < n; i++) {
      const h = (w09adaPts[i][0] < best.thr ? 1 : -1) * best.sign;
      score[i] += alpha * h;
      w[i] *= Math.exp(h === w09adaPts[i][1] ? -alpha : alpha);
    }
    const z = w.reduce((s, v) => s + v, 0);
    w = w.map(v => v / z);
    let bad = 0;
    for (let i = 0; i < n; i++) {
      if ((score[i] >= 0 ? 1 : -1) !== w09adaPts[i][1]) bad += 1;
    }
    out.push({ j: j, w: w.slice(), thr: best.thr, sign: best.sign, wrong: best.wrong,
               err: best.err, alpha: alpha, ens: bad / n,
               score: score.slice() });
  }
  return out;
})();
function w09adaApply(f) {
  const host = w09frame('w09adaSvg', 320);
  if (!host) return;
  const X0 = 48, W = 552, gx = v => X0 + v / 10 * W;
  const yA = 92, yB = 200;
  w09mk(host, 'rect', { x: X0, y: 40, width: W, height: 210, fill: '#fff',
                        stroke: 'var(--card-border)', 'stroke-width': 1 });
  if (f.thr !== null) {
    const left = f.sign === 1 ? 'var(--pt-a)' : 'var(--pt-b)';
    const right = f.sign === 1 ? 'var(--pt-b)' : 'var(--pt-a)';
    w09mk(host, 'rect', { x: X0, y: 40, width: gx(f.thr) - X0, height: 210,
                          fill: left, opacity: 0.1 });
    w09mk(host, 'rect', { x: gx(f.thr), y: 40, width: X0 + W - gx(f.thr), height: 210,
                          fill: right, opacity: 0.1 });
    w09mk(host, 'line', { x1: gx(f.thr), y1: 40, x2: gx(f.thr), y2: 250,
                          stroke: 'var(--ink)', 'stroke-width': 2.2,
                          'stroke-dasharray': '6 4' });
    w09mk(host, 'text', { x: gx(f.thr), y: 34, 'text-anchor': 'middle',
                          fill: 'var(--ink)',
                          style: w09MONO + 'font-size:10px;font-weight:700' },
          'x = ' + HC.fmt(f.thr, 2));
  }
  w09mk(host, 'text', { x: X0 - 6, y: yA + 4, 'text-anchor': 'end', cls: 'axlab' }, 'A 類');
  w09mk(host, 'text', { x: X0 - 6, y: yB + 4, 'text-anchor': 'end', cls: 'axlab' }, 'B 類');
  const wrong = new Set(f.wrong);
  w09adaPts.forEach((p, i) => {
    const cy = p[1] === 1 ? yA : yB;
    const r = 4 + 34 * f.w[i];
    w09mk(host, 'circle', { cx: gx(p[0]), cy: cy, r: Math.min(16, r),
                            fill: p[1] === 1 ? 'var(--pt-a)' : 'var(--pt-b)',
                            opacity: 0.85,
                            stroke: wrong.has(i) ? 'var(--ink)' : '#fff',
                            'stroke-width': wrong.has(i) ? 3 : 1 });
    if (wrong.has(i)) {
      w09mk(host, 'text', { x: gx(p[0]), y: cy - Math.min(16, r) - 5,
                            'text-anchor': 'middle', fill: 'var(--ink)',
                            style: w09MONO + 'font-size:11px;font-weight:700' }, '✗');
    }
  });
  w09mk(host, 'text', { x: X0, y: 275, cls: 'axtitle' },
        '圈的大小＝權重 · 粗黑框＝這一輪答錯（權重下一輪會變大）');
  if (f.score) {
    w09mk(host, 'text', { x: X0, y: 296, cls: 'axtitle' }, '集成目前的判斷：');
    for (let k = 0; k < 60; k++) {
      const x = 10 * (k + 0.5) / 60;
      let s = 0;
      for (let m = 1; m <= f.j; m++) {
        const fr = w09adaFrames[m];
        s += fr.alpha * (x < fr.thr ? 1 : -1) * fr.sign;
      }
      w09mk(host, 'rect', { x: gx(x) - 4, y: 302, width: 8, height: 9, rx: 2,
                            fill: s >= 0 ? 'var(--pt-a)' : 'var(--pt-b)', opacity: 0.8 });
    }
  }
  document.getElementById('w09adaRound').textContent = f.j + ' / ' + w09adaRounds;
  document.getElementById('w09adaThr').textContent =
    f.thr === null ? '—' : 'x = ' + HC.fmt(f.thr, 2) + (f.sign === 1 ? '（左為 A）' : '（左為 B）');
  document.getElementById('w09adaErr').textContent = HC.fmt(f.err, 4);
  document.getElementById('w09adaAlpha').textContent = HC.fmt(f.alpha, 4);
  document.getElementById('w09adaEns').textContent =
    Number.isNaN(f.ens) ? '—' : HC.pct(f.ens, 1);
  setStatus('w09adaStatus', f.j === 0
    ? '第 0 輪：18 筆資料的權重全部相同（1/18），還沒有任何分類器。'
    : '第 ' + f.j + ' 輪：最好的 stump 切在 x = ' + HC.fmt(f.thr, 2)
      + '，加權錯誤率 e = ' + HC.fmt(f.err, 3) + '，所以這一輪的份量 α = ½ ln((1−e)/e) = '
      + HC.fmt(f.alpha, 3) + '。答錯的 ' + f.wrong.length
      + ' 個點權重乘上 e^α、答對的乘上 e^−α。集成到目前的訓練錯誤率 '
      + HC.pct(f.ens, 1) + '。');
}
function w09adaStart() {
  w09adaPlayer = new Player({ frames: w09adaFrames, apply: w09adaApply });
  w09adaPlayer.reset();
  w09adaPlayer.play();
}
function w09adaReset() {
  if (w09adaPlayer) w09adaPlayer.stop();
  w09adaPlayer = new Player({ frames: w09adaFrames, apply: w09adaApply });
  w09adaPlayer.reset();
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.line / HC.bar 在 Chart 未載入時本來就安全地回傳 null。 */
w09growReset();
w09impSetup();
w09impDraw();
w09voteRender();
w09bagReset();
w09gbRebuild();
w09adaReset();
HC.ready(() => {
  w09pruneJumpCv();
  w09voteChartDraw();
  w09rfDraw();
  w09vimpDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("tree_based_methods", BODIES, PAGEJS, frames())
