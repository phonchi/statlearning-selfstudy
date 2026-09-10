# Ch1–3 直接連結教材：第二輪閱讀結清

本輪處理共享 `ch1-6-links.json` 中 Ch1–3 原先標為「原文未讀」的 **79 筆**。未改共享 ledger，逐筆結果在 `supplement-links-ch1-3.json`。

- **36 筆**：讀到原連結的相關正文／問答，再與課本、作者文件或獨立推導核對。
- **8 筆**：原站受阻或原入口無正文，改讀同題主要教材／官方文件；保留原始失敗，沒有改稱原文已讀。
- **1 筆**：講義折行造成的截斷重複 URL，以同題完整 URL 讀取。
- **34 筆**：直接核對講義頁面後，確認角色為歷史文獻、人物、工具首頁、資料、競賽、示意漫畫或整課目錄。這些不是待搬入正文的隱藏方法教材，也不宣稱已讀其全文。

`closed=true` 表示來源角色與內容處置已完成，**不代表每個外部網站／整本書都已全文閱讀**。`original_read` 獨立記錄是否實際讀到原文。

## 原始閱讀證據

- 先重用 `ch1-6-fetch.json` 與 `ch1-6-link-text/`，避免重抓。HTTP 200 的短字串／防爬頁不當作有效全文。
- `supplement-link-evidence/` 保存 web 工具取得的原文段落與失敗回應。StackExchange 多數原先 HTTP 403 的教材，改用 web 工具後成功取得正文。
- 本機原始講義已直接讀取：01 pp.25–30、38–39；02 pp.11–15；03 pp.4–5、24、45–47、61，其他 URL 由既有講義索引定位並比對對應段落。
- `Foundations of Data Science` 直接閱讀 PDF pp.16–19（§2.3–2.4.1），不是只看目錄。這本書的其餘數百頁不列為本次高維幾何必要閱讀。
- 作者 `Python for Data Analysis` 視覺化章已讀 Figure/Axes、存圖、pandas/Seaborn、facet 對應段落；pandas 官方速查表已讀 pp.1–2 的 reshape/join/filter/summary 與相關 I/O。

## 本輪新增內容

| 頁面 | 從直接教材找到的缺漏 | 完成方式 |
|---|---|---|
| introduction | median 相對效率缺分布／漸近條件；資料表 reshaping 與 joining 的意義缺例子 | 加常態 2/π 與收合推導；長／寬表、melt/pivot、join 鍵與多對多列數例子 |
| statistical_learning | 只看球／立方體體積比例，尚未交代球內薄殼集中與球體積推導 | 加均勻球內取樣的球殼比例、2/10/50維算例及Gaussian積分收合推導 |
| linear_regression | 固定/隨機 X、中心化交互作用、內外學生化、殘差圖橫軸、任意預測R²的限制 | 補完整條件、刪除公式與t自由度、兩則收合推導、複製資料假精度、R²反例；保留前組最新低VIF修改 |

母檔定位標記為 `# LINK-CLOSURE-CH1-3`。本輪只動上述三個 enrich 母檔與生成 HTML，不修改共享工具或其他代理的章節。新增一般推導共 **4 則**，均使用 `proof()` 預設收合；公式、條件與算例保留正文。

## 排除的來源錯誤

讀到來源不代表照抄來源。以下錯誤／省略已明確辨識：

- median 問答未先說分布條件，且回應中有限樣本公式排版有歧義；網站只使用已獨立核對的常態漸近結果。
- 兩篇 bias–variance 部落格把 training residual／插值誤差直接稱作 bias，與重複抽樣的定義不同。網站採 ISLP 定義與既有完整分解，不複製錯誤敘述。
- R² 問答的首個答案有 SSR／SSE 互換錯誤；網站使用含截距 OLS 正交性，並補 arbitrary prediction 反例。
- 誤差相關的問答以複製資料說明虛假精度，但其中 F 比率與 variance 式有代數錯誤。網站獨立推出正確係數變異數比例 `(n-m)/(cn-m)`。
- Gaussian MLE 作者教材的 Y 寫作 iid 過度概括；不同 x 的條件平均不同，Y 不必同分布。估 σ 時也不能刪掉依賴 σ 的對數項。
- Wiki leverage 的「沒有鄰近點」不是正式必要條件；網站依帽子矩陣、殘差與刪除影響區分。

## 受阻與替代

- PSU 五個直接教材網址：requests 連線錯誤，web 再試仍為 502／timeout。依講義所指主題，以已讀本機 ISLP Ch3、作者 MLE 教材與 R 官方 deletion diagnostics 核對。保留受阻，不標原文已讀。
- StackExchange 310687：完整與短 URL 的 web 讀取均失敗，原 HTTP 403；用已讀 ISLP 及網站獨立風險推導結清對應教學內容。沒有虛構原答案。
- Seaborn introduction：原 URL 對兩種讀取方式皆無正文；以同站 function overview 核對圖族／Axes層級，既有 P5 內容已覆蓋。
- OReilly 連結是整書入口且受阻，同一講義頁另明指 Foundations Ch2，已讀其幾何段落。
- 截斷的 SE85560 URL 與完整題目重複；完整題目已成功讀到信賴帶中心／斜率不確定性的推導。

## 驗證與凍結

- `supplement-links-generate.log`：三頁使用既有 `FRAMES_*` 重建，沒有重跑 Lab 或烘焙模擬。
- `supplement-links-numerics.py`／`.log`：**24 項獨立數值檢查通過**。包括每筆獨立刪除重擬合對照 RSS 與學生化公式、交互作用中心化、殘差投影、球殼比例及R²反例。
- `supplement-links-browser.log`：三頁全部通過，**0 個問題**；exec session `87029` 已 exit 0。涵蓋預設收合、鍵盤操作、展開公式、手機版與既有互動。
- `supplement-links-shots/`：每頁 reading、展開後桌面及手機截圖。主代理可取最新三頁加入全站 montage。
- 逐頁 validator 當時只報三頁共同 `GEN-REGION studyguide` 與共享新樣板不同；交由主代理最後統一 build。導論另有476KB建議size警告。**本紀錄不把尚待共用build的validator寫成全綠。** 沒有新增的grounding或ID失敗。
- 三頁母檔與HTML已告知主代理凍結；後續只更新本紀錄，不再改正文。
