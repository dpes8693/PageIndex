# EPUB 轉 JSON 功能文檔

## 概述

已成功實現 EPUB 格式到 JSON 結構的轉換功能。該功能遵循 PageIndex 現有的 PDF 和 Markdown 轉換架構，提供統一的 API 和使用體驗。

## 📋 實現內容

### 1. 核心模組 (`pageindex/page_index_epub.py`)

新增以下主要功能：

#### 元數據提取
- `extract_epub_metadata(epub_path)` - 提取書籍標題、作者、語言等基本信息

#### 內容提取
- `extract_text_from_epub_item(item)` - 從 EPUB 項目中提取純文本
- `extract_chapters_from_epub(epub_path)` - 完整的章節提取，自動識別章節邊界
- `extract_headings_from_text(text)` - 基於啟發式方法識別文本中的標題

#### 結構構建
- `build_tree_from_chapters(chapters)` - 從章節列表構建樹狀結構
- `write_node_id()` - 為每個節點分配唯一 ID

#### 摘要生成
- `get_node_summary_epub(node, threshold)` - 根據 Token 數量智能生成摘要
- `generate_summaries_for_structure_epub(structure)` - 非同步生成整個結構的摘要

#### 主轉換函數
- `epub_to_tree(epub_path, **options)` - 統一入口點，整合所有轉換流程

### 2. 命令行集成 (`run_pageindex.py`)

已更新以支援 EPUB：

```bash
# 基本用法
python run_pageindex.py --epub_path book.epub

# 完整參數
python run_pageindex.py --epub_path book.epub \
    --model gpt-4o-2024-11-20 \
    --if-add-node-summary yes \
    --if-add-node-text no \
    --if-add-doc-description no \
    --summary-token-threshold 200
```

### 3. 模組導出 (`pageindex/__init__.py`)

已添加 `epub_to_tree` 到公開 API：

```python
from pageindex import epub_to_tree
```

### 4. 依賴項更新 (`requirements.txt`)

添加 `ebooklib>=0.18` 依賴

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 命令行使用

```bash
# 基本轉換
python run_pageindex.py --epub_path /path/to/book.epub

# 生成結果將儲存到
./results/{book_name}_structure.json
```

### Python 程式碼使用

```python
import asyncio
from pageindex import epub_to_tree
import json

async def main():
    # 轉換 EPUB 到 JSON
    result = await epub_to_tree(
        epub_path='book.epub',
        if_add_node_summary='yes',
        if_add_node_id='yes',
        model='gpt-4o-2024-11-20'
    )
    
    # 儲存結果
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"已生成: {result['doc_name']}")
    print(f"作者: {result['doc_metadata']['author']}")

asyncio.run(main())
```

### 測試

執行測試指令碼：

```bash
# 無參數 - 將自動建立測試 EPUB
python test_epub.py

# 或指定 EPUB 檔案
python test_epub.py /path/to/book.epub
```

## 📊 輸出格式

### 基本結構

```json
{
  "doc_name": "book_title",
  "doc_metadata": {
    "title": "Book Title",
    "author": "Author Name",
    "language": "en"
  },
  "structure": [
    {
      "title": "Chapter 1",
      "node_id": "0001",
      "summary": "Summary of chapter content...",
      "source_file": "chapter1.xhtml",
      "nodes": []
    },
    {
      "title": "Chapter 2", 
      "node_id": "0002",
      "prefix_summary": "Contains multiple sections...",
      "source_file": "chapter2.xhtml",
      "nodes": [
        {
          "title": "Section 2.1",
          "node_id": "0003",
          "summary": "Details...",
          "source_file": "chapter2_sec1.xhtml",
          "nodes": []
        }
      ]
    }
  ]
}
```

### 帶完整文本的結構

```bash
python run_pageindex.py --epub_path book.epub --if-add-node-text yes
```

會在每個節點中包含完整文本：

```json
{
  "title": "Chapter 1",
  "node_id": "0001",
  "text": "Full chapter text content...",
  "summary": "Summary of the chapter...",
  "source_file": "chapter1.xhtml"
}
```

## 🔧 參數說明

### `epub_to_tree()` 函數參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `epub_path` | str | 必需 | EPUB 檔案路徑 |
| `if_add_node_id` | str | 'yes' | 添加節點 ID |
| `if_add_node_summary` | str | 'yes' | 生成節點摘要 |
| `if_add_doc_description` | str | 'no' | 生成文檔描述 |
| `if_add_node_text` | str | 'no' | 保留完整文本 |
| `summary_token_threshold` | int | 200 | Token 閾值 |
| `model` | str | None | AI 模型名稱 |

### 命令行參數

- `--epub_path` - EPUB 檔案路徑（必需）
- `--model` - AI 模型（預設：gpt-4o-2024-11-20）
- `--if-add-node-id` - 添加 ID（yes/no，預設：yes）
- `--if-add-node-summary` - 生成摘要（yes/no，預設：yes）
- `--if-add-doc-description` - 文檔描述（yes/no，預設：no）
- `--if-add-node-text` - 保留文本（yes/no，預設：no）
- `--summary-token-threshold` - Token 閾值（預設：200）

