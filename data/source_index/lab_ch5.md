# Ch05-resample-lab-zh.ipynb — ISLP 第 5 章

> 由 tools/extract_lab.py 產生。頁面上的程式碼與預期輸出一律從這裡逐字抄，
> `.dx-src` 要標注這裡的儲存格編號。不要重跑：輸出是課程環境下的實跑結果。

## 儲存格 0 [md]


# Chapter 5

## 儲存格 1 [md]

<table align="left">
  <td>
    <a href="https://colab.research.google.com/github/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch05-resample-lab-zh.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
  </td>
  <td>
    <a target="_blank" href="https://kaggle.com/kernels/welcome?src=https://github.com/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch05-resample-lab-zh.ipynb"><img src="https://kaggle.com/static/images/open-in-kaggle.svg" /></a>
  </td>
</table>

## 儲存格 2 [code]

```python
%load_ext cudf.pandas
%load_ext cuml.accel
```

## 儲存格 3 [code]

```python
%pip install ISLP
```

**輸出**

```
Collecting ISLP
  Downloading ISLP-0.4.0-py3-none-any.whl.metadata (7.0 kB)
Requirement already satisfied: numpy>=1.7.1 in /usr/local/lib/python3.12/dist-packages (from ISLP) (2.0.2)
Requirement already satisfied: scipy>=0.9 in /usr/local/lib/python3.12/dist-packages (from ISLP) (1.16.2)
Requirement already satisfied: pandas>=0.20 in /usr/local/lib/python3.12/dist-packages (from ISLP) (2.2.2)
Requirement already satisfied: lxml in /usr/local/lib/python3.12/dist-packages (from ISLP) (5.4.0)
Requirement already satisfied: scikit-learn>=1.2 in /usr/local/lib/python3.12/dist-packages (from ISLP) (1.6.1)
Requirement already satisfied: joblib in /usr/local/lib/python3.12/dist-packages (from ISLP) (1.5.2)
Requirement already satisfied: statsmodels>=0.13 in /usr/local/lib/python3.12/dist-packages (from ISLP) (0.14.5)
Collecting lifelines (from ISLP)
  Downloading lifelines-0.30.0-py3-none-any.whl.metadata (3.2 kB)
Collecting pygam (from ISLP)
  Downloading pygam-0.10.1-py3-none-any.whl.metadata (9.7 kB)
Requirement already satisfied: torch in /usr/local/lib/python3.12/dist-packages (from ISLP) (2.8.0+cu126)
Collecting pytorch-lightning (from ISLP)
  Downloading pytorch_lightning-2.5.5-py3-none-any.whl.metadata (20 kB)
Collecting torchmetrics (from ISLP)
  Downloading torchmetrics-1.8.2-py3-none-any.whl.metadata (22 kB)
Requirement already satisfied: python-dateutil>=2.8.2 in /usr/local/lib/python3.12/dist-packages (from pandas>=0.20->ISLP) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /usr/local/lib/python3.12/dist-packages (from pandas>=0.20->ISLP) (2025.2)
Requirement already satisfied: tzdata>=2022.7 in /usr/local/lib/python3.12/dist-packages (from pandas>=0.20->ISLP) (2025.2)
Requirement already satisfied: threadpoolctl>=3.1.0 in /usr/local/lib/python3.12/dist-packages (from scikit-learn>=1.2->ISLP) (3.6.0)
Requirement already satisfied: patsy>=0.5.6 in /usr/local/lib/python3.12/dist-packages (from statsmodels>=0.13->ISLP) (1.0.1)
Requirement already satisfied: packaging>=21.3 in /usr/local/lib/python3.12/dist-packages (from statsmodels>=0.13->ISLP) (25.0)
Requirement already satisfied: matplotlib>=3.0 in /usr/local/lib/python3.12/dist-packages (from lifelines->ISLP) (3.10.0)
Requirement already satisfied: autograd>=1.5 in /usr/local/lib/python3.12/dist-packages (from lifelines->ISLP) (1.8.0)
Collecting autograd-gamma>=0.3 (from lifelines->ISLP)
  Downloading autograd-gamma-0.5.0.tar.gz (4.0 kB)
  Preparing metadata (setup.py) ... [?25l[?25hdone
Collecting formulaic>=0.2.2 (from lifelines->ISLP)
  Downloading formulaic-1.2.1-py3-none-any.whl.metadata (7.0 kB)
Requirement already satisfied: progressbar2<5,>=4.2.0 in /usr/local/lib/python3.12/dist-packages (from pygam->ISLP) (4.5.0)
Requirement already satisfied: tqdm>=4.57.0 in /usr/local/lib/python3.12/dist-packages (from pytorch-lightning->ISLP) (4.67.1)
Requirement already satisfied: PyYAML>5.4 in /usr/local/lib/python3.12/dist-packages (from pytorch-lightning->ISLP) (6.0.3)
Requirement already satisfied: fsspec>=2022.5.0 in /usr/local/lib/python3.12/dist-packages (from fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (2025.3.0)
Requirement already satisfied: typing-extensions>4.5.0 in /usr/local/lib/python3.12/dist-packages (from pytorch-lightning->ISLP) (4.15.0)
Collecting lightning-utilities>=0.10.0 (from pytorch-lightning->ISLP)
  Downloading lightning_utilities-0.15.2-py3-none-any.whl.metadata (5.7 kB)
Requirement already satisfied: filelock in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (3.19.1)
Requirement already satisfied: setuptools in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (75.2.0)
Requirement already satisfied: sympy>=1.13.3 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (1.13.3)
Requirement already satisfied: networkx in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (3.5)
Requirement already satisfied: jinja2 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (3.1.6)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.6.77 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.77)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.6.77 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.77)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.6.80 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.80)
Requirement already satisfied: nvidia-cudnn-cu12==9.10.2.21 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (9.10.2.21)
Requirement already satisfied: nvidia-cublas-cu12==12.6.4.1 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.4.1)
Requirement already satisfied: nvidia-cufft-cu12==11.3.0.4 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (11.3.0.4)
Requirement already satisfied: nvidia-curand-cu12==10.3.7.77 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (10.3.7.77)
Requirement already satisfied: nvidia-cusolver-cu12==11.7.1.2 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (11.7.1.2)
Requirement already satisfied: nvidia-cusparse-cu12==12.5.4.2 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.5.4.2)
Requirement already satisfied: nvidia-cusparselt-cu12==0.7.1 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (0.7.1)
Requirement already satisfied: nvidia-nccl-cu12==2.27.3 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (2.27.3)
Requirement already satisfied: nvidia-nvtx-cu12==12.6.77 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.77)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.6.85 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (12.6.85)
Requirement already satisfied: nvidia-cufile-cu12==1.11.1.6 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (1.11.1.6)
Requirement already satisfied: triton==3.4.0 in /usr/local/lib/python3.12/dist-packages (from torch->ISLP) (3.4.0)
Collecting interface-meta>=1.2.0 (from formulaic>=0.2.2->lifelines->ISLP)
  Downloading interface_meta-1.3.0-py3-none-any.whl.metadata (6.7 kB)
Requirement already satisfied: narwhals>=1.17 in /usr/local/lib/python3.12/dist-packages (from formulaic>=0.2.2->lifelines->ISLP) (2.6.0)
Requirement already satisfied: wrapt>=1.0 in /usr/local/lib/python3.12/dist-packages (from formulaic>=0.2.2->lifelines->ISLP) (1.17.3)
Requirement already satisfied: aiohttp!=4.0.0a0,!=4.0.0a1 in /usr/local/lib/python3.12/dist-packages (from fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (3.12.15)
Requirement already satisfied: contourpy>=1.0.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (1.3.3)
Requirement already satisfied: cycler>=0.10 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (0.12.1)
Requirement already satisfied: fonttools>=4.22.0 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (4.60.1)
Requirement already satisfied: kiwisolver>=1.3.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (1.4.9)
Requirement already satisfied: pillow>=8 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (11.3.0)
Requirement already satisfied: pyparsing>=2.3.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (3.2.5)
Requirement already satisfied: python-utils>=3.8.1 in /usr/local/lib/python3.12/dist-packages (from progressbar2<5,>=4.2.0->pygam->ISLP) (3.9.1)
Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.12/dist-packages (from python-dateutil>=2.8.2->pandas>=0.20->ISLP) (1.17.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in /usr/local/lib/python3.12/dist-packages (from sympy>=1.13.3->torch->ISLP) (1.3.0)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.12/dist-packages (from jinja2->torch->ISLP) (3.0.3)
Requirement already satisfied: aiohappyeyeballs>=2.5.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (2.6.1)
Requirement already satisfied: aiosignal>=1.4.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.4.0)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (25.3.0)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.7.0)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (6.6.4)
Requirement already satisfied: propcache>=0.2.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (0.3.2)
Requirement already satisfied: yarl<2.0,>=1.17.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.20.1)
Requirement already satisfied: idna>=2.0 in /usr/local/lib/python3.12/dist-packages (from yarl<2.0,>=1.17.0->aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (3.10)
Downloading ISLP-0.4.0-py3-none-any.whl (3.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.6/3.6 MB 61.3 MB/s eta 0:00:00
[?25hDownloading lifelines-0.30.0-py3-none-any.whl (349 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 349.3/349.3 kB 25.7 MB/s eta 0:00:00
[?25hDownloading pygam-0.10.1-py3-none-any.whl (80 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80.2/80.2 kB 6.5 MB/s eta 0:00:00
[?25hDownloading pytorch_lightning-2.5.5-py3-none-any.whl (832 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 832.4/832.4 kB 44.2 MB/s eta 0:00:00
[?25hDownloading torchmetrics-1.8.2-py3-none-any.whl (983 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 983.2/983.2 kB 57.4 MB/s eta 0:00:00
[?25hDownloading formulaic-1.2.1-py3-none-any.whl (117 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 117.3/117.3 kB 9.6 MB/s eta 0:00:00
[?25hDownloading lightning_utilities-0.15.2-py3-none-any.whl (29 kB)
Downloading interface_meta-1.3.0-py3-none-any.whl (14 kB)
Building wheels for collected packages: autograd-gamma
  Building wheel for autograd-gamma (setup.py) ... [?25l[?25hdone
  Created wheel for autograd-gamma: filename=autograd_gamma-0.5.0-py3-none-any.whl size=4030 sha256=cf0c05c4d177d8bcb5daf4b0749af0b304205a9eadf5399ac3c027cffdb31c94
  Stored in directory: /root/.cache/pip/wheels/50/37/21/0a719b9d89c635e89ff24bd93b862882ad675279552013b2fb
Successfully built autograd-gamma
Installing collected packages: lightning-utilities, interface-meta, autograd-gamma, pygam, formulaic, torchmetrics, lifelines, pytorch-lightning, ISLP
Successfully installed ISLP-0.4.0 autograd-gamma-0.5.0 formulaic-1.2.1 interface-meta-1.3.0 lifelines-0.30.0 lightning-utilities-0.15.2 pygam-0.10.1 pytorch-lightning-2.5.5 torchmetrics-1.8.2
```

