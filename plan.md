# World-Class Codex Prompts for CLI Tools

Here are production-ready prompts for each tool. These follow shot-scraper's philosophy: single responsibility, composable, agent-friendly, excellent docs.

---

## 1. text-chunker

```
Create a Python CLI tool called 'text-chunker' that intelligently splits text into chunks for LLM processing.

REFERENCE QUALITY BENCHMARK:
Study https://github.com/simonw/shot-scraper for code quality, documentation style, and CLI design patterns. Match that level of polish.

CORE FUNCTIONALITY:
- Accept text from file or stdin
- Split text into chunks respecting token limits
- Support multiple chunking strategies: character, token, sentence, paragraph, semantic
- Output JSON with chunks + metadata (character count, token count, boundaries)
- Handle overlap between chunks for context continuity
- Support multiple encoding models (cl100k_base for GPT-4, p50k_base for GPT-3, etc.)

CLI INTERFACE:
text-chunker [OPTIONS] [FILE]

Options:
  --max-tokens INTEGER         Maximum tokens per chunk (default: 1000)
  --max-chars INTEGER          Maximum characters per chunk (alternative to tokens)
  --overlap INTEGER            Overlap tokens between chunks (default: 0)
  --strategy [character|token|sentence|paragraph|semantic]
                              Chunking strategy (default: sentence)
  --encoding [cl100k_base|p50k_base|r50k_base]
                              Token encoding model (default: cl100k_base)
  --metadata / --no-metadata   Include metadata in output (default: true)
  --format [json|jsonl|text]  Output format (default: json)
  --help                      Show this message and exit

TECHNICAL REQUIREMENTS:
- Use Click for CLI (like shot-scraper)
- Use tiktoken for token counting
- For semantic chunking: split on paragraph boundaries, then sentence boundaries if needed
- Preserve markdown structure when detected (headings are chunk boundaries)
- Handle edge cases: empty input, single massive paragraph, unicode
- Exit codes: 0 success, 1 error
- Write to stdout (compatible with pipes)

OUTPUT FORMAT (JSON):
{
  "chunks": [
    {
      "index": 0,
      "text": "chunk content here...",
      "tokens": 250,
      "characters": 1024,
      "start_offset": 0,
      "end_offset": 1024,
      "boundaries": {"type": "paragraph", "complete": true}
    }
  ],
  "metadata": {
    "total_chunks": 5,
    "total_tokens": 1234,
    "total_characters": 5678,
    "strategy": "sentence",
    "max_tokens": 1000,
    "overlap": 100,
    "encoding": "cl100k_base"
  }
}

PROJECT STRUCTURE:
text-chunker/
  ├── text_chunker/
  │   ├── __init__.py
  │   ├── cli.py           # Click commands
  │   ├── chunker.py       # Core chunking logic
  │   ├── strategies.py    # Different chunking strategies
  │   └── utils.py         # Token counting, helpers
  ├── tests/
  │   ├── test_chunker.py
  │   ├── test_strategies.py
  │   └── fixtures/        # Test documents
  ├── docs/
  │   └── index.md         # Full documentation like shot-scraper
  ├── setup.py
  ├── README.md
  └── LICENSE              # Apache 2.0

DOCUMENTATION REQUIREMENTS:
- README with installation, quick start, examples
- Full docs site (use same structure as shot-scraper docs)
- Examples for each strategy
- Common use cases: "Chunking for RAG", "Splitting long documents"
- API reference for programmatic use

TESTING:
- Test each chunking strategy
- Test edge cases (empty, huge, unicode, markdown)
- Test exact token counts match tiktoken
- Test overlap works correctly
- Achieve >90% coverage

EXAMPLES TO INCLUDE IN DOCS:
# Basic usage
cat document.txt | text-chunker --max-tokens 500 > chunks.json

# Semantic chunking with overlap
text-chunker --strategy semantic --max-tokens 1000 --overlap 100 article.md

# JSONL output for streaming
text-chunker --format jsonl large-doc.txt | while read chunk; do
  echo "$chunk" | jq '.text'
done

QUALITY CHECKLIST:
- [ ] Passes mypy type checking
- [ ] Black formatted
- [ ] Works with Python 3.8+
- [ ] Zero external service dependencies
- [ ] Deterministic output (same input = same chunks)
- [ ] Fast (process 1MB in <1 second)
- [ ] Helpful error messages
- [ ] Works in pipes and scripts
```

