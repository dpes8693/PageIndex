# EPUB 轉 JSON - 快速參考卡片

## 🎯 快速開始

### 安裝
```bash
pip install -r requirements.txt
```

### 基本用法
```bash
python run_pageindex.py --epub_path book.epub
```

## 📦 新增模組

### `pageindex/page_index_epub.py`
核心轉換模組，包含以下主要函數：

```python
# 提取元數據
metadata = extract_epub_metadata('book.epub')

# 提取章節
chapters = extract_chapters_from_epub('book.epub')

# 完整轉換（非同步）
result = await epub_to_tree('book.epub', if_add_node_summary='yes')
```

## 🔧 配置選項

### Python API
```python
result = await epub_to_tree(
    epub_path='/path/to/book.epub',
    if_add_node_id='yes',              # 添加節點 ID
    if_add_node_summary='yes',         # 生成摘要
    if_add_doc_description='no',       # 生成文檔描述
    if_add_node_text='no',             # 保留完整文本
    summary_token_threshold=200,       # Token 閾值
    model='gpt-4o-2024-11-20'          # AI 模型
)
```

### 命令行
```bash
python run_pageindex.py --epub_path book.epub \
    --model gpt-4o-2024-11-20 \
    --if-add-node-summary yes \
    --if-add-node-text no \
    --summary-token-threshold 200
```

## 📊 輸出格式

```json
{
  "doc_name": "book_title",
  "doc_metadata": {
    "title": "Book Title",
    "author": "Author",
    "language": "en"
  },
  "structure": [
    {
      "title": "Chapter 1",
      "node_id": "0001",
      "summary": "...",
      "source_file": "chapter1.xhtml",
      "nodes": []
    }
  ]
}
```

## 📁 檔案結構

```
pageindex/
├── page_index_epub.py          # ✨ 新增 EPUB 轉換模組
├── page_index_md.py            # Markdown 轉換
├── page_index.py               # PDF 轉換
├── utils.py                    # 共享工具函數
└── epub/
    ├── readme.md               # EPUB 文檔
    └── USAGE.md                # ✨ 詳細使用指南

run_pageindex.py                # ✨ 已更新：添加 EPUB 支援
test_epub.py                    # ✨ 新增 EPUB 測試工具
EPUB_CONVERSION_GUIDE.md        # ✨ 完整使用文檔
IMPLEMENTATION_SUMMARY.md       # ✨ 實現總結
```

## 🧪 測試

```bash
# 執行完整測試
python test_epub.py

# 測試特定 EPUB
python test_epub.py /path/to/book.epub
```

測試項目：
- ✓ 元數據提取
- ✓ 章節提取
- ✓ 樹結構轉換
- ✓ 摘要生成（可選）

## 📋 常用命令

### 基本轉換
```bash
python run_pageindex.py --epub_path novel.epub
```

### 生成摘要
```bash
python run_pageindex.py --epub_path textbook.epub \
    --if-add-node-summary yes
```

### 包含完整文本
```bash
python run_pageindex.py --epub_path ebook.epub \
    --if-add-node-text yes
```

### 自訂 Token 閾值
```bash
python run_pageindex.py --epub_path book.epub \
    --summary-token-threshold 500
```

### 文檔描述
```bash
python run_pageindex.py --epub_path book.epub \
    --if-add-doc-description yes
```

## 🔑 主要特性

| 特性 | 描述 |
|------|------|
| 自動識別 | 自動識別章節邊界 |
| 元數據 | 提取標題、作者、語言 |
| 節點 ID | 自動分配唯一 ID |
| 摘要 | 智能 AI 摘要生成 |
| 非同步 | 並行處理提高效率 |
| 錯誤恢復 | 多編碼支援和故障轉移 |

## ⚙️ 依賴項

- `ebooklib>=0.18` - EPUB 解析庫（新增）
- `openai` - AI 模型 API
- `tiktoken` - Token 計算
- 其他現有依賴保持不變

## 📌 注意事項

1. **API 金鑰** - 摘要生成需要 `CHATGPT_API_KEY` 環境變數
2. **檔案格式** - 僅支援標準 EPUB 2/3 格式
3. **DRM 保護** - 不支援受 DRM 保護的 EPUB
4. **輸出位置** - 結果儲存到 `./results/{name}_structure.json`

## 🔗 相關文檔

- [EPUB_CONVERSION_GUIDE.md](EPUB_CONVERSION_GUIDE.md) - 詳細指南
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - 技術總結
- [pageindex/epub/USAGE.md](pageindex/epub/USAGE.md) - API 參考

## 💡 提示

- 第一次轉換可能較慢（模型載入）
- 摘要生成需要有效的 API 金鑰
- 大型 EPUB 建議先不生成摘要測試效能
- 使用 `--if-add-node-text yes` 進行完整分析

## 🐛 故障排除

### 缺少 ebooklib
```bash
pip install ebooklib
```

### 沒有 API 金鑰
設定環境變數：
```bash
export CHATGPT_API_KEY="your-key-here"
```

### 檔案無法開啟
- 確認 EPUB 不受 DRM 保護
- 確認檔案未損壞
- 嘗試用 7-Zip 驗證 ZIP 完整性

## 📈 性能提示

- **小型 EPUB**：完整轉換 < 1 分鐘
- **中型 EPUB**：帶摘要 5-10 分鐘
- **大型 EPUB**：建議批次處理

---

**版本**: 1.0.0 ✅
**狀態**: 生產就緒 🚀
