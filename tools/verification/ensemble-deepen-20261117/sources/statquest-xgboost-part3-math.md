# XGBoost Part 3 (of 4): Mathematical Details（StatQuest with Josh Starmer）
- URL: https://www.youtube.com/watch?v=ZVFeW798-2I
- 講義頁: p.53
- 抓取狀態: OK（YouTube 自動字幕 `auto`，英文；只有語音。**畫面上的公式與符號排版未擷取**，以下 LaTeX 是依口述重建，不是影片畫面上的式子。影片 27:24，上傳 2020-02-10）
- 讀取日期: 2026-11-17
- 原始逐字稿：`~/.local/share/youtube-read/ZVFeW798-2I/transcript.md`

## 重點（以中文撰寫，術語保留原文）
- 本片推導 similarity score 與 output value 的方程式，並說迴歸與分類唯一差異是 loss function。["the only difference between regression and classification is the loss function"]（[00:58]）
- **初始預測**：迴歸與分類都從「通常是 0.5」的初始預測開始。["XG Boost starts with an initial prediction that is usually 0.5"]（[01:55]）
- **符號**：口述「Y sub I」是觀測值，「P sub I」是對應的預測。["P sub I stands for a prediction"]（[02:23]–[02:51]）。分類時 $y_i\in\{0,1\}$，$p_i$ 是介於 0 與 1 的預測值（[03:49]–[04:18]）。
- **初始預測的符號**：口述為「the initial prediction P of zero」，並把 $p_i$ 換成「$p^0$ + 新樹輸出」。["we can replace the prediction piece of I with the initial prediction P of zero plus the output value"]（[06:13]）。字幕只聽得到「P of zero」（推測畫面為 $p_i^0$ 或 $p^0$），**確切排版未驗證**。
- 迴歸 loss：$L(y_i,p_i)=\tfrac12(y_i-p_i)^2$；分類 loss：negative log likelihood（[02:23]、[03:49]）。
- **目標函數**（依口述重建）：
  $$\sum_{i=1}^n L\big(y_i,\,p_i^0+O_{\text{value}}\big)+\tfrac12\lambda O_{\text{value}}^2$$
  第二項是「像 ridge regression」的正則化；1/2 只是讓數學變簡單。["we square the output value from the new tree and scale it with lambda"]（[05:44]–[06:13]）
- **γT 被省略**：原論文有 $\gamma T$（T 為葉數），作者省略它，因為剪枝在整棵樹建好後才做，不影響最佳 output value 與 similarity 的推導。["This term, gamma * t, where t is the number of terminal nodes"]（[04:47]–[05:16]）
- **λ 的直覺**：λ 越大，拋物線最低點越靠近 0，即 output value 被縮向 0。["the optimal output value gets closer to zero"]（[09:36]–[10:04]）
- 一般（unextreme）gradient boost 對迴歸直接解、對分類用二階 Taylor；XGBoost 對**兩者都**用二階 Taylor 近似。["XGBoost uses a second-order Taylor approximation for both regression and classification"]（[11:03]）
- **g 與 Hessian 命名**：一階導數與 gradient 有關，記為 g；二階導數與 Hessian 有關，記為 h。["XGBoost uses H to represent the second derivative of the loss function"]（[12:01]）
- 不含 output value 的項為常數，可省略；整理後對 output value 微分令為 0（[12:57]–[14:23]）。依口述重建：
  $$\Big(\sum g_i\Big)O+\tfrac12\Big(\sum h_i+\lambda\Big)O^2\;\Rightarrow\;O^*=\frac{-\sum g_i}{\sum h_i+\lambda}$$
  ["We have finally solved for the optimal output value for the leaf"]（[14:23]）
- **迴歸**：$g_i=-(y_i-p_i)$（負殘差），$h_i=1$，故 $O^*=\sum r_i/(n+\lambda)$。["G sub I is the negative residual"]（[15:19]）；["is the number one"]（[15:46]–[16:14]）
- **分類**：$g_i$ 仍是負殘差，分子為殘差和；分母 $\sum p_i(1-p_i)+\lambda$，其中 $p_i$ 是「先前預測的機率」而非先前的 log-odds。["we're using previous probability to specify the previously predicted probability rather than the previously predicted log odds"]（[19:04]）
- **log-odds**：分類 loss 的導數之所以費工，是因為 output value 是以 log-odds 為單位；推導細節在 Gradient Boost Part 4。["the output values are in terms of the log odds"]（[17:39]）
- **Similarity score 的來源**：把省略常數後的二次式乘以 −1，拋物線最高點的 y 座標就是（論文版）similarity score；實作版是它的兩倍。["the similarity score used in the implementations is actually two times that number"]（[21:27]–[21:56]）
  $$\text{論文版}=\tfrac12\frac{(\sum g_i)^2}{\sum h_i+\lambda},\qquad \text{實作版}=\frac{(\sum g_i)^2}{\sum h_i+\lambda}$$
  實作省略 1/2 是因為 similarity 只是相對量，同倍縮放不影響比較。["this 1/2 is omitted because the similarity score is only a relative measure"]（[22:54]）