---

## 2. api-mocker

```
Create a Python CLI tool called 'api-mocker' that spins up mock API servers from OpenAPI specs.

REFERENCE QUALITY BENCHMARK:
Study https://github.com/simonw/shot-scraper for code quality, documentation, and CLI design.

CORE FUNCTIONALITY:
- Accept OpenAPI 3.0+ specification (JSON or YAML)
- Start HTTP server serving mock endpoints
- Generate realistic fake data based on schemas
- Support path parameters, query params, request bodies
- Return appropriate status codes
- Log all requests with optional replay capability
- Support CORS for browser testing

CLI INTERFACE:
api-mocker [OPTIONS] SPEC_FILE

Options:
  --port INTEGER              Port to run server on (default: 8000)
  --host TEXT                 Host to bind to (default: 127.0.0.1)
  --log / --no-log           Log requests (default: true)
  --log-file PATH            Save request log to file
  --replay / --no-replay     Enable request replay endpoint (default: false)
  --delay INTEGER            Add delay to responses in ms (default: 0)
  --cors / --no-cors         Enable CORS headers (default: true)
  --validate / --no-validate Validate requests against schema (default: true)
  --help                     Show this message and exit

TECHNICAL REQUIREMENTS:
- Use Click for CLI
- Use Flask or FastAPI for HTTP server
- Use openapi-core for spec parsing and validation
- Use Faker for realistic fake data generation
- Support JSON Schema types: string, number, integer, boolean, array, object
- Handle $ref references in schemas
- Thread-safe request logging
- Graceful shutdown on SIGTERM

MOCK DATA GENERATION:
- Respect schema constraints (min/max, pattern, enum)
- Generate realistic data based on field names:
  - "email" → valid email addresses
  - "phone" → valid phone numbers  
  - "uuid" → valid UUIDs
  - "date" / "datetime" → ISO format
- Use examples from spec when provided
- Support custom data generators via config file

REQUEST LOGGING:
Store requests as JSONL:
{
  "timestamp": "2025-02-12T10:30:00Z",
  "method": "POST",
  "path": "/api/users",
  "headers": {...},
  "body": {...},
  "response_status": 201,
  "response_body": {...}
}

REPLAY ENDPOINT:
When --replay enabled, expose /_mock/requests:
GET /_mock/requests         # List all requests
GET /_mock/requests/{id}    # Get specific request
POST /_mock/replay/{id}     # Replay a request

PROJECT STRUCTURE:
api-mocker/
  ├── api_mocker/
  │   ├── __init__.py
  │   ├── cli.py           # Click interface
  │   ├── server.py        # HTTP server logic
  │   ├── generator.py     # Fake data generation
  │   ├── validator.py     # Request validation
  │   └── logger.py        # Request logging
  ├── tests/
  │   ├── test_server.py
  │   ├── test_generator.py
  │   └── fixtures/        # Sample OpenAPI specs
  ├── docs/
  ├── examples/
  │   └── petstore.yaml    # Example spec
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Start mock server
api-mocker openapi.yaml

# Custom port with request logging
api-mocker --port 3000 --log-file requests.jsonl api-spec.yaml

# Add latency simulation
api-mocker --delay 200 openapi.yaml

# With validation and replay
api-mocker --validate --replay spec.yaml

USE CASES TO DOCUMENT:
1. Frontend development before backend is ready
2. Testing error scenarios
3. CI/CD integration testing
4. API client library testing
5. Agent/automation testing

QUALITY CHECKLIST:
- [ ] Handles all OpenAPI 3.x features
- [ ] Fast startup (<1 second)
- [ ] Clear error messages for invalid specs
- [ ] Graceful shutdown
- [ ] Memory efficient for long-running mocks
- [ ] Cross-platform (Windows/Mac/Linux)
```

