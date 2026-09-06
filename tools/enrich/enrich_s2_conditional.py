#!/usr/bin/env python3
"""s2_conditional.html（統計先備 S2 · 複合與條件機率）完整自學充實。冪等。

內容依據 Seeing Theory 第 2 章網頁與講義第 19–30 頁，文字、數值例與互動皆為
本站重新設計。這是概念頁，不引用課程 lab，也不產生 deck-extra 卡。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, hook, info, info_card, qa, quiz, rows_card, svg, table, viz  # noqa: E402

ST2 = "https://seeing-theory.brown.edu/compound-probability/index.html"
STPDF = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf"


def source(section, page):
    return (f'<p class="source-note"><strong>原始教材：</strong>'
            f'<a href="{ST2}">Seeing Theory 第 2 章 · {section}</a> · '
            f'<a href="{STPDF}#page={page}">PDF p.{page}</a>。'
            '本頁文字、例題與圖均重新製作。</p>')


def accessible_svg(sid, label, height):
    return svg(sid, height).replace("<svg ", f'<svg role="img" aria-label="{label}" ')


BODIES = {}

BODIES["events"] = f"""
  <p>做機率題的第一步，是把「可能發生什麼」說清楚。樣本空間（sample space）
  記作 $\\Omega$，包含一次實驗的所有可能結果；事件（event）則是其中一部分。
  例如擲一顆公平六面骰，$\\Omega=\\{{1,2,3,4,5,6\\}}$。令
  $A=\\{{2,4,6\\}}$ 表示「偶數」，$B=\\{{4,5,6\\}}$ 表示「至少 4」。</p>

{info("集合語言", "交集 $A\\cap B$ 表示兩件事同時成立；聯集 $A\\cup B$ 表示至少一件成立；"
      "補集 $A^c$ 表示 $A$ 沒有發生。這三個動作會在條件機率裡反覆出現。")}

  <p>上例中，$A\\cap B=\\{{4,6\\}}$，所以 $P(A\\cap B)=2/6=1/3$；
  $A\\cup B=\\{{2,4,5,6\\}}$，所以 $P(A\\cup B)=4/6=2/3$。若兩個事件可能重疊，
  加法規則要把重複算到的交集扣掉：</p>
  $$P(A\\cup B)=P(A)+P(B)-P(A\\cap B).$$

{table(["事件", "包含的點數", "機率", "讀法"], [
    ["$A$", "2、4、6", "$3/6$", "骰出偶數"],
    ["$B$", "4、5、6", "$3/6$", "骰出至少 4"],
    ["$A\\cap B$", "4、6", "$2/6$", "既是偶數且至少 4"],
    ["$A\\cup B$", "2、4、5、6", "$4/6$", "是偶數或至少 4（含兩者皆是）"],
])}

{qa("觀念釐清", [
    ("機率題裡的「或」會排除兩者同時發生嗎？",
     "通常不會。$A\\cup B$ 是包含式的「或」：$A$、$B$ 至少一個成立，也包含兩者都成立。若題目明說只能擇一，才另外排除交集。"),
])}

{quiz("qEvent", "PART 01 · 自我檢測", "擲一顆公平六面骰，$A$ 為偶數、$B$ 為至少 4。$P(A\\cup B)$ 是多少？", [
    (False, "$1$", "把 $P(A)$ 與 $P(B)$ 直接相加，會把交集 4、6 各算兩次。"),
    (True, "$2/3$", "對。聯集是 {2,4,5,6}，共 4 個等可能結果，所以機率是 4/6。"),
    (False, "$1/3$", "這是交集 {4,6} 的機率，不是聯集。"),
])}
{source("Set Theory", 19)}
"""

BODIES["conditional"] = f"""
  <p>條件機率（conditional probability）會把分母換掉。$P(A\\mid B)$ 的意思是：
  已知 $B$ 發生後，只在 $B$ 這個縮小的樣本空間裡，計算同時也屬於 $A$ 的比例。</p>
  $$P(A\\mid B)=\\frac{{P(A\\cap B)}}{{P(B)}}\\qquad(P(B)>0).$$

