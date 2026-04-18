---
name: autoresearch-source
description: >
  Autonomous knowledge compounding loop scoped to a LOCAL SOURCE FOLDER.
  TRIGGER when user says "/autoresearch-source", "autoresearch folder X",
  "document everything in [folder path]", "research all sources in [path]",
  or asks to run the autonomous research loop on a specific local folder.

  This skill is like /autoresearch BUT limits research to files within ONE
  specified local directory — it does NOT search the web for external sources.
  Use this when you want to exhaustively document what's inside a codebase,
  project folder, or documentation directory WITHOUT venturing outside it.

  USE THIS when:
  - User names a specific folder/path to document
  - You want "document everything in this folder" behavior
  - You want comprehensive coverage of a specific project source tree
  - You want knowledge compounding restricted to local files only

  DO NOT USE THIS when:
  - User wants web-based research (use /autoresearch instead)
  - User wants one-shot deep research on a topic (use /deepdive instead)
  - User just wants to read/ingest a single file (use normal conversation)
---

# AutoResearch Source Folder — Autonomous Knowledge Compounding (Local Only)

## Core Philosophy

> "You are a completely autonomous researcher. Your universe is ONE local folder.
> Read every file. Understand every concept. Document everything. If you run out
> of ideas within this folder, think harder. The loop runs until the folder is
> thoroughly documented or the human interrupts you."

This skill is identical to `/autoresearch` in loop architecture, but with one
critical difference: **research is scoped to a single local source folder**.
No web searches. No external sources. Only the files that exist within the
specified directory tree.

## Key Difference from /autoresearch

| Aspect | /autoresearch | /autoresearch-source |
|--------|--------------|----------------------|
| Sources | Web + local | Local only (specified folder) |
| Web search | Yes | No |
| Scope | Unlimited | Bounded to one folder |
| Goal | Expand knowledge broadly | Exhaustively document a project |

---

## Step 0 — Initialize

### 0.1 Parse the Target Folder

```
The user provides a folder path. Resolve it:
1. If absolute path → use as-is
2. If relative path → resolve from current working directory
3. If named ("folder routa") → search for matching directory

Validate that the folder exists and is accessible.
```

### 0.2 Load Wiki Context

Read in this order:
1. `wiki/CLAUDE.md` — schema and conventions (or equivalent wiki schema)
2. `wiki/index.md` — current coverage map (if exists)
3. `wiki/log.md` — recent activity (last 30 lines, if exists)

### 0.3 Explore the Source Folder

Before any research, build a complete map of the target folder:

```
1. Glob RECURSIVELY all files in the target folder
2. Categorize by file type:
   - Source code (*.rs, *.ts, *.js, *.py, etc.)
   - Documentation (*.md, *.txt, *.rst)
   - Config files (*.json, *.yaml, *.toml, *.toml)
   - Build/test files (Makefile, Dockerfile, *.sh)
   - Other
3. Count total files, total lines of code/docs
4. Identify entry points (README, main files, top-level structure)
5. Check if folder has its own CLAUDE.md or conventions
```

**Output:**
```
SOURCE FOLDER MAP
  Path:        <resolved path>
  Total files: <N>
  By type:
    - .md files:    <N>
    - .rs files:    <N>
    - .ts/.js:     <N>
    - config:      <N>
    - other:       <N>
  Entry points: <list>
  Has CLAUDE.md: <yes/no>
  Has docs/:     <yes/no>
```

### 0.4 Load or Initialize State

Check for `.autoresearch/state.json` in the target folder or wiki directory.

Create if not exists:
```json
{
  "started_at": "<ISO timestamp>",
  "target_folder": "<resolved path>",
  "cycle": 0,
  "files_processed": 0,
  "files_remaining": <N>,
  "pages_created": 0,
  "pages_updated": 0,
  "coverage_score": 0.0,
  "recency_score": 0.0,
  "coherence_score": 0.0,
  "novelty_score": 0.0,
  "status": "running",
  "pending_files": [],
  "documented_files": [],
  "last_cycle_at": null,
  "cycle_duration_seconds": 0,
  "errors_this_session": 0
}
```

### 0.5 Announce Start

