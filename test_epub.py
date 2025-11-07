#!/usr/bin/env python3
"""
EPUB to JSON 轉換測試指令碼

這個指令碼示範如何使用 page_index_epub 模組將 EPUB 檔案轉換為 JSON 結構。
"""

import asyncio
import json
import os
import sys

# 確保可以導入 pageindex 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pageindex.page_index_epub import epub_to_tree, extract_chapters_from_epub, extract_epub_metadata
from pageindex.utils import print_toc, print_json


def test_metadata_extraction(epub_path):
    """測試元數據提取功能"""
    print("=" * 60)
    print("測試 1: 元數據提取")
    print("=" * 60)
    
    try:
        metadata = extract_epub_metadata(epub_path)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        print("✓ 元數據提取成功\n")
        return True
    except Exception as e:
        print(f"✗ 元數據提取失敗: {e}\n")
        return False


def test_chapter_extraction(epub_path):
    """測試章節提取功能"""
    print("=" * 60)
    print("測試 2: 章節提取")
    print("=" * 60)
    
    try:
        chapters = extract_chapters_from_epub(epub_path)
        print(f"提取到 {len(chapters)} 個章節:")
        for i, chapter in enumerate(chapters, 1):
            content_preview = chapter['content'][:100] + "..." if len(chapter['content']) > 100 else chapter['content']
            print(f"\n{i}. {chapter['title']}")
            print(f"   檔名: {chapter['file_name']}")
            print(f"   內容預覽: {content_preview}")
        print(f"\n✓ 章節提取成功\n")
        return True
    except Exception as e:
        print(f"✗ 章節提取失敗: {e}\n")
        return False


async def test_tree_conversion(epub_path):
    """測試樹結構轉換功能"""
    print("=" * 60)
    print("測試 3: 樹結構轉換（無摘要）")
    print("=" * 60)
    
    try:
        result = await epub_to_tree(
            epub_path=epub_path,
            if_add_node_id='yes',
            if_add_node_summary='no',
            if_add_doc_description='no',
            if_add_node_text='no',
            model=None
        )
        
        print(f"文檔名稱: {result['doc_name']}")
        print(f"作者: {result['doc_metadata'].get('author')}")
        print(f"標題: {result['doc_metadata'].get('title')}")
        print(f"語言: {result['doc_metadata'].get('language')}")
        
        print("\n目錄結構:")
        print_toc(result['structure'])
        
        print(f"\n✓ 樹結構轉換成功\n")
        return True, result
    except Exception as e:
        print(f"✗ 樹結構轉換失敗: {e}\n")
        return False, None


async def test_summary_generation(epub_path):
    """測試摘要生成功能（需要 AI 模型）"""
    print("=" * 60)
    print("測試 4: 摘要生成（需要 AI 模型）")
    print("=" * 60)
    
    try:
        # 檢查是否設定了 API 金鑰
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("CHATGPT_API_KEY")
        if not api_key:
            print("⚠ 未設定 CHATGPT_API_KEY，跳過此測試\n")
            return None
        
        result = await epub_to_tree(
            epub_path=epub_path,
            if_add_node_id='yes',
            if_add_node_summary='yes',
            if_add_doc_description='no',
            if_add_node_text='no',
            summary_token_threshold=200,
            model='gpt-4o-2024-11-20'
        )
        
        print("部分結構（包含摘要）:")
        print_json(result, max_len=60)
        
        print(f"\n✓ 摘要生成成功\n")
        return True
    except Exception as e:
        print(f"✗ 摘要生成失敗: {e}\n")
        return False


def create_sample_epub_for_testing():
    """建立一個簡單的測試 EPUB 檔案"""
    print("=" * 60)
    print("建立測試 EPUB 檔案")
    print("=" * 60)
    
    try:
        from ebooklib import epub
        
        # 建立書籍
        book = epub.EpubBook()
        
        # 設定元數據
        book.set_identifier('test_book_001')
        book.set_title('Test Book for EPUB to JSON')
        book.add_author('Test Author')
        book.set_language('en')
        
        # 建立章節
        chapters = [
            ('chap1.xhtml', 'Chapter 1', '<h1>Chapter 1</h1><p>This is the first chapter of our test book. It contains some sample content to demonstrate the EPUB to JSON conversion functionality.</p>'),
            ('chap2.xhtml', 'Chapter 2', '<h1>Chapter 2</h1><p>This is the second chapter. It provides more sample content for testing.</p><p>Additional paragraph with more details.</p>'),
            ('chap3.xhtml', 'Chapter 3', '<h1>Chapter 3</h1><p>The final chapter of our test book with concluding remarks.</p>'),
        ]
        
        items = []
        for file_name, title, content in chapters:
            c = epub.EpubHtml(title=title, file_name=file_name, lang='en')
            c.content = content
            book.add_item(c)
            items.append(c)
        
        # 設定 TOC 和 spine
        book.toc = tuple(items)
        book.spine = ['nav'] + items
        
        # 建立 EPUB 檔案
        os.makedirs('./tests/epubs', exist_ok=True)
        epub_path = './tests/epubs/test_book.epub'
        epub.write_epub(epub_path, book, {})
        
        print(f"✓ 測試 EPUB 檔案已建立: {epub_path}\n")
        return epub_path
    except ImportError:
        print("✗ ebooklib 未安裝，無法建立測試 EPUB 檔案\n")
        return None
    except Exception as e:
        print(f"✗ 建立測試 EPUB 檔案失敗: {e}\n")
        return None


async def main():
    """主測試函數"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "EPUB to JSON 轉換功能測試".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # 檢查是否提供了 EPUB 檔案路徑
    if len(sys.argv) > 1:
        epub_path = sys.argv[1]
    else:
        # 嘗試建立或使用測試檔案
        epub_path = create_sample_epub_for_testing()
        if not epub_path:
            print("請提供 EPUB 檔案路徑作為命令行參數")
            print("用法: python test_epub.py <path_to_epub_file>")
            sys.exit(1)
    
    # 驗證檔案存在
    if not os.path.exists(epub_path):
        print(f"✗ 檔案不存在: {epub_path}")
        sys.exit(1)
    
    print(f"使用 EPUB 檔案: {epub_path}\n")
    
    # 執行各項測試
    test_results = []
    
    # 測試 1: 元數據提取
    test_results.append(("元數據提取", test_metadata_extraction(epub_path)))
    
    # 測試 2: 章節提取
    test_results.append(("章節提取", test_chapter_extraction(epub_path)))
    
    # 測試 3: 樹結構轉換
    success, result = await test_tree_conversion(epub_path)
    test_results.append(("樹結構轉換", success))
    
    # 測試 4: 摘要生成（如果有 API 金鑰）
    summary_result = await test_summary_generation(epub_path)
    if summary_result is not None:
        test_results.append(("摘要生成", summary_result))
    
    # 列印測試總結
    print("=" * 60)
    print("測試總結")
    print("=" * 60)
    
    for test_name, success in test_results:
        status = "✓ 通過" if success else "✗ 失敗"
        print(f"{test_name}: {status}")
    
    # 儲存結果到檔案
    if result:
        output_path = './results/test_epub_structure.json'
        os.makedirs('./results', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 結果已儲存到: {output_path}")
    
    print("\n測試完成！")


if __name__ == "__main__":
    asyncio.run(main())
