# 來源筆記索引（2026-11-17）

| 檔案 | 抓取狀態 |
|---|---|
| ai-assisted-stats-ch06.md | OK（curl，HTTP 200）。**注意：此頁是書的配套 notebook 渲染結果 |
| axk51013-kaggle-categorical-encoding.md | 失敗（HTTP 403；curl 帶瀏覽器 UA 與 WebFetch 皆被 Medium 擋下。依 |
| bart-cgm2010-paper.md | OK（PDF 共 35 頁，pdftotext 抽取；只讀了 §2.2–§3.1） |
| bart-lopes-slides.md | OK（PDF 共 45 頁投影片，pdftotext 抽取，第 20–23、25 頁另轉成� |
| catboost-docs-bootstrap.md | OK（curl 取得 HTML，`yfm-latex` 公式已解碼） |
| catboost-docs-cat-to-numeric.md | OK（curl 取得 HTML。公式以 `yfm-latex` 的 `data-content` 屬性存放， |
| catboost-paper.md | OK（PDF 共 11 頁，用 pdftotext 抽取；補充材料未抓。表格被逐� |
| catboost-training-parameters.md | OK（curl 取得 HTML 並轉純文字；`boosting_type` 的預設表另以原始 |
| catboost-tutorial-categorical-params.md | OK（從 raw.githubusercontent.com 取得 .ipynb JSON，讀取全部 markdown、 |
| chefboost-readme.md | OK（從 raw.githubusercontent.com 取得 master 分支的 README.md） |
| dafriedman-mlbook-boosting.md | OK（WebFetch 讀取；AdaBoost 的 α、權重更新、標籤編碼、AdaBoost. |
| datasketches-quantiles-overview.md | 部分（講義原網址回 **HTTP 404**。改讀：①現行搬移後頁面 htt |
| esl-8-7-bagging.md | OK（`pdftotext -layout`；公式排版被拆散，以下 LaTeX 依原式重寫� |
| esl-ch10-boosting.md | OK（`pdftotext -layout` 抽取；書頁 = PDF 頁 − 19，例如書 p.339 = PD |
| esl-ch15-rf.md | OK（`pdftotext -layout` 全文；公式因排版被拆散，以下 LaTeX 依原 |
| esl-solutions-yuhangzhou.md | OK（首頁目錄與下列各題頁面皆以 curl 取得，HTTP 200。完整讀� |
| fisher-1958-grouping.md | 失敗（Taylor & Francis 頁面 HTTP 403，curl 與 WebFetch 皆同）。只透 |
| grinsztajn-2022-trees-vs-dl.md | OK（arXiv v1，2022-07-18，PDF 經 pdftotext 抽取。圖表數值無法從文 |
| hackmd-lightgbm-wangjengyun.md | 部分（HTML 內嵌的 Markdown 原文完整取得，約 11.8k 字元；文中� |
| ho1998-random-subspace.md | 部分（IEEE Xplore 回 HTTP 202、內容為空的 JS 殼；書目資料取自  |
| islp-8-2-1-2.md | OK（`pdftotext -layout`；公式的 $\frac1B$ 被排版拆開，以下依原式 |
| islp-8-2-3.md | OK（`pdftotext -layout`；書頁 = PDF 頁 − 7，例如書 p.349 = PDF p.356� |
| latency-numbers-gist.md | OK（GitHub gist HTML，讀取 `latency.txt` 內容） |
| lightgbm-features.md | OK（curl 直接取得 HTML；頁內示意圖為圖片，未讀取） |
| lightgbm-paper.md | OK（PDF 共 9 頁，用 pdftotext 抽取；補充材料未抓） |
| lightgbm-parameters.md | OK（curl 取得 HTML，轉純文字後 grep 各參數條目） |
| louppe-geurts-2012-random-patches.md | 部分（Springer 頁面 303 轉向 idp.springer.com 後只回 "Client Challenge |
| mlbook-bagging.md | OK（curl 取得靜態 HTML，HTTP 200；頁面無程式碼，只有文字與 La |
| mlbook-random-forests.md | OK（curl 取得靜態 HTML，HTTP 200；無程式碼、無數值例） |
| mse-majority-vote-binomial.md | 部分（網頁本身 HTTP 403 擋爬；問題與 2 則回答全文改由官方  |
| neptune-catboost-vs-xgb-lgbm.md | 失敗（TLS 憑證過期：curl 回報 "SSL certificate problem: certificate ha |
| pourya-kfold-target-encoding.md | 失敗（HTTP 403；curl 帶瀏覽器 UA 與 WebFetch 皆被 Medium 擋下。依 |
| psu-stat414-variance-sample-mean.md | 部分（原站 TLS 憑證鏈驗證失敗：curl "unable to get local issuer cer |
| riskified-xgb-lgbm-catboost.md | 失敗（HTTP 403；curl 帶瀏覽器 UA 與 WebFetch 皆被 Medium 擋下。依 |
| se-leafwise-levelwise.md | 部分。網頁直接抓取回 HTTP 403（curl 與 WebFetch 皆同），改用� |
| sefiks-gbdt-step-by-step.md | 部分（WebFetch 兩次讀取成功，但內容經 WebFetch 摘要模型轉述� |
| sklearn-ensemble-guide.md | OK（curl，HTTP 200；頁面標題顯示版本 **scikit-learn 1.9.1**。使用� |
| sklearn-tree-algorithms.md | OK（頁面標題 "1.10. Decision Trees — scikit-learn 1.9.1 documentation"； |
| stackexchange-xgboost-taylor.md | 部分（WebFetch 被擋："unable to fetch from stats.stackexchange.com"；改� |
| stackoverflow-tree-split-thresholds.md | 部分（網頁直接抓取回 HTTP 403 / Cloudflare 挑戰頁；改用公開 St |
| statquest-gradient-boost-part1-regression.md | OK（YouTube 自動字幕 `auto`，英文，youtube-transcript-api；只有語� |
| statquest-xgboost-part1-regression.md | OK（YouTube 自動字幕 `auto`，英文；只有語音，畫面上的散佈圖 |
| statquest-xgboost-part3-math.md | OK（YouTube 自動字幕 `auto`，英文；只有語音。**畫面上的公式� |
| statquest-xgboost-part4-optimizations.md | OK（YouTube 自動字幕 `auto`，英文；**字幕品質差**：無標點，� |
| stats-se-xgboost-feature-scaling.md | 部分（網頁直接抓取回 HTTP 403 / Cloudflare 挑戰頁；改用公開 St |
| tds-catboost-lgbm-xgboost.md | 失敗（HTTP 403；curl 帶瀏覽器 UA 與 WebFetch 皆被擋。依委派指� |
| wikipedia-id3.md | OK（curl 取得 HTML 並轉純文字） |
| xgboost-categorical.md | OK（"Categorical Data — xgboost 3.4.2 documentation"） |
| xgboost-dart.md | OK（"DART — xgboost 3.4.2 documentation"） |
| xgboost-docs-index.md | OK（"XGBoost Documentation — xgboost 3.5.0-dev documentation"；首頁僅為� |
| xgboost-docs-tree-boosting-tutorial.md | OK（WebFetch 讀渲染頁；逐字內容另以原始檔 https://raw.githubuserc |
| xgboost-faq-missing-values.md | OK（"Frequently Asked Questions — xgboost 3.4.2 documentation"） |
| xgboost-paper.md | OK（PDF 下載成功，以 `pdftotext` 抽文字；第 4 頁另行渲染成圖� |
| xgboost-parameters.md | OK（頁面標題 "XGBoost Parameters — xgboost 3.4.2 documentation"） |
| xgboost-tree-methods.md | OK（"Tree Methods — xgboost 3.4.2 documentation"） |
