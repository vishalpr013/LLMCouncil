# LLM Council - Multi-Model Debate Pipeline

A production-ready full-stack application that implements a sophisticated multi-stage debate system using local and remote LLMs to generate high-quality, fact-checked answers.

## 🏗️ Architecture Overview

```
User Query
    ↓
┌─────────────────────────────────────┐
│     STAGE 1: First Opinions         │
│  • Llama-7B (Local, 4-bit GGUF)    │
│  • GPT-OSS-20B (HF Inference API)  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  STAGE 2: Claim Extraction          │
│  • GPT-J-6B (Local, quantized)     │
│    Paraphrases into canonical claims│
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│     STAGE 3: Peer Review            │
│  • Mistral-7B-Distill (Reviewer A) │
│  • DeepSeek-R1-Distill-7B (Rev. B) │
│    Evaluate claims independently    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│     STAGE 4: Aggregation            │
│  • Combine verdicts                 │
│  • Identify consensus/disputes      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│     STAGE 5: Chairman Synthesis     │
│  • Gemini API                       │
│    Final authoritative answer       │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
LLMCouncil/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Configuration & env vars
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py          # Pydantic models
│   │   │   └── responses.py        # Response structures
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py     # Main pipeline orchestrator
│   │   │   ├── local_models.py     # Local model runners
│   │   │   ├── remote_models.py    # HF & Gemini API calls
│   │   │   ├── paraphrase.py       # Claim extraction
│   │   │   ├── reviewers.py        # Reviewer logic
│   │   │   ├── aggregator.py       # Verdict aggregation
│   │   │   └── chairman.py         # Final synthesis
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── stage1.py           # First opinion prompts
│   │   │   ├── paraphrase.py       # Claim extraction prompts
│   │   │   ├── reviewer.py         # Reviewer prompts
│   │   │   └── chairman.py         # Chairman prompts
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── cache.py            # Caching layer
│   │       ├── logger.py           # Logging setup
│   │       └── error_handler.py    # Error handling
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── QueryInput.js
│   │   │   ├── Stage1Tabs.js
│   │   │   ├── ClaimsPanel.js
│   │   │   ├── ReviewerPanel.js
│   │   │   ├── FinalAnswer.js
│   │   │   └── LoadingSpinner.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── utils/
│   │       └── formatting.js
│   ├── package.json
│   └── .env.example
├── local-models/
│   ├── llama-server-config.json    # llama.cpp server config
│   ├── model-download.sh           # Model download script
│   └── start-servers.ps1           # PowerShell server startup
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
└── docs/
    ├── SETUP.md                    # Detailed setup guide
    ├── API.md                      # API documentation
    └── PIPELINE.md                 # Pipeline explanation
```

## 🚀 Quick Start

### Prerequisites

- **Hardware**: RTX 3050 (6GB VRAM) or better
- **Software**:
  - Python 3.9+
  - Node.js 16+
  - llama.cpp or text-generation-webui
  - Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/LLMCouncil.git
cd LLMCouncil
```

### 2. Download & Setup Local Models

```powershell
# Download GGUF models
cd local-models
.\model-download.sh

# Models to download (4-bit quantized):
# - llama-2-7b.Q4_K_M.gguf
# - gpt-j-6B.Q4_0.gguf
# - mistral-7b-instruct-v0.2.Q4_K_M.gguf
# - deepseek-r1-distill-qwen-7b.Q4_K_M.gguf
```

**Download Links:**
- Llama-7B: https://huggingface.co/TheBloke/Llama-2-7B-GGUF
- GPT-J-6B: https://huggingface.co/TheBloke/GPT-J-6B-GGUF
- Mistral-7B: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- DeepSeek-R1: https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF

### 3. Start Local Model Servers

```powershell
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release

# Start model servers (in separate terminals)
.\local-models\start-servers.ps1
```

This will start 4 servers:
- Llama-7B: http://localhost:8001
- GPT-J-6B: http://localhost:8002
- Mistral-7B: http://localhost:8003
- DeepSeek-7B: http://localhost:8004

### 4. Setup Backend

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - HUGGINGFACE_API_TOKEN
# - GEMINI_API_KEY
```

### 5. Setup Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

### 6. Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

Access the app at: http://localhost:3000

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Local Model Endpoints
LLAMA_7B_URL=http://localhost:8001
GPTJ_6B_URL=http://localhost:8002
MISTRAL_7B_URL=http://localhost:8003
DEEPSEEK_7B_URL=http://localhost:8004

# Remote APIs
HUGGINGFACE_API_TOKEN=your_hf_token_here
HUGGINGFACE_MODEL=EleutherAI/gpt-neo-20b
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-1.5-pro

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=120
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📖 API Documentation

### POST /api/query

Submit a query to the LLM Council pipeline.

**Request:**
```json
{
  "query": "What causes climate change?",
  "options": {
    "use_cache": true,
    "timeout": 120
  }
}
```

**Response:**
```json
{
  "query": "What causes climate change?",
  "stage1_opinions": [...],
  "paraphrased_claims": [...],
  "reviewer_verdicts": [...],
  "aggregation": {...},
  "final_answer": {...},
  "metadata": {...}
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "models": {
    "llama_7b": "online",
    "gptj_6b": "online",
    "mistral_7b": "online",
    "deepseek_7b": "online",
    "hf_api": "online",
    "gemini_api": "online"
  }
}
```

## 🧪 Testing

```powershell
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 🐳 Docker Deployment

```powershell
# Build and run all services
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## 📊 Performance Optimization

### Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | RTX 3050 (6GB) | RTX 4070 (12GB) |
| RAM | 16GB | 32GB |
| Storage | 50GB SSD | 100GB NVMe |

### Memory Management

- Use 4-bit quantization (Q4_K_M) for all local models
- Run only one local model at a time if VRAM < 8GB
- Enable model offloading to CPU if needed

### Latency Optimization

- Stage-1 models run in parallel (~10-15s)
- Paraphrase stage is batched (~5s)
- Reviewers run in parallel (~8-12s)
- Total pipeline: ~30-40s

## 🛠️ Troubleshooting

### Model Server Not Starting

```powershell
# Check if port is in use
netstat -ano | findstr :8001

# Kill process if needed
taskkill /PID <pid> /F
```

### Out of Memory (OOM)

- Reduce context length in model configs
- Use smaller quantization (Q3_K_M)
- Enable CPU offloading: `--n-gpu-layers 20`

### API Rate Limits

- Use caching to reduce API calls
- Implement exponential backoff
- Consider self-hosting alternatives

## 🔒 Security Notes

- Never commit `.env` files
- Rotate API keys regularly
- Use HTTPS in production
- Implement rate limiting
- Sanitize user inputs

## 📚 Additional Resources

- [Detailed Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Pipeline Explanation](docs/PIPELINE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- llama.cpp team for local inference
- Hugging Face for model hosting
- Google for Gemini API
- Open source LLM community

## 📞 Support

- GitHub Issues: https://github.com/yourusername/LLMCouncil/issues
- Email: support@llmcouncil.dev
- Discord: https://discord.gg/llmcouncil

---

**Built with ❤️ by the LLM Council Team**
