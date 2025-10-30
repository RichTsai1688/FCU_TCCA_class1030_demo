# 設備振動監測 Agent 專案

這是一個使用 AI Agent 進行設備振動數據分析的示範專案，整合了 MySQL 資料庫查詢、OpenAI/Ollama LLM，以及智能分析功能。

## 專案簡介

本專案展示如何使用 AI Agent 自動化分析工廠設備的振動數據，提供異常偵測、維護建議和故障排除功能。Agent 會自動：
1. 從 MySQL 資料庫查詢振動數據
2. 進行統計分析（平均值、標準差、離群值檢測）
3. 提供專業的設備維護建議

## 功能特色

- ✅ **自動化數據查詢**：透過 function tools 自動查詢 MySQL 資料庫
- ✅ **智能分析**：使用 AI Agent 分析振動數據並識別異常
- ✅ **多模型支援**：支援 OpenAI GPT 和 Ollama 本地模型
- ✅ **專業建議**：模擬設備維護工程師，提供維護建議
- ✅ **環境變數管理**：使用 `.env` 安全管理敏感資訊

## 安裝套件

首先安裝必要的 Python 套件：

```bash
pip install -r requirements.txt
```

## 環境變數設定

1. 複製 `.env.example` 為 `.env`：

   ```bash
   cp .env.example .env
   ```

2. 編輯 `.env` 檔案，填入實際的設定值。

### 環境變數說明

#### MySQL 資料庫設定

- `MYSQL_HOST`: MySQL 伺服器位址
- `MYSQL_PORT`: MySQL 連接埠
- `MYSQL_USER`: MySQL 使用者名稱
- `MYSQL_PASSWORD`: MySQL 密碼
- `MYSQL_DATABASE`: 資料庫名稱
- `MYSQL_TABLE`: 資料表名稱

#### Ollama API 設定

- `OLLAMA_BASE_URL`: 遠端 Ollama API 網址
- `OLLAMA_API_KEY`: Ollama API 金鑰
- `OLLAMA_LOCAL_BASE_URL`: 本地 Ollama API 網址

## 專案檔案說明

### 1. `connect_mysql_openai.py`
**使用 OpenAI GPT 模型的設備監測 Agent**

- **功能**：使用 OpenAI GPT-5-mini 模型
- **工具函數**：
  - `get_vibration_all_on_date()`: 取得指定日期的所有振動數據
  - `find_vibration_outliers_on_date()`: 找出指定日期的離群值
  - `analyze_vibration_list()`: 統計分析振動數據（平均值、標準差）
  - `get_vibration_max_on_date()`: 取得指定日期的最大振動值
  - `current_time()`: 取得當前時間

- **Agent 特性**：
  - 扮演設備維護工程師角色
  - 使用繁體中文回覆
  - 提供數據分析與維護建議

- **執行範例**：
  ```bash
  python connect_mysql_openai.py
  ```

### 2. `connect_mysql_ollama.py`
**使用 Ollama 本地模型的設備監測 Agent**

- **功能**：使用 Ollama 的 gpt-oss:20b 模型（可更換）
- **工具函數**：與 `connect_mysql_openai.py` 相同
- **差異**：
  - 使用本地或遠端 Ollama 服務
  - 支援串流輸出 (streaming)
  - 適合離線或私有部署環境

- **執行範例**：
  ```bash
  python connect_mysql_ollama.py
  ```

### 3. `agent.py`
**本地 Ollama Agent 基礎範例**

- **功能**：展示如何建立簡單的 AI Agent
- **模型**：使用本地 Ollama 的 gemma3:1b 模型
- **特點**：
  - 輕量級範例
  - 支援串流輸出
  - 適合測試本地 Ollama 連接

- **執行範例**：
  ```bash
  python agent.py
  ```

### 4. `test.py`
**Ollama API 串流測試**

- **功能**：測試遠端 Ollama API 的串流功能
- **模型**：gemma3n:e4b
- **特點**：
  - 互動式問答
  - 即時串流輸出
  - 適合測試 API 連接

- **執行範例**：
  ```bash
  python test.py
  ```

### 5. `Agent_demo.py`
**OpenAI Agent 基礎範例**

- **功能**：展示最基本的 OpenAI Agent 建立方式
- **工具**：`current_time()` - 取得當前時間
- **用途**：學習 Agent 基礎架構

## 使用流程示範

### 情境：查詢設備異常振動

1. **執行程式**：
   ```bash
   python connect_mysql_openai.py
   ```

2. **Agent 自動執行流程**：
   ```
   使用者查詢 → Agent 規劃 → 調用工具查詢資料庫 
   → 統計分析 → 異常偵測 → 生成維護建議
   ```

3. **範例輸出**：
   ```
   分析 2025-07-27 與 7-28 的振動數據：
   
   - 平均振動值：12.5
   - 標準差：3.2
   - 離群值：共發現 5 筆
   - 最大振動值：28.3 (發生於 2025-07-28 14:23)
   
   維護建議：
   1. 檢查軸承磨損情況
   2. 確認螺栓是否鬆動
   3. 建議進行設備校準
   ```

## Function Tools 說明

### `get_vibration_all_on_date(date_str: str)`
取得指定日期的所有振動數據，自動偵測時間欄位並對振動值取絕對值。

**參數**：
- `date_str`: 日期字串，格式如 "2025-07-27"

**回傳**：所有振動數據的文字列表

### `find_vibration_outliers_on_date(date_str: str, threshold: float = 3.0)`
找出指定日期的離群值（預設為平均值 ± 3 倍標準差）。

**參數**：
- `date_str`: 日期字串
- `threshold`: 離群值閾值（預設 3.0）

**回傳**：離群值列表

### `analyze_vibration_list(date_str: str)`
統計分析指定日期的振動數據。

**參數**：
- `date_str`: 日期字串

**回傳**：包含平均值、標準差、最大值、最小值的統計結果

### `get_vibration_max_on_date(date_str: str)`
取得指定日期的最大振動值及發生時間。

**參數**：
- `date_str`: 日期字串

**回傳**：最大振動值及其時間戳記

## 技術架構

```
使用者輸入
    ↓
AI Agent (OpenAI/Ollama)
    ↓
Function Tools
    ↓
MySQL Database (equipment_data)
    ↓
數據分析 & 建議生成
    ↓
輸出結果
```

## 安全注意事項

⚠️ **重要**：

- `.env` 檔案包含敏感資訊，已加入 `.gitignore`，**請勿提交到版本控制**
- 請妥善保管你的密碼和 API 金鑰
- 如需分享專案，請使用 `.env.example` 作為範本
- 建議定期更換資料庫密碼

## 常見問題

### Q1: 如何切換 AI 模型？
修改程式中的 `model` 參數：
- OpenAI: `model="gpt-5-mini"`
- Ollama: `model=OpenAIChatCompletionsModel(model="gemma3:1b", openai_client=client)`

### Q2: 如何調整離群值的敏感度？
修改 `find_vibration_outliers_on_date()` 的 `threshold` 參數，數值越小越敏感。

### Q3: 資料庫連線失敗怎麼辦？
1. 檢查 `.env` 中的連線資訊是否正確
2. 確認網路連線和防火牆設定
3. 驗證 MySQL 服務是否正常運行

## 授權

本專案僅供教學與示範使用。

## 聯絡資訊

如有問題或建議，歡迎提出 Issue。
