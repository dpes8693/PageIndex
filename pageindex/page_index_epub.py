import asyncio
import json
import re
import os
from pathlib import Path

try:
    from .utils import *
except ImportError:
    from utils import *

try:
    from ebooklib import epub
except ImportError:
    import sys
    print("Error: ebooklib is not installed. Please install it with: pip install ebooklib")
    sys.exit(1)


def extract_epub_metadata(epub_path):
    """
    提取 EPUB 檔案的基本元數據
    """
    try:
        book = epub.read_epub(epub_path)
        metadata = {
            'title': book.title or 'Untitled',
            'author': ', '.join([author[0] for author in book.metadata.get('http://purl.org/dc/elements/1.1/', {}).get('author', [])]) if book.metadata else 'Unknown',
            'language': book.language or 'unknown',
        }
        return metadata
    except Exception as e:
        logging.error(f"Error extracting EPUB metadata: {e}")
        return {
            'title': 'Untitled',
            'author': 'Unknown',
            'language': 'unknown'
        }


def extract_text_from_epub_item(item):
    """
    從 EPUB 項目中提取文本內容
    """
    try:
        if item.get_type() == epub.ITEM_DOCUMENT:
            content = item.get_content()
            # 解碼內容
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    content = content.decode('latin-1')
            
            # 基本的 HTML 標籤移除
            text = re.sub(r'<[^>]+>', ' ', content)
            # 清理多個空格
            text = ' '.join(text.split())
            return text
    except Exception as e:
        logging.warning(f"Error extracting text from EPUB item: {e}")
        return ""


def extract_chapters_from_epub(epub_path):
    """
    從 EPUB 檔案提取章節結構
    """
    try:
        book = epub.read_epub(epub_path)
        
        chapters = []
        chapter_counter = 1
        
        # 遍歷書籍的 spine（主要內容順序）
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                text_content = extract_text_from_epub_item(item)
                
                if text_content.strip():  # 只有在有內容時才添加
                    # 嘗試從文件名或標題提取章節名稱
                    chapter_title = item.get_name() or f"Chapter {chapter_counter}"
                    
                    # 清理檔名作為標題
                    chapter_title = os.path.splitext(chapter_title)[0]
                    chapter_title = re.sub(r'[_\-]', ' ', chapter_title)
                    chapter_title = chapter_title.strip()
                    
                    if not chapter_title or chapter_title.lower() in ['nav', 'toc', 'cover']:
                        chapter_title = f"Chapter {chapter_counter}"
                    
                    chapters.append({
                        'title': chapter_title,
                        'content': text_content,
                        'file_name': item.get_name(),
                        'uid': item.get_id()
                    })
                    chapter_counter += 1
        
        return chapters
    except Exception as e:
        logging.error(f"Error extracting chapters from EPUB: {e}")
        return []


def extract_headings_from_text(text):
    """
    從文本中提取可能的標題（基於文本結構啟發式）
    """
    lines = text.split('\n')
    headings = []
    
    for line_num, line in enumerate(lines):
        stripped = line.strip()
        # 啟發式：短行可能是標題
        if (1 < len(stripped) < 100 and 
            not stripped.endswith('.') and 
            not stripped.endswith(',') and
            len(stripped.split()) < 15):
            
            headings.append({
                'line_num': line_num,
                'text': stripped,
                'length': len(stripped)
            })
    
    return headings


async def get_node_summary_epub(node, summary_token_threshold=200, model=None):
    """
    獲取節點的摘要（如果文本較短則直接返回文本）
    """
    node_text = node.get('text', '')
    num_tokens = count_tokens(node_text, model=model)
    if num_tokens < summary_token_threshold:
        return node_text
    else:
        return await generate_node_summary(node, model=model)


async def generate_summaries_for_structure_epub(structure, summary_token_threshold, model=None):
    """
    為結構中的所有節點生成摘要
    """
    nodes = structure_to_list(structure)
    tasks = [get_node_summary_epub(node, summary_token_threshold=summary_token_threshold, model=model) for node in nodes]
    summaries = await asyncio.gather(*tasks)
    
    for node, summary in zip(nodes, summaries):
        if not node.get('nodes'):
            node['summary'] = summary
        else:
            node['prefix_summary'] = summary
    return structure


def build_tree_from_chapters(chapters):
    """
    從章節列表構建樹狀結構
    """
    if not chapters:
        return []
    
    tree_nodes = []
    node_counter = 1
    
    for chapter in chapters:
        tree_node = {
            'title': chapter['title'],
            'node_id': str(node_counter).zfill(4),
            'text': chapter['content'],
            'source_file': chapter['file_name'],
            'nodes': []
        }
        tree_nodes.append(tree_node)
        node_counter += 1
    
    return tree_nodes


