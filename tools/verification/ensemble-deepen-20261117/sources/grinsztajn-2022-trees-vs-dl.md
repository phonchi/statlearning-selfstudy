# Why do tree-based models still outperform deep learning on tabular data?（Grinsztajn, Oyallon, Varoquaux 2022）
- URL: https://arxiv.org/pdf/2207.08815.pdf
- 講義頁: p.62
- 抓取狀態: OK（arXiv v1，2022-07-18，PDF 經 pdftotext 抽取。圖表數值無法從文字取得，只引用正文敘述）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **主結論**：在中型資料（約 10K 樣本）上，即使不考慮速度優勢，樹模型仍是 state-of-the-art。原文："tree-based models remain state-of-the-art on medium-sized data (∼10K samples) even without accounting for their superior speed."（Abstract；PDF 原印為 "treebased"）
- **基準設定**：
  - 45 個資料集。
  - 每個學習器約 20,000 compute hours 的超參數隨機搜尋。
  - 樹模型：sklearn RandomForest、GradientBoostingTrees（有類別特徵時改用 HistGradientBoosting）、XGBoost。
  - 深度模型：MLP、Resnet、FT-Transformer、SAINT。（§4.1）
- **資料篩選與「排除的子問題」**（§3）：
  - 移除特徵少於 4 個或樣本少於 3,000 的資料集。
  - 移除「太容易」的資料集：線性模型與預設 Resnet、預設 HistGradientBoosting 的分數差距都在 5% 以內者。
  - 移除 target 為確定性函數的資料集（如棋類）。
  - 訓練集截到 10,000 筆。
  - 移除缺失值。
  - 分類任務二元化並平衡類別。
  - 移除超過 20 個類別的類別特徵。
  - 移除少於 10 個不同值的數值特徵。
- **三個發現（§5）**。以下分析僅限數值特徵、分類任務、中型資料。原文："we restrict our analysis to numerical variables and classification tasks on medium-sized datasets."（§5.1）
  1. **Finding 1：NN 偏好過度平滑的解。** 作法是用 Gaussian kernel 平滑訓練集的 target。lengthscale 小時，平滑會明顯降低樹模型的準確率，對 NN 幾乎沒有影響，表示資料的目標函數並不平滑，而 NN 不擅長擬合不規則的函數。原文："NNs struggle to fit these irregular functions compared to tree-based models."（§5.2）作者也提到樹模型 "learn piece-wise constant functions"，沒有這種偏誤。
  2. **Finding 2：無資訊特徵對 MLP 類 NN 影響較大。** 依 RF 特徵重要度移除特徵，GBT 在移除到一半特徵前幾乎不受影響；只用「被移除的特徵」訓練的 GBT 準確率很低，表示這些特徵多半是無資訊，而不只是冗餘。移除無資訊特徵會縮小 MLP（Resnet）與其他模型的差距，加入則擴大差距。原文："This shows that MLPs are less robust to uninformative features"（§5.3）
  3. **Finding 3：資料不具旋轉不變性，學習程序也不該具有。** MLP 的學習程序具旋轉不變性（Ng 2004）。這類程序在最壞情況下，樣本複雜度至少隨無關特徵數線性成長。實驗中對資料做隨機旋轉後，只有 Resnet 不受影響，而且效能排序反轉，NN 反而勝過樹模型。原文："random rotations reverse the performance order"（§5.4）
- **給 tabular NN 研究者的三個挑戰**（Abstract）：原文 "1. be robust to uninformative features, 2. preserve the orientation of the data, and 3. be able to easily learn irregular functions."
- **大型資料（附錄 A.2.2，訓練集 50,000 筆）**：資料集較少，比較不夠明確，但原文 "in most cases, increasing the train set size reduces the gap between neural networks and tree-based models."

## 可用的算例或圖解想法
- **階梯函數 vs 平滑函數**：一維目標 $f(x)=\mathbb 1\{x>0.5\}+\mathbb 1\{x>0.8\}$。單棵樹用 2 次分裂就能完全擬合；小型 MLP 會把跳躍處抹平。這直接呼應 Finding 1，以及「決策樹是階梯函數」。（推論，論文 A.4 有類似的例子，但本次未讀附錄圖。）
- **旋轉實驗的教學版**：取兩個特徵、一個有用一個是雜訊，旋轉 45° 後有用的訊號被混進兩軸。軸對齊的樹需要很多分裂才能逼近斜邊界。（推論）
- **無資訊特徵**：把 RF 的 $m\approx\sqrt p$ 與「雜訊特徵多」連結。若每次只抽少數特徵而雜訊特徵很多，可能常抽不到好特徵；但樹在選分裂時會自動忽略無用特徵。（推論，論文未討論 $m$。）

## 與下列問題的關聯（只寫有關的）
- **決策樹與階梯函數**：論文明說樹模型 "learn piece-wise constant functions"，並以此解釋它對不規則目標函數的優勢。
- **base learner 怎麼選**：論文指出表格資料上最好的方法有兩個共同點：都是 ensemble（bagging 或 boosting），且 weak learner 都是決策樹。關鍵在「樹」本身。原文："The decisive point seems to be the tree aspect"（§5.1）
- **random subspace／特徵選擇**：Finding 2 與 3 支持「逐特徵（軸對齊）處理」對表格資料有利。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **沒有評測 LightGBM 與 CatBoost**：樹模型只有 RF、sklearn GBT／HistGBT 與 XGBoost。講義若寫「GBDT（含 LightGBM／CatBoost）勝過 DL」，屬於外推。
- **適用範圍有限**：結論限於中型（約 10K）、無缺失、低基數類別（≤ 20）、平衡分類的設定，§5 的機制分析更只做數值特徵與分類任務。附錄也指出資料越大差距越小。
- 本次讀的是 2022-07 的 arXiv v1，未查證正式發表版本。之後的表格深度學習進展不在本文範圍，引用時應註明年份。
