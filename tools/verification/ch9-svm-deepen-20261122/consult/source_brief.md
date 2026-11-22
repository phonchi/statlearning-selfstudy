# 第 9 章講義連結讀取指引（給讀來源的 subagent）

每個連結寫一份 `sources/<短名>.md`，格式：

```
# <標題>
- URL:
- 講義頁: p.N（錨文字）
- 抓取狀態: OK（工具、HTTP 狀態）／失敗（實際錯誤訊息）／部分（說明）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）
- 逐條列出與下列問題有關的內容，附原文短引句（英文原句 ≤ 25 字）與位置（頁碼／小節／式號）。
## 與下列問題的關聯（只寫有關的題號）
```

不要寫入其他檔案；沒讀到原文就照實寫「未讀」，不要憑記憶補內容。被擋（403 等）時可改用官方替代：
Stack Exchange 用 `https://api.stackexchange.com/2.3/questions/<id>?site=<site>&filter=withbody` 與 `/answers?...&filter=withbody`；PDF 用 curl 下載後 `pdftotext -layout`（存在 scratchpad，不要放進 repo）。

## 學生問題（來自課堂後的問答，依講義頁序）
1. p.4 SVM 優點：「p>n 時仍有效」「決策函數只用支持向量，所以執行時間與記憶體都有效率」是什麼意思？效率是跟誰比（KNN？LR／LDA 只存權重）？p>n 是否跟 dual 有關？
2. p.5 超平面是 p−1 維的 flat affine subspace：flat、affine、linear subspace 的定義與差別。
3. p.6 點到直線距離、scalar projection 與 vector projection。
4. p.15 三個等價式：max M s.t. ‖β‖=1 → 除以 ‖β‖ → 令 M=1/‖β‖ 變成 min ‖β‖；β 會變但邊界不變的原因、slack 為何不變、直覺。
5. p.17 primal（適合 p 小）與 dual（適合 n 小、可用 kernel）的關係、½‖β‖² 代入後的負號、Lagrange multiplier 必須 ≥0 還是 >0。
6. p.18 ½‖β‖²+C∑ε 的 C 是否就是 Lagrange multiplier；C 與 const 反比的意義。
7. p.19 線性邊界「找不到合適解」：預算夠大時是否一定有可行解？
8. kernel 想法是否也用在 LR、PCA、線性迴歸的 normal equation（kernel ridge）？dual PCA 用 XXᵀ？
9. p.26 Mercer's theorem 是什麼；RBF 為何是無窮維；γ 越大代表什麼。
10. 支持向量在圖上怎麼認（在 margin 上或違反 margin）。
11. p.30 hinge＋ridge 的改寫（ESL 習題 12.1）；hinge 的轉折為何在 1；兩種 logistic loss 寫法；SVM 像 L2-LR 還是原本的 LR。
12. SVC 能不能用在迴歸（SVR、ε-insensitive loss）。
13. p.32–33 SGD、kernel approximation、LinearSVC／SVC／NuSVC、probability 估計（Platt）。
