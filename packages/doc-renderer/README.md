# doc-renderer

Convert documents between Markdown, HTML, PDF, DOCX, and ODT via Pandoc.

## Install

```bash
python3 -m pip install doc-renderer
brew install pandoc   # or your platform equivalent
```

## Usage

```bash
doc-renderer --to pdf README.md
doc-renderer --to html --template custom.html --css style.css docs.md
doc-renderer --batch "*.md" --to pdf
```
