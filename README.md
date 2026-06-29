[Japanese](README_J.md) | [English](README.md)

# wpxml2md

## Overview
A tool that converts WordPress export XML files into Markdown format suitable for Obsidian.

## Key Features
- Converts WordPress XML posts into individual Markdown files (one post per file)
- Uses Pandoc for HTML-to-Markdown conversion
- Generates front matter optimized for Obsidian
- Tag normalization
- Supports incremental/update-only imports
- Supports code blocks and image links

## Requirements
- Pandoc 3.x+
- Python 3.9+
- WordPress export XML file

[Pandoc](https://pandoc.org/) is required. If you haven't installed it, please download it [here](https://pandoc.org/installing.html). 
[Python](https://www.python.org/) is required. If you haven't installed it, please download it [here](https://www.python.org/downloads/). Note: On macOS, the script has been verified working with Python v3.9.6 (bundled with Tahoe 26.x).

## Usage
1. Prepare media files
Copy the media files (images, videos, etc.) used in WordPress to an appropriate location within your Obsidian Vault, or create a symbolic link to the media file folder.
2. User settings
Open the script in a text editor and modify the **User Settings** section at the beginning of the script to match your environment. 
`DEFAULT_OUT_DIR`: The default output directory for converted Markdown files. By default, it is set to a path matching the author's environment. 
`DEFAULT_SKIP_EXISTING`: Whether to skip files that have already been output. The default is `True` (i.e., skip existing files). 
3. Granting execution permissions
```bash
chmod +x wpxml2md.py
```
4. Usage examples
Basic
```bash
./wpxml2md.py WordPress.xml
```

Regenerate all items
```bash
./wpxml2md.py WordPress.xml --force
```

Specify output directory
```bash
./wpxml2md.py WordPress.xml --out ~/Desktop/Import
```

5. Options
The script supports the following options:
```text
--include-pages       Export pages as well
--all-status          Export posts regardless of status
--debug-title DEBUG_TITLE
                      Export only posts whose title contains the specified string
--force               Re-export existing posts
--out OUT             Output directory
```

## Verified environments
- macOS Tahoe 26.x
- Python 3.9.6
- Python 3.14.5
- Pandoc 3.8.2
- Pandoc 3.10

Since the script is written entirely in Python, it should work on systems other than macOS (e.g., Windows, Linux).

## Notes
### Regarding output files
For posts sharing the same `wordpress_post_id`, the script skips processing if the `wordpress_post_modified` timestamp is unchanged, and overwrites the file if it has been updated.
### Regarding image links
Self-links pointing to the same image (often used for features like WordPress Lightbox) are converted to simple image references, as they are unnecessary in Obsidian. Links to non-image content and external links are preserved. 

## At the end
This script was designed and refined through interactions with ChatGPT. The author was responsible for Final design, implementation, testing and maintenance.

## License
This script is licensed under the MIT License. Please refer to [LICENSE](LICENSE) for details.