---

## 3. rate-limiter

```
Create a universal CLI tool called 'rate-limiter' that wraps any command with rate limiting.

REFERENCE QUALITY BENCHMARK:
Study https://github.com/simonw/shot-scraper for simplicity and composability.

CORE FUNCTIONALITY:
- Wrap any shell command with rate limiting
- Support multiple rate limit strategies (RPM, RPS, burst)
- Persist state across invocations (optional)
- Queue commands when limit is reached
- Work seamlessly in shell scripts and pipes
- Zero dependencies beyond standard library

CLI INTERFACE:
rate-limiter [OPTIONS] -- COMMAND [ARGS...]

Options:
  --rpm INTEGER              Requests per minute (default: 60)
  --rps INTEGER              Requests per second (overrides --rpm)
  --burst INTEGER            Allow burst of N requests (default: 1)
  --state-file PATH          Persist rate limit state (default: in-memory)
  --wait / --no-wait         Wait if limit exceeded vs error (default: wait)
  --timeout INTEGER          Max wait time in seconds (default: 300)
  --key TEXT                 Rate limit key for grouping (default: command)
  --verbose / --quiet        Show rate limit status (default: quiet)
  --help                     Show this message and exit

TECHNICAL REQUIREMENTS:
- Use Python (or Go for single-binary distribution)
- Implement token bucket algorithm
- Use fcntl for file locking if state-file used
- Exit codes: preserve wrapped command's exit code
- Stdout/stderr: pass through wrapped command's output
- Handle signals properly (SIGTERM, SIGINT)

RATE LIMITING ALGORITHM:
Token bucket with:
- Capacity = burst size
- Refill rate = rpm/60 tokens per second (or rps)
- On command execution: consume 1 token
- If no tokens available: wait (if --wait) or exit 1

STATE FILE FORMAT (JSON):
{
  "key": "curl-api-example",
  "last_refill": "2025-02-12T10:30:00Z",
  "tokens": 5.7,
  "capacity": 10,
  "refill_rate": 1.0
}

PROJECT STRUCTURE:
rate-limiter/
  ├── rate_limiter/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── bucket.py        # Token bucket implementation
  │   └── state.py         # State persistence
  ├── tests/
  │   ├── test_bucket.py
  │   ├── test_cli.py
  │   └── test_state.py
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Limit API calls to 60/minute
for url in $(cat urls.txt); do
  rate-limiter --rpm 60 -- curl "$url"
done

# Burst of 5, then 10 per minute
rate-limiter --rpm 10 --burst 5 -- curl https://api.example.com

# Persistent state across script runs
rate-limiter --rpm 100 --state-file ~/.cache/api-limits -- \
  curl https://api.example.com/data

# Different limits for different APIs
rate-limiter --rpm 60 --key github-api -- gh api /user/repos
rate-limiter --rpm 30 --key twitter-api -- twitter-cli get

# In a loop with error handling
while read line; do
  if ! rate-limiter --rpm 30 --timeout 60 -- process "$line"; then
    echo "Failed: $line" >> errors.log
  fi
done < input.txt

USE CASES:
1. API calls in scripts
2. Web scraping
3. Bulk operations
4. CI/CD pipelines
5. Agent workflows calling external APIs

ADVANCED FEATURES (v2):
- Multiple rate limits (--rpm 60 --hourly 1000)
- Exponential backoff on errors
- Distributed rate limiting (Redis backend)

QUALITY CHECKLIST:
- [ ] Works with ANY command (no special handling)
- [ ] Accurate rate limiting (within 1% of target)
- [ ] Low overhead (<10ms per call)
- [ ] Safe concurrent usage (file locking)
- [ ] Handles edge cases (leap seconds, system time changes)
- [ ] Clear documentation of token bucket algorithm
```

---

## 4. schema-guesser