{info("先看分母", "看到直線右邊的事件，就先把它圈成新的全部。"
      "$P(A\\mid B)$ 的分母是 $B$；$P(B\\mid A)$ 的分母是 $A$。兩者通常不相等。", "warm")}

{viz(accessible_svg("w22condSvg", "事件 A 與 B 的可編輯二乘二人數表", 330),
     [info_card("事件定義",
                "以 100 人為例：<strong>A＝真的有某疾病</strong>，"
                "<strong>B＝篩檢呈陽性</strong>。四格可自行改成任何非負整數。"),
      rows_card("即時計算", [
          ("總人數", "100", "w22condN"),
          ("P(A)", "10/100 = 0.100", "w22condPA"),
          ("P(B)", "18/100 = 0.180", "w22condPB"),
          ("P(A｜B)", "8/18 = 0.444", "w22condAB"),
          ("P(B｜A)", "8/10 = 0.800", "w22condBA"),
      ]),
      info_card("怎麼讀四格",
                "左上格是 $A\\cap B$。求 $P(A\\mid B)$ 時，分母取整個 B 欄；"
                "求 $P(B\\mid A)$ 時，分母取整個 A 列。分子雖相同，分母不同。")],
     "w22condStatus", "目前共有 18 人篩檢陽性，其中 8 人真的有疾病。",
     '<label>A 且 B <input id="w22n11" type="number" min="0" max="999" value="8" '
     'aria-label="事件 A 與 B 同時發生的人數" oninput="w22condDraw()"></label>'
     '<label>A 且非 B <input id="w22n10" type="number" min="0" max="999" value="2" '
     'aria-label="事件 A 發生且 B 未發生的人數" oninput="w22condDraw()"></label>'
     '<label>非 A 且 B <input id="w22n01" type="number" min="0" max="999" value="10" '
     'aria-label="事件 A 未發生且 B 發生的人數" oninput="w22condDraw()"></label>'
     '<label>皆否 <input id="w22n00" type="number" min="0" max="999" value="80" '
     'aria-label="事件 A 與 B 都未發生的人數" oninput="w22condDraw()"></label>'
     '<button class="btn btn-reset" onclick="w22condReset()">重置</button>',
     provenance=("illustrative", "本站自訂 2×2 人數表；所有比例由輸入值即時計算。"))}

{qa("觀念釐清", [
    ("如果條件事件一個人都沒有呢？",
     "分母為 0 時，條件機率在這個初階定義下沒有定義。互動元件會顯示「未定義」，不會把它誤算成 0。"),
])}

{quiz("qCond", "PART 02 · 自我檢測", "某班 30 人中有 12 人修微積分，其中 9 人也修程式設計。已知一位同學修微積分，他也修程式設計的機率是多少？", [
    (True, "$9/12=0.75$", "對。條件是修微積分，所以分母只剩這 12 人，其中 9 人也修程式設計。"),
    (False, "$9/30=0.30$", "這用的是全班 30 人當分母，算到的是兩科都修的聯合比例。"),
    (False, "$12/30=0.40$", "這是修微積分的邊際機率，沒有利用「其中 9 人也修程式設計」。"),
])}
{source("Conditional Probability", 27)}
"""

BODIES["independence"] = f"""
  <p>若知道 $B$ 發生後，$A$ 的機率完全不變，我們稱 $A$ 與 $B$ 獨立（independent）：</p>
  $$P(A\\mid B)=P(A),$$
  <p>只要相關機率有定義，這等價於乘法式：</p>
  $$P(A\\cap B)=P(A)P(B).$$

  <p>例如連續擲兩次公平硬幣，令 $A$ 為「第一次正面」、$B$ 為「第二次正面」。
  四個結果 HH、HT、TH、TT 等可能，$P(A)=P(B)=1/2$ 且 $P(A\\cap B)=1/4$，
  正好等於乘積。知道第一次結果，不會改變第二次正面的機率。</p>

{info("獨立不等於互斥", "互斥事件不能同時發生，所以 $P(A\\cap B)=0$。"
      "若兩事件都有正機率，這不等於 $P(A)P(B)$，因此它們反而不獨立。", "warm")}