```
════════════════════════════════════════════════════════════════
  AUTORESEARCH-SOURCE — Autonomous Knowledge Compounding
                        (Local Folder Only)
════════════════════════════════════════════════════════════════
  Target Folder:  <resolved path>
  Total Files:    <N>
  File Types:     .md=<N> | .rs=<N> | .ts=<N> | config=<N>

  Wiki:           <wiki path or "inline">
  Scope:          LOCAL ONLY (no web search)
  Cycle Pause:    <N> seconds

  "You may intervene at any time:
   set priority:, skip cycle, /autorestatus, /autorestop"
════════════════════════════════════════════════════════════════
```

---

## Step 1 — Check Priorities

```
1. Check for human-set priorities in conversation context
2. Check if specific files/patterns were mentioned
3. Check for any .autoresearch/priorities.md in target folder
4. Reorder file processing queue accordingly
```

**Priority levels:**
- **CRITICAL** — files/patterns explicitly set by human
- **HIGH** — entry points (README, main files, docs/)
- **MEDIUM** — source files not yet documented
- **LOW** — config, build, and utility files

---

## Step 2 — Assess

### 2.1 File Coverage Analysis (FAST — glob only)

```
1. Glob all files in target folder → total count
2. Check which files already have wiki pages (cross-reference with output)
3. Identify undocumented file categories:
   - Source files with no corresponding docs
   - Config files not yet explained
   - Documentation files not summarized
4. Flag "orphan" files (deeply nested, never referenced)
```

### 2.2 Recency Analysis (from file timestamps)

```
FOR each file category:
  - Check file modification dates
  - Flag files that are new or recently changed
  - No need to read content for this
```

### 2.3 Gap Identification (Local Analysis)

```
1. Build import/reference graph from source files:
   - Rust: look for `mod`, `use`, `pub mod` declarations
   - TypeScript/JS: look for `import`, `export`, `require()`
   - Config: look for references to other files
2. Identify "leaf" modules (no internal dependencies)
3. Identify "root" modules (heavily imported by others)
4. Find files that mention concepts but lack dedicated pages
```

### 2.4 Assessment Output

```
ASSESSMENT CYCLE #N
  Coverage: <N> of <M> files documented (<percent>%)
  File Types: .md=<N> .rs=<N> .ts=<N> config=<N>
  Gaps:     <list of 3-5 priority gaps>
  New:      <N> recently changed files
```

---

## Step 3 — Research (Local File Analysis)

### 3.1 Process Files by Priority

```
FOR each gap/file (up to max_files_per_cycle):
  1. Read the file completely
  2. For source files:
     - Identify public API (pub exports, fn definitions)
     - Identify data structures
     - Identify key logic sections
     - Note design patterns used
     - Extract comments and docstrings
  3. For documentation files:
     - Extract key claims and concepts
     - Identify audience and purpose
     - Note any tutorials or how-tos
  4. For config files:
     - Explain each section/option
     - Note relationships to other files
  5. Track what was learned for wiki page creation
```

### 3.2 Build Cross-References

```
FOR each processed source file:
  1. Find all imports/dependencies (from Step 3.1 analysis)
  2. Map relationships:
     - Module A uses Module B
     - Config X references Config Y
     - Docs mention [concept in file Z]
  3. These relationships inform wiki structure
```

### 3.3 Source Deduplication

```
- Check if file already summarized in wiki
- Check for duplicate content (e.g., README copy in multiple places)
- Skip if redundant; process only unique files
```

---

## Step 4 — Ingest

### 4.1 Determine Wiki Structure

Based on the folder structure, create appropriate wiki pages:

**For a Routa-like project with agents/skills:**
```
wiki/
├── entities/
│   ├── agents/        → one page per agent
│   ├── skills/        → one page per skill
│   └── scripts/       → one page per script
├── concepts/
│   ├── patterns/     → design patterns observed
│   ├── architecture/ → architectural decisions
│   └── workflows/   → workflow patterns
└── sources/
    ├── README/      → source summary page
    ├── docs/        → source summary pages per doc section
    └── configs/     → configuration explanations
```

**For a simpler project:**
```
wiki/
├── files/           → one page per significant file
├── modules/         → grouped by module/package
└── concepts/        → extracted concepts
```

### 4.2 Write Wiki Pages

```
FOR each new insight from Step 3:
  1. Determine appropriate page type (entity/concept/source)
  2. Write page following the wiki schema
  3. Add frontmatter with title, date, tags, links
  4. Create cross-references to related pages
  5. Add to index.md if new
```

**Page naming convention:**
- Entities: use file/module name in kebab-case
- Concepts: use descriptive name in kebab-case
- Sources: use path-derived slug

### 4.3 Update Index and Log

