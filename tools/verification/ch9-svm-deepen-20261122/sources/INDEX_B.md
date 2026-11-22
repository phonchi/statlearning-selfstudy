# 來源索引 B（讀取日期 2026-11-22）

PDF 以 curl 下載、`pdftotext -layout` 轉文字，公式頁另以 `pdftoppm` 渲染核對；暫存檔只放在 session scratchpad，未進 repo。頁碼為 PDF 實體頁（括號內附投影片頁尾編號）。

| 檔案 | URL | 講義頁 | 狀態 |
|---|---|---|---|
| htlin-202-dual-svm.md | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf | p.17 | OK（curl 200，PDF 28 頁；p.5–6、p.11–13 已渲染核對） |
| htlin-204-soft-margin.md | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf | p.18 | OK（curl 200，PDF 27 頁；p.10、p.16、p.18（200 dpi 看圖）、p.23 已渲染核對，含 □/△ 圖例） |
| htlin-206-svr.md | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf | p.34 | OK（curl 200，PDF 28 頁；文字抽取遺失 ε，p.5–6、10–15、17–19 已渲染補回） |
| cmu-svm-recitation.md | https://www.cs.cmu.edu/~epxing/Class/10701-08s/recitation/svm.pdf | p.18 | OK（curl 200，PDF 10 頁）；原文未展開 soft-margin dual 推導，dual 上界 γ 未定義，記為原文未涵蓋 |
| bourret-kernel-feature-map.md | https://xavierbourretsicotte.github.io/Kernel_feature_map.html | p.24 | OK（curl 200）；頁內圖片未檢視；列出 5 項原文疑誤 |
| esl-ex12-1-solution.md | https://yuhangzhou88.github.io/ESL_Solution/ESL-Solution/_12-Flexible-Discriminants/ex12-01/ | p.30 | OK（curl 200）；頁面未重述 ESL (12.25) 原式，未憑記憶補 |
| htlin-mooc-index.md | https://www.csie.ntu.edu.tw/~htlin/mooc/ | p.36 | OK（curl 200）；201–206 handout 皆 HTTP 200；201 已下載未讀 |
| htlin-203-kernel-svm.md | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/203_handout.pdf | 經 p.36 索引頁（非直接連結） | OK（curl 200，PDF 27 頁；p.15 已渲染核對） |
| htlin-205-kernel-lr.md | https://www.csie.ntu.edu.tw/~htlin/mooc/doc/205_handout.pdf | 經 p.36 索引頁（非直接連結） | OK（curl 200，PDF 26 頁；p.5、6、8、11、21 已渲染核對） |
