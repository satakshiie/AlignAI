# AlignAI

AlignAI is a multi-agent resume tailoring tool that takes a candidate's resume and a job description, scores the resume against the JD using a three-layer ATS engine, and then generates grounded, hallucination-aware suggestions — rewrites, gap analyses, and a learning roadmap — through an agentic pipeline that includes a Critic node and an optional human-in-the-loop review step before any output is committed. It is built for CS students and early-career engineers who want to understand *why* their resume underperforms on a specific JD, not just receive a score. What makes it different is that every suggestion is grounded in the actual resume text, audited by an independent Critic that actively looks for overreach rather than just confirming the prior reasoning, and routed to human review when the Critic's confidence drops below a calibrated threshold — so the system refuses to fabricate alignment it cannot verify.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            UPLOAD                                   │
│   Resume PDF / JD PDF → file validation → MIME check → save to disk│
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          EXTRACTION                                 │
│                                                                     │
│  PyMuPDF (primary) ──► text length check ──► Tesseract OCR (fallback│
│                                                if text < 100 chars) │
│                                                                     │
│  Deterministic layer (spaCy + regex)                                │
│    ├── section splitting (Education, Experience, Projects, Skills…) │
│    ├── contact/link extraction + hyperlink categorisation           │
│    └── years-of-experience detection, degree detection             │
│                                                                     │
│  LLM layer (Groq / Llama 3.3 70B)                                  │
│    ├── resume: structured JSON (skills[], work_history[], etc.)     │
│    └── jd: required_skills[], preferred_skills[], responsibilities[]│
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           STORAGE                                   │
│                                                                     │
│  PostgreSQL (SQLAlchemy ORM)                                        │
│    ├── Document table  — file-level facts (filename, mime, path…)  │
│    └── ParsedContext table — JSONB (deterministic_fields,          │
│                               parsed_data), FK → Document           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ATS ENGINE (3 layers)                       │
│                                                                     │
│  Layer 1 · Skill Match (weight 50%)                                 │
│    RapidFuzz fuzzy matching against required + preferred skill lists │
│                                                                     │
│  Layer 2 · Section Coverage (weight 35%)                            │
│    Structural checks: experience present, years gap, degree match,  │
│    certifications, leadership signals, skills section               │
│                                                                     │
│  Layer 3 · TF-IDF Content Similarity (weight 15%)                  │
│    Cosine similarity across experience/projects vs responsibilities  │
│    Kept as an independent sanity check; weighted low on purpose     │
│                                                                     │
│  → final_score (0–100) + structured gap list (severity-ranked)      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TAILORING GRAPH (LangGraph, 5 nodes)             │
│                                                                     │
│  ① Skill Gap Resolver                                               │
│       classifies each gap as "true_gap" or "implied"               │
│       (implied = not stated explicitly but evident from context)    │
│                                                                     │
│  ② Bullet Rewriter                                                  │
│       rewrites resume bullets for JD alignment — conservative bias  │
│       each rewrite includes grounding[] citing specific resume text  │
│                                                                     │
│  ③ Roadmap Generator                                               │
│       builds a prioritised learning plan for true gaps              │
│                                                                     │
│  ④ Critic  ◄── independent audit node                              │
│       re-reads implied claims and bullet rewrites with a skeptical  │
│       prompt; assigns its own confidence score (0–1); anything      │
│       below 0.7 is flagged for human review                         │
│                                                                     │
│  ⑤ Human Review (conditional — only if Critic flags anything)      │
│       graph pauses via LangGraph MemorySaver checkpoint;            │
│       user approves or rejects each flagged item;                   │
│       graph resumes with decisions folded back into output          │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
                     Final tailored suggestions
              (bullet rewrites, gap items, learning roadmap)