```
Create a CLI tool called 'schema-guesser' that infers JSON schemas from example data.

REFERENCE QUALITY BENCHMARK:
Match shot-scraper's quality: clear interface, JSON output, excellent docs.

CORE FUNCTIONALITY:
- Accept JSON data from file or stdin
- Analyze structure and infer JSON Schema
- Calculate confidence scores for inferred types
- Detect optional vs required fields
- Infer string formats (email, uri, date, etc.)
- Support multiple examples to improve accuracy
- Output valid JSON Schema Draft 7

CLI INTERFACE:
schema-guesser [OPTIONS] [FILES...]

Options:
  --samples INTEGER          Number of samples to analyze (default: all)
  --confidence FLOAT         Minimum confidence threshold (default: 0.8)
  --strict / --lenient       Strict type inference (default: lenient)
  --format [json|yaml]       Output format (default: json)
  --title TEXT               Schema title
  --description TEXT         Schema description
  --stdin / --no-stdin       Read from stdin (default: auto-detect)
  --help                     Show this message and exit

TECHNICAL REQUIREMENTS:
- Pure Python, minimal dependencies
- Use jsonschema for validation
- Infer types by majority vote across samples
- Detect patterns: email, URL, UUID, ISO date, phone
- Handle nested objects and arrays
- Support union types (anyOf) when data varies
- Calculate confidence: (consistent_samples / total_samples)

INFERENCE LOGIC:
1. Parse all JSON samples
2. Build type frequency map for each field
3. Determine dominant type (>threshold = required, <threshold = optional)
4. Detect formats by pattern matching
5. Infer constraints (min/max length, numeric ranges)
6. Build schema with confidence annotations

OUTPUT FORMAT:
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email",
      "x-confidence": 1.0
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 120,
      "x-confidence": 0.95
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "x-confidence": 0.85
    }
  },
  "required": ["email", "age"],
  "x-metadata": {
    "samples_analyzed": 100,
    "inference_date": "2025-02-12T10:30:00Z"
  }
}

PROJECT STRUCTURE:
schema-guesser/
  ├── schema_guesser/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── inferrer.py      # Core inference logic
  │   ├── patterns.py      # Format detection patterns
  │   └── constraints.py   # Constraint detection
  ├── tests/
  │   ├── test_inferrer.py
  │   ├── test_patterns.py
  │   └── fixtures/
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Single file
schema-guesser data.json

# Multiple samples for better inference
schema-guesser sample1.json sample2.json sample3.json

# From API response
curl https://api.example.com/users | schema-guesser --stdin

# JSONL input (one JSON object per line)
cat users.jsonl | schema-guesser --format yaml

# Strict mode (fail on ambiguous types)
schema-guesser --strict --confidence 0.95 data.json

USE CASES:
1. Document unknown APIs
2. Generate TypeScript interfaces
3. Create validation for incoming data
4. Understand third-party data structures
5. Agent exploration of new data sources

PATTERN DETECTION:
- Email: RFC 5322 regex
- URL: starts with http(s)://
- UUID: v4 format
- Date: ISO 8601
- Phone: E.164 format
- IPv4/IPv6
- Credit card (Luhn check)

QUALITY CHECKLIST:
- [ ] Handles 100k+ samples efficiently
- [ ] Accurate type inference (>95% on test suite)
- [ ] Produces valid JSON Schema
- [ ] Handles edge cases (null, empty arrays, mixed types)
- [ ] Memory efficient (streaming for large files)
```

---

## 5. webhook-relay

