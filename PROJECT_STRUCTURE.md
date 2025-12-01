# LLM Council - Complete Project Structure

```
LLMCouncil/
│
├── README.md                          # Main project documentation
├── quick-start.ps1                    # Quick start script for Windows
│
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Configuration management
│   │   │
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Request/Response schemas
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py        # Main pipeline orchestrator
│   │   │   ├── local_models.py        # Local model runners (llama.cpp)
│   │   │   ├── remote_models.py       # HF & Gemini API clients
│   │   │   ├── paraphrase.py          # Claim extraction service
│   │   │   ├── reviewers.py           # Peer review service
│   │   │   ├── aggregator.py          # Verdict aggregation
│   │   │   └── chairman.py            # Final synthesis service
│   │   │
│   │   ├── prompts/                   # Prompt templates
│   │   │   ├── __init__.py
│   │   │   ├── stage1.py              # Stage-1 prompts
│   │   │   ├── paraphrase.py          # Paraphrase prompts
│   │   │   ├── reviewer.py            # Reviewer prompts
│   │   │   └── chairman.py            # Chairman prompts
│   │   │
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── logger.py              # Logging setup
│   │       ├── cache.py               # Caching layer
│   │       └── error_handler.py       # Error handling
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables template
│   └── .env                           # Your actual environment variables (git-ignored)
│
├── frontend/                          # React Frontend
│   ├── public/
│   │   ├── index.html                 # HTML template
│   │   └── favicon.ico                # Favicon
│   │
│   ├── src/
│   │   ├── index.js                   # React entry point
│   │   ├── index.css                  # Global styles
│   │   ├── App.js                     # Main App component
│   │   ├── App.css                    # App styles
│   │   │
│   │   ├── components/                # React components
│   │   │   ├── QueryInput.js          # Query input component
│   │   │   ├── QueryInput.css
│   │   │   ├── Stage1Tabs.js          # Stage-1 opinions tabs
│   │   │   ├── Stage1Tabs.css
│   │   │   ├── ClaimsPanel.js         # Claims display panel
│   │   │   ├── ClaimsPanel.css
│   │   │   ├── ReviewerPanel.js       # Reviewer verdicts panel
│   │   │   ├── ReviewerPanel.css
│   │   │   ├── FinalAnswer.js         # Final answer display
│   │   │   ├── FinalAnswer.css
│   │   │   ├── LoadingSpinner.js      # Loading indicator
│   │   │   └── LoadingSpinner.css
│   │   │
│   │   ├── services/
│   │   │   └── api.js                 # API client functions
│   │   │
│   │   └── utils/
│   │       └── formatting.js          # Formatting utilities
│   │
│   ├── package.json                   # NPM dependencies
│   ├── .env.example                   # Frontend env template
│   └── .env                           # Your frontend env (git-ignored)
│
├── local-models/                      # Local model configuration
│   ├── models/                        # GGUF model files directory
│   │   ├── llama-2-7b.Q4_K_M.gguf
│   │   ├── gpt-j-6b.Q4_0.gguf
│   │   ├── mistral-7b-instruct-v0.2.Q4_K_M.gguf
│   │   └── deepseek-r1-distill-qwen-7b.Q4_K_M.gguf
│   │
│   ├── llama-server-config.json       # Model server configuration
│   ├── model-download.sh              # Model download script
│   └── start-servers.ps1              # Server startup script (Windows)
│
├── docs/                              # Documentation
│   ├── SETUP.md                       # Detailed setup guide
│   ├── API.md                         # API documentation
│   └── PIPELINE.md                    # Pipeline explanation
│
├── docker/                            # Docker configuration (optional)
│   ├── docker-compose.yml             # Docker Compose setup
│   ├── Dockerfile.backend             # Backend container
│   └── Dockerfile.frontend            # Frontend container
│
└── .gitignore                         # Git ignore rules
```

## Key Files Explained

### Backend Core Files

