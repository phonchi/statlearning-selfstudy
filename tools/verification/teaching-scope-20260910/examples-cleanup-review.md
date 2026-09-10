# 精確算例清理審查

只保存預案與備份，此步尚未修改內容。此預案回應先前寬標記風險：每個實際移除片段逐項列在下方及JSON中，套用時只允許已記錄SHA256的完整前稿。

保留所有原Lab code/output/card呼叫、原有教學互動、Seeing Theory一般公式與證明。只刪已定位的本站自訂觀測/程式、重复數字表，以及ISLP Ch10沒有要求的額外Lipschitz定理；不刪整章。

## 來源核對

- S1：母檔原說明明列通勤與二點分布為本站自訂；Seeing Theory Ch1來源為硬幣、骰子、期望/變異與一致性，原一般公式保留。
- S2：母檔說明所有數值例由本站重新設計；刪的是1%/90%/5%篩檢數字與五人班長例，不刪Bayes、全機率、排列/組合的一般式。
- S3：λ=2的計數/等待段是在Coverage completion區自行追加；Seeing Theory的Poisson PMF與Exponential PDF及正規化推導原樣保留。骰子CLT等同源例暫不刪。
- S4：52與[2,4,4,8]五次重抽是本站新增的固定算例，正文概念互動和一般SE/CI/Bootstrap式保留。未以「已知σ」寬標記刪除任何模型假設。
- S5：7正3反、Beta(20,20)比較等是本站自訂示意資料，刪數值表/手算；Beta密度、正規化、共軛更新及一般MLE證明保留。
- S6：五筆OLS資料與A/B/C三組數字，母檔/圖例已明說自訂；移除靜態手算，保留必要概念圖、OLS/RSS/ANOVA一般公式與證明。
- P2：三個hl區塊的旁文均明寫「自訂語法/函式練習」；它們不是Ch02/Ch05原Lab。所有原Lab函式與for/zip例不变。
- DL：人工x=2,y=1及權重更新段明標本站自訂；ISLP §10.7.1–10.7.4 (pp.428–431)原推導是梯度/鏈式法則/正則化，未引入L-Lipschitz下降定理。刪額外定理，保留原本單層與必要backprop、官方Lab、原題、標量函數界限。

## enrich_deeplearning.py

原Lab呼叫保留：`{'lab_code': 25, 'lab_output': 12, 'card': 13}`

- 1417：non-source x=2,y=1,weights example
```text
<h3>手算一次更新</h3>
<p>本站自訂算例：只有一個輸入與一個 ReLU 單元，$x=2,y=1$，
$w=0.5,w_0=0,\beta=0.4,\beta_0=0.1$。
前向傳播得 $z=1,a=1,f=0.5,e=-0.5$，損失為 0.125。
依照 $(\beta_0,\beta,w_0,w)$ 的順序，梯度是 $(-0.5,-0.5,-0.2,-0.4)$。</p>
<p>學習率 0.1 時，新參數為 $(0.15,0.45,0.02,0.54)$。
重新前向傳播得 $z=1.10,f=0.645$，新損失為 $\tfrac12(0.645-1)^2=0.0630125$。
這次確實下降；任意資料與任意學習率並無同樣保證。</p>

```

- 1450：extra Lipschitz theorem; retain original scalar function limitation
```text
<h3>梯度下降的條件與圖中函數的限制</h3>
<p>若可微目標的梯度為 L-Lipschitz，取 $0&lt;\rho&lt;2/L$ 可保證單步下降；
若目標另有下界，能進一步推得梯度範數趨近 0。這仍不等於全域最佳，也不自動保證參數序列收斂。
ReLU 在折點不可微，不能直接把這個光滑函數論證當作所有網路的保證。</p>

```