```
Create a CLI tool called 'webhook-relay' that receives webhooks locally without exposing ports.

REFERENCE QUALITY BENCHMARK:
Shot-scraper level of polish and documentation.

CORE FUNCTIONALITY:
- Start local HTTP server for receiving webhooks
- No external tunnel service required (unlike ngrok)
- Store received requests with full details
- Web UI for inspecting requests
- Optional forwarding to local services
- Request replay capability
- Webhook signature validation

CLI INTERFACE:
webhook-relay [OPTIONS]

Options:
  --port INTEGER             Port for webhook receiver (default: 8080)
  --forward URL              Forward requests to this URL
  --storage PATH             SQLite database for requests (default: memory)
  --ui-port INTEGER          Web UI port (default: 8081)
  --validate-signature TEXT  Validate webhook signatures (e.g., "github", "stripe")
  --secret TEXT              Secret for signature validation
  --capacity INTEGER         Max stored requests (default: 1000)
  --help                     Show this message and exit

TECHNICAL REQUIREMENTS:
- Python with Flask/FastAPI
- SQLite for request storage
- Simple web UI (vanilla JS + Tailwind)
- WebSocket for real-time request updates
- Support common webhook signatures (GitHub, Stripe, Shopify)
- CORS enabled for web UI

REQUEST STORAGE:
requests table:
  id TEXT PRIMARY KEY
  timestamp TEXT
  method TEXT
  path TEXT
  headers JSON
  body BLOB
  query_params JSON
  forwarded_status INTEGER
  signature_valid BOOLEAN

WEB UI FEATURES:
- List all received requests
- Search/filter by path, method, timestamp
- View request details (headers, body)
- Replay request to local service
- Delete requests
- Export as cURL command

PROJECT STRUCTURE:
webhook-relay/
  ├── webhook_relay/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── server.py         # Webhook receiver
  │   ├── ui.py             # Web UI server
  │   ├── storage.py        # SQLite operations
  │   ├── signatures.py     # Signature validation
  │   └── static/
  │       ├── index.html
  │       └── app.js
  ├── tests/
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Start webhook receiver
webhook-relay

# Forward to local dev server
webhook-relay --forward http://localhost:3000

# Validate GitHub webhooks
webhook-relay --validate-signature github --secret "your-secret"

# Persistent storage
webhook-relay --storage webhooks.db

# Custom ports
webhook-relay --port 9000 --ui-port 9001

SIGNATURE VALIDATION:
Support for:
- GitHub: X-Hub-Signature-256 (HMAC SHA256)
- Stripe: Stripe-Signature (timestamp + signature)
- Shopify: X-Shopify-Hmac-Sha256
- Generic HMAC

API ENDPOINTS:
POST /*                     # Catch all webhooks
GET /_relay/requests        # List requests (JSON)
GET /_relay/requests/:id    # Get specific request
POST /_relay/replay/:id     # Replay request
DELETE /_relay/requests/:id # Delete request

REAL-TIME UPDATES:
WebSocket at /_relay/ws:
{
  "type": "new_request",
  "request": {
    "id": "abc123",
    "method": "POST",
    "path": "/webhook",
    "timestamp": "2025-02-12T10:30:00Z"
  }
}

USE CASES:
1. Local webhook testing
2. Debugging webhook integrations
3. Developing webhook handlers
4. Testing webhook signatures
5. Agent development with webhooks

QUALITY CHECKLIST:
- [ ] Zero external dependencies (no tunneling service)
- [ ] Fast startup (<1 second)
- [ ] Handles concurrent requests
- [ ] Clean, responsive UI
- [ ] Works on all platforms
- [ ] Proper error handling and logging
```

---

## 6. page-differ