## 🏗️ 架構設計

### 轉換流程

```
EPUB 檔案
    │
    ├─→ extract_epub_metadata()
    │   └─→ 書籍元數據
    │
    ├─→ extract_chapters_from_epub()
    │   ├─→ 章節提取
    │   ├─→ 文本清理（移除 HTML）
    │   └─→ 章節列表
    │
    ├─→ build_tree_from_chapters()
    │   └─→ 樹狀結構
    │
    ├─→ write_node_id()
    │   └─→ 添加節點 ID
    │
    └─→ generate_summaries_for_structure_epub() (可選)
        ├─→ Token 計算
        ├─→ 智能摘要生成
        └─→ 最終結構

    結果 → JSON 檔案
```

## 🔄 與其他轉換的統一性

### 功能對比

| 功能 | PDF | Markdown | EPUB |
|------|-----|----------|------|
| 基本解析 | ✓ | ✓ | ✓ |
| 元數據提取 | ✓ | ✗ | ✓ |
| 結構建立 | ✓ | ✓ | ✓ |
| 節點 ID | ✓ | ✓ | ✓ |
| 摘要生成 | ✓ | ✓ | ✓ |
| 文檔描述 | ✓ | ✓ | ✓ |

### API 一致性

所有轉換均遵循統一的命令行介面：

```bash
python run_pageindex.py --pdf_path file.pdf
python run_pageindex.py --md_path file.md
python run_pageindex.py --epub_path file.epub
```

## ⚙️ 特性詳解

### 1. 自動章節識別

- 自動遍歷 EPUB 的 spine（內容順序）
- 從 XHTML 檔案提取純文本
- 自動移除 HTML 標籤

### 2. HTML 清理

```python
# 自動轉換
<h1>Chapter 1</h1>
<p>Content here</p>

# 到
Chapter 1
Content here
```

### 3. 智能摘要生成

- 低於 Token 閾值的文本直接作為摘要
- 超過閾值自動調用 AI 生成摘要
- 支援非同步並行處理

### 4. 編碼處理

自動處理多種編碼：
- UTF-8（主要）
- Latin-1（備用）

## 💡 使用案例

### 案例 1: 快速提取 EPUB 結構

```bash
python run_pageindex.py --epub_path novel.epub \
    --if-add-node-summary no \
    --if-add-node-text no
```

輸出：純結構（title, node_id, source_file）

### 案例 2: 生成帶摘要的索引

```bash
python run_pageindex.py --epub_path textbook.epub \
    --if-add-node-summary yes \
    --summary-token-threshold 300
```

輸出：包含智能摘要的結構

### 案例 3: 完整分析

```bash
python run_pageindex.py --epub_path ebook.epub \
    --if-add-node-summary yes \
    --if-add-node-text yes \
    --if-add-doc-description yes
```

輸出：包含文本、摘要和文檔描述的完整結構

## 🔍 錯誤處理

該實現包含以下錯誤處理機制：

1. **檔案驗證**
   - 檔案存在性檢查
   - 副檔名驗證

2. **元數據解析**
   - 缺失元數據的預設值
   - 例外情況的優雅降級

3. **文本提取**
   - 多編碼支援
   - HTML 解析錯誤恢復

4. **非同步操作**
   - 異常捕獲和重試機制
   - 正確的並行處理

## 📝 日誌記錄

所有操作均有詳細的 console 輸出：

```
Processing EPUB file: book.epub
Extracting EPUB metadata...
Extracting chapters from EPUB...
Building tree structure from chapters...
Generating summaries for each node...
Formatting tree structure...
```

## 🧪 測試

### 執行測試套件

```bash
python test_epub.py
```

會執行以下測試：
1. ✓ 元數據提取
2. ✓ 章節提取
3. ✓ 樹結構轉換
4. ✓ 摘要生成（可選，需要 API 金鑰）

### 建立測試 EPUB

測試指令碼會自動建立簡單的測試 EPUB 檔案：

```
tests/epubs/test_book.epub
```

## 🚀 性能考慮

- **大型 EPUB**：支援逐章處理
- **摘要生成**：非同步並行處理多個節點
- **Token 計算**：緩存以避免重複計算

## 🔮 未來改進

- [ ] EPUB 的 TOC 自動解析
- [ ] 嵌套章節結構識別
- [ ] 圖像提取和清單
- [ ] DRM 保護檔案支援
- [ ] 增量處理大型檔案

## 📚 相關檔案

- `pageindex/page_index_epub.py` - 核心實現
- `run_pageindex.py` - 命令行介面
- `test_epub.py` - 測試指令碼
- `pageindex/epub/USAGE.md` - 詳細使用指南

## 📄 許可證

遵循 PageIndex 專案的現有許可證

## 🤝 貢獻

歡迎提交改進建議或報告問題！
