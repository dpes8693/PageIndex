# EPUB to JSON 轉換功能使用指南

## 概述

這個新功能允許將 EPUB 電子書檔案轉換為結構化的 JSON 格式，類似於現有的 PDF 和 Markdown 轉換功能。

## 主要特性

### 1. **章節提取** (`extract_chapters_from_epub`)
- 從 EPUB 檔案中自動識別和提取所有章節
- 提取每個章節的文本內容
- 保留原始檔案名稱和 UID 用於參考

### 2. **元數據提取** (`extract_epub_metadata`)
- 自動讀取書籍標題、作者和語言等元數據
- 提供故障轉移機制以應對缺失或不完整的元數據

### 3. **樹狀結構生成** (`build_tree_from_chapters`)
- 基於章節生成層級樹結構
- 自動分配節點 ID（格式：0001, 0002 等）

### 4. **摘要生成** (`generate_summaries_for_structure_epub`)
- 支援為每個節點自動生成摘要
- Token 閾值設定：低於閾值的文本將直接作為摘要
- 支援非同步並行處理以加快生成速度

### 5. **主轉換函數** (`epub_to_tree`)
- 統一入口點，整合所有上述功能
- 支援多種配置選項

## 使用方法

### 命令行使用

```bash
# 基本用法 - 使用預設設定
python run_pageindex.py --epub_path /path/to/book.epub

# 指定 AI 模型
python run_pageindex.py --epub_path /path/to/book.epub --model gpt-4o

# 不生成摘要，只提取結構
python run_pageindex.py --epub_path /path/to/book.epub --if-add-node-summary no

# 包含文本內容
python run_pageindex.py --epub_path /path/to/book.epub --if-add-node-text yes

# 包含文檔描述
python run_pageindex.py --epub_path /path/to/book.epub --if-add-doc-description yes

# 自訂 Token 閾值
python run_pageindex.py --epub_path /path/to/book.epub --summary-token-threshold 300
```

### Python 程式碼使用

```python
import asyncio
from pageindex.page_index_epub import epub_to_tree

# 基本用法
result = asyncio.run(epub_to_tree(
    epub_path='/path/to/book.epub',
    if_add_node_summary='yes',
    model='gpt-4o-2024-11-20'
))

# 輸出結構
print(result['doc_name'])
print(result['doc_metadata'])
print(result['structure'])

# 儲存到檔案
import json
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
```

## 輸出格式

### 範例輸出

```json
{
  "doc_name": "example_book",
  "doc_metadata": {
    "title": "Example Book Title",
    "author": "Author Name",
    "language": "en"
  },
  "structure": [
    {
      "title": "Chapter 1",
      "node_id": "0001",
      "summary": "This chapter introduces...",
      "source_file": "ch01.xhtml",
      "nodes": []
    },
    {
      "title": "Chapter 2",
      "node_id": "0002",
      "prefix_summary": "The second chapter covers...",
      "source_file": "ch02.xhtml",
      "nodes": [
        {
          "title": "Section 2.1",
          "node_id": "0003",
          "summary": "Details about section...",
          "source_file": "ch02_sec1.xhtml",
          "nodes": []
        }
      ]
    }
  ]
}
```

## 參數說明

### `epub_to_tree` 函數參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `epub_path` | str | 必需 | EPUB 檔案的路徑 |
| `if_add_node_id` | str | 'yes' | 是否為節點添加 ID |
| `if_add_node_summary` | str | 'yes' | 是否為節點生成摘要 |
| `if_add_doc_description` | str | 'no' | 是否為整個文檔生成描述 |
| `if_add_node_text` | str | 'no' | 是否保留節點的完整文本 |
| `summary_token_threshold` | int | 200 | Token 數量閾值，低於此值的文本直接作為摘要 |
| `model` | str | None | 要使用的 AI 模型名稱 |

## 命令行參數

### EPUB 特定參數

- `--epub_path`: EPUB 檔案路徑（必需）

### 共享參數

- `--model`: AI 模型選擇（預設：gpt-4o-2024-11-20）
- `--if-add-node-id`: 是否添加節點 ID（預設：yes）
- `--if-add-node-summary`: 是否生成摘要（預設：yes）
- `--if-add-doc-description`: 是否生成文檔描述（預設：no）
- `--if-add-node-text`: 是否保留文本內容（預設：no）
- `--summary-token-threshold`: Token 閾值（預設：200）

## 輸出位置

轉換結果將儲存到 `./results/` 目錄，檔案名稱格式為：
```
{EPUB_FILE_NAME_WITHOUT_EXTENSION}_structure.json
```

例如：`book_name_structure.json`

## 功能架構

### 核心模組 (`page_index_epub.py`)

```
┌─────────────────────────────────────┐
│   extract_epub_metadata()            │  ← 讀取書籍元數據
└──────────────────┬──────────────────┘
                   │
┌──────────────────┴──────────────────┐
│   extract_chapters_from_epub()       │  ← 提取章節內容
└──────────────────┬──────────────────┘
                   │
┌──────────────────┴──────────────────┐
│   build_tree_from_chapters()         │  ← 構建樹結構
└──────────────────┬──────────────────┘
                   │
    ┌──────────────┴──────────────────┐
    │                                  │
    ▼                                  ▼
write_node_id()           generate_summaries_for_structure_epub()
(添加 ID)                 (非同步生成摘要)
    │                                  │
    └──────────────┬──────────────────┘
                   │
                   ▼
          format_structure()
         (格式化輸出結構)
                   │
                   ▼
          生成最終 JSON 輸出
```

## 錯誤處理

該功能包含以下錯誤處理機制：

1. **檔案驗證**: 檢查檔案存在性和副檔名
2. **元數據解析**: 對於缺失的元數據提供預設值
3. **文本提取**: 自動處理編碼問題（UTF-8/Latin-1）
4. **HTML 清理**: 移除 HTML 標籤並規範化空白

## 與其他轉換格式的比較

| 功能 | PDF | Markdown | EPUB |
|------|-----|----------|------|
| TOC 提取 | ✓ | 基於標題等級 | ✓ |
| 元數據 | ✓ | ✗ | ✓ |
| 頁面索引 | ✓ | ✗ | ✗ |
| 章節結構 | 自動識別 | 基於標題 | 自動識別 |
| 摘要生成 | ✓ | ✓ | ✓ |
| 文檔描述 | ✓ | ✓ | ✓ |

## 限制與已知問題

1. **嵌套章節**: 目前不自動識別 EPUB 內的嵌套結構，需要依賴 EPUB 的 spine 順序
2. **複雜 HTML**: 複雜的 HTML 結構可能無法完全保留
3. **媒體內容**: 圖片、音樂等多媒體內容不被提取
4. **DRM 保護**: 受 DRM 保護的 EPUB 檔案無法處理

## 依賴項

- `ebooklib>=0.18`: 用於讀取和解析 EPUB 檔案
- 其他依賴項同 pageindex 項目

## 未來改進方向

- [ ] 支援嵌套章節結構識別
- [ ] 圖像和多媒體提取
- [ ] 目錄（TOC）自動識別與使用
- [ ] DRM 支援（如果可能）
- [ ] 增量処理支援（針對大型 EPUB 檔案）
- [ ] 雙語內容支援

## 貢獻

如果您發現任何問題或有改進建議，請提交 Issue 或 Pull Request。