- 1457：extra L-Lipschitz proof absent from ISLP Ch10; original backprop proof retained
```text
proof('w11proof-descent','光滑函數的下降界限',r"""
<p>L-Lipschitz 梯度給出 $R(\theta+d)\le R(\theta)+\nabla R(\theta)^\top d+\tfrac L2\|d\|^2$。
代入 $d=-\rho\nabla R(\theta)$：</p>
$$R(\theta-\rho\nabla R(\theta))\le R(\theta)-\rho(1-L\rho/2)\|\nabla R(\theta)\|^2.$$
<p>若 $0&lt;\rho&lt;2/L$，非零梯度給出下降。固定步長、目標有下界時，逐次加總可得梯度平方和有限，故梯度範數趨近 0。</p>
""")
```

## enrich_p2_flow_functions.py

原Lab呼叫保留：`{'lab_code': 1, 'lab_output': 1, 'card': 12}`

- 40：authored example paragraph
```text
<p>這是自訂語法練習，不是 lab 的實跑輸出。先猜會執行哪一個 print，再把 mpg 改成 20 重跑。冒號開始區塊；同一區塊的縮排必須一致。</p>
```

- 56：authored example paragraph
```text
<p>這個自訂例子依序取出三個數字，每次都做相同判斷。下面的 NumPy／pandas 遮罩把整欄一起判斷；若尚不熟資料表，可以先讀下一節的基本迴圈，學完 P3、P4 再回來對照。</p>
```

- 184：authored example paragraph
```text
<p>這是自訂函式練習。<code>def</code> 定義名字和參數；<code>return</code> 交回真假值，外面的 print 才負責顯示。先改門檻，確認每次呼叫如何使用引數。以下是學完基本語法後的課程應用；OLS、設計矩陣與 MSE 可在 <a href="p6_modeling_api.html">P6</a> 詳讀。</p>
```

- 39：explicitly labeled custom program; Ch02/05 source Lab calls retained
```text
hl("mpg = 30\nif mpg >= 25:\n    print('達到門檻')\nelse:\n    print('未達門檻')")
```

- 55：explicitly labeled custom program; Ch02/05 source Lab calls retained
```text
hl("values = [18, 30, 24]\nfor mpg in values:\n    if mpg >= 25:\n        print(mpg)")
```

- 183：explicitly labeled custom program; Ch02/05 source Lab calls retained
```text
hl("def above_threshold(value, threshold=25):\n    return value >= threshold\n\nfor value in [18, 30, 24]:\n    print(above_threshold(value))")
```

## enrich_s1_probability.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 19：authored example paragraph
```text
<p>假設取得的通勤時間是 10、15、15、20、40 分鐘。樣本平均數為：</p>
```

- 21：authored example paragraph
```text
<p>排序後居中的值是中位數 15 分鐘。40 分鐘拉高了平均數；兩者描述的中心位置有所不同。
這些數字是本站自訂的算例。全班的 μ 仍未知，不能直接宣稱也是 20 分鐘。</p>
```

- 67：authored example paragraph
```text
<p>若把每次獎勵定為 Y = 2X + 10，平均獎勵是 E[Y] = 2E[X] + 10。
以骰子為例，期望獎勵為 17。公式先對每個可能結果套用同一個換算，再取加權平均。</p>
```

- 87：authored example paragraph
```text
<p>例如 X 的變異數為 1，Y = 3X + 10 的變異數就是 9，標準差是 3。
做單位換算時也一樣：乘數在變異數裡要平方，標準差則乘上乘數的絕對值。</p>
```

- 169：authored example paragraph
```text
<p>例如單次測量標準差是 6，取 9 次獨立測量的平均，其標準差是 $6/\sqrt9=2$。
若測量彼此相關，就不能直接套用這個除以 n 的變異數公式。</p>
```

- 23：table of explicitly authored observations; generic formulas outside table retained
```text
table(['問題', '例子'], [('母體是誰？', '這一班所有同學。'), ('樣本是誰？', '受訪的五位同學。'),
    ('樣本怎麼來？', '只問附近同學可能漏掉其他座位或缺席的人。'), ('推論需要什麼？', '清楚的抽樣方式，以及對代表性與誤差的說明。')])
```