{table(["關係", "定義／檢查式", "知道 B 後對 A 的影響", "能否同時發生"], [
    ["獨立", "$P(A\\cap B)=P(A)P(B)$", "不改變", "通常可以"],
    ["互斥", "$A\\cap B=\\varnothing$", "B 發生便排除 A", "不可以"],
])}

{quiz("qInd", "PART 03 · 自我檢測", "一顆公平骰子只擲一次。$A$＝出現偶數，$B$＝出現 5。兩事件的關係是什麼？", [
    (False, "獨立，因為偶數和 5 沒有關係", "口語上覺得無關還不夠。B 發生便確定 A 沒發生，因此條件機率已改變。"),
    (True, "互斥但不獨立", "對。兩事件不能同時發生；而 P(A)P(B)=1/12 不等於交集機率 0。"),
    (False, "既互斥又獨立", "兩個正機率事件若互斥，交集為 0，但邊際機率乘積大於 0，不符合獨立。"),
])}
{source("Set Theory 與條件機率", 21)}
"""

BODIES["bayes"] = f"""
  <p>Bayes 定理用來把條件方向翻過來。已知「有病時驗出陽性」並不等於
  「驗出陽性時真的有病」；後者還取決於疾病原本有多常見。</p>
  $$P(A\\mid B)=\\frac{{P(B\\mid A)P(A)}}{{P(B)}}.$$
  <p>若 $A$ 與 $A^c$ 分割所有人，分母可用全機率公式展開：</p>
  $$P(B)=P(B\\mid A)P(A)+P(B\\mid A^c)P(A^c).$$

  <p><strong>數值例。</strong>某疾病盛行率為 1%，檢測對病人的陽性率為 90%，
  對健康者的偽陽性率為 5%。在 10,000 人中，預期有 100 位病人，其中 90 位陽性；
  9,900 位健康者中約 495 位也陽性。因此：</p>
  $$P(\\text{{疾病}}\\mid +)=\\frac{{90}}{{90+495}}\\approx0.154.$$
  <p>陽性結果確實提高了患病機率，從 1% 變成約 15.4%；但高靈敏度本身無法保證陽性後機率很高。
  這就是基準率（base rate）不可省略的原因。</p>

{hook("後續用途", "<a href='classification.html#lda'>分類第 LDA 節</a>會用 Bayes 定理把類別條件密度轉成後驗類別機率；"
      "<a href='statistical_learning.html#bayes'>統計學習的 Bayes 分類器</a>則選後驗機率最大的類別。")}

{quiz("qBayes", "PART 04 · 自我檢測", "沿用上例，一個人驗出陽性後，最接近的患病機率是哪一個？", [
    (False, "90%", "90% 是 P(陽性｜疾病)，條件方向與題目要的 P(疾病｜陽性) 相反。"),
    (True, "15%", "對。陽性者預期共有 90+495=585 人，其中 90 人有病，90/585 約為 15.4%。"),
    (False, "1%", "1% 是檢測前的基準率；陽性結果會更新這個機率。"),
])}
{source("Bayes Rule", 28)}
"""

BODIES["counting"] = f"""
  <p>當每個基本結果等可能時，機率常化成「符合條件的數量／全部數量」。計數時先問順序是否重要。
  從 $n$ 個不同物件中選 $r$ 個：若順序重要，用排列；若只在乎選了哪一些，用組合。</p>
  $$P_{{n,r}}=\\frac{{n!}}{{(n-r)!}},\\qquad
    \\binom{{n}}{{r}}=\\frac{{n!}}{{r!(n-r)!}}.$$

  <p>符號 $n!$ 讀作 n 的階乘，表示從 n 乘到 1，例如 $4!=4\\times3\\times2\\times1=24$；約定 $0!=1$。這裡 n 與 r 為整數，且 $0\\le r\\le n$，每個物件最多選一次。</p>
  <p><strong>數值例。</strong>五位同學選班長與副班長，職位不同，所以有
  $P_{{5,2}}=5\\times4=20$ 種；若只選兩位代表而不分職位，則每一對的先後被重算兩次，
  共有 $\\binom{{5}}{{2}}=10$ 組。</p>

