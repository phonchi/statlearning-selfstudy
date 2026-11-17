# XGBoost Loss function Approximation With Taylor Expansion（Cross Validated Q&A）
- URL: https://stats.stackexchange.com/questions/202858/xgboost-loss-function-approximation-with-taylor-expansion
- 講義頁: p.53
- 抓取狀態: 部分（WebFetch 被擋："unable to fetch from stats.stackexchange.com"；改用官方 Stack Exchange API `api.stackexchange.com/2.3/questions/202858` 與 `/answers?filter=withbody` 取得問題與答案全文，HTTP 200。API 只回 1 個答案，question.answer_count=1；未取得留言）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 問題（Alex R.，2016-03-21，score 43，無 accepted answer）：寫出第 t 輪目標 $\mathcal L^{(t)}=\sum_i\ell(y_i,\hat y_i^{(t-1)}+f_t(\mathbf x_i))+\Omega(f_t)$ 與其二階近似，問：(1) 與完整目標相比失去了什麼高階行為；(2) 若損失有很大的三次成分，近似為何不出問題。原文："What I'm asking for is convincing arguments to demystify why the above approximation works"。
- 唯一答案（Winks，score 97，2016-03-29 發表、2019-03 編輯，未被 accept）的論點：
  1. **傳統 gradient boosting**（引 Wikipedia 版本）：算偽殘差 $r_{im}=-\partial\ell(y_i,H_{m-1}(x_i))/\partial H_{m-1}(x_i)$，以 base learner 擬合，再用 line search 求**單一**乘數 $\gamma=\arg\min_\gamma\sum_i\ell(y_i,H_{m-1}(x_i)+\gamma h_m(x_i))$。
  2. 用 MSE 迴歸樹擬合殘差只是代理目標。原文："you are not directly minimizing what you want, but using the residuals and the MSE as a proxy"。
  3. 類比：gradient boosting ↔ gradient descent；XGBoost ↔ Newton 法。原文："XGBoost is to Gradient Boosting what Newton's Method is to Gradient Descent."
  4. Taylor 展開只在小步長附近準確；learning rate（如 0.1、0.01）把每步縮小，正好讓近似適用。原文："approximation works very well if you want to compute the value of f in the neighbourhood of x"。
  5. 計算上的理由：同一輪中 $\ell(y_i,\hat y_i^{(t-1)})$、$g_i$、$h_i$ 都是常數，評估每個候選分裂只需加總與少量乘法。原文："most of the expression can be computed once, and reused as constant for all splits"。
  6. 結論：二階近似比 naive gradient boosting 的一階近似更準；高階資訊未用，但因只需起點附近的好近似而不必要。

## 可用的算例或圖解想法
- 「GD vs Newton」並列圖：一維凸損失上，一階切線 vs 二階拋物線近似，Newton 一步跳到拋物線最低點（推論：可畫 logistic loss 對 F 的曲線，於 $F_0=0$ 處比較）。
- 把答案第 5 點做成表：哪些量每輪只算一次（$g_i,h_i$）、哪些每個候選分裂要重算（$G_L,H_L,G_R,H_R$ 的加總）。

## 與下列問題的關聯
- 為何以 Hessian 當權重／gradient 與殘差：答案把 $g_i,h_i$ 定位為 Newton 步的一階、二階資訊。
- 梯度提升為何對每片葉取 argmin：答案描述的「傳統 GB」用**單一** γ 乘數，與 ESL 演算法 10.3 的**每片葉各自** $\gamma_{jm}$ 不同（Friedman 2001 原文本批未取得）（見 `esl-ch10-boosting.md` p.359、p.361）；教學時應以 ESL 版本為準。
- learning rate 與近似有效性：答案第 4 點。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 問題的近似式有筆誤（寫成 $g_tf_t(\mathbf x_i)$，應為 $g_i$），且求和沒有加括號。
- 答案說 Newton 更新"should point more precisely towards the x such that f(x)=0"——混淆了求根與求極小；最小化時 Newton 找的是 $f'(x)=0$（推論）。答案後面加註「或極小點」，但敘述不精確。
- 答案寫 Newton 更新為 $x-\nabla f/\mathrm{Hess}f$（純量除法寫法），多維時應為 $\mathrm{Hess}^{-1}\nabla f$（推論）。
- 答案中 AdaBoost 的 $h_m=\arg\max\sum_i w_ih_m(x_i)$、"$w_i$ are the residuals" 是引自外部投影片的鬆散說法，與 ESL §10.4（最小化加權誤分率 10.10）的表述不同，不宜直接引用。
- "If you drop a continuous feature, the number of splits explode" 語意不通，應是「加入連續特徵」（推論）。
- 答案未回答問題 (2)「大三次項」的具體情形，只以小步長論證帶過。
- 2016 年的答案；未涉及之後的 hist 方法等實作細節。
