# Ch02-statlearn-lab-zh.ipynb — ISLP 第 2 章

> 由 tools/extract_lab.py 產生。頁面上的程式碼與預期輸出一律從這裡逐字抄，
> `.dx-src` 要標注這裡的儲存格編號。不要重跑：輸出是課程環境下的實跑結果。

## 儲存格 0 [md]

# 第 2 章

## 儲存格 1 [md]

<table align="left">
  <td>
    <a href="https://colab.research.google.com/github/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch02-statlearn-lab-zh.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
  </td>
  <td>
    <a target="_blank" href="https://kaggle.com/kernels/welcome?src=https://github.com/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch02-statlearn-lab-zh.ipynb"><img src="https://kaggle.com/static/images/open-in-kaggle.svg" /></a>
  </td>
</table>

## 儲存格 2 [code]

```python
%load_ext cudf.pandas
%load_ext cuml.accel
```

**輸出**

```
cuML: Accelerator installed.
```

## 儲存格 3 [code]

```python
# 本 Notebook 使用的匯入（imports）
import os  # 檔案與環境變數/路徑處理
import numpy as np  # 數值運算與陣列處理
import pandas as pd  # 資料表格與資料處理
from matplotlib.pyplot import subplots  # 建立子圖與繪圖版面
try:
    from google.colab import drive  # Colab：掛載 Google Drive
except Exception:
    drive = None  # 非 Colab 環境
```

## 儲存格 4 [md]

# 實驗：Python 入門

## 儲存格 5 [md]

## 快速開始（Getting Started）

## 儲存格 6 [md]

