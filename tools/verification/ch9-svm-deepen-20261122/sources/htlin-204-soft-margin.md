# 林軒田《機器學習技法》Lecture 4: Soft-Margin Support Vector Machine（handout）
- URL: https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf
- 講義頁: p.18（林軒田 Soft-Margin SVM handout 連結）
- 抓取狀態: OK（curl，HTTP 200，application/pdf，2,089,610 bytes；`pdftotext -layout`；PDF p.10、p.16、p.18（另以 200 dpi 看圖）、p.23 以 `pdftoppm` 渲染核對公式與圖例符號）
- 讀取日期: 2026-11-22

頁碼慣例：「PDF p.X」為 PDF 實體頁；括號內為投影片頁尾編號（x/22）。
記號對照：N = 樣本數、d̃ = 轉換後維度、zₙ = Φ(xₙ)、ξₙ = slack（source_brief 問題中寫作 ε）；此 C 為**懲罰權重**（越大越不容忍違規）。推論：source_brief Q6 提到「C 與 const 反比」，暗示課程講義另有「Σε ≤ const」的預算寫法；預算越大越容忍違規，方向與此 C 相反。
公式轉寫：PDF p.10、p.16、p.18、p.23 依渲染圖；其餘依 `pdftotext -layout` 版面轉寫。英文引句只取自文字條列。

## 重點（中文撰寫，術語保留原文）

### Primal 與 C 的意義
- 動機：hard-margin 一定要可分（⇒ 可以 shatter），「have power to overfit to noise」（PDF p.3，2/22）。
- 先寫成「½wᵀw + C·Σ⟦yₙ ≠ sign(wᵀzₙ + b)⟧」的組合，「C: trade-off of large margin & noise tolerance」（PDF p.4，3/22）。但 ⟦·⟧ 非線性、不是 QP，且「cannot distinguish small error … or large error」，因此改用 margin violation ξₙ（PDF p.5，4/22）。
- Soft-margin primal（轉寫）：min_{b,w,ξ} ½wᵀw + C·Σξₙ s.t. yₙ(wᵀzₙ + b) ≥ 1 − ξₙ、ξₙ ≥ 0（PDF p.5–6）。
- 「parameter C: trade-off of large margin & margin violation」；「large C: want less margin violation」；「small C: want large margin」（PDF p.6，5/22）。
- 大小：「QP of d̃ + 1 + N variables, 2N constraints」（PDF p.6）。

### Slack 的解讀
- Fun Time（PDF p.7–8，6/22）：若 y₁(wᵀz₁ + b) = −10，則 ξ₁ = 11；「ξ₁ is simply 1 − y₁(wᵀz₁ + b) when y₁(wᵀz₁ + b) ≤ 1」。
- Fun Time（PDF p.19–20，16/22）：「If ξₙ ≥ 1, then the violation causes a 0/1 error」；「it is also possible that ξₙ < 1, and in that case the violation does not cause a 0/1 error」。

### Dual：box constraint 0 ≤ αₙ ≤ C（PDF p.9–12，已渲染 p.10）
- Lagrange function 對兩組限制各配乘數 αₙ ≥ 0、βₙ ≥ 0（PDF p.9，7/22）。
- ∂L/∂ξₙ = 0 = C − αₙ − βₙ；「no loss of optimality if solving with implicit constraint βₙ = C − αₙ and explicit constraint 0 ≤ αₙ ≤ C: βₙ removed」（PDF p.10，8/22）。推論：αₙ ≤ C 就是 βₙ = C − αₙ ≥ 0 的另一種寫法。
- 其餘步驟「inner problem same as hard-margin SVM」（PDF p.11，9/22）。
- 標準 dual：min ½ΣΣαₙαₘyₙyₘzₙᵀzₘ − Σαₙ s.t. Σyₙαₙ = 0、0 ≤ αₙ ≤ C；「only difference to hard-margin: upper bound on αₙ」；「another (convex) QP, with N variables & 2N + 1 constraints」（PDF p.12，10/22）。
- Fun Time（PDF p.13–14，11/22）：「C is exactly the upper bound of αₙ」——C 增加 2，dual 的上界就增加 2。
- 推論（供 Q6 參考）：在此講義的形式中，C 是 primal 目標函數中預先給定的權重，在 dual 中表現為 αₙ 的上界；C 本身不是被求解的 Lagrange multiplier（被求解的是 αₙ、βₙ）。原文沒有直接說「C 不是 Lagrange multiplier」。

### Kernel soft-margin 與求 b（PDF p.15–16）
- 「almost the same as hard-margin」；「more flexible than hard-margin —primal/dual always solvable」（PDF p.15，12/22）。這裡指懲罰形式（ξ 無上限）永遠有可行解，不是預算形式。
- Complementary slackness（轉寫）：αₙ(1 − ξₙ − yₙ(wᵀzₙ + b)) = 0、(C − αₙ)ξₙ = 0。
- 「free (αₛ < C) ⇒ ξₛ = 0」，因此用 free SV 求唯一 b：b = yₛ − Σ_{SV} αₙyₙK(xₙ, xₛ)；否則只得「range of b」（PDF p.16，13/22）。

### Free vs bounded SV，以及圖上怎麼認（PDF p.18，15/22；已看渲染圖）
- non SV（αₙ = 0）：ξₙ = 0，「‘away from’/on fat boundary」。
- □ free SV（0 < αₙ < C）：ξₙ = 0，「on fat boundary, locates b」。
- △ bounded SV（αₙ = C）：「ξₙ = violation amount, ‘violate’/on fat boundary」。
- 圖例（以 200 dpi 重新渲染 PDF p.18 右側圖目視）：藍 ○ 與紅 × 為兩類；黑色實線為決策邊界，兩側灰色帶狀區為 fat boundary（margin）。free SV 以**方框（□）**框起，共 3 點（2 藍 1 紅），位在帶狀區的邊緣上；bounded SV 以**三角形（△）**框起，共 4 點，都在帶狀區內，其中 2 個藍 ○ 與 1 個紅 × 已越過黑線落在對方一側（被誤分），另 1 個紅 × 在帶內但仍在正確一側。其餘未框起的點在帶外（non SV）。點數與位置為本筆記目視判讀，非原文文字。
- 「αₙ can be used for data analysis」。
- Fun Time（PDF p.19–20）：N = 10000、1126 個 SV、其中 1000 個 bounded，E_in 範圍為 0 ≤ E_in ≤ 0.1000——只有 bounded SV 可能違反 fat boundary，且違反不一定造成分類錯誤。

### C 的效果與選擇
- Soft-margin Gaussian SVM，C = 1、10、100 的圖：「large C ⇒ less noise tolerance ⇒ ‘overfit’?」；「need careful selection of (γ, C)」（PDF p.17，14/22）。
- 用 cross validation 在格點上選 (C, γ)（PDF p.21–22）；「claim: E_loocv ≤ #SV / N」（PDF p.23，19/22）；nSV「just an upper bound!」，常作 safety check（PDF p.24，20/22）。

## 與下列問題的關聯
- Q6：C 是 trade-off 權重、在 dual 中變成 αₙ 上界（PDF p.6、p.10、p.12、p.14）；此 C 越大越不容忍違規，與預算形式的 const 方向相反（推論，見記號對照）。
- Q7：「primal/dual always solvable」（PDF p.15）——指懲罰形式；預算形式未討論。
- Q9：大 C、大 γ 都可能 overfit（PDF p.17）。
- Q10：free SV（□，在 margin 邊線上）vs bounded SV（△，違反 margin），PDF p.18 圖。
