# Latency Numbers Every Programmer Should Know（jboner gist 2841832）
- URL: https://gist.github.com/jboner/2841832
- 講義頁: p.55
- 抓取狀態: OK（GitHub gist HTML，讀取 `latency.txt` 內容）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 表頭："Latency Comparison Numbers (~2012 except when noted)"。
- 與記憶體階層有關的列（原文數字）：
  | 操作 | 延遲 | 備註（原文） |
  |---|---|---|
  | L1 cache reference | 0.5 ns | |
  | Branch mispredict | 5 ns | |
  | L2 cache reference | 7 ns | "14x L1 cache" |
  | Mutex lock/unlock | 25 ns | |
  | Main memory reference | 100 ns | "20x L2 cache, 200x L1 cache" |
  | Compress 1K bytes with Zippy | 3,000 ns | |
  | Read 4K randomly from SSD | 150,000 ns | |
  | Read 1 MB sequentially from memory | 250,000 ns | |
  | Read 1 MB sequentially from SSD | 1,000,000 ns | "4X memory" |
  | Disk seek | 10,000,000 ns | |
  | Read 1 MB sequentially from disk | 20,000,000 ns | "80x memory, 20X SSD" |
- Credit："By Jeff Dean"；"Originally by Peter Norvig"。
- 檔案近期被加入 2026 年的 LLM 列（例如 "Frontier LLM, generate 1 token 20,000,000 ns"、"Local LLM, generate 1 token 15,000,000 ns"），標註 "(2026)"。

## 可用的算例或圖解想法
- **與 XGBoost §4.2 cache-aware access 的關係（推論，gist 本身未提 XGBoost）**：pre-sorted column block 依「特徵值順序」掃描，但梯度統計 $g_i,h_i$ 依「列索引」存放，於是每一步都是對主記憶體的隨機存取。若資料不在 cache，一次 main memory reference ≈ 100 ns，是 L1（0.5 ns）的 200 倍；論文 §4.2 說的 "non-continuous memory access" 與 "cache miss" 就是付這個差價。prefetch 到 thread 內 buffer 再 mini-batch 累加、以及把 block 大小設在 $2^{16}$ 列讓梯度統計放得進 cache，都是在把 100 ns 等級的存取換成 cache 等級的存取。
- **與 §4.3 out-of-core 的關係（推論）**：磁碟順序讀 1 MB 20 ms、是記憶體的 80 倍，而 "Compress 1K bytes with Zippy" 只要 3 µs——說明論文為何用 block compression「以解壓運算換磁碟 IO」，以及多磁碟 sharding 增加吞吐。
- 粗估：$n=10^7$ 筆、每層每特徵一次掃描，若每次梯度讀取都 cache miss，約 $10^7\times100\text{ ns}=1$ s；全在 L1 則約 5 ms（純推論的數量級示意，非實測）。

## 與下列問題的關聯（只寫有關的）
- 精確貪婪的成本（優先查證 1 的系統面）：除了排序的 $\log n$，exact 法依特徵序存取梯度的隨機記憶體存取也是成本來源；直方圖法把連續值換成 bin 索引、累加到小陣列，存取更連續（推論）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 數字是 "~2012"，硬體已變（SSD、記憶體頻寬尤其明顯）；只適合當數量級比較。
- gist 已被修改加入 2026 年 LLM 延遲列，與講義當時看到的版本可能不同；引用時寫讀取日期。