{table(["問題", "順序重要嗎", "計算", "結果"], [
    ["5 人選班長、副班長", "重要", "$5\\times4$", "20"],
    ["5 人選 2 位代表", "不重要", "$5\\times4/2!$", "10"],
    ["擲 3 次硬幣恰有 2 次正面", "正面在哪兩次很重要", "$\\binom{{3}}{{2}}(1/2)^3$", "$3/8$"],
])}

{quiz("qCount", "PART 05 · 自我檢測", "10 本不同的書選 3 本帶走，不考慮排列順序，應用哪一個數量？", [
    (False, "$10^3$", "這允許同一本書被重複選，而且把三次選取視為有順序，不符合題意。"),
    (False, "$10\\times9\\times8$", "這算排列，把相同三本書的 3! 種先後都分開計算。"),
    (True, "$\\binom{{10}}{{3}}=120$", "對。物件不同、不重複，且只在乎選到哪三本，所以用組合。"),
])}
{source("Counting", 23)}
"""

BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 原創", "袋中有 3 顆紅球、2 顆藍球，不放回抽兩顆。第二顆是紅球，且已知第一顆是藍球，其機率為何？", [
    (False, "$3/5$", "條件發生後袋中只剩 4 顆球，分母要更新。"),
    (True, "$3/4$", "對。第一顆藍球已移除，剩 3 紅、1 藍。"),
    (False, "$2/4$", "剩下的藍球只有 1 顆；題目問的是紅球。"),
])}
{quiz("qEx2", "EXERCISE 2 · 原創", "若 $P(A)=0.4$、$P(B)=0.5$ 且兩事件獨立，$P(A\\cup B)$ 為何？", [
    (True, "$0.7$", "對。交集為 0.4×0.5=0.2，所以聯集為 0.4+0.5−0.2=0.7。"),
    (False, "$0.9$", "直接相加沒有扣掉交集，會把同時發生算兩次。"),
    (False, "$0.2$", "0.2 是獨立時的交集機率，不是聯集。"),
])}
{quiz("qEx3", "EXERCISE 3 · 原創", "某警報在火災時有 98% 會響，無火災時有 2% 會誤響。要算警報響後有火災的機率，還缺哪項？", [
    (False, "警報音量", "音量不在目前的機率模型裡，無法補出 Bayes 公式的先驗。"),
    (True, "火災的基準率", "對。還需要 P(火災)，才能加權真陽性與偽陽性。"),
    (False, "把 98% 和 2% 相加", "兩個條件機率不能直接相加；它們還要分別乘上火災與無火災的機率。"),
])}
{quiz("qEx4", "EXERCISE 4 · 計數延伸〔選讀〕", "八位跑者選出金、銀、銅牌，假設不並列，共有幾種名次結果？", [
    (False, "$\\binom{{8}}{{3}}=56$", "獎牌有順序，同三人交換金銀銅會是不同結果。"),
    (True, "$8\\times7\\times6=336$", "對。依序選金、銀、銅，每次少一人。"),
    (False, "$8^3=512$", "這允許同一人同時拿多面獎牌，不符合不重複。"),
])}
  <p class="source-note"><strong>題目來源：</strong>四題均為本站原創，觀念範圍對照
  <a href="{ST2}">Seeing Theory 第 2 章</a>與<a href="{STPDF}#page=19">PDF pp.19–30</a>。</p>
"""

BODIES["reference"] = f"""
{table(["看到的語句", "分母／計算", "先檢查"], [
    ["A 或 B", "$P(A)+P(B)-P(A\\cap B)$", "交集是否被重複計算"],
    ["已知 B，求 A", "$P(A\\cap B)/P(B)$", "$P(B)>0$"],
    ["A、B 獨立", "$P(A\\cap B)=P(A)P(B)$", "不能只靠語感判斷"],
    ["由 B 反推 A", "$P(B\\mid A)P(A)/P(B)$", "先驗／基準率與分母"],
    ["選 r 個且順序重要", "$n!/(n-r)!$", "是否可重複選"],
    ["選 r 個且順序不重要", "$\\binom{{n}}{{r}}$", "是否每組等可能"],
])}
  <p><a href="{ST2}">Seeing Theory · Compound Probability</a>提供集合、計數與條件機率的原始互動章節；
  <a href="{STPDF}#page=19">Seeing Theory PDF pp.19–30</a>提供公式推導與完整例題脈絡。</p>
  <p class="ver-note">本頁例題、測驗與互動圖均為本站原創；即時計算不使用外部資料。頁面沒有課程 lab 卡，沒有烘焙圖表；互動重置會完整回到預設人數。</p>
"""


