# AI Content Studio — Design Spec

## Overview

An AI-powered content production system that generates brand-aligned LinkedIn posts, cold emails, newsletters, and blog content from a central brand repository. The system has three layers: **research** (what's working), **swipe file** (the patterns), and **generation** (the output). A portable `writing-skills.md` file makes the brand voice reusable across any AI platform.

## Architecture

```
                    RESEARCH LAYER
  Firecrawl ──► LinkedIn Scraper ──► Performance Analysis
  Firecrawl ──► Newsletter Archive ──► Subject Line Patterns
  Firecrawl ──► Competitor Blogs ──► Topic Clusters
                        │
                        ▼
                  swipe-file/whats-working.md
                        │
                    ┌───┴───┐
                    │       │
                    ▼       ▼
          ┌─────────────────────────────┐
          │      OBSIDIAN VAULT         │
          │  brands/{name}/             │
          │   ├── brand-kit.md          │
          │   ├── swipe-file/           │
          │   │   ├── hooks.md          │
          │   │   ├── frameworks.md     │
          │   │   ├── subject-lines.md  │
          │   │   ├── cta-library.md    │
          │   │   ├── channel-rules/    │
          │   │   │   ├── linkedin.md   │
          │   │   │   ├── email.md      │
          │   │   │   └── blog.md       │
          │   │   └── whats-working.md  │
          │   ├── content-library/      │
          │   └── generated/            │
          └─────────────────────────────┘
                        │
                    compile_skills.py
                        │
                        ▼
                  writing-skills.md ◄──── Load into any AI
                        │
                        ▼
          ┌─────────────────────────────┐
          │    GENERATION AGENTS        │
          │                             │
          │  generate_linkedin.py       │
          │  generate_email.py          │
          │  generate_blog.py           │
          │  repurpose.py               │
          │                             │
          │  All: --brand --demo        │
          │       --dry-run             │
          └─────────────────────────────┘
                        │
                   ┌────┴────┐
                   ▼         ▼
              Obsidian/   n8n/
              generated   publish
```

## Directory Layout

```
ai-content-studio/
├── code/
│   ├── research_scout.py         # Firecrawl-based channel performance analysis
│   ├── compile_skills.py         # brand-kit + swipe-file → writing-skills.md
│   ├── generate_linkedin.py      # LinkedIn post drafts
│   ├── generate_email.py         # Cold emails & newsletters
│   ├── generate_blog.py          # Blog outlines → sections → drafts
│   └── repurpose.py              # One piece → all channel variants
├── automation/
│   ├── content-studio.json       # n8n workflow: generate → obsidian + publish
│   └── research-scan.json        # n8n weekly research scanner
├── swipe-file/
│   ├── hooks.md
│   ├── frameworks.md
│   ├── subject-lines.md
│   ├── cta-library.md
│   └── channel-rules/
│       ├── linkedin.md
│       ├── email.md
│       └── blog.md
└── README.md
```

## Component Specs

### 1. `research_scout.py`

**Purpose:** Analyze what content is performing across channels. Uses Firecrawl to scrape LinkedIn posts, newsletter archives, and competitor blogs. Outputs structured findings to `swipe-file/whats-working.md`.

**Inputs:**
- `--brand` — brand name (loads brand config)
- `--source` — linkedin | newsletter | competitor | all
- `--demo` — use cached sample data instead of Firecrawl
- `--dry-run` — print findings without writing to vault

**Outputs:**
- Updates `swipe-file/whats-working.md` with:
  - Top-performing post patterns (hooks, length, format)
  - High-open subject line clusters
  - Emerging topic clusters by channel
  - Engagement benchmarks

**Error handling:** Firecrawl failures → fall back to demo data with warning. Partial results still written.

### 2. `compile_skills.py`

**Purpose:** Reads the brand kit + full swipe file → generates `writing-skills.md` — a single portable markdown file that any AI can ingest as a system prompt.

**Inputs:**
- `--brand` — brand name
- `--output` — output path (default: `brands/{name}/writing-skills.md`)
- `--dry-run` — print what would be compiled

**Output format (`writing-skills.md`):**

```markdown
# Writing Skills: Awesome Hires

## Brand Voice
- Direct, analytical, occasionally blunt
- Evidence-forward with data and named sources
- Short paragraphs, one-sentence punch lines
- Second-person address for guidance

## Audiences
- Founders hiring early teams
- Hiring managers and team leads
- Recruiters and talent ops

## Channel Rules

### LinkedIn
- Character count: 900-1500
- Hook: question or bold claim
- Format: 2-3 line breaks, one idea per paragraph
- Hashtags: 3-5, all lowercase

### Email
- Subject line: 35-50 characters
- Preview text: mandatory, under 100 chars
- Personalization: {{company}}, {{role}}
- CTA: exactly one per email

### Blog
- H2 every 300 words
- Data point in first 300 words
- Internal link to at least one other post

## Swipe File: Proven Hooks
- "Most [industry] teams get [X] wrong. Here's why."
- "We analyzed [N] [topic] and found [surprising pattern]."
- "Stop doing [common mistake]. Do this instead."

## Swipe File: CTAs
| Intent | CTA |
|--------|-----|
| Demo booking | "See it in action →" |
| Content click | "Read the full analysis →" |
| Apply (job) | "Apply in 30 seconds →" |

## Swipe File: Subject Lines
- "[Number] ways to [benefit] without [pain]"
- "Your weekly [topic] roundup"
```
```

### 3. `generate_linkedin.py`

**Purpose:** Generate LinkedIn post drafts grounded in brand voice.

**Inputs:**
- `--brand` — brand name
- `--topic` — content topic
- `--angle` — thought-leadership | product | culture | educational
- `--variants` — number of variants (default 2)
- `--demo` — use sample brand data
- `--dry-run` — preview without writing

**Output:**
- Writes `.md` to `brands/{name}/generated/{date}-linkedin-{slug}.md`
- Prints JSON to stdout for n8n consumption:
```json
{
  "brand": "awesome-hires",
  "content_type": "linkedin_post",
  "variants": [{"variant": "a", "hook": "...", "body": "...", "cta": "..."}],
  "suggested_hashtags": ["#hiring", "#ai"],
  "best_time_to_post": "Tue 10am EST"
}
```

### 4. `generate_email.py`

**Purpose:** Cold email or newsletter generation.

**Inputs:**
- `--brand`, `--topic`, `--type` (cold | newsletter | follow-up)
- `--recipient-segment` —  icp-fit | warm | lost-deal
- `--variants`, `--demo`, `--dry-run`

**Output:**
- Subject line variants with predicted open rate indicators
- Preview text
- Body with personalization tokens
- CTA variants

### 5. `generate_blog.py`

**Purpose:** Outline → section-by-section blog drafting.

**Inputs:**
- `--brand`, `--topic`, `--length` (short | medium | long)
- `--seo-keyword` — primary keyword for optimization
- `--outline-only` — generate just the outline
- `--demo`, `--dry-run`

**Output:**
- Blog draft with H2 sections
- SEO metadata (title, description, keywords)
- Internal link suggestions
- 2-3 image briefs for featured/ad images

### 6. `repurpose.py`

**Purpose:** Take one piece of content and generate variants across all channels.

**Inputs:**
- `--brand`, `--input` (path to source .md or text)
- `--channels` — linkedin | email | blog | all
- `--demo`, `--dry-run`

**Flow:**
1. Read source content
2. Extract core narrative / data points / angle
3. Generate LinkedIn post (condensed, hook-driven)
4. Generate email version (personalized, direct)
5. Generate blog version (expanded, structured)
6. All variants → Obsidian `generated/` + JSON for n8n

## Data Flow

```
1. Weekly: research_scout.py ──Firecrawl──► whats-working.md
2. Continual: Human adds patterns → swipe-file/
3. On brand update: compile_skills.py → writing-skills.md
4. On request: generate_*.py reads writing-skills.md → drafts
5. Generated content → Obsidian generated/ (review) + n8n (publish)
```

## Brand Path Resolution

The `--brand` flag resolves to `brands/{name}/` inside the Obsidian vault root. The vault root is set via:
- `OBSIDIAN_VAULT_PATH` environment variable
- `.env` file in `shared/config/`
- Default: `./brands/` (relative to the ai-content-studio directory)

If the path doesn't exist, the agent prints available brands and exits.

## writing-skills.md Usage

This file is designed as a **system prompt** — not a standalone instruction file. Usage depends on the AI:

| Platform | How to Load |
|----------|-------------|
| Claude Projects | Copy into Project Instructions |
| ChatGPT Custom GPT | Paste into "Instructions" field |
| Gemini Saved Prompts | Load as context before generation |
| OpenCode Skills | Save as `.opencode/skills/{brand}-writing/skill.md` |
| Any other AI | Paste as system prompt or context preamble |

The file is intentionally flat and copy-paste friendly — no dependencies on Obsidian paths or external files.

## n8n Connectors

The n8n workflows reference LinkedIn, Gmail, and Ghost as illustrative targets. Actual connectors depend on deployment. The JSON output from agents is designed to be connector-agnostic — any HTTP-capable platform can consume it.

## Error Handling

| Failure | Behavior |
|---------|----------|
| Firecrawl timeout | Fall back to demo data, log warning |
| Missing brand-kit.md | Print error with path, exit code 1 |
| Invalid brand name | List available brands from vault |
| LLM API failure | Retry once, then exit with error |
| n8n unavailable | Write to Obsidian only, log warning |

## Output Conventions

- Brand markdown in Obsidian: always `.md`
- Generated content: `{date}-{type}-{slug}.md` with YAML frontmatter
- JSON for n8n: flat structure, no nested objects beyond variants
- writing-skills.md: single file, max 200 lines, ready to copy-paste into any AI

## Success Criteria

- writing-skills.md loads into Claude Project, ChatGPT Custom GPT, Gemini, OpenCode and produces on-brand output
- repurpose.py generates 3 channel variants from a single blog post in under 30 seconds
- research_scout.py surfaces at least 5 actionable patterns per scan
- Every agent runs with --demo and produces realistic output without API keys
- n8n workflow can schedule generated content to LinkedIn + email