- 20：display belonging only to removed authored numerical case
```text
$$\bar{x}=\frac{10+15+15+20+40}{5}=20\text{ 分鐘}.$$
```

## enrich_s2_conditional.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 136：authored example paragraph
```text
<p><strong>數值例。</strong>某疾病盛行率為 1%，檢測對病人的陽性率為 90%，
  對健康者的偽陽性率為 5%。在 10,000 人中，預期有 100 位病人，其中 90 位陽性；
  9,900 位健康者中約 495 位也陽性。因此：</p>
```

- 140：authored example paragraph
```text
<p>陽性結果確實提高了罹病機率，從 1% 變成約 15.4%；但高敏感度本身無法保證陽性後機率很高。
  這就是基準率（base rate）不可省略的原因。</p>
```

- 157：authored example paragraph
```text
<p><strong>數值例。</strong>五位同學選班長與副班長，職位不同，所以有
  $P_{{5,2}}=5\\times4=20$ 種；若只選兩位代表而不分職位，則每一對的先後被重算兩次，
  共有 $\\binom{{5}}{{2}}=10$ 組。</p>
```

- 161：table of explicitly authored observations; generic formulas outside table retained
```text
table(["問題", "順序重要嗎", "計算", "結果"], [
    ["5 人選班長、副班長", "重要", "$5\\times4$", "20"],
    ["5 人選 2 位代表", "不重要", "$5\\times4/2!$", "10"],
    ["擲 3 次硬幣恰有 2 次正面", "正面在哪兩次很重要", "$\\binom{{3}}{{2}}(1/2)^3$", "$3/8$"],
])
```

- 139：display belonging only to removed authored numerical case
```text
$$P(\\text{{疾病}}\\mid +)=\\frac{{90}}{{90+495}}\\approx0.154.$$
```

## enrich_s3_distributions.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 485：authored example paragraph
```text
<p>λ=2 時，零次的機率為 $e^{-2}\approx0.1353$，恰好一次為 $2e^{-2}\approx0.2707$。
<a href="classification.html#poisson">分類章的 Poisson 迴歸</a>讓這個條件平均隨解釋變數改變。
若資料有明顯過度離散，單純 Poisson 的變異數假設就需要再檢查。</p>
```

- 491：authored example paragraph
```text
<p>例如每分鐘率 λ=2 的模型，平均等待時間為 0.5 分鐘，等待超過一分鐘的機率為 $e^{-2}$。
在同質 Poisson 過程中，長度 t 的計數平均是 λt，而相鄰事件等待時間是此指數分布；任意計數資料不一定符合這種過程。</p>
```

## enrich_s4_inference.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 109：authored example paragraph
```text
<p>已知 $\sigma=10$，抽 $n=25$ 人得到 $\bar x=52$。95% 的臨界值為 1.96，誤差範圍是
  $1.96\times10/\sqrt{{25}}=3.92$，因此區間為</p>
```

- 232：authored example paragraph
```text
<p>原始樣本是 $[2,4,4,8]$，平均為 4.5。五次示意重抽可得到
  $[2,2,4,8]$、$[4,4,4,8]$、$[8,4,2,8]$、$[2,4,2,4]$、$[8,8,4,4]$；
  對應平均為 4、5、5.5、3、6，樣本標準差約 1.204。</p>
```

- 238：table of explicitly authored observations; generic formulas outside table retained
```text
table(["重抽樣本", "bootstrap 平均"],
       [["[2, 2, 4, 8]", "4.0"], ["[4, 4, 4, 8]", "5.0"],
        ["[8, 4, 2, 8]", "5.5"], ["[2, 4, 2, 4]", "3.0"],
        ["[8, 8, 4, 4]", "6.0"]])
```

- 111：display belonging only to removed authored numerical case
```text
$$[52-3.92,\ 52+3.92]=[48.08,\ 55.92]。$$
```

- 108：heading for removed authored example
```text
<h3>算一次：95% 信賴區間</h3>
```

- 231：heading for removed authored example
```text
<h3>小例子：看清楚「有放回」</h3>
```