請參考本書網站 [statlearning.com](https://www.statlearning.com) 的 Python 資源頁面，以取得在我們的電腦上安裝及使用 `Python` 和 `Jupyter` 的最新資訊。

## 儲存格 7 [md]

我們需要安裝 `ISLP` 套件，此套件提供我們所使用的資料集與自訂函式的存取功能。
在 macOS 或 Linux 終端機中輸入 `pip install ISLP`；這也會安裝在實驗中所需的其他大部分套件。Python 資源頁面上有 `ISLP` 說明文件網站的連結。

要執行這個實驗，請從 Python 資源頁面下載 `Ch02-statlearn-lab.ipynb` 檔案。
然後在命令列執行以下指令：`Jupyter lab Ch02-statlearn-lab.ipynb`。

如果我們使用的是 Windows，可以透過「開始選單」存取 `Anaconda`，並依照連結指示進行。例如，要安裝 `ISLP` 並執行此實驗，我們可以在 `Anaconda` shell 中執行上述相同的程式碼。

## 儲存格 8 [code]

```python
%pip install ISLP
```

**輸出**

```
Collecting ISLP
  Downloading ISLP-0.4.0-py3-none-any.whl.metadata (7.0 kB)
Requirement already satisfied: numpy>=1.7.1 in /usr/local/lib/python3.12/dist-packages (from ISLP) (2.0.2)
Requirement already satisfied: scipy>=0.9 in /usr/local/lib/python3.12/dist-packages (from ISLP) (1.16.1)
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
  Downloading formulaic-1.2.0-py3-none-any.whl.metadata (7.0 kB)
Requirement already satisfied: progressbar2<5,>=4.2.0 in /usr/local/lib/python3.12/dist-packages (from pygam->ISLP) (4.5.0)
Requirement already satisfied: tqdm>=4.57.0 in /usr/local/lib/python3.12/dist-packages (from pytorch-lightning->ISLP) (4.67.1)
Requirement already satisfied: PyYAML>5.4 in /usr/local/lib/python3.12/dist-packages (from pytorch-lightning->ISLP) (6.0.2)
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
Requirement already satisfied: narwhals>=1.17 in /usr/local/lib/python3.12/dist-packages (from formulaic>=0.2.2->lifelines->ISLP) (2.3.0)
Requirement already satisfied: wrapt>=1.0 in /usr/local/lib/python3.12/dist-packages (from formulaic>=0.2.2->lifelines->ISLP) (1.17.3)
Requirement already satisfied: aiohttp!=4.0.0a0,!=4.0.0a1 in /usr/local/lib/python3.12/dist-packages (from fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (3.12.15)
Requirement already satisfied: contourpy>=1.0.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (1.3.3)
Requirement already satisfied: cycler>=0.10 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (0.12.1)
Requirement already satisfied: fonttools>=4.22.0 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (4.59.2)
Requirement already satisfied: kiwisolver>=1.3.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (1.4.9)
Requirement already satisfied: pillow>=8 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (11.3.0)
Requirement already satisfied: pyparsing>=2.3.1 in /usr/local/lib/python3.12/dist-packages (from matplotlib>=3.0->lifelines->ISLP) (3.2.3)
Requirement already satisfied: python-utils>=3.8.1 in /usr/local/lib/python3.12/dist-packages (from progressbar2<5,>=4.2.0->pygam->ISLP) (3.9.1)
Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.12/dist-packages (from python-dateutil>=2.8.2->pandas>=0.20->ISLP) (1.17.0)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in /usr/local/lib/python3.12/dist-packages (from sympy>=1.13.3->torch->ISLP) (1.3.0)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.12/dist-packages (from jinja2->torch->ISLP) (3.0.2)
Requirement already satisfied: aiohappyeyeballs>=2.5.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (2.6.1)
Requirement already satisfied: aiosignal>=1.4.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.4.0)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (25.3.0)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.7.0)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (6.6.4)
Requirement already satisfied: propcache>=0.2.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (0.3.2)
Requirement already satisfied: yarl<2.0,>=1.17.0 in /usr/local/lib/python3.12/dist-packages (from aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (1.20.1)
Requirement already satisfied: idna>=2.0 in /usr/local/lib/python3.12/dist-packages (from yarl<2.0,>=1.17.0->aiohttp!=4.0.0a0,!=4.0.0a1->fsspec[http]>=2022.5.0->pytorch-lightning->ISLP) (3.10)
Downloading ISLP-0.4.0-py3-none-any.whl (3.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.6/3.6 MB 23.8 MB/s eta 0:00:00
[?25hDownloading lifelines-0.30.0-py3-none-any.whl (349 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 349.3/349.3 kB 33.8 MB/s eta 0:00:00
[?25hDownloading pygam-0.10.1-py3-none-any.whl (80 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80.2/80.2 kB 10.1 MB/s eta 0:00:00
[?25hDownloading pytorch_lightning-2.5.5-py3-none-any.whl (832 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 832.4/832.4 kB 51.8 MB/s eta 0:00:00
[?25hDownloading torchmetrics-1.8.2-py3-none-any.whl (983 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 983.2/983.2 kB 58.8 MB/s eta 0:00:00
[?25hDownloading formulaic-1.2.0-py3-none-any.whl (117 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 117.2/117.2 kB 15.1 MB/s eta 0:00:00
[?25hDownloading lightning_utilities-0.15.2-py3-none-any.whl (29 kB)
Downloading interface_meta-1.3.0-py3-none-any.whl (14 kB)
Building wheels for collected packages: autograd-gamma
  Building wheel for autograd-gamma (setup.py) ... [?25l[?25hdone
  Created wheel for autograd-gamma: filename=autograd_gamma-0.5.0-py3-none-any.whl size=4030 sha256=e83a92da55e75c46943e5e8343f5777f801f985bb6b70c5e2c7340a3f03c6b07
  Stored in directory: /root/.cache/pip/wheels/50/37/21/0a719b9d89c635e89ff24bd93b862882ad675279552013b2fb
Successfully built autograd-gamma
Installing collected packages: lightning-utilities, interface-meta, autograd-gamma, pygam, formulaic, torchmetrics, lifelines, pytorch-lightning, ISLP
Successfully installed ISLP-0.4.0 autograd-gamma-0.5.0 formulaic-1.2.0 interface-meta-1.3.0 lifelines-0.30.0 lightning-utilities-0.15.2 pygam-0.10.1 pytorch-lightning-2.5.5 torchmetrics-1.8.2
```

## 儲存格 9 [md]

## 基本指令（Basic Commands）

## 儲存格 10 [md]

在本實驗中，我們將介紹一些簡單的 `Python` 指令。
想要了解 `Python` 的更多資源，大家可以參考 [docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/) 的教學。

## 儲存格 11 [md]

如同大部分程式語言，`Python` 使用*函式*來執行運算。要執行名為 `fun` 的函式，我們輸入 `fun(input1,input2)`，其中輸入值（或*引數*）`input1` 和 `input2` 告訴 `Python` 如何執行該函式。一個函式可以有任意數量的輸入值。例如，`print()` 函式會將其所有引數的文字表示輸出到控制台。

## 儲存格 12 [code]

```python
print('fit a model with', 11, 'variables')
```

**輸出**

```
fit a model with 11 variables
```

## 儲存格 13 [md]

以下指令將提供有關 `print()` 函式的資訊。

## 儲存格 14 [code]

```python
print?
```

## 儲存格 15 [md]

在 `Python` 中將兩個整數相加是非常直觀的。

## 儲存格 16 [code]

```python
3 + 5
```

**輸出**

```
8
```

## 儲存格 17 [md]

在 `Python` 中，文字資料使用*字串*來處理。例如，`"hello"` 和 `'hello'` 都是字串。我們可以使用加號 `+` 符號來連接它們。

## 儲存格 18 [code]

```python
"hello" + " " + "world"
```

**輸出**

```
'hello world'
```

## 儲存格 19 [md]

字串實際上是*序列*的一種類型：這是有序清單的通用術語。三種最重要的序列類型是 `lists`（清單）、`tuples`（元組）和 `strings`（字串）。我們現在來介紹清單。

## 儲存格 20 [md]

以下指令指示 `Python` 將數字 3、4、5 組合在一起，並將它們儲存為名為 `x` 的*清單*。當我們輸入 `x` 時，它會回傳給我們該清單。

## 儲存格 21 [code]

```python
x = [3, 4, 5]
x
```

**輸出**

```
[3, 4, 5]
```

## 儲存格 22 [md]

注意：我們使用方括號 `[]` 來建構這個清單。

我們經常會想要將兩組數字加在一起。嘗試以下程式碼是合理的，雖然它不會產生期望的結果。

## 儲存格 23 [code]

```python
y = [4, 9, 7]
x + y
```

**輸出**

```
[3, 4, 5, 4, 9, 7]
```

## 儲存格 24 [md]

結果可能顯得有些反直覺：為什麼 `Python` 不會逐個元素地將清單項目相加？在 `Python` 中，清單儲存*任意*物件，並使用*串接*的方式進行相加。事實上，串接就是我們先前在輸入 `"hello" + " " + "world"` 時看到的行為。

## 儲存格 25 [md]

這個例子反映了 `Python` 是一個通用程式語言的事實。`Python` 的大部分資料處理功能來自其他套件，特別是 `numpy` 和 `pandas`。在下一節中，我們將介紹 `numpy` 套件。詳細資訊請參見 [docs.scipy.org/doc/numpy/user/quickstart.html](https://docs.scipy.org/doc/numpy/user/quickstart.html)。

## 儲存格 26 [md]

## Numerical Python 介紹

## 儲存格 27 [md]

如前所述，本書使用了包含在 `numpy` *函式庫*或*套件*中的功能。套件是一個模組集合，這些模組不一定包含在基礎 `Python` 發行版中。`numpy` 這個名稱是 *numerical Python* 的縮寫。

## 儲存格 28 [md]

要存取 `numpy`，我們必須先將其 `import` 匯入。

## 儲存格 29 [md]

在前面的程式碼行中，我們將 `numpy` *模組*命名為 `np`；這是一個方便參考的縮寫。

## 儲存格 30 [md]

在 `numpy` 中，*array*（陣列）是一個多維數字集合的通用術語。我們使用 `np.array()` 函式來定義 `x` 和 `y`，它們是一維陣列，即向量。

## 儲存格 31 [code]

```python
x = np.array([3, 4, 5])
y = np.array([4, 9, 7])
```

## 儲存格 32 [md]

注意：如果我們忘記執行前面的 `import numpy as np` 指令，那麼在呼叫前一行的 `np.array()` 函式時會遇到錯誤。語法 `np.array()` 表示被呼叫的函式是 `numpy` 套件的一部分，我們將其縮寫為 `np`。

## 儲存格 33 [md]

由於 `x` 和 `y` 都是使用 `np.array()` 定義的，當我們將它們相加時會得到合理的結果。將此與上一節的結果比較，當時我們嘗試在不使用 `numpy` 的情況下將兩個清單相加。

## 儲存格 34 [code]

```python
x + y
```

**輸出**

```
array([ 7, 13, 12])
```

## 儲存格 35 [md]

在 `numpy` 中，矩陣通常表示為二維陣列，而向量表示為一維陣列。雖然也可以使用 `np.matrix()` 來建立矩陣，但我們在本書的實驗中將全程使用 `np.array()`。
我們可以如下建立二維陣列。

## 儲存格 36 [code]

```python
x = np.array([[1, 2], [3, 4]])
x
```

**輸出**

```
array([[1, 2],
       [3, 4]])
```

## 儲存格 37 [md]

此物件 `x` 有數個*屬性*，或相關聯的物件。要存取 `x` 的屬性，我們輸入 `x.attribute`，其中我們將 `attribute` 替換為屬性名稱。例如，我們可以如下存取 `x` 的 `ndim` 屬性。

## 儲存格 38 [code]

```python
x.ndim
```

**輸出**

```
2
```

## 儲存格 39 [md]

輸出顯示 `x` 是一個二維陣列。類似地，`x.dtype` 是物件 `x` 的*資料類型*屬性。這表示 `x` 是由 64 位元整數組成的：

## 儲存格 40 [code]

```python
x.dtype
```

**輸出**

```
dtype('int64')
```

## 儲存格 41 [md]

為什麼 `x` 是由整數組成的？這是因為我們建立 `x` 時只傳入整數給 `np.array()` 函式。如果我們傳入任何小數，那麼我們就會得到*浮點數*（即實數值）的陣列。

## 儲存格 42 [code]

```python
np.array([[1, 2], [3.0, 4]]).dtype
```

**輸出**

```
dtype('float64')
```

## 儲存格 43 [md]

輸入 `fun?` 會讓 `Python` 顯示與函式 `fun` 相關的說明文件（如果存在）。我們可以對 `np.array()` 試試這個方法。

## 儲存格 44 [code]

```python
np.array?
```

## 儲存格 45 [md]

這份說明文件表示我們可以透過將 `dtype` 引數傳入 `np.array()` 來建立浮點數陣列。

## 儲存格 46 [code]

```python
np.array([[1, 2], [3, 4]], float).dtype
```

**輸出**

```
dtype('float64')
```

## 儲存格 47 [md]

陣列 `x` 是二維的。我們可以透過查看其 `shape` 屬性來找出列數和欄數。

## 儲存格 48 [code]

```python
x.shape
```

**輸出**

```
(2, 2)
```

## 儲存格 49 [md]

*method*（方法）是與物件相關聯的 function。
例如，對於給定的陣列 `x`，表達式 `x.sum()` 會使用陣列的 `sum()` method 來加總其所有元素。
呼叫 `x.sum()` 會自動將 `x` 作為第一個引數提供給其 `sum()` method。

## 儲存格 50 [code]

```python
x = np.array([1, 2, 3, 4])
x.sum()
```

**輸出**

```
np.int64(10)
```

## 儲存格 51 [md]

我們也可以透過將 `x` 作為引數傳入 `np.sum()` function 來對 `x` 的元素進行加總。

## 儲存格 52 [code]

```python
x = np.array([1, 2, 3, 4])
np.sum(x)
```

**輸出**

```
np.int64(10)
```

## 儲存格 53 [md]

另一個例子是，`reshape()` method 會回傳一個新的陣列，其元素與 `x` 相同，但形狀不同。
我們在呼叫 `reshape()` 時透過傳入一個 `tuple`（在此情況下為 `(2, 3)`）來實現。這個 tuple 指定我們想要建立一個具有 $2$ 列和 $3$ 欄的二維陣列。和 lists 一樣，tuples 表示一個物件序列。為什麼我們需要多種方式來建立序列？tuples 和 lists 之間有一些差異，但也許最重要的是 tuple 的元素不能被修改，而 list 的元素則可以。

在下面的內容中，`\n` 字元會建立一個*新行*。

## 儲存格 54 [code]

```python
x = np.array([1, 2, 3, 4, 5, 6])
print('beginning x:\n', x)
x_reshape = x.reshape((2, 3))
print('reshaped x:\n', x_reshape)
```

**輸出**

```
beginning x:
 [1 2 3 4 5 6]
reshaped x:
 [[1 2 3]
 [4 5 6]]
```

## 儲存格 55 [md]

前面的輸出顯示 `numpy` 陣列是以*列*的序列來指定的。這稱為*行主要排序*（row-major ordering），相對於*欄主要排序*（column-major ordering）。

## 儲存格 56 [md]

`Python`（以及 `numpy`）使用以 0 為基底的索引。這意味著要存取 `x_reshape` 的左上角元素，我們輸入 `x_reshape[0,0]`。

## 儲存格 57 [code]

```python
x_reshape[0, 0]
```

**輸出**

```
np.int64(1)
```

## 儲存格 58 [md]

同樣地，`x_reshape[1,2]` 會產生 `x_reshape` 第二列第三欄的元素。

## 儲存格 59 [code]

```python
x_reshape[1, 2]
```

**輸出**

```
np.int64(6)
```

## 儲存格 60 [md]

同樣地，`x[2]` 產生 `x` 的第三個項目。

現在，讓我們修改 `x_reshape` 的左上角元素。令我們驚訝的是，我們發現 `x` 的第一個元素也被修改了！

## 儲存格 61 [code]

```python
print('x before we modify x_reshape:\n', x)
print('x_reshape before we modify x_reshape:\n', x_reshape)
x_reshape[0, 0] = 5
print('x_reshape after we modify its top left element:\n', x_reshape)
print('x after we modify top left element of x_reshape:\n', x)
```

**輸出**

```
x before we modify x_reshape:
 [1 2 3 4 5 6]
x_reshape before we modify x_reshape:
 [[1 2 3]
 [4 5 6]]
x_reshape after we modify its top left element:
 [[5 2 3]
 [4 5 6]]
x after we modify top left element of x_reshape:
 [5 2 3 4 5 6]
```

## 儲存格 62 [md]

修改 `x_reshape` 也修改了 `x`，因為這兩個物件佔用記憶體中的同一個空間。

## 儲存格 63 [md]

我們剛才看到我們可以修改陣列的元素。我們也可以修改 tuple 嗎？事實證明我們不能——嘗試這樣做會引發*例外*（exception），或錯誤。

## 儲存格 64 [code]

```python
my_tuple = (3, 4, 5)
my_tuple[0] = 2
```

**輸出**

```
TypeError: 'tuple' object does not support item assignment
```

## 儲存格 65 [md]

我們現在簡單提及陣列的一些屬性，這些會很實用。陣列的 `shape` 屬性包含其維度；這總是一個 tuple。
`ndim` 屬性產生維度的數目，而 `T` 提供其轉置。

## 儲存格 66 [code]

```python
x_reshape.shape, x_reshape.ndim, x_reshape.T
```

**輸出**

```
((2, 3),
 2,
 array([[5, 4],
        [2, 5],
        [3, 6]]))
```

## 儲存格 67 [md]

注意三個個別輸出 `(2,3)`、`2` 和 `array([[5, 4],[2, 5], [3,6]])` 本身被輸出為一個 tuple。

我們經常會想要對陣列套用 functions。例如，我們可以使用 `np.sqrt()` function 來計算項目的平方根：

## 儲存格 68 [code]

```python
np.sqrt(x)
```

**輸出**

```
array([2.23606798, 1.41421356, 1.73205081, 2.        , 2.23606798,
       2.44948974])
```

## 儲存格 69 [md]

我們也可以對元素進行平方：

## 儲存格 70 [code]

```python
x**2
```

**輸出**

```
array([25,  4,  9, 16, 25, 36])
```

## 儲存格 71 [md]

我們可以使用相同的表示法來計算平方根，將次方從 2 改為 $1/2$。

## 儲存格 72 [code]

```python
x**0.5
```

**輸出**

```
array([2.23606798, 1.41421356, 1.73205081, 2.        , 2.23606798,
       2.44948974])
```

## 儲存格 73 [md]

在本書中，我們經常會想要產生隨機資料。
`np.random.normal()` function 產生一個隨機常態變數的向量。我們可以透過呼叫 `np.random.normal?` 查看說明頁面來了解更多有關此 function 的資訊。
說明頁面的第一行寫著 `normal(loc=0.0, scale=1.0, size=None)`。
這個*簽名*行告訴我們 function 的引數是 `loc`、`scale` 和 `size`。這些是*關鍵字*引數，意味著當它們被傳入 function 時，可以透過名稱來引用（以任何順序）。

> `Python` 也使用*位置*引數。位置引數不需要使用關鍵字。要查看例子，輸入 `np.sum?`。我們看到 `a` 是一個位置引數，即此 function 假設它接收到的第一個未命名引數是要被加總的陣列。相比之下，`axis` 和 `dtype` 是關鍵字引數：這些引數被輸入到 `np.sum()` 中的位置並不重要。

預設情況下，此 function 會產生平均值（`loc`）為 $0$、標準差（`scale`）為 $1$ 的隨機常態變數；此外，除非 `size` 引數被改變，否則會產生單一隨機變數。

我們現在從 $N(0,1)$ 分佈產生 50 個獨立隨機變數。

## 儲存格 74 [code]

```python
x = np.random.normal(size=50)
x
```

**輸出**

```
array([ 0.76922192, -0.79072506, -0.62902948, -1.41081366, -0.28431536,
        0.6433348 ,  0.93424379, -0.07888492,  1.15269858,  0.61342214,
        0.51152073, -0.10526611,  0.96353617, -0.08524647,  0.79062988,
       -0.14291613,  0.17868399,  1.04301847,  1.72803276, -0.02500259,
        0.503374  , -0.09272353,  0.50660005,  0.45836829, -0.64084964,
        0.28565039, -0.34282389,  1.63776627,  1.38336359,  0.25838181,
        0.09187549, -1.55661103, -0.14880653,  0.62972929,  0.21650677,
        0.34658862, -0.49039577, -0.77656903,  1.26857526, -1.15450712,
        1.00398922, -1.07171239, -0.627228  , -0.95075515, -0.31327062,
       -1.07904779, -1.00249413, -0.39303692, -2.87259992, -0.01487073])
```

## 儲存格 75 [md]

我們透過將獨立的 $N(50,1)$ 隨機變數添加到 `x` 的每個元素來建立陣列 `y`。

## 儲存格 76 [code]

```python
y = x + np.random.normal(loc=50, scale=1, size=50)
```

## 儲存格 77 [md]

`np.corrcoef()` function 計算 `x` 和 `y` 之間的相關矩陣。非對角元素給出 `x` 和 `y` 之間的相關性。

## 儲存格 78 [code]

```python
np.corrcoef(x, y)
```

**輸出**

```
array([[1.        , 0.78689588],
       [0.78689588, 1.        ]])
```

## 儲存格 79 [md]

如果你在自己的 `Jupyter` notebook 中跟著操作，那麼你可能注意到當你執行過去幾個指令時會得到不同的結果集。特別是，每次我們呼叫 `np.random.normal()` 時，我們都會得到不同的答案，如下面的例子所示。

## 儲存格 80 [code]

```python
print(np.random.normal(scale=5, size=2))
print(np.random.normal(scale=5, size=2))
```

**輸出**

```
[9.78166034 7.77407713]
[-1.41427653 -4.97598078]
```

## 儲存格 81 [md]

為了確保我們的程式碼每次執行時都能提供完全相同的結果，我們可以使用 `np.random.default_rng()` function 來設定*隨機種子*。
此 function 接受一個任意的、使用者指定的整數引數。如果我們在產生隨機資料之前設定隨機種子，那麼重新執行我們的程式碼將產生相同的結果。
物件 `rng` 基本上具有 `np.random` 中找到的所有隨機數產生 methods。因此，要產生常態資料，我們使用 `rng.normal()`。

## 儲存格 82 [code]

```python
rng = np.random.default_rng(1303)
print(rng.normal(scale=5, size=2))
rng2 = np.random.default_rng(1303)
print(rng2.normal(scale=5, size=2))
```

**輸出**

```
[ 4.09482632 -1.07485605]
[ 4.09482632 -1.07485605]
```

## 儲存格 83 [md]

在本書的實驗中，每當我們在 `numpy` 中執行涉及隨機數量的計算時，我們都會使用 `np.random.default_rng()`。原則上，這應該使大家能夠精確重現所述結果。然而，隨著新版本 `numpy` 的推出，實驗中的輸出與 `numpy` 的輸出之間可能會出現一些小差異。

`np.mean()`、`np.var()` 和 `np.std()` functions 可以用來計算陣列的平均值、變異數和標準差。這些 functions 也可以作為陣列上的 methods 使用。

## 儲存格 84 [code]

```python
rng = np.random.default_rng(3)
y = rng.standard_normal(10)
np.mean(y), y.mean()
```

**輸出**

```
(np.float64(-0.1126795190952861), np.float64(-0.1126795190952861))
```

## 儲存格 85 [code]

```python
np.var(y), y.var(), np.mean((y - y.mean())**2)
```

**輸出**

```
(np.float64(2.7243406406465125),
 np.float64(2.7243406406465125),
 np.float64(2.7243406406465125))
```

## 儲存格 86 [md]

注意預設情況下 `np.var()` 除以樣本大小 $n$ 而非 $n-1$；請參見 `np.var?` 中的 `ddof` 引數。

## 儲存格 87 [code]

```python
np.sqrt(np.var(y)), np.std(y)
```

**輸出**

```
(np.float64(1.6505576756498128), np.float64(1.6505576756498128))
```

## 儲存格 88 [md]

`np.mean()`、`np.var()` 和 `np.std()` functions 也可以套用到矩陣的列和欄。為了看到這一點，我們建構一個 $10 \times 3$ 的 $N(0,1)$ 隨機變數矩陣，並考慮計算其列和。

## 儲存格 89 [code]

```python
X = rng.standard_normal((10, 3))
X
```

**輸出**

```
array([[ 0.22578661, -0.35263079, -0.28128742],
       [-0.66804635, -1.05515055, -0.39080098],
       [ 0.48194539, -0.23855361,  0.9577587 ],
       [-0.19980213,  0.02425957,  1.54582085],
       [ 0.54510552, -0.50522874, -0.18283897],
       [ 0.54052513,  1.93508803, -0.26962033],
       [-0.24355868,  1.0023136 , -0.88645994],
       [-0.29172023,  0.88253897,  0.58035002],
       [ 0.0915167 ,  0.67010435, -2.82816231],
       [ 1.02130682, -0.95964476, -1.66861984]])
```

## 儲存格 90 [md]

由於陣列是行主要排序的，第一個軸，即 `axis=0`，指的是其列。我們將此引數傳遞到物件 `X` 的 `mean()` method 中。

## 儲存格 91 [code]

```python
X.mean(axis=0)
```

**輸出**

```
array([ 0.15030588,  0.14030961, -0.34238602])
```

## 儲存格 92 [md]

以下會產生相同的結果。

## 儲存格 93 [code]

```python
X.mean(0)
```

**輸出**

```
array([ 0.15030588,  0.14030961, -0.34238602])
```

## 儲存格 94 [md]

## 圖形繪製

## 儲存格 95 [md]

在 `Python` 中，通常使用 `matplotlib` 函式庫來進行圖形繪製。然而，由於 `Python` 並非專為資料分析而設計，繪圖的概念並非語言本身的內建功能。我們將使用 `matplotlib.pyplot` 中的 `subplots()` 函式來建立圖形和繪製資料的軸。
如需更多關於如何在 `Python` 中製作圖表的範例，建議大家造訪 [matplotlib.org/stable/gallery/](https://matplotlib.org/stable/gallery/index.html)。

在 `matplotlib` 中，一個圖表包含一個*圖形*和一個或多個*軸*。我們可以將圖形想像成空白畫布，上面將顯示一個或多個繪圖：它是整個繪圖視窗。*軸*包含每個繪圖的重要資訊，例如其 $x$ 軸和 $y$ 軸標籤、標題等。（注意：在 `matplotlib` 中，*axes* 這個詞不是 *axis* 的複數：一個圖表的 *axes* 包含的資訊遠比 $x$ 軸和 $y$ 軸多得多。）

我們先從 `matplotlib` 匯入 `subplots()` 函式。在建立圖形時我們會一直使用這個函式。該函式回傳長度為二的元組：圖形物件以及相關的軸物件。我們通常會將 `figsize` 作為關鍵字引數傳入。建立軸後，我們嘗試使用其 `plot()` 方法進行第一次繪圖。要了解更多資訊，請輸入 `ax.plot?`。

## 儲存格 96 [code]

```python
fig, ax = subplots(figsize=(8, 8))
x = rng.standard_normal(100)
y = rng.standard_normal(100)
ax.plot(x, y);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 97 [md]

我們在此暫停，注意我們已將 `subplots()` 回傳的長度為二的 tuple *解包*到兩個不同的變數 `fig` 和 `ax` 中。解包通常優於以下等效但稍微冗長的程式碼：

## 儲存格 98 [code]

```python
output = subplots(figsize=(8, 8))
fig = output[0]
ax = output[1]
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 99 [md]

我們看到我們之前的 cell 產生了線圖，這是預設的。要建立散佈圖，我們向 `ax.plot()` 提供額外的引數，指示應顯示圓圈。

## 儲存格 100 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.plot(x, y, 'o');
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 101 [md]

此額外引數的不同值可以用來產生不同顏色的線條以及不同的線條樣式。

## 儲存格 102 [md]

或者，我們可以使用 `ax.scatter()` function 來建立散佈圖。

## 儲存格 103 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.scatter(x, y, marker='o');
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 104 [md]

注意在上面的程式碼區塊中，我們在最後一行的末尾加了分號。這防止 `ax.plot(x, y)` 在 notebook 中印出文字。然而，它不會阻止繪圖被產生。
如果我們省略結尾的分號，那麼我們會得到以下輸出：

## 儲存格 105 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.scatter(x, y, marker='o')
```

**輸出**

```
<matplotlib.collections.PathCollection at 0x79557e887fb0><Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 106 [md]

在接下來的內容中，每當要輸出的文字與手邊的討論不相關時，我們將使用結尾分號。

## 儲存格 107 [md]

要為我們的繪圖加標籤，我們使用 `ax` 的 `set_xlabel()`、`set_ylabel()` 和 `set_title()` methods。

## 儲存格 108 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.scatter(x, y, marker='o')
ax.set_xlabel("this is the x-axis")
ax.set_ylabel("this is the y-axis")
ax.set_title("Plot of X vs Y");
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 109 [md]

擁有圖形物件 `fig` 本身的存取權限意味著我們可以進入並更改一些方面，然後重新顯示它。在這裡，我們將大小從 `(8, 8)` 更改為 `(12, 3)`。

## 儲存格 110 [code]

```python
fig.set_size_inches(12,3)
fig
```

**輸出**

```
<Figure size 1200x300 with 1 Axes><figure omitted>
```

## 儲存格 111 [md]

有時我們想要在圖形中建立多個繪圖。這可以透過向 `subplots()` 傳遞額外引數來實現。
下面，我們在大小由 `figsize` 引數決定的圖形中建立 $2 \times 3$ 的繪圖格網。在這種情況下，繪圖中的軸之間經常存在關係。例如，所有繪圖可能有共同的 $x$ 軸。當傳遞關鍵字引數 `sharex=True` 時，`subplots()` function 可以自動處理這種情況。
下面的 `axes` 物件是一個指向圖形中不同繪圖的陣列。

## 儲存格 112 [code]

```python
fig, axes = subplots(nrows=2,
                     ncols=3,
                     figsize=(15, 5))
```

**輸出**

```
<Figure size 1500x500 with 6 Axes><figure omitted>
```

## 儲存格 113 [md]

我們現在在第一列的第二欄產生帶有 `'o'` 的散佈圖，並在第二列的第三欄產生帶有 `'+'` 的散佈圖。

## 儲存格 114 [code]

```python
axes[0,1].plot(x, y, 'o')
axes[1,2].scatter(x, y, marker='+')
fig
```

**輸出**

```
<Figure size 1500x500 with 6 Axes><figure omitted>
```

## 儲存格 115 [md]

輸入 `subplots?` 來了解更多有關 `subplots()` 的資訊。

## 儲存格 116 [md]

要儲存 `fig` 的輸出，我們呼叫其 `savefig()` method。引數 `dpi` 是每英寸的點數，用來決定圖形在像素中的大小。

## 儲存格 117 [code]

```python
fig.savefig("Figure.png", dpi=400)
fig.savefig("Figure.pdf", dpi=200);
```

## 儲存格 118 [md]

我們可以使用逐步更新繼續修改 `fig`；例如，我們可以修改 $x$ 軸的範圍、重新儲存圖形，甚至重新顯示它。

## 儲存格 119 [code]

```python
axes[0,1].set_xlim([-1,1])
fig.savefig("Figure_updated.jpg")
fig
```

**輸出**

```
<Figure size 1500x500 with 6 Axes><figure omitted>
```

## 儲存格 120 [md]

我們現在建立一些更複雜的繪圖。
`ax.contour()` method 產生*等高線圖*，用來表示三維資料，類似於地形圖。它接受三個引數：

* `x` 值的向量（第一維度），
* `y` 值的向量（第二維度），和
* 一個矩陣，其元素對應於每對 `(x,y)` 座標的 `z` 值（第三維度）。

要建立 `x` 和 `y`，我們將使用指令 `np.linspace(a, b, n)`，它回傳一個包含 `n` 個數字的向量，從 `a` 開始，到 `b` 結束。

## 儲存格 121 [code]

```python
fig, ax = subplots(figsize=(8, 8))
x = np.linspace(-np.pi, np.pi, 50)
y = x
f = np.multiply.outer(np.cos(y), 1 / (1 + x**2))
ax.contour(x, y, f);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 122 [md]

我們可以透過向影像添加更多級別來增加解析度。

## 儲存格 123 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.contour(x, y, f, levels=45);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 124 [md]

要微調 `ax.contour()` function 的輸出，透過輸入 `?plt.contour` 查看說明檔案。

`ax.imshow()` method 與 `ax.contour()` 類似，不同之處在於它產生一個顏色編碼的繪圖，其顏色取決於 `z` 值。這被稱為*熱圖*，有時用於在天氣預報中繪製溫度。

## 儲存格 125 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.imshow(f);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 126 [md]

## 序列與切片表示法

## 儲存格 127 [md]

如上所述，function `np.linspace()` 可以用來建立一個數字序列。

## 儲存格 128 [code]

```python
seq1 = np.linspace(0, 10, 11)
seq1
```

**輸出**

```
array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10.])
```

## 儲存格 129 [md]

function `np.arange()` 回傳一個由 `step` 間隔開的數字序列。如果未指定 `step`，則使用預設值 $1$。讓我們建立一個從 $0$ 開始到 $10$ 結束的序列。

## 儲存格 130 [code]

```python
seq2 = np.arange(0, 10)
seq2
```

**輸出**

```
array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
```

## 儲存格 131 [md]

為什麼上面沒有輸出 $10$？這與 `Python` 中的*切片*表示法有關。
切片表示法用於索引序列，如 lists、tuples 和陣列。
假設我們想要檢索字串的第四到第六個（包含）項目。我們使用索引表示法 `[3:6]` 來取得字串的切片。

## 儲存格 132 [code]

```python
"hello world"[3:6]
```

**輸出**

```
'lo '
```

## 儲存格 133 [md]

在上面的程式碼區塊中，當在 `[]` 內使用時，表示法 `3:6` 是 `slice(3,6)` 的簡寫。

## 儲存格 134 [code]

```python
"hello world"[slice(3,6)]
```

**輸出**

```
'lo '
```

## 儲存格 135 [md]

你可能期望 `slice(3,6)` 輸出文字字串中的第四到第七個字元（回想 `Python` 從零開始索引），但它實際上輸出的是第四到第六個。
這也解釋了為什麼之前的 `np.arange(0, 10)` 指令只輸出從 $0$ 到 $9$ 的整數。
參見文件 `slice?` 來了解建立切片的實用選項。

## 儲存格 136 [md]

## 資料索引

## 儲存格 137 [md]

首先，我們建立一個二維 `numpy` 陣列。

## 儲存格 138 [code]

```python
A = np.array(np.arange(16)).reshape((4, 4))
A
```

**輸出**

```
array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11],
       [12, 13, 14, 15]])