```

---

## Key design decisions

- **JSONB columns over rigid schema for parsed output** — resume and JD parsed data differ structurally (a resume has `work_history[]`, a JD has `responsibilities[]`), so forcing both into a shared typed schema would have required either nullable columns everywhere or two separate tables. JSONB lets the LLM output shape evolve without a migration every iteration. *Tradeoff accepted:* no column-level type enforcement on parsed fields; runtime shape errors surface as application exceptions rather than DB constraints.

- **TF-IDF weighted at 15%, not higher, after empirically observing near-zero scores on relevant pairs** — during testing, TF-IDF cosine similarity between a clearly relevant resume and JD frequently returned scores in the 0.03–0.12 range, even when the candidate was an obvious match, because resume language ("Led development of…") and JD language ("Looking for someone to…") are stylistically so different that shared vocabulary is sparse. Weighting it higher would have made the final score unreliable. *Tradeoff accepted:* TF-IDF contributes only a weak sanity signal; a candidate with very unusual vocabulary may be slightly underscored even when a good match.

- **Critic is prompted as a skeptical adversary, not a confirmation pass** — the Critic node uses the same underlying model (Llama 3.3 70B via Groq) as the agents it audits, which means it is not truly independent. To compensate, the prompt explicitly tells the model its job is to find reasons a claim might be *wrong*, with a rubric that reserves confidence above 0.85 for claims with multiple independent pieces of grounding. *Tradeoff accepted:* the Critic still shares priors with the generator; a sophisticated hallucination that sounds internally consistent may fool both. True independence would require a different model or a retrieval-based verification step.

- **Conservative bullet rewrite bias after observing the model over-reaching on soft-skill connections** — early iterations of the Bullet Rewriter would take a technical bullet ("Built a REST API using FastAPI") and, if the JD mentioned "cross-functional collaboration," add collaboration language that had no basis in the original text. The prompt was tuned with explicit instructions to not add language not supported by the source bullet, accepting that this will occasionally leave a rewrite unchanged when a looser interpretation might have been valid. *Tradeoff accepted:* missed rewrites over fabricated claims.

- **IP-address-based usage limiting as a placeholder for auth** — the daily usage limit (1 tailoring run per day) is enforced by hashing the client IP, isolated in a single `get_identifier()` function so it can be swapped for `request.state.user_id` once authentication exists. The hash is stored, not the raw IP, to avoid retaining PII. *Tradeoff accepted:* IP-based limiting is easily bypassed and breaks for users behind NAT/shared IPs; it is explicitly a dev-phase constraint, not a production-ready auth mechanism.

---

## Tech stack

### Extraction
| Tool | Role |
|---|---|
| PyMuPDF (`fitz`) | Primary PDF text extraction — fast, preserves layout |
| Tesseract OCR | Fallback for scanned/image-based PDFs |
| spaCy (`en_core_web_sm`) | NLP for deterministic section detection and entity hints |
| pdfminer / pdfplumber | Available in requirements; used for hyperlink + metadata edge cases |
| python-magic | MIME type validation before any parsing |

### Scoring
| Tool | Role |
|---|---|
| RapidFuzz | Fuzzy skill matching for Layer 1 (handles abbreviations, casing) |
| scikit-learn (TF-IDF + cosine) | Layer 3 content similarity |
| Custom heuristics | Layer 2 structural checks (regex + parsed fields) |

### Agents
| Tool | Role |
|---|---|
| LangGraph | Stateful multi-node graph with conditional routing and checkpoint-based pause/resume for human review |
| LangChain-Groq | LLM client integration |
| Groq API + Llama 3.3 70B Versatile | Inference for all LLM nodes (Skill Gap Resolver, Bullet Rewriter, Roadmap Generator, Critic) |

### Storage & API
| Tool | Role |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy ORM | Database access layer |
| PostgreSQL | Primary data store (Documents, ParsedContext, ResultCache, UsageLog) |
| Alembic | Schema migrations |
| LangGraph MemorySaver | In-memory graph checkpoint for human-review pause/resume |

### Frontend
| Tool | Role |
|---|---|
| React + Vite | SPA framework |
| Vanilla CSS | Styling |

---

## Known limitations

- **Small test sample.** The ATS scoring weights and the Critic's 0.7 confidence threshold were calibrated on a limited number of resume/JD pairs. Both values may need adjustment with broader data; the weights in particular reflect observed behaviour during development, not a statistically validated optimisation.

- **The Critic is not truly independent.** The Critic node uses the same model and API as the agents it reviews — only the prompt changes. A well-constructed hallucination that sounds internally consistent is likely to fool both. True independence would require either a different model family or a retrieval-augmented verification step that checks claims against the original source text programmatically, not via another LLM call.

- **Section splitting fails on unconventional resume layouts.** The deterministic section detector uses heading-keyword matching and layout heuristics. Resumes with creative layouts, merged sections, dense two-column formats, or non-standard heading names (e.g. "What I've built" instead of "Projects") will produce incomplete or misattributed section splits, which degrades both ATS scoring and bullet rewriting quality.

- **Doc-type heuristic has a precision floor.** The keyword-based content classifier (used to reject a resume uploaded as a JD, or vice-versa) requires a confidence gap of ≥ 2 signals before blocking. Sparse or unusual documents will fall below this threshold and pass through as UNDETECTED. A very atypical resume with few of the expected keywords could be uploaded in the wrong slot without being caught.

- **Usage limiting is bypassable and breaks under NAT.** The daily 1-run limit is IP-hash-based, with no authentication. Multiple users behind a corporate NAT or shared WiFi will share a single quota. A single user with multiple IPs (VPN, mobile data) can bypass it trivially. This is a known acceptable tradeoff for the current development phase.

- **LangGraph graph state is in-memory only.** `MemorySaver` stores the checkpoint in process memory. A server restart between a user submitting a `/tailor/start` request and submitting their `/tailor/resume` review decisions will lose the graph state, returning a 404 on the thread_id. Production use would require a persistent checkpointer (e.g. LangGraph's PostgresSaver).

- **No authentication.** There are no user accounts. Document IDs are UUIDs passed directly between screens on the frontend. Anyone with a document UUID can score or tailor against it.

---

## Setup / running locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (running locally)
- Tesseract OCR installed (`brew install tesseract` on macOS)

### 1. Clone and set up the backend

```bash
git clone https://github.com/satakshiie/AlignAI.git
cd AlignAI/backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure environment variables

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://alignai:your_password@localhost:5432/alignai
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### 3. Set up the database

```bash
# Create the database and user in psql
psql -U postgres -c "CREATE USER alignai WITH PASSWORD 'your_password';"
psql -U postgres -c "CREATE DATABASE alignai OWNER alignai;"

# Run migrations
cd backend
alembic upgrade head
```

### 4. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`.

### Environment variables reference

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for LLM inference (all agent nodes use this) |
| `DATABASE_URL` | PostgreSQL connection string (`postgresql://user:pass@host:port/db`) |