- 迴歸 similarity：$(\sum r_i)^2/(n+\lambda)$（[23:50]）；分類 similarity：$(\sum r_i)^2/(\sum p_i(1-p_i)+\lambda)$（[24:24]–[24:54]）。
- **Cover**：cover 與葉中最少殘差數有關，等於 similarity 分母減 λ，即 Hessian 和；迴歸 cover = 葉中殘差數，分類 cover = $\sum p_i(1-p_i)$。["cover is the sum of the Hessians, the H sub i's"]（[25:07]–[26:03]）
- 描述欄來源：XGBoost 原論文（arXiv 1603.02754）、Tianqi Chen 的 BoostedTree 投影片、XGBoost 文件。

## 可用的算例或圖解想法
影片的例子（口述）：迴歸用 3 個觀測值、初始預測 0.5。
- Output value = 0 → 總 loss 104.4；= −1 → 109.4；= +1 → 102.4（[03:19]、[08:11]、[09:08]）。
- λ = 4、λ = 40 時拋物線最低點越來越靠近 0（[09:36]–[10:04]），**影片未口述這兩種情況的最佳值**。

自行核算（推論）：
- 由 104.4、109.4、102.4 可解出 $\sum r_i^2 \approx 208.8$、$\sum r_i = 3.5$。殘差 {−10.5, 6.5, 7.5}（即 Part 1 四點中的前三點）完全吻合：104.375 / 109.375 / 102.375。**影片字幕從未說出這三個殘差**，這是推論。
- 最佳 output value $=3.5/(3+\lambda)$：λ=0 → 1.167；λ=4 → 0.5；λ=40 → 0.081（推論，非影片數字）。
- 論文版 similarity（拋物線頂點高度）於 λ=0 為 $\tfrac12 \cdot 3.5^2/3 = 2.042$，實作版 4.083（推論）。
- 分類的 $h=p(1-p)$：p=0.5 → 0.25（最大），p=0.1 或 0.9 → 0.09（推論，與 Part 4 的權重例一致）。

互動元件想法（推論）：畫 $\sum\tfrac12(r_i-O)^2+\tfrac12\lambda O^2$ 對 O 的拋物線，λ 滑桿讓最低點 $3.5/(3+\lambda)$ 移向 0；再切換「×(−1) 翻轉」顯示頂點高度即 similarity（論文版），並標示實作版為 2 倍。分類版可加 p 滑桿顯示 $h=p(1-p)$。

## 與下列問題的關聯（只寫有關的）
- **XGBoost 葉輸出與 p、p₀、log-odds 的關係**：影片把新預測寫成 $p_i^0+O$（[06:13]），分類時 output 以 log-odds 為單位（[17:39]），分母用的是「先前預測機率」$p_i$（[19:04]）。推論：分類時「$p^0+O$」只有在 log-odds 空間才是字面相加，即 $\operatorname{logit}(p_i^{\text{new}})=\operatorname{logit}(p_i^0)+\eta O$；初始 0.5 對應 log-odds 0。影片字幕沒有明說這一步，教學時應補上。
- **λ 的直覺**：像 ridge，把 output 縮向 0（[05:44]、[09:36]–[10:04]）。
- **gradient 與殘差**：兩種 loss 下 $g_i$ 都是負殘差（[15:19]、[18:35]）。推論：分類時這裡的殘差是 $y_i-p_i$（機率尺度），導數對 log-odds 取。
- **分類時 h = p(1−p)**：[19:04]、[24:24]、[25:36]。
- **為何以 Hessian 當權重／min_child_weight**：本片只說 cover = Hessian 和、與「葉中最少殘差數」有關（[25:07]），**未提到 `min_child_weight` 這個參數名**。
- **梯度提升為何對每片葉取 argmin**：本片明確以「找使 loss + 正則化最小的 output value」為目標（[05:44]、[26:03]）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 口述在迴歸段說導數「with respect to the predicted value, p sub i」（[15:19]），分類段則說導數是對 log-odds 取、分母卻用機率表示（[17:39]–[19:04]）。同一個符號 $p_i$ 在兩處尺度不同，學生容易混淆（推論）。
- 初始預測「usually 0.5」是 2020 年版本的說法；新版 `base_score` 行為需以官方文件核對（未查證）。
- 分類的「negative log likelihood」式子只在畫面上，字幕無公式，無法逐字核對。
- 影片沒有分類 output value 的數值例；數值例在 XGBoost Part 2（8b1JEDvenQU，未指派、未讀）。
- 自動字幕品質良好，但「P of zero」等符號口述無法確定畫面排版。
