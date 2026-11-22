**目前不宜直接定稿。**主要問題是三式等價的適用條件、核嶺迴歸的置中處理，以及正文已修正、測驗與詞彙卡卻仍保留的錯誤。

以下以**實際 HTML／JSON**為準，未將文字快照中的舊句當成現況。`consult/`、`sources/` 均指 `tools/verification/ch9-svm-deepen-20261122/` 下的目錄。全程未修改檔案。

1. **[嚴重] `w10-detail-three-forms`／`w10-soft-feasible`：「兩題的最佳解是同一個超平面」「預算給得夠多雖然一定解得出來」**  
   — **問題：** 混淆「存在可行點」與「存在有限最佳解」。三式的幾何等價需要有限正 margin、非零法向量；預算大時，最大化 \(M\) 可能無界，第三式則可能得到 \(\beta=0\)，不能反推超平面。  
   — **證據：** [HTML:1192](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1192)、[HTML:1295](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1295)。獨立反例：兩筆 \((x,y)=(-1,-1),(1,1)\)，取 \(\beta=1,b=0,B=2\)。任何 \(M\ge1\)，令兩筆 \(\epsilon_i=1-1/M\)，總預算 \(2-2/M\le2\)，所以 \(M\) 無上界。第三式卻可取 \(\beta=b=0,\epsilon_i=1\)，目標為零。  
   — **建議修法：** 補上等價條件；將「一定解得出來」改成「一定可行，但不保證存在有限最大 margin」。若談標準懲罰式，另說明 \(C>0\) 時可求最佳解，但可能得到常數分類器。這直接影響學生 msg17–27、37、39。

2. **[中] `w10-detail-three-forms`及題庫「三個等價式」：「最近點函數間隔為 1」**  
   — **問題：** 把硬邊界的尺度解釋套到軟邊界。軟邊界固定的是參考間隔 \(f=\pm1\)，最近訓練點可以在帶內，甚至被分錯。  
   — **證據：** [HTML:1185](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1185)、[題庫:30](/home/phonchi/statlearning-selfstudy/data/questions_zh/ch9.json:30)。例如上述兩點取 \(B=1\)，第一式可得 \(M=2,\epsilon_i=0.5\)，第三式得到 \(\beta=0.5\)，兩筆函數間隔都是 \(0.5\)，不是 1。  
   — **建議修法：** 改成「將兩條參考 margin 固定為 \(f=\pm1\)」；「最近點函數間隔為 1」限定於硬邊界最佳解。

3. **[中] `w10-detail-kernel-beyond`：「先把 \(X\) 與 \(y\) 置中」／「\(\lambda=0\)…\(XX^T\) 可逆」**  
   — **問題：** 前後條件不相容。欄置中後 \(\mathbf1^TX=0\)，因此 \(XX^T\mathbf1=0\)，不論 \(p\) 多大，\(XX^T\) 都不可逆。「所以實務上的核化都會保留 \(\lambda>0\)」也過度概括。  
   — **證據：** [HTML:2050](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:2050)、[HTML:2059](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:2059)。`sources/htlin-206-svr.md` 的核嶺解只支持「\(\lambda>0\) 保證可逆」，沒有支持這段置中 OLS 推論。  
   — **建議修法：** 已置中資料使用偽逆；滿列秩插值例子另明示為「未置中、無截距」。不要把正則化說成所有核化都必須具備的條件。

4. **[中] `w10-detail-kernel-beyond`：「把 \(K\) 與 \(k_*\) 換成核值，就是核嶺迴歸」**  
   — **問題：** 沿用上文「截距另外處理」時，原始 \(X\) 置中不等於非線性特徵 \(\phi(X)\) 置中；直接替換成原始核值，並不能保留相同的截距處理。  
   — **證據：** [HTML:2050–2056 的起點](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:2050)。獨立核算：\(x=(-2,1,1),y=(-1,0,1)\) 都已置中，取 \(K_{ij}=x_i^2x_j^2,\lambda=1\)，依頁面公式得到的殘差總和為 \(0.947368\)，不滿足不受罰截距所需的殘差和為零。  
   — **建議修法：** 最簡單是明示核公式採無截距模型；若保留截距，補上訓練核與測試核向量的特徵空間置中，以及預測時回加 \(\bar y\)。

5. **[中] `soft`／`qSvOptions`：「剛好落在 margin…以及跑進 margin 帶內或分錯的點」全部判為支持向量**  
   — **問題：** 與本頁採用的「選定對偶解中 \(\alpha_i>0\)」定義矛盾。margin 上的點可能有零乘子。  
   — **證據：** [HTML:1366](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1366) 的正確選項及回饋，與同頁 KKT 表第 1240 行衝突。反例：\(x=(-1,-1,1),y=(-1,-1,1),C=1\)，\(w=1,b=0,\alpha=(0.5,0,0.5)\) 滿足 KKT，primal、dual 值均為 \(0.5\)；三點都在 margin，但第二點乘子為零。  
   — **建議修法：** 改成「帶內或分錯的點是支持向量；恰在 margin 上的點可能是，需看乘子」。同步修正前方「在圖上認出支持向量」的絕對敘述。

