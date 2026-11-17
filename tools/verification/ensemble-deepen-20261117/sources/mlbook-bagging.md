# Bagging — Machine Learning from Scratch（Danny Friedman, §6.1 Tree Ensemble Methods）
- URL: https://dafriedman97.github.io/mlbook/content/c6/s1/bagging.html
- 講義頁: p.32
- 抓取狀態: OK（curl 取得靜態 HTML，HTTP 200；頁面無程式碼，只有文字與 LaTeX）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 定義：bagging 是 bootstrap aggregating，「combines the results of several learners trained on bootstrapped samples」（頁首段）。
- Bootstrap 原本用途是**估計**估計量的變異：對 $b=1,\dots,B$ 從 $\mathcal D$（大小 $N$）有放回抽 $N$ 筆得 $\mathcal D^*_b$，算 $\hat\theta^*_b=f(\mathcal D^*_b)$，再取 $\{\hat\theta^*_1,\dots,\hat\theta^*_B\}$ 的樣本變異數當 $\widehat{\operatorname{Var}}(\hat\theta)$（"Bootstrap Procedure" 小節）。
- 轉折句："Bagging uses the bootstrap to reduce—rather than estimate—the variance of a model."（Bootstrapping 節末）
- Bagging 程序（"Bagging for Decision Trees" 小節）：(1) 對每個 $b$ 抽 bootstrap 樣本 $\mathcal D^*_b$，對它建一棵決策樹 $T^*_b$；(2) 對每個測試點 $t$ 取各樹預測 $\hat y^*_{tb}$，合併為 $\hat y_t$。作者註明 "though the approach works for other learners"。
- 合併方式：連續目標取平均；類別目標取 "the class that receives the plurality vote"。

## 可用的算例或圖解想法
- 頁面把「bootstrap 估變異」與「bagging 降變異」放在同一個程序骨架下，適合做成兩欄對照圖：左欄 $\hat\theta^*_b\to$ 取變異數；右欄 $\hat f^*_b(x)\to$ 取平均。

## 與下列問題的關聯（只寫有關的）
- base learner 怎麼選：此頁只說流程以決策樹示範、也可用於其他 learner，沒有討論為何選高變異 learner（這部分應引 ESL §15.1／ISLP §8.2.1）。
- 硬／軟投票：分類用 plurality vote（即 hard voting）；頁面沒有提到平均機率（soft）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 結尾 "the bootstrap provides our model with more training samples in order to improve its estimates" 容易誤導：bootstrap 不會增加資訊或新樣本，每個 bootstrap 樣本約只含 63.2% 的不同觀測。ESL §15.2 與 ISLP §8.2.1 都把 bagging 的效果歸因於**降變異**（推論：教學時不要沿用「更多訓練樣本」的說法）。
- 頁面沒提 OOB、沒提 $B$ 增加不會過擬合、沒提 bagging 對線性估計量無效；需以課本補足。
