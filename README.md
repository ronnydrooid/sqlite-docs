# SQLite Documentation

This repository contains the official SQLite documentation in HTML format.

## Combined Plain Text Export

For convenience, this repository provides a single combined plain text file that contains all the SQLite documentation content. This allows users to download and search through the entire documentation set offline in a simple text format.

### Download

The combined documentation is available as: **[combined-sqlite-docs.txt](combined-sqlite-docs.txt)**

This file contains:
- All HTML documentation converted to readable plain text
- Preserved code blocks and examples
- Table of contents with file references
- UTF-8 encoding for full character support

### Regenerating the Combined Text File

The combined text file is automatically updated when changes are made to the repository. However, you can manually regenerate it using:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the extraction script
python scripts/build_text_dump.py

# Or with custom ordering
python scripts/build_text_dump.py --order-file my_order.txt
```

#### Script Options

- `--root-dir`: Directory to search for HTML files (default: current directory)
- `--output`: Output filename (default: combined-sqlite-docs.txt)
- `--order-file`: Optional file specifying custom ordering of HTML files

#### Custom Ordering

You can specify a custom order for the HTML files by providing a text file with one filename per line:

```
index.html
about.html
cli.html
# Lines starting with # are comments
lang_select.html
```

Files not listed in the order file will be appended alphabetically after the specified files.

### Technical Details

- The script uses BeautifulSoup4 to parse HTML and extract meaningful text
- Navigation menus, headers, footers, and scripts are excluded
- Code blocks (`<pre>` and `<code>` tags) are preserved with proper spacing
- Multiple blank lines are normalized to at most two consecutive lines
- Progress is shown during processing (number of documents processed)

The extraction process automatically handles all `.html` files in the repository, including subdirectories, while excluding hidden directories.