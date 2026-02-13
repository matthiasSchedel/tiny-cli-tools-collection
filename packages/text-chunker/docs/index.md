# text-chunker docs

## Quick Start

```bash
cat doc.txt | text-chunker --max-tokens 500 > chunks.json
```

## Common Patterns

### RAG pre-processing

```bash
text-chunker --strategy semantic --max-tokens 800 --overlap 80 docs.md
```

### Streaming chunks

```bash
text-chunker --format jsonl long.txt | jq -r '.text'
```