```
Create a CLI tool called 'page-differ' that detects semantic changes between web page versions.

REFERENCE QUALITY BENCHMARK:
Shot-scraper quality: composable, JSON output, clear documentation.

CORE FUNCTIONALITY:
- Compare two versions of a web page (URLs or HTML files)
- Detect DOM structural changes
- Find content changes (text added/removed/modified)
- Visual diffing (screenshot comparison)
- Ignore dynamic content (timestamps, ads)
- Output semantic change report

CLI INTERFACE:
page-differ [OPTIONS] URL1 URL2

Options:
  --mode [dom|content|visual|all]  Comparison mode (default: all)
  --ignore-selectors TEXT          CSS selectors to ignore
  --threshold FLOAT                Visual diff threshold (default: 0.01)
  --format [json|html|text]        Output format (default: json)
  --screenshots / --no-screenshots Save diff images (default: false)
  --output PATH                    Output file (default: stdout)
  --help                           Show this message and exit

TECHNICAL REQUIREMENTS:
- Use Playwright or Selenium for page rendering
- BeautifulSoup for DOM parsing
- Pillow for image comparison
- difflib for text diffing
- Output structural changes as JSON

COMPARISON MODES:

1. DOM Mode:
- Parse HTML into tree structure
- Detect added/removed/moved elements
- Report: element path, type, attributes

2. Content Mode:
- Extract visible text
- Ignore whitespace/formatting changes
- Diff at paragraph/sentence level
- Report: additions, deletions, modifications

3. Visual Mode:
- Take screenshots of both pages
- Pixel-by-pixel comparison
- Highlight changed regions
- Report: bounding boxes of differences

OUTPUT FORMAT (JSON):
{
  "url1": "https://example.com/v1",
  "url2": "https://example.com/v2",
  "timestamp": "2025-02-12T10:30:00Z",
  "changes": {
    "dom": {
      "added": [
        {"selector": "div.new-feature", "html": "..."}
      ],
      "removed": [
        {"selector": "div.old-banner", "html": "..."}
      ],
      "modified": [
        {"selector": "h1", "before": "Old Title", "after": "New Title"}
      ]
    },
    "content": {
      "added_paragraphs": ["New paragraph text..."],
      "removed_paragraphs": ["Old paragraph text..."],
      "text_similarity": 0.85
    },
    "visual": {
      "diff_percentage": 2.5,
      "changed_regions": [
        {"x": 100, "y": 200, "width": 300, "height": 150}
      ]
    }
  },
  "summary": {
    "significant_changes": true,
    "change_score": 0.15
  }
}

PROJECT STRUCTURE:
page-differ/
  ├── page_differ/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── dom_differ.py
  │   ├── content_differ.py
  │   ├── visual_differ.py
  │   └── utils.py
  ├── tests/
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Compare two versions
page-differ https://example.com/old https://example.com/new

# DOM changes only
page-differ --mode dom old.html new.html

# Ignore dynamic elements
page-differ --ignore-selectors ".timestamp,.ad" url1 url2

# Visual comparison with screenshots
page-differ --mode visual --screenshots before.html after.html

# HTML report
page-differ --format html --output report.html url1 url2

SMART IGNORING:
Default ignore patterns:
- .timestamp, .date, time elements
- Script/style tags
- Comments
- Analytics/tracking codes
- Ad containers

USE CASES:
1. Monitor website changes
2. Detect unauthorized modifications
3. Track competitor changes
4. A/B test verification
5. Regression testing for web apps

QUALITY CHECKLIST:
- [ ] Accurate DOM diffing
- [ ] Fast comparison (<5 seconds for typical pages)
- [ ] Handles JavaScript-heavy sites
- [ ] Configurable ignore patterns
- [ ] Clear change summaries
```

---

## 7. form-filler

