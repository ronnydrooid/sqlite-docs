#!/usr/bin/env python3
"""
Build combined plain text export of SQLite documentation.

This script recursively traverses the repository looking for .html files,
extracts readable text using BeautifulSoup, and builds a combined text file
with a table of contents.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:
    print("Error: BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
    sys.exit(1)


def extract_text_from_html(html_path: str) -> Tuple[str, str]:
    """
    Extract readable text from HTML file, preserving code blocks.
    
    Returns:
        Tuple of (title, extracted_text)
    """
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {html_path}: {e}")
        return "", ""
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else os.path.basename(html_path)
    
    # Remove navigation, header, footer elements
    for selector in [
        '.nosearch',       # Top navigation
        '.menu',           # Menu elements
        '.searchmenu',     # Search menu
        'script',          # JavaScript
        'style',           # CSS
        'head'             # Head section
    ]:
        for element in soup.select(selector):
            element.decompose()
    
    # Handle code blocks by marking them specially
    code_blocks = []
    for i, code_elem in enumerate(soup.find_all(['pre', 'code'])):
        placeholder = f"__CODE_BLOCK_{i}__"
        code_text = code_elem.get_text()
        code_blocks.append(code_text)
        code_elem.string = placeholder
    
    # Extract text from body or entire document if no body
    body = soup.find('body')
    if body:
        extracted_text = body.get_text(separator=' ', strip=True)
    else:
        extracted_text = soup.get_text(separator=' ', strip=True)
    
    # Restore code blocks with proper formatting
    for i, code_text in enumerate(code_blocks):
        placeholder = f"__CODE_BLOCK_{i}__"
        extracted_text = extracted_text.replace(placeholder, f"\n\n{code_text}\n\n")
    
    # Add formatting for headings by finding them in the original structure
    # This is a simpler approach that preserves the basic text while adding some structure
    heading_pattern = r'^([A-Z][A-Za-z0-9\s.,]+)$'
    lines = extracted_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line and re.match(heading_pattern, line) and len(line) < 200:
            # Likely a heading - add some formatting
            formatted_lines.append(f"\n\n{'='*60}\n{line}\n{'='*60}\n")
        else:
            formatted_lines.append(line)
    
    extracted_text = '\n'.join(formatted_lines)
    
    # Normalize whitespace - collapse multiple blank lines to at most two
    normalized_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', extracted_text)
    
    # Clean up extra whitespace
    normalized_text = re.sub(r'[ \t]+', ' ', normalized_text)
    normalized_text = normalized_text.strip()
    
    return title, normalized_text


def find_html_files(root_dir: str, order_file: Optional[str] = None) -> List[str]:
    """
    Find all HTML files in the repository.
    
    Args:
        root_dir: Root directory to search
        order_file: Optional file specifying custom ordering
        
    Returns:
        List of HTML file paths
    """
    html_files = []
    
    # If order file is provided, use that ordering
    if order_file and os.path.exists(order_file):
        try:
            with open(order_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        file_path = os.path.join(root_dir, line)
                        if os.path.exists(file_path) and file_path.endswith('.html'):
                            html_files.append(file_path)
        except Exception as e:
            print(f"Warning: Could not read order file {order_file}: {e}")
    
    # Find all HTML files recursively
    all_html_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                all_html_files.append(file_path)
    
    # If we have ordered files, add any remaining files not in the order
    if html_files:
        ordered_set = set(html_files)
        for file_path in sorted(all_html_files):
            if file_path not in ordered_set:
                html_files.append(file_path)
    else:
        # Sort alphabetically by filename
        html_files = sorted(all_html_files, key=lambda x: os.path.basename(x))
    
    return html_files


def build_combined_text(root_dir: str, output_file: str, order_file: Optional[str] = None):
    """
    Build the combined text file from all HTML files.
    
    Args:
        root_dir: Root directory containing HTML files
        output_file: Path to output text file
        order_file: Optional file specifying custom ordering
    """
    html_files = find_html_files(root_dir, order_file)
    
    if not html_files:
        print("No HTML files found!")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    # Build table of contents and extract content
    toc_entries = []
    content_sections = []
    
    for i, html_path in enumerate(html_files, 1):
        print(f"Processing [{i}/{len(html_files)}]: {os.path.relpath(html_path, root_dir)}")
        
        title, text_content = extract_text_from_html(html_path)
        
        if text_content.strip():
            relative_path = os.path.relpath(html_path, root_dir)
            toc_entries.append(f"{i:3d}. {title} ({relative_path})")
            
            # Add section header
            section_header = f"\n\n{'='*80}\n"
            section_header += f"FILE: {relative_path}\n"
            section_header += f"TITLE: {title}\n"
            section_header += f"{'='*80}\n\n"
            
            content_sections.append(section_header + text_content)
    
    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("SQLite Documentation - Combined Text Export\n")
        f.write("="*50 + "\n\n")
        f.write("This file contains all SQLite documentation converted to plain text.\n")
        f.write(f"Generated from {len(html_files)} HTML files.\n\n")
        
        # Write table of contents
        f.write("TABLE OF CONTENTS\n")
        f.write("="*20 + "\n\n")
        for toc_entry in toc_entries:
            f.write(toc_entry + "\n")
        f.write("\n")
        
        # Write content
        f.write("\nDOCUMENTATION CONTENT\n")
        f.write("="*25 + "\n")
        
        for section in content_sections:
            f.write(section)
            f.write("\n\n")
    
    print(f"Combined text file written to: {output_file}")
    print(f"Total sections: {len(content_sections)}")


def main():
    parser = argparse.ArgumentParser(
        description="Build combined plain text export of SQLite documentation"
    )
    parser.add_argument(
        '--root-dir', 
        default='.',
        help='Root directory to search for HTML files (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='combined-sqlite-docs.txt',
        help='Output filename (default: combined-sqlite-docs.txt)'
    )
    parser.add_argument(
        '--order-file',
        help='File specifying custom ordering of HTML files'
    )
    
    args = parser.parse_args()
    
    # Ensure we're working with absolute paths
    root_dir = os.path.abspath(args.root_dir)
    output_file = os.path.join(root_dir, args.output)
    
    if not os.path.exists(root_dir):
        print(f"Error: Root directory does not exist: {root_dir}")
        sys.exit(1)
    
    print(f"Building combined text export...")
    print(f"Root directory: {root_dir}")
    print(f"Output file: {output_file}")
    if args.order_file:
        print(f"Order file: {args.order_file}")
    
    build_combined_text(root_dir, output_file, args.order_file)


if __name__ == "__main__":
    main()