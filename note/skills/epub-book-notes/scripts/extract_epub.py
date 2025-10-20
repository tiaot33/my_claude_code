#!/usr/bin/env python3
"""
EPUB Book Content Extractor

This script extracts the complete content and structure from an EPUB file,
including metadata, table of contents, and all chapter content.

Dependencies:
    pip install ebooklib beautifulsoup4 lxml

Usage:
    python extract_epub.py <epub_file_path> [--output <output_file>]

Example:
    python extract_epub.py book.epub --output book_content.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("\nPlease install required packages:")
    print("  pip install ebooklib beautifulsoup4 lxml")
    sys.exit(1)


class EPUBExtractor:
    """Extract content and structure from EPUB files."""

    def __init__(self, epub_path: str):
        self.epub_path = Path(epub_path)
        if not self.epub_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")

        self.book = epub.read_epub(str(self.epub_path))
        self.metadata = self._extract_metadata()
        self.toc = []
        self.chapters = []

    def _extract_metadata(self) -> Dict:
        """Extract book metadata."""
        metadata = {}

        # Title
        title = self.book.get_metadata('DC', 'title')
        metadata['title'] = title[0][0] if title else 'Unknown'

        # Author(s)
        authors = self.book.get_metadata('DC', 'creator')
        metadata['authors'] = [author[0] for author in authors] if authors else ['Unknown']

        # Language
        language = self.book.get_metadata('DC', 'language')
        metadata['language'] = language[0][0] if language else 'Unknown'

        # Publisher
        publisher = self.book.get_metadata('DC', 'publisher')
        metadata['publisher'] = publisher[0][0] if publisher else 'Unknown'

        # Publication date
        date = self.book.get_metadata('DC', 'date')
        metadata['date'] = date[0][0] if date else 'Unknown'

        # Description
        description = self.book.get_metadata('DC', 'description')
        metadata['description'] = description[0][0] if description else ''

        # ISBN
        identifier = self.book.get_metadata('DC', 'identifier')
        metadata['identifier'] = identifier[0][0] if identifier else ''

        return metadata

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text."""
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())

        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_toc(self) -> List[Dict]:
        """Extract table of contents."""
        toc_list = []

        def process_toc_item(item, level=0):
            if isinstance(item, tuple):
                # (Section, [children])
                section = item[0]
                if hasattr(section, 'title') and hasattr(section, 'href'):
                    toc_list.append({
                        'title': section.title,
                        'href': section.href,
                        'level': level
                    })
                if len(item) > 1 and isinstance(item[1], list):
                    for child in item[1]:
                        process_toc_item(child, level + 1)
            elif isinstance(item, ebooklib.epub.Link):
                toc_list.append({
                    'title': item.title,
                    'href': item.href,
                    'level': level
                })
            elif isinstance(item, ebooklib.epub.Section):
                toc_list.append({
                    'title': item.title,
                    'href': '',
                    'level': level
                })

        try:
            toc = self.book.toc
            for item in toc:
                process_toc_item(item)
        except Exception as e:
            print(f"Warning: Could not extract TOC - {e}")

        return toc_list

    def extract_chapters(self) -> List[Dict]:
        """Extract all chapter content."""
        chapters = []
        chapter_num = 0

        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapter_num += 1

                # Get content
                content_html = item.get_content().decode('utf-8', errors='ignore')
                content_text = self._clean_html(content_html)

                # Skip if empty or too short
                if len(content_text.strip()) < 50:
                    continue

                # Try to find title from TOC
                file_name = item.get_name()
                title = f"Chapter {chapter_num}"

                for toc_item in self.toc:
                    if toc_item['href'] and file_name in toc_item['href']:
                        title = toc_item['title']
                        break

                chapters.append({
                    'chapter_number': chapter_num,
                    'title': title,
                    'file_name': file_name,
                    'content': content_text,
                    'word_count': len(content_text.split())
                })

        return chapters

    def extract_all(self) -> Dict:
        """Extract all content from the EPUB file."""
        print(f"Extracting content from: {self.epub_path.name}")

        # Extract TOC
        print("Extracting table of contents...")
        self.toc = self._extract_toc()

        # Extract chapters
        print("Extracting chapters...")
        self.chapters = self.extract_chapters()

        result = {
            'metadata': self.metadata,
            'toc': self.toc,
            'chapters': self.chapters,
            'stats': {
                'total_chapters': len(self.chapters),
                'total_words': sum(ch['word_count'] for ch in self.chapters)
            }
        }

        print(f"✅ Extraction complete!")
        print(f"   - Chapters: {result['stats']['total_chapters']}")
        print(f"   - Total words: {result['stats']['total_words']:,}")

        return result


def main():
    parser = argparse.ArgumentParser(
        description='Extract content and structure from EPUB files'
    )
    parser.add_argument(
        'epub_file',
        help='Path to the EPUB file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (optional, prints to stdout if not specified)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    try:
        # Extract content
        extractor = EPUBExtractor(args.epub_file)
        result = extractor.extract_all()

        # Output
        indent = 2 if args.pretty else None
        json_output = json.dumps(result, ensure_ascii=False, indent=indent)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_output, encoding='utf-8')
            print(f"\n📄 Output saved to: {output_path}")
        else:
            print("\n" + "="*80)
            print(json_output)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
