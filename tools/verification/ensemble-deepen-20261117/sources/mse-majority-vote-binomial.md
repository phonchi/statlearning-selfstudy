# How did you get 75% and 97% with which formula?（Mathematics Stack Exchange Q4363939）
- URL: https://math.stackexchange.com/questions/4363939/how-did-you-get-75-and-97-with-which-formula
- 講義頁: p.31
- 抓取狀態: 部分（網頁本身 HTTP 403 擋爬；問題與 2 則回答全文改由官方 Stack Exchange API `api.stackexchange.com/2.3/questions/4363939[/answers]?site=math&filter=withbody` 取得；無留言。問題已被關閉，closed_reason = "Not suitable for this site"，score −1）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 問題引用 *Hands-on Machine Learning*（Géron）的偏硬幣例：正面機率 51%，丟 1,000 次「majority of heads」機率接近 75%，10,000 次超過 97%；提問者問如何算出。原句："the probability of obtaining a majority of heads after 1,000 tosses is close to 75%"（問題本文）。
- 回答 1（Atmos，score 1，未採納）：令 $X\sim\text{Bin}(n,p)$、$p=0.51$，$P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}$；對偶數 $n$ 取 $P(X\ge n/2)=\sum_{k=n/2}^{n}P(X=k)$，$n=1000$ 得 $0.745\approx75\%$；$n=10000$「my calculator won't do it」，未算出。
- 回答 2（Golden_Ratio，score 1，**已採納**）：以 CLT 常態近似，$\dfrac{X-Np}{\sqrt{Np(1-p)}}$ 近似標準常態，
  $$P(X\ge N/2)\approx 1-\Phi\!\left(\frac{\sqrt N\,(1/2-p)}{\sqrt{p(1-p)}}\right),$$
  得 1,000 次約 0.74、10,000 次約 0.98。原句："This approximation gives about 0.74 for 1,000 tosses"。
- 兩則回答都只回答「硬幣」的數學，沒有討論把它類比到集成投票時需要的「分類器互相獨立」假設（推論：這是來源缺漏，不是來源說錯）。

## 自行驗算（推論，非來源內容）
以 Python 精確加總二項機率（log-space），$p=0.51$：

| $n$ | $P(X\ge n/2)$（平手算贏） | $P(X>n/2)$（嚴格過半） | CLT 無連續校正 |
|---|---|---|---|
| 1,000 | 0.7468 | 0.7261 | 0.7365 |
| 10,000 | 0.9778 | 0.9767 | 0.9773 |

- 回答 1 寫 0.745，與精確值 0.7468（四捨五入為 0.747）略有出入，且未列出計算過程；它用 $\ge n/2$，把 500:500 平手（機率約 2.1%）算成「多數」。若定義為嚴格過半，1,000 次只有約 72.6%，「close to 75%」較勉強；10,000 次兩種定義都 >97%。
- 回答 2 的 CLT 近似未做連續校正（0.7365），加上校正（以 $n/2+0.5$）後與嚴格過半的精確值 0.7261 一致。

## 可用的算例或圖解想法
- 「1,000 個各 51% 準確、彼此獨立的分類器做 hard voting」= $\text{Bin}(1000,0.51)$ 過半機率。可畫 $P(\text{majority correct})$ 對 $n$ 的曲線（$n$ 取奇數避免平手），疊上 CLT 近似。
- 對比相關情形：加一個共同擾動讓分類器相關，曲線就停在某個上限之下，可連到 ESL (15.1) 的 $\rho\sigma^2$ 項（見 `esl-ch15-rf.md`）。

## 與下列問題的關聯（只寫有關的）
- 硬／軟投票：hard voting 的「群眾智慧」直覺就是這個二項計算；ESL §8.7 p.286 也用 $S_1(x)\sim\text{Bin}(B,1-e)$ 說明，並強調 "the main caveat here is “independent,”"（見 `esl-8-7-bagging.md`）。
- base learner 怎麼選：要「略優於隨機（>50%）」且「彼此不相關」，投票才會放大準確度（推論，依二項計算）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 「majority」的定義（$\ge$ 或 $>$）影響 n=1000 的數字（74.7% vs 72.6%），回答 1 未說明；教學時應選奇數 $n$ 或明說平手規則。
- 原書（Géron）數字成立的前提是各次獨立；類比到分類器時，同一資料訓練的模型高度相關，這個前提通常不成立。兩則回答都沒提到。
- 問題已被 MSE 關閉、score −1；可用來說明計算，但不宜當權威引用，權威出處宜改引 ESL §8.7。