```
Create a CLI tool called 'form-filler' that fills web forms declaratively from JSON/YAML.

REFERENCE QUALITY BENCHMARK:
Shot-scraper's simplicity and reliability.

CORE FUNCTIONALITY:
- Accept form data as JSON/YAML
- Navigate to URL and fill forms
- Support all input types (text, select, checkbox, radio, file)
- Handle multi-step forms
- Screenshot before/after
- Return submission result

CLI INTERFACE:
form-filler [OPTIONS] URL DATA_FILE

Options:
  --format [json|yaml]         Data format (default: auto-detect)
  --wait-for TEXT              CSS selector to wait for
  --screenshot / --no-screenshot  Save screenshots (default: false)
  --submit / --no-submit       Submit form vs just fill (default: submit)
  --output PATH                Save result (default: stdout)
  --browser [chromium|firefox|webkit]  Browser to use (default: chromium)
  --help                       Show this message and exit

DATA FILE FORMAT (YAML):
url: https://example.com/contact
wait_for: "form#contact"
fields:
  - selector: "#name"
    value: "John Doe"
  - selector: "#email"
    value: "john@example.com"
  - selector: "#country"
    value: "US"
    type: select
  - selector: "#subscribe"
    value: true
    type: checkbox
  - selector: "#avatar"
    value: "./photo.jpg"
    type: file
submit_button: "button[type=submit]"
wait_after_submit: 2000
expected_redirect: https://example.com/thank-you

TECHNICAL REQUIREMENTS:
- Use Playwright for browser automation
- Support CSS selectors and XPath
- Handle iframes
- Wait for dynamic content
- Validate form was filled correctly
- Return structured result

OUTPUT FORMAT:
{
  "status": "success",
  "url": "https://example.com/contact",
  "filled_fields": 5,
  "submitted": true,
  "final_url": "https://example.com/thank-you",
  "screenshots": {
    "before": "before.png",
    "after": "after.png"
  },
  "duration_ms": 2341,
  "errors": []
}

PROJECT STRUCTURE:
form-filler/
  ├── form_filler/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── filler.py        # Core filling logic
  │   ├── validators.py    # Field validation
  │   └── utils.py
  ├── tests/
  ├── examples/
  │   ├── contact-form.yaml
  │   └── registration.yaml
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Fill and submit form
form-filler https://example.com/contact data.yaml

# Fill without submitting
form-filler --no-submit https://example.com/form data.json

# With screenshots
form-filler --screenshot contact.example.com form-data.yaml

FIELD TYPES SUPPORTED:
- text/email/tel/number/url: input[type=...]
- textarea
- select (single and multi)
- checkbox
- radio
- file upload
- date/datetime-local

MULTI-STEP FORMS:
steps:
  - url: https://example.com/step1
    fields:
      - selector: "#email"
        value: "test@example.com"
    submit: "button.next"
    wait_for: "#step2"
  
  - fields:
      - selector: "#password"
        value: "secret123"
    submit: "button.finish"

USE CASES:
1. Automated form testing
2. Bulk form submissions
3. Registration automation
4. Data migration
5. Agent form interaction

QUALITY CHECKLIST:
- [ ] Handles all HTML5 input types
- [ ] Robust waiting strategies
- [ ] Clear error messages
- [ ] Works with SPAs and traditional forms
- [ ] File upload support
- [ ] Cross-browser compatibility
```

---

## 8. json-patcher

```
Create a CLI tool called 'json-patcher' for smart JSON patching and merging.

REFERENCE QUALITY BENCHMARK:
Shot-scraper's clarity and composability.

CORE FUNCTIONALITY:
- Apply JSON patches (RFC 6902)
- Merge JSON documents with strategies
- JSONPath-based transformations
- Validation after patching
- Diff generation between JSON docs
- Output structured results

CLI INTERFACE:
json-patcher [OPTIONS] COMMAND [ARGS]

Commands:
  patch   Apply JSON patch to document
  merge   Merge two JSON documents
  diff    Generate patch between documents
  query   Extract values using JSONPath

Options for patch:
  --patch FILE              Patch operations file
  --validate SCHEMA         Validate result against schema
  --in-place               Modify file in-place
  --format [json|yaml]     Output format

Options for merge:
  --strategy [replace|merge|append|smart]
  --array-strategy [replace|concat|unique]

TECHNICAL REQUIREMENTS:
- Pure Python, jsonpatch library
- Support RFC 6902 operations (add, remove, replace, move, copy, test)
- JSONPath queries (jsonpath-ng)
- Schema validation (jsonschema)
- Preserve formatting when possible

PATCH OPERATIONS (RFC 6902):
[
  {"op": "add", "path": "/new_field", "value": "data"},
  {"op": "remove", "path": "/old_field"},
  {"op": "replace", "path": "/existing", "value": "new_value"},
  {"op": "move", "from": "/old/path", "path": "/new/path"},
  {"op": "copy", "from": "/source", "path": "/dest"},
  {"op": "test", "path": "/check", "value": "expected"}
]

MERGE STRATEGIES:
- replace: Right overrides left completely
- merge: Deep merge objects, last wins for scalars
- append: Arrays concatenate
- smart: Context-aware (merge objects, concat arrays)

PROJECT STRUCTURE:
json-patcher/
  ├── json_patcher/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── patcher.py
  │   ├── merger.py
  │   ├── differ.py
  │   └── query.py
  ├── tests/
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Apply patch
json-patcher patch data.json --patch changes.json

# Merge configs
json-patcher merge base.json override.json --strategy smart

# Generate diff
json-patcher diff old.json new.json > changes.patch

# Query with JSONPath
json-patcher query data.json "$.users[?(@.active)]"

# Validate after patch
json-patcher patch data.json --patch ops.json --validate schema.json

# In-place update
json-patcher patch --in-place config.json --patch updates.json

OUTPUT FORMAT:
{
  "success": true,
  "operations_applied": 5,
  "result": {...},
  "validation": {
    "valid": true,
    "errors": []
  }
}

USE CASES:
1. Config file updates
2. API response transformations
3. Test data generation
4. Migration scripts
5. Agent data manipulation

QUALITY CHECKLIST:
- [ ] RFC 6902 compliant
- [ ] Handles large JSON (100MB+)
- [ ] Preserves number precision
- [ ] Unicode safe
- [ ] Atomic operations (all or nothing)
```