## enrich_s5_bayesian.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 47：authored example paragraph
```text
<p><strong>算例。</strong>7 次正面、3 次反面時，最大概似估計是 $0.7$。
  $p=0.7$ 相對於 $p=0.5$ 的概似比為
  $0.7^7 0.3^3/(0.5^{10})\approx2.28$。這表示目前資料在前一參數下約有 2.28 倍支持度；
  它不表示「$p=0.7$ 的機率是 2.28 倍」。若完全沒有資料，所有 $p$ 都使概似達到同一最大值，
  因此 MLE 不唯一，資料無法選出單一估計。</p>
```

- 67：authored example paragraph
```text
<p><strong>算例。</strong>$\operatorname{Beta}(2,2)$ 先驗加上 7 次正面、3 次反面，得到
  $\operatorname{Beta}(9,5)$ 後驗；平均由 $1/2$ 移到 $9/14\approx0.643$。
  下圖可以重做這筆計算，也能檢查均勻先驗與零筆資料等端點。</p>
```

- 113：authored example paragraph
```text
<p><strong>算例。</strong>同樣觀察 3 次正面、1 次反面。均勻先驗
  $\operatorname{Beta}(1,1)$ 產生 $\operatorname{Beta}(4,2)$，後驗平均為 $2/3$；
  集中在 0.5 的 $\operatorname{Beta}(20,20)$ 產生 $\operatorname{Beta}(23,21)$，後驗平均約 0.523。
  四筆資料對較集中的先驗影響較小。</p>
```

- 117：table of explicitly authored observations; generic formulas outside table retained
```text
table(
    ["情況", "後驗參數", "後驗平均", "閱讀重點"],
    [["Beta(1,1)＋3 正 1 反", "Beta(4,2)", "0.667", "資料比例影響明顯"],
     ["Beta(20,20)＋3 正 1 反", "Beta(23,21)", "0.523", "先驗總量較大"],
     ["Beta(20,20)＋300 正 100 反", "Beta(320,120)", "0.727", "大量資料取得較大權重"]],
)
```

## enrich_s6_regression.py

原Lab呼叫保留：`{'lab_code': 0, 'lab_output': 0, 'card': 0}`

- 51：authored example paragraph
```text
<p><strong>算例。</strong>固定資料 $(0,1),(1,2),(2,2),(3,4),(4,5)$ 的
  $\bar x=2$、$\bar y=2.8$、$S_{xy}=10$、$S_{xx}=10$，所以 OLS 線是
  $\hat y=0.8+1.0x$，RSS 為 0.8。拖動下面兩個滑桿，再按「顯示 OLS 解」核對。</p>
```

- 85：authored example paragraph
```text
<p><strong>算例。</strong>上一節 OLS 線對五筆資料的預測為
  $(0.8,1.8,2.8,3.8,4.8)$，所以殘差為 $(0.2,0.2,-0.8,0.2,0.2)$。
  它們加總為 0，平方和為 $4(0.2^2)+(-0.8)^2=0.8$。中間那筆貢獻 RSS 的 80%，
  顯示平方損失會放大較大的殘差。</p>
```

- 123：authored example paragraph
```text
<p><strong>算例。</strong>A 組 $(1,2)$、B 組 $(3,4)$、C 組 $(5,6)$；三組平均為 1.5、3.5、5.5，
  總平均為 3.5。$SS_{\mathrm{Between}}=16$、$SS_{\mathrm{Within}}=1.5$，
  所以 $SS_{\mathrm{Total}}=17.5$。自由度為 2 與 3，得到 $F=(16/2)/(1.5/3)=16$。</p>
```

- 126：table of explicitly authored observations; generic formulas outside table retained
```text
table(
    ["來源", "平方和", "自由度", "均方", "F"],
    [["組間", "16", "3−1=2", "8", "16"],
     ["組內", "1.5", "6−3=3", "0.5", "—"],
     ["總計", "17.5", "6−1=5", "—", "—"]],
)
```

