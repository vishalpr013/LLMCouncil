# Detailed Setup Guide for LLM Council

This guide walks you through the complete setup process for the LLM Council multi-model debate pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installing llama.cpp](#installing-llamacpp)
3. [Downloading Models](#downloading-models)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Starting the Application](#starting-the-application)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

- **GPU**: RTX 3050 (6GB VRAM) or better
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB free space (for models and data)
- **CPU**: Modern multi-core processor (4+ cores recommended)

### Software Requirements

#### Windows

- **Python 3.9+**: Download from [python.org](https://www.python.org/downloads/)
- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org/)
- **Git**: Download from [git-scm.com](https://git-scm.com/)
- **CMake**: Download from [cmake.org](https://cmake.org/download/)
- **Visual Studio Build Tools**: For C++ compilation

#### Linux/Mac

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm git cmake build-essential

# macOS (using Homebrew)
brew install python node git cmake
```

---

## Installing llama.cpp

llama.cpp is required to run local GGUF models efficiently.

### Windows

```powershell
# Clone llama.cpp
cd $HOME
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CMake (CUDA support)
cmake -B build -DLLAMA_CUBLAS=ON
cmake --build build --config Release

# Verify installation
.\build\bin\Release\server.exe --version
```

### Linux (with CUDA)

```bash
# Clone llama.cpp
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Build with CUDA support
make LLAMA_CUBLAS=1

# Verify installation
./server --version
```

### Mac (Metal acceleration)

```bash
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

make LLAMA_METAL=1

./server --version
```

---

## Downloading Models

### Option 1: Using the Download Script (Recommended)

```bash
cd LLMCouncil/local-models
chmod +x model-download.sh
./model-download.sh
```

This will download all 4 required models (~16 GB total).

### Option 2: Manual Download

Download each model from Hugging Face:

1. **Llama-2-7B** (4.1 GB)
   ```
   https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf
   ```

2. **GPT-J-6B** (3.5 GB)
   ```
   https://huggingface.co/TheBloke/GPT-J-6B-GGUF/resolve/main/gpt-j-6b.Q4_0.gguf
   ```

3. **Mistral-7B-Instruct-v0.2** (4.4 GB)
   ```
   https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

4. **DeepSeek-R1-Distill-Qwen-7B** (4.3 GB)
   ```
   https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF/resolve/main/deepseek-r1-distill-qwen-7b.Q4_K_M.gguf
   ```

Save all models to `LLMCouncil/local-models/models/`.

---

## Backend Setup

### 1. Create Virtual Environment

```powershell
cd LLMCouncil/backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your text editor
notepad .env
```

**Required Configuration:**

```env
# Hugging Face API Token
HUGGINGFACE_API_TOKEN=hf_your_token_here
# Get from: https://huggingface.co/settings/tokens

# Gemini API Key
GEMINI_API_KEY=your_gemini_key_here
# Get from: https://makersuite.google.com/app/apikey

# Local model endpoints (default ports)
LLAMA_7B_URL=http://localhost:8001
GPTJ_6B_URL=http://localhost:8002
MISTRAL_7B_URL=http://localhost:8003
DEEPSEEK_7B_URL=http://localhost:8004
```

### 4. Test Backend

```bash
# Start backend server
uvicorn app.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/api/health
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd LLMCouncil/frontend
npm install
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit if needed (default should work)
# REACT_APP_API_URL=http://localhost:8000
```

### 3. Test Frontend

```bash
npm start
```

Browser should open at `http://localhost:3000`.

---

## Starting the Application

### Complete Startup Sequence

**Terminal 1: Start Local Model Servers**

```powershell
cd LLMCouncil/local-models
.\start-servers.ps1
```

Wait for all 4 servers to start (~10-20 seconds).

**Terminal 2: Start Backend**

```powershell
cd LLMCouncil/backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3: Start Frontend**

```powershell
cd LLMCouncil/frontend
npm start
```

### Verify Everything is Running

1. **Model Servers**: Visit http://localhost:8001/health (and 8002, 8003, 8004)
2. **Backend**: Visit http://localhost:8000/docs
3. **Frontend**: Visit http://localhost:3000

---

## Troubleshooting

### Issue: Model Server Won't Start

**Symptoms**: Server process exits immediately

**Solutions**:
1. Check GPU drivers are up to date
2. Reduce `gpu_layers` in start-servers.ps1 (try 20 instead of 35)
3. Verify model file exists and isn't corrupted
4. Check port isn't already in use: `netstat -ano | findstr :8001`

### Issue: Out of Memory (OOM)

**Symptoms**: Server crashes or system freezes

**Solutions**:
1. Run only one model at a time
2. Reduce context size to 1024
3. Use Q3_K_M quantization instead of Q4_K_M
4. Enable CPU offloading: `--n-gpu-layers 20`

### Issue: Backend Can't Connect to Models

**Symptoms**: "Model API error" or timeouts

**Solutions**:
1. Verify model servers are running
2. Check firewall isn't blocking ports
3. Increase `LOCAL_MODEL_TIMEOUT` in .env
4. Test manually: `curl http://localhost:8001/health`

### Issue: Slow Response Times

**Symptoms**: Queries take >2 minutes

**Solutions**:
1. Reduce max_tokens in prompts
2. Enable parallel execution in options
3. Increase GPU layers for faster inference
4. Use response cache (enabled by default)

### Issue: Gemini API Errors

**Symptoms**: "Chairman synthesis failed"

**Solutions**:
1. Verify API key is correct
2. Check API quota hasn't been exceeded
3. Enable fallback synthesis in config
4. Test API key: 
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_key")
   model = genai.GenerativeModel("gemini-1.5-pro")
   response = model.generate_content("Test")
   print(response.text)
   ```

### Issue: Frontend Build Errors

**Symptoms**: npm start fails

**Solutions**:
1. Clear node_modules: `rm -rf node_modules package-lock.json`
2. Reinstall: `npm install`
3. Update Node.js to latest LTS version
4. Check for port conflicts (3000)

### Getting Help

1. **Check Logs**:
   - Backend: `backend/logs/app.log`
   - Model servers: Check terminal output
   
2. **Enable Debug Mode**:
   ```env
   DEBUG_MODE=true
   LOG_LEVEL=DEBUG
   SAVE_DEBUG_OUTPUTS=true
   ```

3. **Community Support**:
   - GitHub Issues: [Your repo URL]
   - Discord: [Your Discord link]
   - Email: support@llmcouncil.dev

---

## Performance Tuning

### For RTX 3050 (6GB VRAM)

```json
{
  "gpu_layers": 25,
  "context_size": 1536,
  "batch_size": 512,
  "threads": 4
}
```

### For RTX 4070 (12GB VRAM)

```json
{
  "gpu_layers": 43,
  "context_size": 4096,
  "batch_size": 1024,
  "threads": 8
}
```

### For CPU-Only Systems

```json
{
  "gpu_layers": 0,
  "context_size": 1024,
  "batch_size": 256,
  "threads": 8
}
```

---

## Next Steps

- Read [API.md](API.md) for API documentation
- Read [PIPELINE.md](PIPELINE.md) for pipeline details
- Customize prompts in `backend/app/prompts/`
- Add more models to the pipeline
- Deploy to production with Docker

---

**Happy Building! 🚀**