6. **[中] 題庫「預算與懲罰」：「兩者在正則化路徑上一一對應」**  
   — **問題：** 不保證一對一；整段 \(C\) 可以對應相同總 slack。  
   — **證據：** [題庫:67](/home/phonchi/statlearning-selfstudy/data/questions_zh/ch9.json:67)，與 HTML 第 1476 行「可能有平坦區」矛盾。兩筆 \((x,y)=(-1,-1),(1,1)\)，所有 \(C\ge0.5\) 都可得到相同硬邊界解及零總 slack。  
   — **建議修法：** 刪除「一一」，改成「透過最佳解與預算限制的乘子建立對應，可能有平坦區」。同題把「預算大可能無解」直接判錯的回饋，也應依第 1 項區分可行性與有限最佳解。

7. **[中] 詞彙卡「ε-不敏感損失」：「只有…管子外的點才計入損失，也才會成為支持向量」**  
   — **問題：** 管邊界的零損失點也可能是支持向量。  
   — **證據：** [詞彙卡:148](/home/phonchi/statlearning-selfstudy/data/flashcards_zh/ch9.json:148)，與 HTML 第 2147–2150 行的自由乘子、截距公式矛盾；`sources/htlin-206-svr.md`「SVR dual 與稀疏性」明列支持向量可在管邊界或管外。  
   — **建議修法：** 改成「只有管外點產生正損失；管邊界也可能是支持向量，嚴格管內點的乘子才必為零」。HTML 內嵌卡片也須同步更新。

8. **[中] `vslogit`／`w10-detail-model-comparison`：「邏輯斯迴歸（加 ridge 懲罰）」在可分時「不如 SVM」**  
   — **問題：** 把經驗傾向寫成必然優劣，並用未懲罰 LR 的 MLE 發散解釋已加 ridge 的比較對象，論據不適用。  
   — **證據：** [HTML:2018](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:2018)、第 2021–2024、2034 行。講義 p.31 確有簡寫，但 ISLP §9.5，**書頁 385／PDF 第 392 頁**使用的是傾向性敘述。  
   — **建議修法：** 改成「類別分得很開時，SVC 常有良好表現；與適當正則化 LR 的優劣仍需驗證」。MLE 不存在明確限定為未懲罰 LR。

9. **[中] `w10-soft-three-forms`：「同一個問題的三種寫法」及逐步代數變換**  
   — **問題：** 正文保留三套完整最佳化式與推導，接著收合再講一次，不符合本次「正文 2–4 句直覺，推導與定義放收合」的定案。  
   — **證據：** [HTML:1137](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1137) 至 1166 行在 `<details>` 外；1186 行起再次證明。`consult/audit.md:12` 記錄原規則，但第 20 行又自行要求公式全部提回正文，規格本身矛盾。  
   — **建議修法：** 正文只留縮放、邊界與 slack 的直覺；公式與變換集中進既有收合。`maxmargin`、`soft` 的正式最佳化定義亦須按同一規則整理。

10. **[中] `w10-why-svm`／`w10-detail-why-svm`：「比較對象是 KNN」「只有和 KNN 這類…才是省」**  
    — **問題：** 把補充解讀寫成來源指定的比較對象，且放入正文；「只有」也過度排他。通常使用全部訓練點的核嶺迴歸、核邏輯斯迴歸，同樣是合理比較對象。  
    — **證據：** [HTML:779](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:779)、第 793 行；`sources/sklearn-svm.md:15` 明載原文沒有指定比較對象，講義 p.4 也沒有。  
    — **建議修法：** 正文保留「決策函數只用支持向量」；比較移入收合，標明「例如與 KNN 或通常使用全部訓練點的核模型相比」，避免「只有」。

11. **[中] `w10-detail-mercer`：「拿掉連續性，展開式就不再一致收斂」**  
    — **問題：** 把「不再保證」寫成「必定不成立」，沿用了來源的過強措辭。  
    — **證據：** [HTML:1818](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1818)、`sources/wiki-mercer.md:25`。反例：不連續函數 \(g\) 所構成的 \(K(s,t)=g(s)g(t)\) 是 rank-one 半正定核，只有一個非零展開項，仍然一致收斂。  
    — **建議修法：** 改成「拿掉連續性後，不能再由此保證一致收斂；適當條件下仍可有 \(L^2\) 收斂」。

12. **[輕] 詞彙卡「法向量」：「\(f(x)\) 的值除以 \(\|\beta\|\)…就是垂直距離」**  
    — **問題：** 漏掉絕對值，與正文及純量投影卡矛盾。  
    — **證據：** [詞彙卡:8](/home/phonchi/statlearning-selfstudy/data/flashcards_zh/ch9.json:8)；HTML 第 834–840 行已正確區分。  
    — **建議修法：** 改成「\(f(x)/\|\beta\|\) 是帶號距離，其絕對值才是垂直距離」。