```

## 儲存格 139 [md]

輸入 `A[1,2]` 檢索對應於第二列和第三欄的元素。（如往常一樣，`Python` 從 $0$ 開始索引。）

## 儲存格 140 [code]

```python
A[1,2]
```

**輸出**

```
np.int64(6)
```

## 儲存格 141 [md]

開括號符號 `[` 後的第一個數字指的是列，第二個數字指的是欄。

## 儲存格 142 [md]

### 索引列、欄和子矩陣

## 儲存格 143 [md]

要一次選擇多列，我們可以傳入一個指定我們選擇的 list。例如，`[1,3]` 將檢索第二列和第四列：

## 儲存格 144 [code]

```python
A[[1,3]]
```

**輸出**

```
array([[ 4,  5,  6,  7],
       [12, 13, 14, 15]])
```

## 儲存格 145 [md]

要選擇第一欄和第三欄，我們將 `[0,2]` 作為方括號中的第二個引數傳入。
在這種情況下，我們需要提供第一個引數 `:`，它選擇所有列。

## 儲存格 146 [code]

```python
A[:,[0,2]]
```

**輸出**

```
array([[ 0,  2],
       [ 4,  6],
       [ 8, 10],
       [12, 14]])
```

## 儲存格 147 [md]

現在，假設我們想要選擇由第二列和第四列以及第一欄和第三欄組成的子矩陣。這是索引變得稍微棘手的地方。自然地嘗試使用 lists 來檢索列和欄：

## 儲存格 148 [code]

```python
A[[1,3],[0,2]]
```

**輸出**

```
array([ 4, 14])
```

## 儲存格 149 [md]

糟糕——發生了什麼？我們得到了一個長度為二的一維陣列，等同於

## 儲存格 150 [code]

```python
np.array([A[1,0],A[3,2]])
```

**輸出**

```
array([ 4, 14])
```

## 儲存格 151 [md]

同樣地，以下程式碼未能萃取由第二列和第四列以及第一、第三和第四欄組成的子矩陣：

## 儲存格 152 [code]

```python
A[[1,3],[0,2,3]]
```

**輸出**

```
IndexError: shape mismatch: indexing arrays could not be broadcast together with shapes (2,) (3,)
```

## 儲存格 153 [md]

我們可以看出這裡出了什麼問題。當提供兩個索引 lists 時，`numpy` 的解釋是這些提供了一系列項目的 $i,j$ 索引對。這就是為什麼這對 lists 必須有相同的長度。然而，這不是我們的本意，因為我們在尋找一個子矩陣。

一種簡單的方法如下。我們首先透過子集化 `A` 的列來建立子矩陣，然後即時透過子集化其欄來進一步建立子矩陣。

## 儲存格 154 [code]

```python
A[[1,3]][:,[0,2]]
```

**輸出**

```
array([[ 4,  6],
       [12, 14]])
```

## 儲存格 155 [md]

有更有效的方法來實現相同的結果。

*便利 function* `np.ix_()` 允許我們透過建立中間*網格*物件，使用 lists 來萃取子矩陣。

## 儲存格 156 [code]

```python
idx = np.ix_([1,3],[0,2,3])
A[idx]
```

**輸出**

```
array([[ 4,  6,  7],
       [12, 14, 15]])
```

## 儲存格 157 [md]

或者，我們可以使用切片來有效地子集化矩陣。

切片 `1:4:2` 捕獲序列的第二和第四個項目，而切片 `0:3:2` 捕獲第一和第三個項目（切片序列中的第三個元素是步長大小）。

## 儲存格 158 [code]

```python
A[1:4:2,0:3:2]
```

**輸出**

```
array([[ 4,  6],
       [12, 14]])
```

## 儲存格 159 [md]

為什麼我們能夠使用切片直接檢索子矩陣，但不能使用 lists？
這是因為它們是不同的 `Python` 類型，並且被 `numpy` 不同地對待。
切片可以用來從任意序列中萃取物件，如字串、lists 和 tuples，而使用 lists 進行索引則更有限。

## 儲存格 160 [md]

### Boolean 索引

## 儲存格 161 [md]

在 `numpy` 中，*Boolean* 是一種等於 `True` 或 `False`（也分別表示為 $1$ 和 $0$）的類型。
下一行建立一個由 $0$ 組成的向量，以 Booleans 表示，長度等於 `A` 的第一維度。

## 儲存格 162 [code]

```python
keep_rows = np.zeros(A.shape[0], bool)
keep_rows
```

**輸出**

```
array([False, False, False, False])
```

## 儲存格 163 [md]

我們現在將其中兩個元素設定為 `True`。

## 儲存格 164 [code]

```python
keep_rows[[1,3]] = True
keep_rows
```

**輸出**

```
array([False,  True, False,  True])
```

## 儲存格 165 [md]

注意：當作為整數來看時，`keep_rows` 的元素與 `np.array([0,1,0,1])` 的值相同。下面，我們使用 `==` 來驗證它們的相等性。當套用到兩個陣列時，`==` 運算是逐元素套用的。

## 儲存格 166 [code]

```python
np.all(keep_rows == np.array([0,1,0,1]))
```

**輸出**

```
np.True_
```

## 儲存格 167 [md]

（在這裡，function `np.all()` 檢查了陣列的所有項目是否都是 `True`。類似的 function `np.any()` 可以用來檢查陣列的任何項目是否為 `True`。）

## 儲存格 168 [md]

然而，儘管 `np.array([0,1,0,1])` 和 `keep_rows` 根據 `==` 是相等的，但它們索引不同的列集！
前者檢索 `A` 的第一、第二、第一和第二列。

## 儲存格 169 [code]

```python
A[np.array([0,1,0,1])]
```

**輸出**

```
array([[0, 1, 2, 3],
       [4, 5, 6, 7],
       [0, 1, 2, 3],
       [4, 5, 6, 7]])
```

## 儲存格 170 [md]

相比之下，`keep_rows` 只檢索 `A` 的第二列和第四列——即 Boolean 等於 `TRUE` 的列。

## 儲存格 171 [code]

```python
A[keep_rows]
```

**輸出**

```
array([[ 4,  5,  6,  7],
       [12, 13, 14, 15]])
```

## 儲存格 172 [md]

這個例子顯示 Booleans 和整數被 `numpy` 不同地對待。

## 儲存格 173 [md]

我們再次使用 `np.ix_()` function 來建立一個包含第二列和第四列以及第一、第三和第四欄的網格。這次，我們將 function 套用到 Booleans，而不是 lists。

## 儲存格 174 [code]

```python
keep_cols = np.zeros(A.shape[1], bool)
keep_cols[[0, 2, 3]] = True
idx_bool = np.ix_(keep_rows, keep_cols)
A[idx_bool]
```

**輸出**

```
array([[ 4,  6,  7],
       [12, 14, 15]])
```

## 儲存格 175 [md]

我們也可以在 `np.ix_()` 的引數中混合使用 list 和 Booleans 陣列：

## 儲存格 176 [code]

```python
idx_mixed = np.ix_([1,3], keep_cols)
A[idx_mixed]
```

**輸出**

```
array([[ 4,  6,  7],
       [12, 14, 15]])
```

## 儲存格 177 [md]

有關 `numpy` 中索引的更多細節，大家可以參考之前提到的 `numpy` 教學。

## 儲存格 178 [md]

## 載入資料

## 儲存格 179 [md]

資料集通常包含不同類型的資料，並且可能有與列或行相關聯的名稱。因此，它們通常最適合使用 *data frame*（資料框）來容納。我們可以將資料框想像成一系列長度相同的陣列；這些是欄位。不同陣列中的項目可以結合形成列。`pandas` 函式庫可以用來建立和處理資料框物件。

## 儲存格 180 [md]

### 讀取資料集

## 儲存格 181 [md]

大多數分析的第一步都涉及將資料集匯入 `Python`。在嘗試載入資料集之前，我們必須確保 `Python` 知道在哪裡找到包含它的檔案。如果檔案與此 notebook 檔案位於同一位置，那麼我們就沒問題。否則，可以使用 `os.chdir()` 指令來*改變目錄*。（我們需要在呼叫 `os.chdir()` 之前先呼叫 `import os`。）

## 儲存格 182 [md]



```
# 此內容會顯示為程式碼
```

我們將從讀取[本書網站上提供](https://www.statlearning.com/s/ALL-CSV-FILES-2nd-Edition-corrected.zip)的 `Auto.csv` 開始。這是一個逗號分隔檔案，可以使用 `pd.read_csv()` 讀取：

## 儲存格 183 [code]

```python
drive.mount('/content/drive')
```

**輸出**

```
Mounted at /content/drive
```

## 儲存格 184 [code]

```python
# Replace DATA_PATH with your path
DATA_PATH = "/content/drive/MyDrive/00_Statistical_learning/Lab/Data/"
```

## 儲存格 185 [code]

```python
Auto = pd.read_csv(os.path.join(DATA_PATH,'Auto.csv'))
Auto
```

**輸出**

```
     Unnamed: 0   mpg  cylinders  displacement  horsepower  weight  \
0             1  18.0          8         307.0         130    3504   
1             2  15.0          8         350.0         165    3693   
2             3  18.0          8         318.0         150    3436   
3             4  16.0          8         304.0         150    3433   
4             5  17.0          8         302.0         140    3449   
..          ...   ...        ...           ...         ...     ...   
387         393  27.0          4         140.0          86    2790   
388         394  44.0          4          97.0          52    2130   
389         395  32.0          4         135.0          84    2295   
390         396  28.0          4         120.0          79    2625   
391         397  31.0          4         119.0          82    2720   

     acceleration  year  origin                       name  
0            12.0    70       1  chevrolet chevelle malibu  
1            11.5    70       1          buick skylark 320  
2            11.0    70       1         plymouth satellite  
3            12.0    70       1              amc rebel sst  
4            10.5    70       1                ford torino  
..            ...   ...     ...                        ...  
387          15.6    82       1            ford mustang gl  
388          24.6    82       2                  vw pickup  
389          11.6    82       1              dodge rampage  
390          18.6    82       1                ford ranger  
391          19.4    82       1                 chevy s-10  

[392 rows x 10 columns]
```

## 儲存格 186 [md]

本書網站也有此資料的空白分隔版本，稱為 `Auto.data`。可以按以下方式讀取：

## 儲存格 187 [code]

```python
Auto = pd.read_csv(os.path.join(DATA_PATH,'Auto.data'), sep=r"\s+")
Auto
```

**輸出**

```
      mpg  cylinders  displacement horsepower  weight  acceleration  year  \
0    18.0          8         307.0      130.0  3504.0          12.0    70   
1    15.0          8         350.0      165.0  3693.0          11.5    70   
2    18.0          8         318.0      150.0  3436.0          11.0    70   
3    16.0          8         304.0      150.0  3433.0          12.0    70   
4    17.0          8         302.0      140.0  3449.0          10.5    70   
..    ...        ...           ...        ...     ...           ...   ...   
392  27.0          4         140.0      86.00  2790.0          15.6    82   
393  44.0          4          97.0      52.00  2130.0          24.6    82   
394  32.0          4         135.0      84.00  2295.0          11.6    82   
395  28.0          4         120.0      79.00  2625.0          18.6    82   
396  31.0          4         119.0      82.00  2720.0          19.4    82   

     origin                       name  
0         1  chevrolet chevelle malibu  
1         1          buick skylark 320  
2         1         plymouth satellite  
3         1              amc rebel sst  
4         1                ford torino  
..      ...                        ...  
392       1            ford mustang gl  
393       2                  vw pickup  
394       1              dodge rampage  
395       1                ford ranger  
396       1                 chevy s-10  

[397 rows x 9 columns]
```

## 儲存格 188 [md]

`Auto.csv` 和 `Auto.data` 都只是純文字檔案。在將資料載入 `Python` 之前，建議使用文字編輯器或其他軟體（如 Microsoft Excel）來檢視它。

## 儲存格 189 [md]

我們現在來看看 `Auto` 中對應於變數 `horsepower` 的欄位：

## 儲存格 190 [code]

```python
Auto['horsepower']
```

**輸出**

```
0      130.0
1      165.0
2      150.0
3      150.0
4      140.0
       ...  
392    86.00
393    52.00
394    84.00
395    79.00
396    82.00
Name: horsepower, Length: 397, dtype: object
```

## 儲存格 191 [md]

我們看到這個欄位的 `dtype` 是 `object`。
事實證明，在讀取資料時，`horsepower` 欄位的所有值都被解釋為字串。
我們可以透過查看唯一值來找出原因。

## 儲存格 192 [code]

```python
np.unique(Auto['horsepower'])
```

**輸出**

```
array(['100.0', '102.0', '103.0', '105.0', '107.0', '108.0', '110.0',
       '112.0', '113.0', '115.0', '116.0', '120.0', '122.0', '125.0',
       '129.0', '130.0', '132.0', '133.0', '135.0', '137.0', '138.0',
       '139.0', '140.0', '142.0', '145.0', '148.0', '149.0', '150.0',
       '152.0', '153.0', '155.0', '158.0', '160.0', '165.0', '167.0',
       '170.0', '175.0', '180.0', '190.0', '193.0', '198.0', '200.0',
       '208.0', '210.0', '215.0', '220.0', '225.0', '230.0', '46.00',
       '48.00', '49.00', '52.00', '53.00', '54.00', '58.00', '60.00',
       '61.00', '62.00', '63.00', '64.00', '65.00', '66.00', '67.00',
       '68.00', '69.00', '70.00', '71.00', '72.00', '74.00', '75.00',
       '76.00', '77.00', '78.00', '79.00', '80.00', '81.00', '82.00',
       '83.00', '84.00', '85.00', '86.00', '87.00', '88.00', '89.00',
       '90.00', '91.00', '92.00', '93.00', '94.00', '95.00', '96.00',
       '97.00', '98.00', '?'], dtype=object)
```

## 儲存格 193 [md]

我們看到罪魁禍首是值 `?`，它被用來編碼遺漏值。

## 儲存格 194 [md]

要解決這個問題，我們必須向 `pd.read_csv()` 提供一個名為 `na_values` 的引數。
現在，檔案中每個 `?` 的實例都被替換為值 `np.nan`，意思是*不是數字*：

## 儲存格 195 [code]

```python
Auto = pd.read_csv(os.path.join(DATA_PATH,'Auto.data'),
                   na_values=['?'],
                   sep=r"\s+")
Auto['horsepower'].sum()
```

**輸出**

```
np.float64(40952.0)
```

## 儲存格 196 [md]

`Auto.shape` 屬性告訴我們資料有 397 個觀察值（或列）和 9 個變數（或欄）。

## 儲存格 197 [code]

```python
Auto.shape
```

**輸出**

```
(397, 9)
```

## 儲存格 198 [md]

有各種方法來處理遺漏資料。
在這個情況下，由於只有五列包含遺漏的觀察值，我們選擇使用 `Auto.dropna()` method 來簡單地移除這些列。

## 儲存格 199 [code]

```python
Auto_new = Auto.dropna()
Auto_new.shape
```

**輸出**

```
(392, 9)
```

## 儲存格 200 [md]

### 選擇列和欄的基礎

## 儲存格 201 [md]

我們可以使用 `Auto.columns` 來檢查變數名稱。

## 儲存格 202 [code]

```python
Auto = Auto_new # overwrite the previous value
Auto.columns
```

**輸出**

```
Index(['mpg', 'cylinders', 'displacement', 'horsepower', 'weight',
       'acceleration', 'year', 'origin', 'name'],
      dtype='object')
```

## 儲存格 203 [md]

存取資料框的列和欄與存取陣列的列和欄相似，但並非完全相同。
回想 `[]` method 的第一個引數總是套用到陣列的列。
同樣地，將切片傳入 `[]` method 會建立一個資料框，其*列*由切片決定：

## 儲存格 204 [code]

```python
Auto[:3]
```

**輸出**

```
    mpg  cylinders  displacement  horsepower  weight  acceleration  year  \
0  18.0          8         307.0       130.0  3504.0          12.0    70   
1  15.0          8         350.0       165.0  3693.0          11.5    70   
2  18.0          8         318.0       150.0  3436.0          11.0    70   

   origin                       name  
0       1  chevrolet chevelle malibu  
1       1          buick skylark 320  
2       1         plymouth satellite
```

## 儲存格 205 [md]

同樣地，陣列 Booleans 可以用來子集化列：

## 儲存格 206 [code]

```python
idx_80 = Auto['year'] > 80
Auto[idx_80]
```

**輸出**

```
      mpg  cylinders  displacement  horsepower  weight  acceleration  year  \
338  27.2          4         135.0        84.0  2490.0          15.7    81   
339  26.6          4         151.0        84.0  2635.0          16.4    81   
340  25.8          4         156.0        92.0  2620.0          14.4    81   
341  23.5          6         173.0       110.0  2725.0          12.6    81   
342  30.0          4         135.0        84.0  2385.0          12.9    81   
343  39.1          4          79.0        58.0  1755.0          16.9    81   
344  39.0          4          86.0        64.0  1875.0          16.4    81   
345  35.1          4          81.0        60.0  1760.0          16.1    81   
346  32.3          4          97.0        67.0  2065.0          17.8    81   
347  37.0          4          85.0        65.0  1975.0          19.4    81   
348  37.7          4          89.0        62.0  2050.0          17.3    81   
349  34.1          4          91.0        68.0  1985.0          16.0    81   
350  34.7          4         105.0        63.0  2215.0          14.9    81   
351  34.4          4          98.0        65.0  2045.0          16.2    81   
352  29.9          4          98.0        65.0  2380.0          20.7    81   
353  33.0          4         105.0        74.0  2190.0          14.2    81   
355  33.7          4         107.0        75.0  2210.0          14.4    81   
356  32.4          4         108.0        75.0  2350.0          16.8    81   
357  32.9          4         119.0       100.0  2615.0          14.8    81   
358  31.6          4         120.0        74.0  2635.0          18.3    81   
359  28.1          4         141.0        80.0  3230.0          20.4    81   
360  30.7          6         145.0        76.0  3160.0          19.6    81   
361  25.4          6         168.0       116.0  2900.0          12.6    81   
362  24.2          6         146.0       120.0  2930.0          13.8    81   
363  22.4          6         231.0       110.0  3415.0          15.8    81   
364  26.6          8         350.0       105.0  3725.0          19.0    81   
365  20.2          6         200.0        88.0  3060.0          17.1    81   
366  17.6          6         225.0        85.0  3465.0          16.6    81   
367  28.0          4         112.0        88.0  2605.0          19.6    82   
368  27.0          4         112.0        88.0  2640.0          18.6    82   
369  34.0          4         112.0        88.0  2395.0          18.0    82   
370  31.0          4         112.0        85.0  2575.0          16.2    82   
371  29.0          4         135.0        84.0  2525.0          16.0    82   
372  27.0          4         151.0        90.0  2735.0          18.0    82   
373  24.0          4         140.0        92.0  2865.0          16.4    82   
374  36.0          4         105.0        74.0  1980.0          15.3    82   
375  37.0          4          91.0        68.0  2025.0          18.2    82   
376  31.0          4          91.0        68.0  1970.0          17.6    82   
377  38.0          4         105.0        63.0  2125.0          14.7    82   
378  36.0          4          98.0        70.0  2125.0          17.3    82   
379  36.0          4         120.0        88.0  2160.0          14.5    82   
380  36.0          4         107.0        75.0  2205.0          14.5    82   
381  34.0          4         108.0        70.0  2245.0          16.9    82   
382  38.0          4          91.0        67.0  1965.0          15.0    82   
383  32.0          4          91.0        67.0  1965.0          15.7    82   
384  38.0          4          91.0        67.0  1995.0          16.2    82   
385  25.0          6         181.0       110.0  2945.0          16.4    82   
386  38.0          6         262.0        85.0  3015.0          17.0    82   
387  26.0          4         156.0        92.0  2585.0          14.5    82   
388  22.0          6         232.0       112.0  2835.0          14.7    82   
389  32.0          4         144.0        96.0  2665.0          13.9    82   
390  36.0          4         135.0        84.0  2370.0          13.0    82   
391  27.0          4         151.0        90.0  2950.0          17.3    82   
392  27.0          4         140.0        86.0  2790.0          15.6    82   
393  44.0          4          97.0        52.0  2130.0          24.6    82   
394  32.0          4         135.0        84.0  2295.0          11.6    82   
395  28.0          4         120.0        79.0  2625.0          18.6    82   
396  31.0          4         119.0        82.0  2720.0          19.4    82   

     origin                               name  
338       1                   plymouth reliant  
339       1                      buick skylark  
340       1             dodge aries wagon (sw)  
341       1                 chevrolet citation  
342       1                   plymouth reliant  
343       3                     toyota starlet  
344       1                     plymouth champ  
345       3                   honda civic 1300  
346       3                             subaru  
347       3                     datsun 210 mpg  
348       3                      toyota tercel  
349       3                        mazda glc 4  
350       1                 plymouth horizon 4  
351       1                     ford escort 4w  
352       1                     ford escort 2h  
353       2                   volkswagen jetta  
355       3                      honda prelude  
356       3                     toyota corolla  
357       3                       datsun 200sx  
358       3                          mazda 626  
359       2          peugeot 505s turbo diesel  
360       2                       volvo diesel  
361       3                    toyota cressida  
362       3                  datsun 810 maxima  
363       1                      buick century  
364       1              oldsmobile cutlass ls  
365       1                    ford granada gl  
366       1             chrysler lebaron salon  
367       1                 chevrolet cavalier  
368       1           chevrolet cavalier wagon  
369       1          chevrolet cavalier 2-door  
370       1         pontiac j2000 se hatchback  
371       1                     dodge aries se  
372       1                    pontiac phoenix  
373       1               ford fairmont futura  
374       2                volkswagen rabbit l  
375       3                 mazda glc custom l  
376       3                   mazda glc custom  
377       1             plymouth horizon miser  
378       1                     mercury lynx l  
379       3                   nissan stanza xe  
380       3                       honda accord  
381       3                     toyota corolla  
382       3                        honda civic  
383       3                 honda civic (auto)  
384       3                      datsun 310 gx  
385       1              buick century limited  
386       1  oldsmobile cutlass ciera (diesel)  
387       1         chrysler lebaron medallion  
388       1                     ford granada l  
389       3                   toyota celica gt  
390       1                  dodge charger 2.2  
391       1                   chevrolet camaro  
392       1                    ford mustang gl  
393       2                          vw pickup  
394       1                      dodge rampage  
395       1                        ford ranger  
396       1                         chevy s-10
```

## 儲存格 207 [md]

然而，如果我們將字串 list 傳入 `[]` method，那麼我們會得到一個包含對應*欄*集合的資料框。

## 儲存格 208 [code]

```python
Auto[['mpg', 'horsepower']]
```

**輸出**

```
      mpg  horsepower
0    18.0       130.0
1    15.0       165.0
2    18.0       150.0
3    16.0       150.0
4    17.0       140.0
..    ...         ...
392  27.0        86.0
393  44.0        52.0
394  32.0        84.0
395  28.0        79.0
396  31.0        82.0

[392 rows x 2 columns]
```

## 儲存格 209 [md]

由於我們在載入資料框時沒有指定*索引*欄，列被使用整數 0 到 396 來標記。

## 儲存格 210 [code]

```python
Auto.index
```

**輸出**

```
Index([  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,
       ...
       387, 388, 389, 390, 391, 392, 393, 394, 395, 396],
      dtype='int64', length=392)
```

## 儲存格 211 [md]

我們可以使用 `set_index()` method 來使用 `Auto['name']` 的內容重新命名列。

## 儲存格 212 [code]

```python
Auto_re = Auto.set_index('name')
Auto_re
```

**輸出**

```
                            mpg  cylinders  displacement  horsepower  weight  \
name                                                                           
chevrolet chevelle malibu  18.0          8         307.0       130.0  3504.0   
buick skylark 320          15.0          8         350.0       165.0  3693.0   
plymouth satellite         18.0          8         318.0       150.0  3436.0   
amc rebel sst              16.0          8         304.0       150.0  3433.0   
ford torino                17.0          8         302.0       140.0  3449.0   
...                         ...        ...           ...         ...     ...   
ford mustang gl            27.0          4         140.0        86.0  2790.0   
vw pickup                  44.0          4          97.0        52.0  2130.0   
dodge rampage              32.0          4         135.0        84.0  2295.0   
ford ranger                28.0          4         120.0        79.0  2625.0   
chevy s-10                 31.0          4         119.0        82.0  2720.0   

                           acceleration  year  origin  
name                                                   
chevrolet chevelle malibu          12.0    70       1  
buick skylark 320                  11.5    70       1  
plymouth satellite                 11.0    70       1  
amc rebel sst                      12.0    70       1  
ford torino                        10.5    70       1  
...                                 ...   ...     ...  
ford mustang gl                    15.6    82       1  
vw pickup                          24.6    82       2  
dodge rampage                      11.6    82       1  
ford ranger                        18.6    82       1  
chevy s-10                         19.4    82       1  

[392 rows x 8 columns]
```

## 儲存格 213 [code]

```python
Auto_re.columns
```

**輸出**

```
Index(['mpg', 'cylinders', 'displacement', 'horsepower', 'weight',
       'acceleration', 'year', 'origin'],
      dtype='object')
```

## 儲存格 214 [md]

我們看到欄位 `'name'` 已經不在了。

現在索引已經設定為 `name`，我們可以使用 `Auto` 的 `loc[]` method 透過 `name` 來存取資料框的列：

## 儲存格 215 [code]

```python
rows = ['amc rebel sst', 'ford torino']
Auto_re.loc[rows]
```

**輸出**

```
                mpg  cylinders  displacement  horsepower  weight  \
name                                                               
amc rebel sst  16.0          8         304.0       150.0  3433.0   
ford torino    17.0          8         302.0       140.0  3449.0   

               acceleration  year  origin  
name                                       
amc rebel sst          12.0    70       1  
ford torino            10.5    70       1
```

## 儲存格 216 [md]

作為使用索引名稱的替代方案，我們可以使用 `iloc[]` method 來檢索 `Auto` 的第 4 列和第 5 列：

## 儲存格 217 [code]

```python
Auto_re.iloc[[3,4]]
```

**輸出**

```
                mpg  cylinders  displacement  horsepower  weight  \
name                                                               
amc rebel sst  16.0          8         304.0       150.0  3433.0   
ford torino    17.0          8         302.0       140.0  3449.0   

               acceleration  year  origin  
name                                       
amc rebel sst          12.0    70       1  
ford torino            10.5    70       1
```

## 儲存格 218 [md]

我們也可以用它來檢索 `Auto_re` 的第 1、第 3 和第 4 欄：

## 儲存格 219 [code]

```python
Auto_re.iloc[:,[0,2,3]]
```

**輸出**

```
                            mpg  displacement  horsepower
name                                                     
chevrolet chevelle malibu  18.0         307.0       130.0
buick skylark 320          15.0         350.0       165.0
plymouth satellite         18.0         318.0       150.0
amc rebel sst              16.0         304.0       150.0
ford torino                17.0         302.0       140.0
...                         ...           ...         ...
ford mustang gl            27.0         140.0        86.0
vw pickup                  44.0          97.0        52.0
dodge rampage              32.0         135.0        84.0
ford ranger                28.0         120.0        79.0
chevy s-10                 31.0         119.0        82.0

[392 rows x 3 columns]
```

## 儲存格 220 [md]

我們可以透過單次呼叫 `iloc[]` 來萃取第 4 和第 5 列以及第 1、第 3 和第 4 欄：

## 儲存格 221 [code]

```python
Auto_re.iloc[[3,4],[0,2,3]]
```

**輸出**

```
                mpg  displacement  horsepower
name                                         
amc rebel sst  16.0         304.0       150.0
ford torino    17.0         302.0       140.0
```

## 儲存格 222 [md]

索引項目不需要是唯一的：資料框中有幾輛車被命名為 `ford galaxie 500`。

## 儲存格 223 [code]

```python
Auto_re.loc['ford galaxie 500', ['mpg', 'origin']]
```

**輸出**

```
                   mpg  origin
name                          
ford galaxie 500  15.0       1
ford galaxie 500  14.0       1
ford galaxie 500  14.0       1
```

## 儲存格 224 [md]

### 更多關於選擇列和欄的內容

## 儲存格 225 [md]

現在假設我們想要建立一個由 `weight` 和 `origin` 組成的資料框，用於 `year` 大於 80 的汽車子集——即 1980 年後製造的汽車。
為此，我們先建立索引列的 Boolean 陣列。
`loc[]` method 允許 Boolean 項目以及字串：

## 儲存格 226 [code]

```python
idx_80 = Auto_re['year'] > 80
Auto_re.loc[idx_80, ['weight', 'origin']]
```

**輸出**

```
                                   weight  origin
name                                             
plymouth reliant                   2490.0       1
buick skylark                      2635.0       1
dodge aries wagon (sw)             2620.0       1
chevrolet citation                 2725.0       1
plymouth reliant                   2385.0       1
toyota starlet                     1755.0       3
plymouth champ                     1875.0       1
honda civic 1300                   1760.0       3
subaru                             2065.0       3
datsun 210 mpg                     1975.0       3
toyota tercel                      2050.0       3
mazda glc 4                        1985.0       3
plymouth horizon 4                 2215.0       1
ford escort 4w                     2045.0       1
ford escort 2h                     2380.0       1
volkswagen jetta                   2190.0       2
honda prelude                      2210.0       3
toyota corolla                     2350.0       3
datsun 200sx                       2615.0       3
mazda 626                          2635.0       3
peugeot 505s turbo diesel          3230.0       2
volvo diesel                       3160.0       2
toyota cressida                    2900.0       3
datsun 810 maxima                  2930.0       3
buick century                      3415.0       1
oldsmobile cutlass ls              3725.0       1
ford granada gl                    3060.0       1
chrysler lebaron salon             3465.0       1
chevrolet cavalier                 2605.0       1
chevrolet cavalier wagon           2640.0       1
chevrolet cavalier 2-door          2395.0       1
pontiac j2000 se hatchback         2575.0       1
dodge aries se                     2525.0       1
pontiac phoenix                    2735.0       1
ford fairmont futura               2865.0       1
volkswagen rabbit l                1980.0       2
mazda glc custom l                 2025.0       3
mazda glc custom                   1970.0       3
plymouth horizon miser             2125.0       1
mercury lynx l                     2125.0       1
nissan stanza xe                   2160.0       3
honda accord                       2205.0       3
toyota corolla                     2245.0       3
honda civic                        1965.0       3
honda civic (auto)                 1965.0       3
datsun 310 gx                      1995.0       3
buick century limited              2945.0       1
oldsmobile cutlass ciera (diesel)  3015.0       1
chrysler lebaron medallion         2585.0       1
ford granada l                     2835.0       1
toyota celica gt                   2665.0       3
dodge charger 2.2                  2370.0       1
chevrolet camaro                   2950.0       1
ford mustang gl                    2790.0       1
vw pickup                          2130.0       2
dodge rampage                      2295.0       1
ford ranger                        2625.0       1
chevy s-10                         2720.0       1
```

## 儲存格 227 [md]

要更簡潔地做到這一點，我們可以使用稱為 `lambda` 的匿名函式：

## 儲存格 228 [code]

```python
Auto_re.loc[lambda df: df['year'] > 80, ['weight', 'origin']]
```

**輸出**

```
                                   weight  origin
name                                             
plymouth reliant                   2490.0       1
buick skylark                      2635.0       1
dodge aries wagon (sw)             2620.0       1
chevrolet citation                 2725.0       1
plymouth reliant                   2385.0       1
toyota starlet                     1755.0       3
plymouth champ                     1875.0       1
honda civic 1300                   1760.0       3
subaru                             2065.0       3
datsun 210 mpg                     1975.0       3
toyota tercel                      2050.0       3
mazda glc 4                        1985.0       3
plymouth horizon 4                 2215.0       1
ford escort 4w                     2045.0       1
ford escort 2h                     2380.0       1
volkswagen jetta                   2190.0       2
honda prelude                      2210.0       3
toyota corolla                     2350.0       3
datsun 200sx                       2615.0       3
mazda 626                          2635.0       3
peugeot 505s turbo diesel          3230.0       2
volvo diesel                       3160.0       2
toyota cressida                    2900.0       3
datsun 810 maxima                  2930.0       3
buick century                      3415.0       1
oldsmobile cutlass ls              3725.0       1
ford granada gl                    3060.0       1
chrysler lebaron salon             3465.0       1
chevrolet cavalier                 2605.0       1
chevrolet cavalier wagon           2640.0       1
chevrolet cavalier 2-door          2395.0       1
pontiac j2000 se hatchback         2575.0       1
dodge aries se                     2525.0       1
pontiac phoenix                    2735.0       1
ford fairmont futura               2865.0       1
volkswagen rabbit l                1980.0       2
mazda glc custom l                 2025.0       3
mazda glc custom                   1970.0       3
plymouth horizon miser             2125.0       1
mercury lynx l                     2125.0       1
nissan stanza xe                   2160.0       3
honda accord                       2205.0       3
toyota corolla                     2245.0       3
honda civic                        1965.0       3
honda civic (auto)                 1965.0       3
datsun 310 gx                      1995.0       3
buick century limited              2945.0       1
oldsmobile cutlass ciera (diesel)  3015.0       1
chrysler lebaron medallion         2585.0       1
ford granada l                     2835.0       1
toyota celica gt                   2665.0       3
dodge charger 2.2                  2370.0       1
chevrolet camaro                   2950.0       1
ford mustang gl                    2790.0       1
vw pickup                          2130.0       2
dodge rampage                      2295.0       1
ford ranger                        2625.0       1
chevy s-10                         2720.0       1
```

## 儲存格 229 [md]

`lambda` 呼叫建立了一個接受單一引數（此處為 `df`）的函式，並回傳 `df['year']>80`。
由於它是在資料框 `Auto_re` 的 `loc[]` method 內建立的，該資料框將作為提供的引數。
作為使用 `lambda` 的另一個例子，假設我們想要所有在 1980 年後製造且每加侖汽油行駛超過 30 英里的汽車：

## 儲存格 230 [code]

```python
Auto_re.loc[lambda df: (df['year'] > 80) & (df['mpg'] > 30),
            ['weight', 'origin']
           ]
```

**輸出**

```
                                   weight  origin
name                                             
toyota starlet                     1755.0       3
plymouth champ                     1875.0       1
honda civic 1300                   1760.0       3
subaru                             2065.0       3
datsun 210 mpg                     1975.0       3
toyota tercel                      2050.0       3
mazda glc 4                        1985.0       3
plymouth horizon 4                 2215.0       1
ford escort 4w                     2045.0       1
volkswagen jetta                   2190.0       2
honda prelude                      2210.0       3
toyota corolla                     2350.0       3
datsun 200sx                       2615.0       3
mazda 626                          2635.0       3
volvo diesel                       3160.0       2
chevrolet cavalier 2-door          2395.0       1
pontiac j2000 se hatchback         2575.0       1
volkswagen rabbit l                1980.0       2
mazda glc custom l                 2025.0       3
mazda glc custom                   1970.0       3
plymouth horizon miser             2125.0       1
mercury lynx l                     2125.0       1
nissan stanza xe                   2160.0       3
honda accord                       2205.0       3
toyota corolla                     2245.0       3
honda civic                        1965.0       3
honda civic (auto)                 1965.0       3
datsun 310 gx                      1995.0       3
oldsmobile cutlass ciera (diesel)  3015.0       1
toyota celica gt                   2665.0       3
dodge charger 2.2                  2370.0       1
vw pickup                          2130.0       2
dodge rampage                      2295.0       1
chevy s-10                         2720.0       1
```

## 儲存格 231 [md]

符號 `&` 執行逐元素的 *and* 運算。
作為另一個例子，假設我們想要檢索所有 `displacement` 小於 300 的 `Ford` 和 `Datsun` 汽車。我們使用資料框的 `index` 屬性的 `str.contains()` method 來檢查每個 `name` 項目是否包含字串 `ford` 或 `datsun`：

## 儲存格 232 [code]

```python
Auto_re.loc[lambda df: (df['displacement'] < 300)
                       & (df.index.str.contains('ford')
                       | df.index.str.contains('datsun')),
            ['weight', 'origin']
           ]
```

**輸出**

```
                       weight  origin
name                                 
ford maverick          2587.0       1
datsun pl510           2130.0       3
datsun pl510           2130.0       3
ford torino 500        3302.0       1
ford mustang           3139.0       1
datsun 1200            1613.0       3
ford pinto runabout    2226.0       1
ford pinto (sw)        2395.0       1
datsun 510 (sw)        2288.0       3
ford maverick          3021.0       1
datsun 610             2379.0       3
ford pinto             2310.0       1
datsun b210            1950.0       3
ford pinto             2451.0       1
datsun 710             2003.0       3
ford maverick          3158.0       1
ford pinto             2639.0       1
datsun 710             2545.0       3
ford pinto             2984.0       1
ford maverick          3012.0       1
ford granada ghia      3574.0       1
datsun b-210           1990.0       3
ford pinto             2565.0       1
datsun f-10 hatchback  1945.0       3
ford granada           3525.0       1
ford mustang ii 2+2    2755.0       1
datsun 810             2815.0       3
ford fiesta            1800.0       1
datsun b210 gx         2070.0       3
ford fairmont (auto)   2965.0       1
ford fairmont (man)    2720.0       1
datsun 510             2300.0       3
datsun 200-sx          2405.0       3
ford fairmont 4        2890.0       1
datsun 210             2020.0       3
datsun 310             2019.0       3
ford fairmont          2870.0       1
datsun 510 hatchback   2434.0       3
datsun 210             2110.0       3
datsun 280-zx          2910.0       3
datsun 210 mpg         1975.0       3
ford escort 4w         2045.0       1
ford escort 2h         2380.0       1
datsun 200sx           2615.0       3
datsun 810 maxima      2930.0       3
ford granada gl        3060.0       1
ford fairmont futura   2865.0       1
datsun 310 gx          1995.0       3
ford granada l         2835.0       1
ford mustang gl        2790.0       1
ford ranger            2625.0       1
```

## 儲存格 233 [md]

這裡，符號 `|` 執行逐元素的 *or* 運算。

總結來說，有一套強大的運算可用於索引資料框的列和欄。對於基於整數的查詢，使用 `iloc[]` method。對於字串和 Boolean 選擇，使用 `loc[]` method。對於過濾列的函式查詢，在列引數中使用帶有函式（通常是 `lambda`）的 `loc[]` method。

## 儲存格 234 [md]

## For 迴圈

## 儲存格 235 [md]

`for` 迴圈是許多程式語言中的標準工具，它重複評估某些程式碼區塊，同時在程式碼內改變不同的值。例如，假設我們迴圈遍歷 list 的元素並計算它們的總和。

## 儲存格 236 [code]

```python
total = 0
for value in [3,2,19]:
    total += value
print('Total is: {0}'.format(total))
```

**輸出**

```
Total is: 24
```

## 儲存格 237 [md]

`for` 陳述式下面的縮排程式碼會針對 `for` 陳述式中指定的序列中的每個值執行。迴圈在 cell 結束時或當程式碼以與原始 `for` 陳述式相同的縮排層級進行縮排時結束。我們看到上面印出總數的最後一行只有在 for 迴圈終止後才執行一次。迴圈可以透過額外的縮排進行巢狀化。

## 儲存格 238 [code]

```python
total = 0
for value in [2,3,19]:
    for weight in [3, 2, 1]:
        total += value * weight
print('Total is: {0}'.format(total))
```

**輸出**

```
Total is: 144
```

## 儲存格 239 [md]

上面，我們對 `value` 和 `weight` 的每個組合進行了加總。我們也利用了 `Python` 中的*遞增*記號：表達式 `a += b` 等同於 `a = a + b`。除了是便利記號外，這在計算量大的任務中可以節省時間，因為 `a+b` 的中間值不需要被顯式建立。

也許更常見的任務是對 `(value, weight)` 成對進行加總。例如，要計算隨機變數的平均值，該變數可能取值 2、3 或 19，機率分別為 0.2、0.3、0.5，我們會計算加權和。這樣的任務通常可以使用 `zip()` function 來完成，它會迴圈遍歷序列元組。

## 儲存格 240 [code]

```python
total = 0
for value, weight in zip([2,3,19],
                         [0.2,0.3,0.5]):
    total += weight * value
print('Weighted average is: {0}'.format(total))
```

**輸出**

```
Weighted average is: 10.8
```

## 儲存格 241 [md]

### String 格式化

## 儲存格 242 [md]

在上面的程式碼區塊中，我們也印出了一個顯示總數的字串。然而，物件 `total` 是整數，而非字串。將某個值插入字串是一個常見任務，使用 `Python` 中一些強大的字串格式化工具可以輕鬆完成。許多資料清理任務涉及以程式方式操作、產生字串。

例如，我們可能想要迴圈遍歷資料框的欄位並印出每個欄位中遺漏的百分比。讓我們建立一個資料框 `D`，其欄位中有 20% 的項目是遺漏的，即設定為 `np.nan`。我們將使用 `rng.standard_normal()` 從平均值為 0、變異數為 1 的常態分佈中建立 `D` 中的值，然後使用 `rng.choice()` 覆寫一些隨機項目。

## 儲存格 243 [code]

```python
rng = np.random.default_rng(1)
A = rng.standard_normal((127, 5))
M = rng.choice([0, np.nan], p=[0.8,0.2], size=A.shape)
A += M
D = pd.DataFrame(A, columns=['food',
                             'bar',
                             'pickle',
                             'snack',
                             'popcorn'])
D[:3]
```

**輸出**

```
       food       bar    pickle     snack   popcorn
0  0.345584  0.821618  0.330437 -1.303157       NaN
1       NaN -0.536953  0.581118  0.364572  0.294132
2       NaN  0.546713       NaN -0.162910 -0.482119
```

## 儲存格 244 [code]

```python
for col in D.columns:
    template = 'Column "{0}" has {1:.2%} missing values'
    print(template.format(col,
          np.isnan(D[col]).mean()))
```

**輸出**

```
Column "food" has 16.54% missing values
Column "bar" has 25.98% missing values
Column "pickle" has 29.13% missing values
Column "snack" has 21.26% missing values
Column "popcorn" has 22.83% missing values
```

## 儲存格 245 [md]

我們看到 `template.format()` method 需要兩個引數 `{0}` 和 `{1:.2%}`，後者包含一些格式化資訊。特別是，它指定第二個引數應表示為具有兩位小數的百分比。

參考資料 [docs.python.org/3/library/string.html](https://docs.python.org/3/library/string.html) 包含許多有用、更複雜的例子。

## 儲存格 246 [md]

## 其他圖形與數值摘要

## 儲存格 247 [md]

我們可以使用 `ax.plot()` 或 `ax.scatter()` functions 來顯示定量變數。然而，簡單地輸入變數名稱會產生錯誤訊息，因為 `Python` 不知道要在 `Auto` 資料集中尋找這些變數。

## 儲存格 248 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.plot(horsepower, mpg, 'o');
```

**輸出**

```
NameError: name 'horsepower' is not defined<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 249 [md]

我們可以透過直接存取欄位來解決這個問題：

## 儲存格 250 [code]

```python
fig, ax = subplots(figsize=(8, 8))
ax.plot(Auto['horsepower'], Auto['mpg'], 'o');
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 251 [md]

或者，我們可以使用 `plot()` method 和呼叫 `Auto.plot()`。使用這個 method，變數可以透過名稱存取。資料框的繪圖 methods 回傳熟悉的物件：軸。我們可以使用它來更新繪圖，如我們之前所做的：

## 儲存格 252 [code]

```python
ax = Auto.plot.scatter('horsepower', 'mpg')
ax.set_title('Horsepower vs. MPG');
```

**輸出**

```
<Figure size 640x480 with 1 Axes><figure omitted>
```

## 儲存格 253 [md]

如果我們想儲存包含給定軸的圖形，我們可以透過存取 `figure` 屬性來找到相關圖形：

## 儲存格 254 [code]

```python
fig = ax.figure
fig.savefig('horsepower_mpg.png');
```

## 儲存格 255 [md]

我們可以進一步指示資料框繪製到特定的軸物件。在這種情況下，對應的 `plot()` method 將回傳我們作為引數傳入的修改軸。注意：當我們請求一個一維的繪圖網格時，物件 `axes` 同樣是一維的。我們將散佈圖放在圖形內三個繪圖的中間繪圖中。

## 儲存格 256 [code]

```python
fig, axes = subplots(ncols=3, figsize=(15, 5))
Auto.plot.scatter('horsepower', 'mpg', ax=axes[1]);
```

**輸出**

```
<Figure size 1500x500 with 3 Axes><figure omitted>
```

## 儲存格 257 [md]

另外請注意，資料框的欄位可以作為屬性存取：嘗試輸入 `Auto.horsepower`。

## 儲存格 258 [md]

我們現在考慮 `cylinders` 變數。輸入 `Auto.cylinders.dtype` 會顯示它被視為定量變數。然而，由於這個變數只有少數可能的值，我們可能希望將其視為定性變數。下面，我們將 `cylinders` 欄位替換為 `Auto.cylinders` 的分類版本。function `pd.Series()` 得名於 `pandas` 經常用於時間序列應用的事實。

## 儲存格 259 [code]

```python
Auto.cylinders = pd.Series(Auto.cylinders, dtype='category')
Auto.cylinders.dtype
```

**輸出**

```
CategoricalDtype(categories=[3, 4, 5, 6, 8], ordered=None, categories_dtype=int64)
```

## 儲存格 260 [md]

現在 `cylinders` 是定性的，我們可以使用 `boxplot()` method 來顯示它。

## 儲存格 261 [code]

```python
fig, ax = subplots(figsize=(8, 8))
Auto.boxplot('mpg', by='cylinders', ax=ax);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 262 [md]

`hist()` method 可以用來繪製*直方圖*。

## 儲存格 263 [code]

```python
fig, ax = subplots(figsize=(8, 8))
Auto.hist('mpg', ax=ax);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 264 [md]

顏色條和 bins 數量可以改變：

## 儲存格 265 [code]

```python
fig, ax = subplots(figsize=(8, 8))
Auto.hist('mpg', color='red', bins=12, ax=ax);
```

**輸出**

```
<Figure size 800x800 with 1 Axes><figure omitted>
```

## 儲存格 266 [md]

請參見 `Auto.hist?` 以獲取更多繪圖選項。

我們可以使用 `pd.plotting.scatter_matrix()` function 來建立*散佈圖矩陣*，以視覺化資料框中欄位之間的所有成對關係。

## 儲存格 267 [code]

```python
pd.plotting.scatter_matrix(Auto);
```

**輸出**

```
<Figure size 640x480 with 49 Axes><figure omitted>
```

## 儲存格 268 [md]

我們也可以為變數子集產生散佈圖。

## 儲存格 269 [code]

```python
pd.plotting.scatter_matrix(Auto[['mpg',
                                 'displacement',
                                 'weight']]);
```

**輸出**

```
<Figure size 640x480 with 9 Axes><figure omitted>
```

## 儲存格 270 [md]

`describe()` method 為資料框中的每個欄位產生數值摘要。

## 儲存格 271 [code]

```python
Auto[['mpg', 'weight']].describe()
```

**輸出**

```
              mpg       weight
count  392.000000   392.000000
mean    23.445918  2977.584184
std      7.805007   849.402560
min      9.000000  1613.000000
25%     17.000000  2225.250000
50%     22.750000  2803.500000
75%     29.000000  3614.750000
max     46.600000  5140.000000
```

## 儲存格 272 [md]

我們也可以只產生單一欄位的摘要。

## 儲存格 273 [code]

```python
Auto['cylinders'].describe()
Auto['mpg'].describe()
```

**輸出**

```
count    392.000000
mean      23.445918
std        7.805007
min        9.000000
25%       17.000000
50%       22.750000
75%       29.000000
max       46.600000
Name: mpg, dtype: float64
```

## 儲存格 274 [md]

要退出 `Jupyter`，選擇「檔案 / 關閉並停止」。

