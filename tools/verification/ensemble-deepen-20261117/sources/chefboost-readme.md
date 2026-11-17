# ChefBoost（serengil/chefboost GitHub README）
- URL: https://github.com/serengil/chefboost
- 講義頁: p.80
- 抓取狀態: OK（從 raw.githubusercontent.com 取得 master 分支的 README.md）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- **定位**：原文 "ChefBoost is a lightweight decision tree framework for Python with categorical feature support."
- **支援的演算法**（README 的 "Regular Decision Trees" 表）：

| Algorithm | Metric |
|---|---|
| ID3 | Entropy, Information Gain |
| C4.5 | Entropy, Gain Ratio |
| CART | GINI |
| CHAID | Chi Square |
| Regression | Standard Deviation |

- **進階方法**：gradient boosting、random forest、adaboost。設定方式分別為 `{'enableGBM': True, 'epochs': 7, 'learning_rate': 1, 'max_depth': 5}`、`{'enableRandomForest': True, 'num_of_trees': 5}`、`{'enableAdaboost': True, 'num_of_weak_classifier': 4}`。
- **不需前處理**：原文 "Chefboost handles the both numeric and nominal features and target values in contrast to its alternatives."
- **輸出**：建好的樹以 Python if 敘述存在 `outputs/rules/`，可以直接讀成規則。README 附了 golf 資料（Outlook／Wind／Humidity）的範例規則。
- **AdaBoost 用 decision stump**：原文 "Adaboost applies a decision stump instead of a decision tree."
- **特徵重要度**：`chef.feature_importance("outputs/rules/rules.py")`，範例中 Humidity 0.3688、Wind 0.3688、Outlook 0.2624、Temperature 0。
- **平行化**：預設開啟（`enableParallelism=True`），各分支平行建立，使用一半的核心數。
- **引用**：Serengil (2021), Zenodo DOI 10.5281/zenodo.5576203；授權 MIT。

## 可用的算例或圖解想法
- 同一份 golf 資料分別用 ID3、C4.5、CART、CHAID 建樹並比較規則差異，搭配 `wikipedia-id3.md` 與 `sklearn-tree-algorithms.md` 的演算法描述。
- 規則輸出成 if-else，可以讓學生看見「樹就是巢狀的 if」。

## 與下列問題的關聯（只寫有關的）
- **base learner 怎麼選**：ChefBoost 讓同一框架可以換 ID3、C4.5、CART、CHAID 當基學習器，AdaBoost 則固定用 stump（高偏差、低變異的弱學習器）。
- **AdaBoost 權重更新**：README 只有質性描述："It then increases the unclassified ones and decreases the classified ones."，沒有給出 $\alpha$ 公式。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- **Random forest 的描述不精確**：原文 "Random forest basically splits the data set into several sub data sets and builds different data set for those sub data sets."。這沒有提到 bootstrap 抽樣（有放回）與每次分裂的隨機特徵子集；「splits the data set」容易讓人誤以為是不重疊的切分。教學時不要引用這句當作 RF 的定義。
- AdaBoost 說 "aims to get min 50% score" 是口語說法。正確條件是：二元分類時，弱分類器的加權錯誤率要低於 0.5。
- Gradient boosting 的設定範例用 `learning_rate: 1`，與一般建議的小學習率不同，只是示範值。
- 這是個人維護的教學型套件，適合教學示範，不適合當成效能基準。（推論）