13. **[輕] `w10-detail-affine`及仿射子空間卡：「不一定含原點，所以對加法不封閉」**  
    — **問題：** 「不一定」不能推出「必定不封閉」；過原點的仿射子空間就是線性子空間。  
    — **證據：** [HTML:819](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:819)、詞彙卡第 120 行。  
    — **建議修法：** 改成「一般不要求對加法與純量乘法封閉；若不含原點，便不具這兩種封閉性」。

14. **[輕] `w10-proof-three-forms`：「兩邊同乘 \(\|\beta\|/M\)」**  
    — **問題：** 操作文字與下一行公式不符；下一行實際是原限制除以 \(M\)。  
    — **證據：** [HTML:1192](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:1192)。  
    — **建議修法：** 改成「兩邊同除以 \(M\)」；顯示公式本身正確。

15. **[輕] `w10-detail-svr`：「誤差小時它與平方損失相近」**  
    — **問題：** 雖忠於林軒田原講義，但容易讓學生誤認為具有平方損失的局部曲率。ε-不敏感損失在管內恆為零、管外線性增加。  
    — **證據：** [HTML:2135](/home/phonchi/statlearning-selfstudy/support_vector_machines.html:2135)、`sources/htlin-206-svr.md`「Tube／ε-insensitive loss」，以及[原講義投影片 9/23](https://www.csie.ntu.edu.tw/~htlin/mooc/doc/206_handout.pdf)。  
    — **建議修法：** 改成「小殘差時兩者損失都小，但形狀不同：管內零損失、管外線性增加」。

學生問題逐題核對結果：原檔有 **30 個 USER 區塊，其中 msg01 是系統替代文字，實際有 29 個提問**。沒有發現整題完全漏答；覆蓋與待修處如下，編號沿用原檔。

| USER msg | 提問主題 | 頁面位置與判定 |
|---|---|---|
| 00、03、05 | 高維、dual、效率比較 | `w10-detail-why-svm`／`hard-dual`；已答，比較來源見第 10 項 |
| 01 | 系統替代文字 | 非問題 |
| 07、09、11、13 | 仿射、flat、線性子空間 | `w10-detail-affine`；已答，封閉性見第 13 項 |
| 15 | 純量與向量投影 | `w10-detail-distance`；正文正確，詞卡見第 12 項 |
| 17、19、21、23、25、27 | 三式、係數、間隔與 slack | `w10-detail-three-forms`；已答，條件及尺度見第 1、2、14 項 |
| 29 | 三式與 primal／dual | `hard-dual`／`soft-dual`；已答 |
| 31、33 | dual 負號、乘子非負 | `w10-detail-hard-dual`；確認無誤 |
| 35 | \(C\) 是否為乘子 | `w10-soft-c-multiplier`；正文正確，題庫見第 6 項 |
| 37、39 | 線性邊界不適合、預算夠大 | `w10-soft-feasible`；可行與最佳解混淆，見第 1 項 |
| 41、43 | 核化其他方法、normal equation | `w10-detail-kernel-beyond`；已答，見第 3、4 項 |
| 45 | 以 \(XX^T\) 做 PCA | 同上；非零特徵值對的推導正確 |
| 47 | Mercer 定理 | `w10-detail-mercer`；已答，見第 11 項 |
| 49、51 | RBF 無窮維、γ | `w10-proof-kernels`／`detail-gamma`；核心公式正確 |
| 54、56 | hinge、logistic、L2 | `loss-normalization`／`l2-logistic`；換算與區分正確 |
| 58 | SVC 能否做迴歸 | `w10-detail-svr`；區分正確，詞卡見第 7 項 |

驗證限制：來源轉述主要對照 repo 筆記與原文摘錄，並非所有外部連結都重新抓取。作者的 `verify_svm.py` 在匯入 SciPy 時因唯讀環境沒有可用暫存目錄而失敗，**不列為通過**；上述反例另以代數及不寫檔的 NumPy 核算確認。頁內錨點檢查是靜態解析，未進行瀏覽器互動驗收。

**確認無誤的部分：** 已核對硬／軟邊界的 Lagrangian、dual 符號、完整 KKT、自由支持向量截距與無自由支持向量時的區間處理；hinge 總和／平均的 \(\lambda=1/(2C)\)、\(1/(2nC)\)；總 hinge 隨 \(C\) 不增的證明；二次核映射、RBF 展開、Gram 半正定、dual PCA 非零特徵對、SVR primal／dual、隨機 Fourier 特徵與單類別 SVM 公式。Platt、LinearSVC 差異及 OVO／`ovr` 輸出區分與 [scikit-learn 官方文件](https://scikit-learn.org/1.6/modules/svm.html)一致。指定講義頁均已有對應內容，未見整個主題遺漏；附錄的 Gaussian 分類與感知器更新錯誤有修正，未冒稱讀過 Medium。37 張詞卡、6 題題庫可解析，頁內連結無缺漏、無重複 id。