- **main.py**: FastAPI application with all endpoints
- **config.py**: Centralized configuration from environment variables
- **orchestrator.py**: Coordinates the entire pipeline execution
- **local_models.py**: Handles communication with llama.cpp servers
- **remote_models.py**: HF Inference API and Gemini API clients

### Prompt Files

All prompts are templated and configurable:
- **stage1.py**: First opinion generation prompts
- **paraphrase.py**: Claim extraction prompts
- **reviewer.py**: Peer review prompts  
- **chairman.py**: Final synthesis prompts

### Frontend Components

- **QueryInput.js**: User query input with example questions
- **Stage1Tabs.js**: Tabbed view of Stage-1 model opinions
- **ClaimsPanel.js**: Display of extracted canonical claims
- **ReviewerPanel.js**: Reviewer verdicts and aggregation
- **FinalAnswer.js**: Final synthesized answer with confidence

### Configuration Files

- **backend/.env**: Backend API keys and settings
- **frontend/.env**: Frontend API URL
- **llama-server-config.json**: Model server configuration

### Scripts

- **quick-start.ps1**: One-click startup for all services
- **start-servers.ps1**: Start all local model servers
- **model-download.sh**: Download all required models

## Data Flow

```
1. User Input (Frontend)
   ↓
2. POST /api/query (Backend API)
   ↓
3. Orchestrator.run_pipeline()
   ↓
4. Stage 1: Local + Remote Models → Opinions
   ↓
5. Stage 2: Paraphrase Service → Canonical Claims
   ↓
6. Stage 3: Reviewer Service → Verdicts
   ↓
7. Stage 4: Aggregator → Consensus
   ↓
8. Stage 5: Chairman → Final Answer
   ↓
9. Response (Backend → Frontend)
   ↓
10. Display Results (Frontend)
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone repo
git clone <repo-url>
cd LLMCouncil

# Download models
cd local-models
./model-download.sh

# Setup backend
cd ../backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys

# Setup frontend
cd ../frontend
npm install
cp .env.example .env
```

### 2. Daily Development
```bash
# Quick start everything
.\quick-start.ps1

# Or manually:
# Terminal 1: Model servers
.\local-models\start-servers.ps1

# Terminal 2: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm start
```

### 3. Testing
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Health check
curl http://localhost:8000/api/health
```

### 4. Production Build
```bash
# Frontend build
cd frontend
npm run build

# Docker deployment
docker-compose up --build
```

## File Size Summary

```
Backend Code:         ~50 KB
Frontend Code:        ~100 KB
Documentation:        ~150 KB
Local Models:         ~16 GB (GGUF files)
Total (with models):  ~16.3 GB
Total (without):      ~300 KB
```

## Important Notes

1. **Git Ignore**: The following are git-ignored:
   - `backend/.env`
   - `frontend/.env`
   - `backend/venv/`
   - `frontend/node_modules/`
   - `local-models/models/*.gguf`
   - `backend/logs/`
   - `backend/cache/`

2. **API Keys Required**:
   - Hugging Face API token
   - Google Gemini API key

3. **Hardware Requirements**:
   - Minimum: RTX 3050 (6GB VRAM)
   - Recommended: RTX 4070 (12GB VRAM)

4. **Port Usage**:
   - 8000: Backend API
   - 8001: Llama-7B server
   - 8002: GPT-J-6B server
   - 8003: Mistral-7B server
   - 8004: DeepSeek-7B server
   - 3000: Frontend dev server

## Quick Reference Commands

```bash
# Start all services
.\quick-start.ps1

# Backend only
cd backend
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm start

# Check health
curl http://localhost:8000/api/health

# View API docs
# Open: http://localhost:8000/docs

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear
```

## Next Steps

1. Read [SETUP.md](docs/SETUP.md) for detailed setup instructions
2. Review [API.md](docs/API.md) for API documentation
3. Understand [PIPELINE.md](docs/PIPELINE.md) for pipeline details
4. Customize prompts in `backend/app/prompts/`
5. Add your own models to the pipeline
6. Deploy to production

---

**Built with ❤️ by the LLM Council Team**