---

## 9. doc-renderer

```
Create a CLI tool called 'doc-renderer' for document format conversion.

REFERENCE QUALITY BENCHMARK:
Shot-scraper quality with focus on reliability.

CORE FUNCTIONALITY:
- Convert between document formats
- Support Markdown, HTML, PDF, DOCX, ODT, RST
- Template support for HTML/PDF
- CSS styling for PDF output
- Batch conversion
- Preserve structure and formatting

CLI INTERFACE:
doc-renderer [OPTIONS] INPUT [OUTPUT]

Options:
  --from [md|html|rst|docx|odt]   Input format (default: auto)
  --to [md|html|pdf|docx|odt]     Output format (required)
  --template PATH                  HTML/PDF template
  --css PATH                       CSS for HTML/PDF
  --metadata FILE                  Document metadata (JSON/YAML)
  --toc / --no-toc                 Table of contents (default: false)
  --batch PATTERN                  Convert multiple files
  --help                           Show this message and exit

TECHNICAL REQUIREMENTS:
- Use Pandoc as conversion engine
- WeasyPrint for PDF generation
- python-docx for DOCX
- Beautiful Soup for HTML processing
- Template engine (Jinja2)

SUPPORTED CONVERSIONS:
Markdown → HTML, PDF, DOCX, ODT, RST
HTML → PDF, Markdown, DOCX
DOCX → Markdown, HTML, PDF
RST → Markdown, HTML, PDF

TEMPLATES:
HTML template (Jinja2):
<!DOCTYPE html>
<html>
<head>
  <title>{{ title }}</title>
  <link rel="stylesheet" href="{{ css }}">
</head>
<body>
  {{ content }}
</body>
</html>

METADATA FILE:
title: "My Document"
author: "John Doe"
date: "2025-02-12"
keywords: ["documentation", "tools"]

PROJECT STRUCTURE:
doc-renderer/
  ├── doc_renderer/
  │   ├── __init__.py
  │   ├── cli.py
  │   ├── converters/
  │   │   ├── md.py
  │   │   ├── html.py
  │   │   ├── pdf.py
  │   │   └── docx.py
  │   ├── templates/
  │   └── utils.py
  ├── tests/
  ├── examples/
  ├── docs/
  ├── setup.py
  └── README.md

EXAMPLES FOR DOCS:
# Markdown to PDF
doc-renderer --to pdf document.md

# With custom template
doc-renderer --to html --template custom.html doc.md

# Batch conversion
doc-renderer --batch "*.md" --to pdf

# With metadata
doc-renderer --to pdf --metadata meta.yaml --toc readme.md

USE CASES:
1. Documentation generation
2. Report creation
3. Format migration
4. Publishing workflows
5. Agent document generation

QUALITY CHECKLIST:
- [ ] High-quality PDF output
- [ ] Preserves formatting
- [ ] Handles large documents
- [ ] Fast conversion
- [ ] Cross-platform
```

---

Each prompt is designed to create a production-ready tool matching shot-scraper's quality. They include:
- ✅ Complete CLI specification
- ✅ Technical implementation details
- ✅ Project structure
- ✅ Output formats
- ✅ Examples and use cases
- ✅ Quality checklists

Would you like me to dive deeper into any of these prompts or help you prioritize which to build first?