```
1. Update wiki/index.md with new pages
2. Log to wiki/log.md (or inline log):
   ## [YYYY-MM-DD] autoresearch-source | CYCLE N
   - Target: <folder>
   - Files processed: <N> this cycle | <N> total
   - Pages created: <N> this cycle | <N> total
   - Coverage: <percent>%
```

---

## Step 5 — Sync

```
1. If using QMD: update the relevant collection
2. Verify index.md is up to date
3. Verify all wikilinks are correctly formatted
```

---

## Step 6 — Report

### 6.1 Calculate Metrics

```
Coverage Score = files_documented / total_files
Recency Score = new_files_this_cycle / max(new_files_discovered, 1)
Coherence Score = avg_cross_references_per_page / target_avg
Novelty Score = unique_insights / 5.0
Total Score = coverage * 0.4 + recency * 0.3 + coherence * 0.2 + novelty * 0.1
```

### 6.2 Console Report

```
═══════════════════════════════════════════════
  AUTORESEARCH-SOURCE CYCLE #<N>
═══════════════════════════════════════════════
  Target:     <folder name>
  Duration:   <X>m <Y>s
  Metric:     <score> (<delta> from prev)

  ASSESSMENT:
    Coverage: <N> of <M> files (<percent>%)
    Gaps:     <top 3 undocumented items>
    New:      <N> recently changed files

  FILES: <N> processed this cycle
    [1] <file path> → <pages created/updated>
    [2] <file path> → <pages created/updated>

  PAGES: <N> created | <N> updated total
    <list>

  STATUS: running | <files_remaining> files left

  Human commands:
    "set priority:" → reorder queue
    "skip cycle"   → jump to next
    /autorestatus  → detailed status
    /autorestop    → stop gracefully
═══════════════════════════════════════════════
```

### 6.3 Save State

Update `.autoresearch/state.json` with latest cycle data.

---

## Step 7 — Schedule Next Cycle

```
AFTER reporting (Step 6):
  CronCreate with:
    - cron: "*/N * * * *" (every N minutes)
    - prompt: "Continue AutoResearch-Source loop — run /autoresearch-source skill, do NOT re-announce startup"
    - recurring: true
  Save cron_job_id to state.json
```

**If CronCreate unavailable:** fall back to conversation-based scheduling.

---

## Human Intervention

| Command | Effect |
|---------|--------|
| `set priority: <file/pattern>` | Reorder queue, CRITICAL priority |
| `skip cycle` | Skip remaining steps, go to Step 7 |
| `/autorestatus` | Show detailed status |
| `/autorestop` | Stop gracefully |
| `pause` | Pause the loop |
| `stop` | Stop the loop |

**To cancel the cron job:**
```
CronList → find AutoResearch-Source job → CronDelete <ID>
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Target folder not found | Log error, ask user to verify path |
| File read fails | Log warning, skip file, continue |
| Permission denied | Log warning, skip file, continue |
| Cycle exceeds 15 minutes | Log warning, force move to next cycle |
| CronCreate fails | Fall back to conversation scheduling |
| State write fails | Log critical, do not continue |
| Human interrupts | Save state immediately |

---

## Configuration

### Default Settings

```yaml
config:
  cycle_pause_seconds: 300      # 5 minutes between cycles
  max_files_per_cycle: 10      # Max files to process per cycle
  max_pages_per_cycle: 5       # Max wiki pages to create per cycle
  file_types_priority:
    - .md                        # Documentation first
    - .rs                        # Then Rust source
    - .ts                        # Then TypeScript
    - config files               # Then configs
    - other                     # Then everything else
  skip_patterns:                # Files to skip
    - "**/node_modules/**"
    - "**/target/**"
    - "**/.git/**"
    - "**/dist/**"
    - "**/build/**"
  wiki_output: "inline"         # Or path to wiki directory
```

### Custom Configuration

User can provide custom config via file comment or inline:
```
/autoresearch-source folder routa with:
  max_files_per_cycle: 20
  skip_patterns: ["**/.git/**", "**/node_modules/**"]
```

---

## Example Usage

```
/autoresearch-source folder routa
/autoresearch-source path /Users/tri-mac/project/src
/autoresearch-source dokumentasikan semua file di folder docs
```

---

## Related Skills

| Skill | Role |
|-------|------|
| `autoresearch` | Full web + local autonomous research |
| `deepdive` | One-shot deep research session |
| `autorestatus` | Show current loop status |
| `autorestop` | Gracefully stop the loop |