## 儲存格 4 [code]

```python
# 本 Notebook 使用的匯入（imports）
import numpy as np  # 數值運算與陣列處理
import seaborn as sns  # 統計視覺化
import matplotlib.pyplot as plt  # 繪圖指令與樣式
import statsmodels.api as sm  # 統計模型與推論
from functools import partial  # 偏函式，便於固定部分參數
from tqdm.notebook import trange, tqdm  # 進度條顯示
from ISLP import load_data  # ISLP 資料載入
from ISLP.models import (
    ModelSpec as MS,
    summarize,
    poly,
    sklearn_sm
)  # 模型公式、摘要、多項式與 sklearn-樣式介面
from sklearn import metrics  # 評估指標（MSE、MAE、R^2 等）
from sklearn.base import clone  # 複製估計器以重設狀態
from sklearn.linear_model import LinearRegression  # 線性回歸
from sklearn.model_selection import LeaveOneOut, cross_validate, ShuffleSplit
from sklearn.model_selection import (  # 重抽樣/驗證工具
    KFold, StratifiedKFold, cross_val_score, train_test_split
)
from sklearn.preprocessing import PolynomialFeatures  # 多項式特徵轉換
```

## 儲存格 5 [md]

# Cross-Validation（交叉驗證）與 Bootstrap