async def epub_to_tree(
    epub_path,
    if_add_node_id='yes',
    if_add_node_summary='yes',
    if_add_doc_description='no',
    if_add_node_text='no',
    summary_token_threshold=200,
    model=None
):
    """
    將 EPUB 檔案轉換為樹狀 JSON 結構
    
    參數:
        epub_path: EPUB 檔案的路徑
        if_add_node_id: 是否添加節點 ID
        if_add_node_summary: 是否為節點添加摘要
        if_add_doc_description: 是否添加文檔描述
        if_add_node_text: 是否包含節點文本
        summary_token_threshold: Token 數量閾值，低於此值的文本將直接作為摘要
        model: 要使用的 AI 模型
    
    返回:
        包含 doc_name、doc_description（可選）和 structure 的字典
    """
    
    print(f"Processing EPUB file: {epub_path}")
    
    # 驗證文件
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    
    if not epub_path.lower().endswith('.epub'):
        raise ValueError("File must have .epub extension")
    
    # 提取元數據
    print("Extracting EPUB metadata...")
    metadata = extract_epub_metadata(epub_path)
    
    # 提取章節
    print("Extracting chapters from EPUB...")
    chapters = extract_chapters_from_epub(epub_path)
    
    if not chapters:
        print("Warning: No chapters found in EPUB file")
        return {
            'doc_name': os.path.splitext(os.path.basename(epub_path))[0],
            'doc_metadata': metadata,
            'structure': []
        }
    
    # 構建樹狀結構
    print("Building tree structure from chapters...")
    tree_structure = build_tree_from_chapters(chapters)
    
    # 添加節點 ID
    if if_add_node_id == 'yes':
        write_node_id(tree_structure)
    
    # 生成摘要
    if if_add_node_summary == 'yes':
        # 保持文本用於摘要生成
        tree_structure = format_structure(tree_structure, order=['title', 'node_id', 'summary', 'prefix_summary', 'text', 'source_file', 'nodes'])
        
        print("Generating summaries for each node...")
        tree_structure = await generate_summaries_for_structure_epub(tree_structure, summary_token_threshold=summary_token_threshold, model=model)
        
        if if_add_node_text == 'no':
            # 移除文本（如果不需要）
            tree_structure = format_structure(tree_structure, order=['title', 'node_id', 'summary', 'prefix_summary', 'source_file', 'nodes'])
        
        if if_add_doc_description == 'yes':
            print("Generating document description...")
            clean_structure = create_clean_structure_for_description(tree_structure)
            doc_description = generate_doc_description(clean_structure, model=model)
            
            return {
                'doc_name': os.path.splitext(os.path.basename(epub_path))[0],
                'doc_metadata': metadata,
                'doc_description': doc_description,
                'structure': tree_structure,
            }
    else:
        # 不需要摘要，根據是否需要文本進行格式化
        if if_add_node_text == 'yes':
            tree_structure = format_structure(tree_structure, order=['title', 'node_id', 'summary', 'prefix_summary', 'text', 'source_file', 'nodes'])
        else:
            tree_structure = format_structure(tree_structure, order=['title', 'node_id', 'summary', 'prefix_summary', 'source_file', 'nodes'])
    
    return {
        'doc_name': os.path.splitext(os.path.basename(epub_path))[0],
        'doc_metadata': metadata,
        'structure': tree_structure,
    }


if __name__ == "__main__":
    import asyncio
    
    # 測試用範例
    EPUB_PATH = os.path.join(os.path.dirname(__file__), '..', 'tests', 'epubs', 'sample.epub')
    
    MODEL = "gpt-4o-2024-11-20"
    IF_SUMMARY = True
    SUMMARY_TOKEN_THRESHOLD = 200
    
    result = asyncio.run(epub_to_tree(
        epub_path=EPUB_PATH,
        if_add_node_id='yes',
        if_add_node_summary='yes' if IF_SUMMARY else 'no',
        if_add_doc_description='no',
        if_add_node_text='no',
        summary_token_threshold=SUMMARY_TOKEN_THRESHOLD,
        model=MODEL
    ))
    
    print('\n' + '='*60)
    print('TREE STRUCTURE')
    print('='*60)
    print_json(result)
    
    print('\n' + '='*60)
    print('TABLE OF CONTENTS')
    print('='*60)
    print_toc(result['structure'])
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', f'{result["doc_name"]}_structure.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nTree structure saved to: {output_path}")