PAGEJS = r"""
const w22condS = HC.svg('w22condSvg', {h: 330, pad: {l: 24, r: 24, t: 48, b: 30}});

function w22condValue(id) {
  const el = document.getElementById(id);
  const raw = Number(el.value);
  if (!Number.isFinite(raw) || raw < 0) {
    el.value = '0';
    return 0;
  }
  const v = Math.min(999, Math.round(raw));
  if (String(v) !== el.value) el.value = String(v);
  return v;
}

function w22condRatio(num, den) {
  return den > 0 ? num + '/' + den + ' = ' + HC.fmt(num / den, 3) : '未定義（分母為 0）';
}

function w22condCell(g, x, y, w, h, fill, title, value) {
  w22condS.add('rect', {x: x, y: y, width: w, height: h, rx: 7,
                        fill: fill, 'fill-opacity': fill === HC.tok.card ? 1 : 0.1, stroke: HC.tok.cardBorder, 'stroke-width': 1.5}, g);
  w22condS.txtPx(x + w / 2, y + 32, title, {cls: 'w22cellLabel', fill: HC.tok.ink, anchor: 'middle'}, g);
  w22condS.txtPx(x + w / 2, y + 74, String(value),
                 {cls: 'w22cellValue', anchor: 'middle', fill: HC.tok.ink}, g);
}

function w22condDraw() {
  if (!w22condS) return;
  const n11 = w22condValue('w22n11');
  const n10 = w22condValue('w22n10');
  const n01 = w22condValue('w22n01');
  const n00 = w22condValue('w22n00');
  const nA = n11 + n10, nB = n11 + n01, n = nA + n01 + n00;
  const g = w22condS.clearLayer('main');
  w22condS.txtPx(186, 30, 'B：陽性', {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent2}, g);
  w22condS.txtPx(444, 30, '非 B：陰性', {cls: 'axtitle', anchor: 'middle'}, g);
  w22condS.txtPx(18, 105, 'A', {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent}, g);
  w22condS.txtPx(18, 235, '非 A', {cls: 'axtitle', anchor: 'middle'}, g);
  w22condCell(g, 54, 50, 264, 108, HC.tok.accent2, 'A 且 B（真陽性）', n11);
  w22condCell(g, 326, 50, 264, 108, HC.tok.card, 'A 且非 B（偽陰性）', n10);
  w22condCell(g, 54, 166, 264, 108, HC.tok.accent3, '非 A 且 B（偽陽性）', n01);
  w22condCell(g, 326, 166, 264, 108, HC.tok.card, '非 A 且非 B（真陰性）', n00);
  document.getElementById('w22condN').textContent = String(n);
  document.getElementById('w22condPA').textContent = w22condRatio(nA, n);
  document.getElementById('w22condPB').textContent = w22condRatio(nB, n);
  document.getElementById('w22condAB').textContent = w22condRatio(n11, nB);
  document.getElementById('w22condBA').textContent = w22condRatio(n11, nA);
  if (nB === 0 || nA === 0 || n === 0) {
    setStatus('w22condStatus', '<b>分母為 0：</b>對應的條件機率沒有定義；請增加條件事件的人數。');
  } else {
    setStatus('w22condStatus', 'B 欄共有 <b>' + nB + '</b> 人，其中 <b>' + n11 +
      '</b> 人屬於 A；A 列共有 <b>' + nA + '</b> 人，其中 <b>' + n11 + '</b> 人屬於 B。');
  }
}

function w22condReset() {
  document.getElementById('w22n11').value = '8';
  document.getElementById('w22n10').value = '2';
  document.getElementById('w22n01').value = '10';
  document.getElementById('w22n00').value = '80';
  w22condDraw();
}

if (w22condS) w22condDraw();
"""


if __name__ == "__main__":
    apply("s2_conditional", BODIES, PAGEJS)