## 儲存格 6 [md]

在本實驗中，我們將探索本章涵蓋的重抽樣技術。本實驗的某些指令在我們的電腦上可能需要一些時間執行。

我們再次從頂層放置大部分的 imports 開始。

## 儲存格 7 [md]

我們必須重新啟動執行環境以使用新安裝的版本！

## 儲存格 8 [code]

```python
%matplotlib inline
sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
```

## 儲存格 9 [md]

為了獲得最佳的 cross-validation（交叉驗證）(CV) 結果穩健性，在建立估計器時傳遞 `RandomState` 實例，或將 `random_state` 留為 `None`。將整數傳遞給 CV 分割器通常是最安全的選擇且較為推薦。更多資訊請參見[這裡](https://scikit-learn.org/stable/common_pitfalls.html#robustness-of-cross-validation-results)。

## 儲存格 10 [code]

```python
rng = np.random.RandomState(42)
```

## 儲存格 11 [md]

## Validation Set（驗證集）方法

## 儲存格 12 [md]

我們探索使用 validation set（驗證集）方法來估計在 [`Auto`](https://islp.readthedocs.io/en/latest/datasets/Auto.html) 資料集上擬合各種線性模型所產生的測試錯誤率。

## 儲存格 13 [code]

```python
Auto = load_data('Auto')
print(Auto.shape)
Auto.info()
```

**輸出**

```
(392, 8)
<class 'pandas.core.frame.DataFrame'>
Index: 392 entries, chevrolet chevelle malibu to chevy s-10
Data columns (total 8 columns):
 #   Column        Non-Null Count  Dtype  
---  ------        --------------  -----  
 0   mpg           392 non-null    float64
 1   cylinders     392 non-null    int64  
 2   displacement  392 non-null    float64
 3   horsepower    392 non-null    int64  
 4   weight        392 non-null    int64  
 5   acceleration  392 non-null    float64
 6   year          392 non-null    int64  
 7   origin        392 non-null    int64  
dtypes: float64(3), int64(5)
memory usage: 27.6+ KB
```

## 儲存格 14 [code]

```python
Auto.head()
```

**輸出**

```
                            mpg  cylinders  displacement  horsepower  weight  \
name                                                                           
chevrolet chevelle malibu  18.0          8         307.0         130    3504   
buick skylark 320          15.0          8         350.0         165    3693   
plymouth satellite         18.0          8         318.0         150    3436   
amc rebel sst              16.0          8         304.0         150    3433   
ford torino                17.0          8         302.0         140    3449   

                           acceleration  year  origin  
name                                                   
chevrolet chevelle malibu          12.0    70       1  
buick skylark 320                  11.5    70       1  
plymouth satellite                 11.0    70       1  
amc rebel sst                      12.0    70       1  
ford torino                        10.5    70       1
```

## 儲存格 15 [md]

我們使用函數 `train_test_split()` 將資料切分為訓練集與驗證集。由於有 392 個觀測值，我們使用參數 `test_size=196` 將其切分為兩個大小為 196 的相等集合。在執行包含隨機元素的操作時，設定隨機種子通常是個好主意，這樣獲得的結果可以在日後精確地重現。我們使用參數 `random_state` 為切分器設定隨機種子。

## 儲存格 16 [code]

```python
Auto_train, Auto_valid = train_test_split(Auto,
                                         test_size=196,
                                         random_state=rng)
```

## 儲存格 17 [md]

現在我們可以僅使用對應於訓練集 `Auto_train` 的觀測值來擬合線性回歸。

## 儲存格 18 [code]

```python
hp_mm = MS(['horsepower'])
X_train = hp_mm.fit_transform(Auto_train)
y_train = Auto_train['mpg']
model = sm.OLS(y_train, X_train)
results = model.fit()
```

## 儲存格 19 [md]

現在我們使用 `results` 的 `predict()` 方法在使用驗證資料集創建的此模型的模型矩陣上進行評估。我們也計算我們模型的驗證 MSE。

## 儲存格 20 [code]

```python
X_valid = hp_mm.transform(Auto_valid)
y_valid = Auto_valid['mpg']
valid_pred = results.predict(X_valid)
np.mean((y_valid - valid_pred)**2)
```

**輸出**

```
np.float64(25.57387818968441)
```

## 儲存格 21 [md]

其他指標可以透過 [`scikit-learn.metrics`](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics) 獲得。

## 儲存格 22 [code]

```python
print("The MAE is: {:.5}".format(metrics.mean_absolute_error(y_valid, valid_pred)))  # (True, Predict)
print("The MSE is: {:.5}".format(metrics.mean_squared_error(y_valid, valid_pred)))
print("The RMSE is: {:.5}".format(np.sqrt( metrics.mean_squared_error(y_valid, valid_pred))))
```

**輸出**

```
The MAE is: 3.9907
The MSE is: 25.574
The RMSE is: 5.0571
```

## 儲存格 23 [md]

因此我們對線性回歸擬合的驗證 MSE 估計為 $25.57$。

我們也可以估計高次多項式回歸的驗證錯誤。我們首先提供一個函數 `evalMSE()`，它接受模型字串以及訓練集、測試集，並返回測試集上的 MSE。

## 儲存格 24 [code]

```python
def evalMSE(terms,
            response,
            train,
            test):

   mm = MS(terms)
   X_train = mm.fit_transform(train)
   y_train = train[response]

   X_test = mm.transform(test)
   y_test = test[response]

   results = sm.OLS(y_train, X_train).fit()
   test_pred = results.predict(X_test)

   return np.mean((y_test - test_pred)**2)
```

## 儲存格 25 [md]

讓我們使用此函數估計線性、二次和三次擬合的驗證 MSE。我們在這裡使用 `enumerate()` 函數，它在迭代 for 迴圈時同時提供值和索引物件。

## 儲存格 26 [code]

```python
MSE = np.zeros(3)
for idx, degree in enumerate(range(1, 4)):
    MSE[idx] = evalMSE([poly('horsepower', degree)],
                       'mpg',
                       Auto_train,
                       Auto_valid)
MSE
```

**輸出**

```
array([25.57387819, 22.21802005, 22.66767544])
```

## 儲存格 27 [md]

這些錯誤率分別為 $25.57、22.22$ 和 $22.67$。如果我們選擇不同的訓練/驗證切分，那麼我們可以預期驗證集上會有略微不同的錯誤。

## 儲存格 28 [code]

```python
Auto_train, Auto_valid = train_test_split(Auto,
                                          test_size=196,
                                          random_state=3)
MSE = np.zeros(3)
for idx, degree in enumerate(range(1, 4)):
    MSE[idx] = evalMSE([poly('horsepower', degree)],
                       'mpg',
                       Auto_train,
                       Auto_valid)
MSE
```

**輸出**

```
array([20.75540796, 16.94510676, 16.97437833])
```

## 儲存格 29 [md]

使用這種觀測值切分為訓練集與驗證集的方式，我們發現線性、二次和三次項模型的驗證集錯誤率分別為 $20.76、16.95$ 和 $16.97$。

這些結果與我們之前的發現一致：使用 `horsepower` 的二次函數來預測 `mpg` 的模型，比僅涉及 `horsepower` 線性函數的模型表現更好，並且沒有證據顯示使用 `horsepower` 的三次函數能帶來改善。

## 儲存格 30 [md]

## Cross-Validation（交叉驗證）

## 儲存格 31 [md]

理論上，cross-validation（交叉驗證）估計可以針對任何廣義線性模型進行計算。然而在實務上，在 Python 中進行交叉驗證的最簡單方式是使用 `scikit-learn`，然而它具有與我們一直用來擬合 GLM 的 `statsmodels` 不同的介面或 API!

這是資料科學家經常面臨的問題：「我有一個執行任務 A 的函數，需要將其輸入到執行任務 B 的東西中，這樣我就可以計算 B(A(D))，其中 D 是我的資料。」當 A 和 B 無法自然地相互溝通時，這就需要使用 *wrapper*。
**在 `ISLP` 套件中，我們提供了一個 wrapper，`sklearn_sm()`，讓我們能夠輕鬆地將 `scikit-learn` 的交叉驗證工具與 `statsmodels` 擬合的模型一起使用。**

類別 [`sklearn_sm()`](https://islp.readthedocs.io/en/latest/api/generated/ISLP.models.sklearn_wrap.html#sklearn-sm) 的第一個參數是來自 `statsmodels` 的模型。它可以接受兩個額外的可選參數：`model_str` 可用來指定公式，而 `model_args` 是在擬合模型時使用的額外參數字典。例如，擬合 logistic 回歸模型時，我們必須指定一個 `family` 參數。這會以 `model_args={'family':sm.families.Binomial()}` 的方式傳遞。

以下是我們的 wrapper 實際運作情況：

## 儲存格 32 [code]

```python
hp_model = sklearn_sm(sm.OLS,
                      MS(['horsepower']))
X, Y = Auto.drop(columns=['mpg']), Auto['mpg']



# 交叉驗證迭代器
cv = LeaveOneOut()
cv_results = cross_validate(hp_model,
                            X,
                            Y,
                            cv=cv
                            )
cv_err = np.mean(cv_results['test_score'])
cv_err
```

**輸出**

```
np.float64(24.23151351792922)
```

## 儲存格 33 [md]

我們也可以如下使用來自 `scikit-learn` 的估計器：

## 儲存格 34 [code]

```python
reg = LinearRegression()

# Use MSE as the scoring metric
scoring = metrics.make_scorer(metrics.mean_squared_error)
# Cross validation iterators
cv = LeaveOneOut()
cv_results = cross_validate(reg,
                            X.horsepower.to_numpy().reshape(-1,1),
                            Y.to_numpy(),
                            scoring=scoring,
                            cv=cv
                            )
cv_err = np.mean(cv_results['test_score'])
cv_err
```

**輸出**

```
np.float64(24.231513517929226)
```

## 儲存格 35 [md]

`cross_validate()` 的參數如下：一個具有適當 `fit()`、`predict()` 和 `score()` 方法的物件，一個特徵陣列 `X` 和一個回應變數 `Y`。我們也在 `cross_validate()` 中包含了額外參數 `cv`；指定整數 $K$ 會導致 $K$-fold cross-validation（交叉驗證）。若我們提供了對應總樣本數的值，則會產生**留一法交叉驗證 (LOOCV)**。`cross_validate()` 函數會產生一個包含多個組件的*字典*；我們這裡只需要交叉驗證的測試分數 (MSE)，其估計值為 24.23。

## 儲存格 36 [md]

我們可以對越來越複雜的多項式擬合重複此程序。為了自動化這個過程，我們再次使用 for 迴圈，它會迭代地擬合 1 到 5 次的多項式回歸，計算相關的交叉驗證錯誤，並將其儲存在向量 `cv_error` 的第 $i$ 個元素中。for 迴圈中的變數 `d` 對應多項式的次數。我們從初始化向量開始。此指令可能需要幾秒鐘來執行。

## 儲存格 37 [code]

```python
cv_error = np.zeros(5)
H = np.array(Auto['horsepower'])
M = sklearn_sm(sm.OLS)
cv = LeaveOneOut()


for i, d in enumerate(trange(1,6)):
    X = np.power.outer(H, np.arange(d+1))
    # You can also use the PolynomialFeatures from sklearn
    # poly = PolynomialFeatures(d, include_bias=True) #ModelSpec will add const, here we do not use ModelSpec, so we need to add const
    # X = poly.fit_transform(H.reshape(-1, 1))
    M_CV = cross_validate(M,
                          X,
                          Y,
                          cv=cv)
    cv_error[i] = np.mean(M_CV['test_score'])
cv_error
```

## 儲存格 38 [md]

如圖 5.4 所示，我們看到線性擬合與二次擬合之間的估計測試 MSE 大幅下降，但使用更高次多項式並沒有明顯的改善。

上面我們介紹了 `np.power()` 函數的 `outer()` 方法。`outer()` 方法適用於具有兩個參數的運算，如 `add()`、`min()` 或 `power()`。它以兩個陣列作為參數，然後形成一個更大的陣列，其中運算會應用於兩個陣列元素的每一對。

## 儲存格 39 [code]

```python
A = np.array([3, 5, 9])
B = np.array([2, 4])
np.power.outer(A, B)
```

**輸出**

```
array([[   9,   81],
       [  25,  625],
       [  81, 6561]])
```

## 儲存格 40 [md]

在上面的 CV 範例中，我們使用了 $K=n$，但當然我們也可以使用 $K<n$。程式碼與上面非常相似（而且速度快很多）。這裡我們使用 `KFold()` 將資料分割為 $K=10$ 個隨機群組。我們使用 `random_state` 設定隨機種子，並初始化一個向量 `cv_error`，我們將在其中儲存對應於 1 到 5 次多項式擬合的 CV 錯誤。注意：傳遞整數給 CV 切分器通常更安全且涵蓋大多數使用情況。

## 儲存格 41 [code]

```python
cv_error = np.zeros(5)
cv = KFold(n_splits=10,
           shuffle=True,
           random_state=0) # use same splits for each degree not rng here, see https://scikit-learn.org/stable/common_pitfalls.html#robustness-of-cross-validation-results
for i, d in enumerate(trange(1,6)):
    X = np.power.outer(H, np.arange(d+1))
    M_CV = cross_validate(M,
                          X,
                          Y,
                          cv=cv)
    cv_error[i] = np.mean(M_CV['test_score'])
cv_error
```

## 儲存格 42 [md]

注意計算時間比 LOOCV 短得多。（原則上，對於最小平方線性模型，LOOCV 的計算時間應該比 $K$-fold CV 快，這是由於 LOOCV 有公式 (5.2) 可用；然而，通用的 `cross_validate()` 函數並沒有使用此公式。）我們仍然看不到什麼證據顯示使用三次或更高次的多項式項會比單純使用二次擬合帶來更低的測試錯誤。

## 儲存格 43 [md]

`cross_validate()` 函數很靈活，可以接受不同的切分機制作為參數。例如，使用 `ShuffleSplit()` 函數實作驗證集方法就像 K-fold cross-validation（交叉驗證）一樣容易。

## 儲存格 44 [code]

```python
validation = ShuffleSplit(n_splits=1,
                          test_size=196,
                          random_state=0)
results = cross_validate(hp_model,
                         Auto.drop(['mpg'], axis=1),
                         Auto['mpg'],
                         cv=validation);
results['test_score']
```

**輸出**

```
array([23.61661707])
```

## 儲存格 45 [md]

可以透過執行以下程式碼來估計測試錯誤的變異性：

## 儲存格 46 [code]

```python
validation = ShuffleSplit(n_splits=10,
                          test_size=196,
                          random_state=0)
results = cross_validate(hp_model,
                         Auto.drop(['mpg'], axis=1),
                         Auto['mpg'],
                         cv=validation)
results['test_score'].mean(), results['test_score'].std()
```

**輸出**

```
(np.float64(23.802232661034168), np.float64(1.4218450941091842))
```

## 儲存格 47 [md]

注意：這個標準差並不是平均測試分數或個別分數之抽樣變異性的有效估計，因為隨機選取的訓練樣本會重疊，因此引入了相關性。但它確實能讓我們了解選擇不同隨機分割時所產生的 Monte Carlo 變異。

## 儲存格 48 [md]

有關在 `scikit-learn` 中使用交叉驗證的更多資訊，請參閱 [https://scikit-learn.org/stable/modules/cross_validation.html](https://scikit-learn.org/stable/modules/cross_validation.html)。

## 儲存格 49 [md]

## The Bootstrap

## 儲存格 50 [md]

我們用第 5.2 節的簡單範例以及涉及估計 `Auto` 資料集上線性回歸模型準確率的範例來說明 bootstrap 的使用。

## 儲存格 51 [md]

### 估計感興趣統計量的準確率

## 儲存格 52 [md]

Bootstrap 方法的一個巨大優勢是它幾乎可以應用於所有情況。不需要複雜的數學計算。雖然 Python 中有數個 bootstrap 的實作，但它用於估計標準誤差的使用簡單到我們可以為資料儲存在 dataframe 的情況自己寫一個函數。

為了說明 bootstrap，我們從簡單的範例開始。`ISLP` 套件中的 [`Portfolio`](https://islp.readthedocs.io/en/latest/datasets/Portfolio.html) 資料集在第 5.2 節中有描述。目標是估計公式 (5.7) 中給定的參數 $\alpha$ 的抽樣變異數。我們將建立函數 `alpha_func()`，它接受一個假設有 `X` 和 `Y` 欄位的 dataframe `D` 作為輸入，以及一個指示應該使用哪些觀測值來估計 $\alpha$ 的向量 `idx`。然後該函數根據選取的觀測值輸出 $\alpha$ 的估計。

## 儲存格 53 [code]

```python
Portfolio = load_data('Portfolio')
def alpha_func(D, idx):
   cov_ = np.cov(D[['X','Y']].loc[idx], rowvar=False)
   return ((cov_[1,1] - cov_[0,1]) /
           (cov_[0,0]+cov_[1,1]-2*cov_[0,1]))
```

## 儲存格 54 [md]

此函數根據將最小變異數公式 (5.7) 應用於由參數 `idx` 索引的觀測值，返回 $\alpha$ 的估計。例如，以下指令使用全部 100 個觀測值來估計 $\alpha$。

## 儲存格 55 [code]

```python
alpha_func(Portfolio, range(100))
```

**輸出**

```
np.float64(0.57583207459283)
```

## 儲存格 56 [md]

接下來我們從 `range(100)` 中有放回地隨機選取 100 個觀測值。這等同於建構新的 bootstrap 資料集，並基於新資料集重新計算 $\hat{\alpha}$。

## 儲存格 57 [code]

```python
rng = np.random.default_rng(0)
alpha_func(Portfolio,
           rng.choice(100,
                      100,
                      replace=True))
```

**輸出**

```
np.float64(0.6074452469619004)
```

## 儲存格 58 [md]

此過程可以一般化，建立一個簡單的函數 `boot_SE()` 來計算任意僅以資料框架為參數的函數的 bootstrap 標準誤差。

## 儲存格 59 [code]

```python
def boot_SE(func,
            D,
            n=None,
            B=1000,
            seed=0):
    rng = np.random.default_rng(seed)
    first_, second_ = 0, 0
    n = n or D.shape[0]
    for _ in trange(B):
        idx = rng.choice(D.index,
                         n,
                         replace=True)
        value = func(D, idx)
        first_ += value
        second_ += value**2
    return np.sqrt(second_ / B - (first_ / B)**2)
```

## 儲存格 60 [md]

注意在 `for _ in range(B)` 中使用 `_` 作為迴圈變數。當計數器的值不重要且只是要確保迴圈執行 `B` 次時，經常使用這種方式。

讓我們使用函數來評估使用 $B=1{,}000$ bootstrap 複製的 $\alpha$ 估計的準確率。

## 儲存格 61 [code]

```python
alpha_SE = boot_SE(alpha_func,
                   Portfolio,
                   B=1000,
                   seed=0)
alpha_SE
```

## 儲存格 62 [md]

最終輸出顯示 ${\rm SE}(\hat{\alpha})$ 的 bootstrap 估計為 $0.0912$。

## 儲存格 63 [md]

### 估計線性回歸模型的準確率

## 儲存格 64 [md]

Bootstrap 方法可以用來評估來自統計學習方法的係數估計和預測的變異性。這裡我們使用 bootstrap 方法來評估線性回歸模型中 $\beta_0$ 和 $\beta_1$（截距項和斜率項）的變異性估計，該模型使用 `horsepower` 來預測 `Auto` 資料集中的 `mpg`。我們將比較使用 bootstrap 獲得的估計與使用第 3.1.2 節中描述的 ${\rm SE}(\hat{\beta}_0)$ 和 ${\rm SE}(\hat{\beta}_1)$ 公式獲得的估計。

要使用我們的 `boot_SE()` 函數，我們必須寫一個函數（作為其第一個參數），該函數僅以資料框架 `D` 和索引 `idx` 作為參數。但這裡我們想要 bootstrap 特定的回歸模型，由模型公式和資料指定。我們將展示如何用幾個簡單步驟來做到這一點。

我們首先寫一個通用函數 `boot_OLS()` 來 bootstrap 回歸模型，該函數接受一個公式來定義對應的回歸。我們使用 `clone()` 函數來複製可以在新資料框架上重新擬合的公式。這意味著任何衍生特徵，如 `poly()` 定義的特徵（我們很快就會看到），將在重新抽樣的資料框架上重新擬合。

## 儲存格 65 [code]

```python
def boot_OLS(model_matrix, response, D, idx):
    # 為了方便檢查，先確保 idx 是一個 NumPy array
    idx = np.asarray(idx)

    # 檢查 idx 的資料類型 (dtype) 是否為整數類型
    if np.issubdtype(idx.dtype, np.integer):
        # 如果是整數，代表是位置 (position)，使用 .iloc
        D_ = D.iloc[idx]
    else:
        # 否則，代表是標籤 (label)，使用 .loc
        D_ = D.loc[idx]

    Y_ = D_[response]
    X_ = clone(model_matrix).fit_transform(D_)
    return sm.OLS(Y_, X_).fit().params
```

## 儲存格 66 [md]

這還不完全是 `boot_SE()` 的第一個參數所需要的。指定模型的前兩個參數在 bootstrap 過程中不會改變，我們希望*凍結*它們。`functools` 模組中的函數 `partial()` 正好做這件事：它接受一個函數作為參數，並從左邊開始凍結其部分參數。我們用它來凍結 `boot_OLS()` 的前兩個模型公式參數。

## 儲存格 67 [code]

```python
hp_func = partial(boot_OLS, MS(['horsepower']), 'mpg')
```

## 儲存格 68 [md]

輸入 `hp_func?` 會顯示它有兩個參數 `D` 和 `idx` --- 它是凍結了前兩個參數的 `boot_OLS()` 版本 --- 因此是 `boot_SE()` 第一個參數的理想選擇。

現在可以使用 `hp_func()` 函數，透過從觀測值中有放回地隨機抽樣來建立截距項和斜率項的 bootstrap 估計。我們首先在 10 個 bootstrap 樣本上展示其用途。

## 儲存格 69 [code]

```python
rng = np.random.default_rng(0)
np.array([hp_func(Auto,
          rng.choice(392,
                     392,
                     replace=True)) for _ in range(10)])
```

**輸出**

```
array([[39.88064456, -0.1567849 ],
       [38.73298691, -0.14699495],
       [38.31734657, -0.14442683],
       [39.91446826, -0.15782234],
       [39.43349349, -0.15072702],
       [40.36629857, -0.15912217],
       [39.62334517, -0.15449117],
       [39.0580588 , -0.14952908],
       [38.66688437, -0.14521037],
       [39.64280792, -0.15555698]])
```

## 儲存格 70 [md]

接著我們使用 `boot_SE()` 函數來計算 1,000 個 bootstrap 估計的截距項和斜率項標準誤差。

## 儲存格 71 [code]

```python
hp_se = boot_SE(hp_func,
                Auto,
                B=1000,
                seed=10)
hp_se
```

## 儲存格 72 [md]

這表示 ${\rm SE}(\hat{\beta}_0)$ 的 bootstrap 估計為 0.73，而 ${\rm SE}(\hat{\beta}_1)$ 的 bootstrap 估計為 0.00609。如第 3.1.2 節所討論的，標準公式可以用來計算線性模型中回歸係數的標準誤差。這些可以使用 `ISLP.models` 中的 `summarize()` 函數獲得。

## 儲存格 73 [code]

```python
hp_model.fit(Auto, Auto['mpg'])
model_se = summarize(hp_model.results_)['std err']
model_se
```

**輸出**

```
intercept     0.717
horsepower    0.006
Name: std err, dtype: float64
```

## 儲存格 74 [md]

使用第 3.1.2 節公式獲得的 $\hat{\beta}_0$ 和 $\hat{\beta}_1$ 標準誤差估計，截距項為 0.717，斜率為 0.006。有趣的是，這些與使用 bootstrap 獲得的估計有些不同。這是否表示 bootstrap 有問題？事實上，它暗示的是相反的。回想第 82 頁方程式 3.8 中給出的標準公式依賴於某些假設。例如，它們依賴於未知參數 $\sigma^2$（雜訊變異數）。然後我們使用 RSS 來估計 $\sigma^2$。現在，雖然標準誤差的公式不依賴於線性模型的正確性，但 $\sigma^2$ 的估計確實如此。我們在第 108 頁的圖 3.8 中看到資料中存在非線性關係，因此來自線性擬合的殘差會被誇大，$\hat{\sigma}^2$ 也會如此。其次，標準公式假設（有些不現實地）$x_i$ 是固定的，所有變異性都來自誤差 $\epsilon_i$ 的變化。Bootstrap 方法不依賴於任何這些假設，因此它可能比來自 `sm.OLS` 的結果給出 $\hat{\beta}_0$ 和 $\hat{\beta}_1$ 標準誤差的更準確估計。

下面我們計算 bootstrap 標準誤差估計以及擬合二次模型資料所產生的標準線性回歸估計。由於此模型對資料提供良好的擬合（圖 3.8），現在 bootstrap 估計與 ${\rm SE}(\hat{\beta}_0)$、${\rm SE}(\hat{\beta}_1)$ 和 ${\rm SE}(\hat{\beta}_2)$ 的標準估計之間有更好的對應關係。

## 儲存格 75 [code]

```python
quad_model = MS([poly('horsepower', 2, raw=True)])
quad_func = partial(boot_OLS,
                    quad_model,
                    'mpg')
boot_SE(quad_func, Auto, B=1000)
```

## 儲存格 76 [md]

我們將結果與使用 `sm.OLS()` 計算的標準誤差進行比較。

## 儲存格 77 [code]

```python
M = sm.OLS(Auto['mpg'],
           quad_model.fit_transform(Auto))
summarize(M.fit())['std err']
```

**輸出**

```
intercept                                  1.800
poly(horsepower, degree=2, raw=True)[0]    0.031
poly(horsepower, degree=2, raw=True)[1]    0.000
Name: std err, dtype: float64
```

