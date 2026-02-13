# text-chunker

Chunk text for LLM pipelines with deterministic output and metadata.

## Install

```bash
python3 -m pip install text-chunker
```

## Usage

```bash
text-chunker --max-tokens 500 document.txt
cat document.txt | text-chunker --strategy semantic --overlap 100 --format jsonl
```

## Strategies

- `character`: fixed-width chunking
- `token`: token-budget chunking
- `sentence`: sentence-aware chunking
- `paragraph`: paragraph-aware chunking
- `semantic`: markdown headings + paragraphs

See `docs/index.md` for more examples.
