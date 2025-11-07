# EbookLib

EbookLib 是一個專為 Python 開發的電子書處理函式庫，主要支援 EPUB2 及 EPUB3 格式，並持續開發 Kindle 格式支援。它被廣泛用於編程方式讀取、編輯、與建立 EPUB 電子書，API 設計簡單，能靈活處理元數據、封面、章節、圖片、CSS 樣式、目錄、書脊（spine）、導航等所有電子書關鍵結構。[1][4]

### 主要特色
- **支援 EPUB2/EPUB3**：可完美處理文檔內容、資源、導航與結構。
- **API 簡潔**：基礎操作與高階功能都能輕易實現，適合快速開發與大規模系統集成。[4]
- **編輯功能豐富**：能夠自由添加、刪除、修改章節、圖片、封面等。
- **元數據控制**：可自訂書名、作者、語言、唯一識別碼等元資訊。[1]
- **靈活的章節、書脊排序**：確保閱讀內容順序正確，支援自訂目錄與導航頁。
- **開源專案採用**：被 Booktype、fanfiction2ebook 等知名開源專案採用，實用性與穩定性高。[4]

### 基本用法範例
- **安裝**：
  ```bash
  pip install EbookLib
  ```

- **讀取 EPUB 檔案**：
  ```python
  from ebooklib import epub
  book = epub.read_epub('book.epub')
  # 例：印出所有圖片
  for img in book.get_items_of_type(epub.ITEM_IMAGE):
      print(img)
  ```

- **建立 EPUB 檔案**：
  ```python
  from ebooklib import epub
  book = epub.EpubBook()
  # 設定元數據
  book.set_title('範例書籍')
  book.add_author('作者')
  # 新增章節
  c1 = epub.EpubHtml(title='簡介', file_name='chap1.xhtml', lang='zh')
  c1.content = '<h1>簡介</h1><p>內容</p>'
  book.add_item(c1)
  # 定義目錄和書脊
  book.toc = (epub.Link('chap1.xhtml', '簡介', 'intro'), )
  book.spine = ['nav', c1]
  epub.write_epub('sample.epub', book, {})
  ```
EbookLib 的彈性與生態穩定，使其成為自動化 EPUB 工具與電子書相關二次開發的首選基礎。[5][1][4]

[1](https://blog.csdn.net/gitblog_01028/article/details/141042473)
[2](https://www.showapi.com/news/article/66fac0214ddd79f11a26a62c)
[3](https://docs.pingcode.com/baike/1255384)
[4](https://blog.csdn.net/gitblog_00096/article/details/138840064)
[5](https://blog.51cto.com/u_16175453/12042162)
[6](https://blog.perillaroc.wang/post/2017/2017-12-01-create-epub-book/)
[7](http://www.360doc.com/content/24/0716/09/62865528_1128887133.shtml)
[8](https://blog.soarli.top/archives/704.html)
[9](https://comate.baidu.com/zh/page/ako6ojt9jkp)