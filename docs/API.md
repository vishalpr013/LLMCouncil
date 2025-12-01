# LLM Council API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. For production, consider adding API key authentication.

---

## Endpoints

### 1. Submit Query

Process a user query through the complete pipeline.

**Endpoint**: `POST /api/query`

**Request Body**:
```json
{
  "query": "Your question here",
  "options": {
    "use_cache": true,
    "timeout": 120,
    "enable_parallel": true,
    "skip_failed_models": true
  }
}
```

**Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | User question (5-1000 chars) |
| options.use_cache | boolean | No | true | Use cached responses |
| options.timeout | integer | No | 120 | Request timeout in seconds |
| options.enable_parallel | boolean | No | true | Run stages in parallel |
| options.skip_failed_models | boolean | No | true | Continue if some models fail |

**Response**: `200 OK`

```json
{
  "query": "What causes climate change?",
  "stage1_opinions": [
    {
      "model_name": "Llama-7B",
      "answer_text": "...",
      "claims": ["...", "..."],
      "citations": [],
      "metadata": {}
    }
  ],
  "paraphrased_claims": [
    {
      "claim_id": "llama-7b_claim_0",
      "original_model": "Llama-7B",
      "original_text": "...",
      "canonical_text": "...",
      "word_count": 15
    }
  ],
  "reviewer_verdicts": [
    {
      "reviewer_name": "Reviewer_A",
      "reviews": [
        {
          "claim_id": "llama-7b_claim_0",
          "verdict": "CORRECT",
          "reason": "...",
          "evidence_needed": false,
          "confidence": 0.85
        }
      ],
      "metadata": {}
    }
  ],
  "aggregation": {
    "total_claims": 8,
    "supported_claims": ["...", "..."],
    "rejected_claims": ["..."],
    "disputed_claims": [],
    "uncertain_claims": ["..."],
    "consensus_score": 0.875,
    "evidence_needed_count": 2
  },
  "final_answer": {
    "final_answer": "Comprehensive answer...",
    "supporting_claims": ["...", "..."],
    "uncertain_points": ["..."],
    "rejected_claims": [],
    "citations": [],
    "confidence": 0.88,
    "reasoning_summary": "..."
  },
  "metadata": {
    "request_id": "req_1234567890",
    "processing_time": 35.67,
    "models_used": ["Llama-7B", "GPT-OSS-20B", "GPT-J-6B", "Mistral-7B", "DeepSeek-7B", "Gemini-1.5-Pro"],
    "cache_hit": false,
    "errors": [],
    "warnings": [],
    "stage_timings": {
      "stage1": 12.3,
      "paraphrase": 5.4,
      "review": 10.2,
      "aggregation": 0.1,
      "chairman": 7.7
    },
    "timestamp": "2025-11-27T10:30:45.123Z"
  }
}
```

**Error Responses**:

- `400 Bad Request`: Invalid query format
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Pipeline execution failed
- `502 Bad Gateway`: Model API error
- `504 Gateway Timeout`: Request timeout

**Example Error**:
```json
{
  "error": "PipelineError",
  "message": "All Stage-1 models failed",
  "request_id": "req_1234567890",
  "processing_time": 15.2
}
```

---

### 2. Health Check

Check status of all models and services.

**Endpoint**: `GET /api/health`

**Response**: `200 OK`

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
  },
  "details": [
    {
      "name": "Llama-7B",
      "status": "online",
      "endpoint": "http://localhost:8001",
      "response_time": 0.15,
      "last_checked": "2025-11-27T10:30:00Z"
    }
  ],
  "timestamp": "2025-11-27T10:30:45Z"
}
```

**Status Values**:
- `healthy`: All models operational
- `degraded`: Some models offline but system functional
- `unhealthy`: Critical models offline

---

### 3. List Models

Get information about all models in the pipeline.

**Endpoint**: `GET /api/models`

**Response**: `200 OK`

```json
{
  "stage1_models": [
    {
      "name": "Llama-7B",
      "type": "local",
      "endpoint": "http://localhost:8001",
      "role": "first_opinion"
    },
    {
      "name": "GPT-OSS-20B",
      "type": "remote",
      "provider": "huggingface",
      "role": "first_opinion"
    }
  ],
  "paraphrase_model": {
    "name": "GPT-J-6B",
    "type": "local",
    "endpoint": "http://localhost:8002",
    "role": "claim_extraction"
  },
  "reviewer_models": [
    {
      "name": "Mistral-7B-Distill",
      "type": "local",
      "endpoint": "http://localhost:8003",
      "role": "reviewer_a"
    },
    {
      "name": "DeepSeek-R1-Distill-7B",
      "type": "local",
      "endpoint": "http://localhost:8004",
      "role": "reviewer_b"
    }
  ],
  "chairman_model": {
    "name": "Gemini-1.5-Pro",
    "type": "remote",
    "provider": "google",
    "role": "final_synthesis"
  }
}
```

---

### 4. Get Statistics

Retrieve pipeline statistics and metrics.

**Endpoint**: `GET /api/stats`

**Response**: `200 OK`

```json
{
  "total_queries": 156,
  "successful_queries": 148,
  "failed_queries": 8,
  "cache_hits": 42,
  "average_processing_time": 38.5,
  "cache_stats": {
    "size": 42,
    "enabled": true,
    "ttl": 3600,
    "directory": "./cache"
  }
}
```

---

### 5. Clear Cache

Clear the response cache.

**Endpoint**: `POST /api/cache/clear`

**Response**: `200 OK`

```json
{
  "message": "Cache cleared successfully"
}
```

---

## Data Models

### Verdict Enum

```
CORRECT    - Claim is factually accurate
INCORRECT  - Claim is factually wrong
UNCERTAIN  - Cannot verify with confidence
```

### Citation Object

```json
{
  "source": "Wikipedia",
  "url": "https://en.wikipedia.org/wiki/Climate_change",
  "snippet": "Climate change refers to long-term shifts..."
}
```

### Claim Object

```json
{
  "claim_id": "model_name_claim_0",
  "original_model": "Llama-7B",
  "original_text": "Full original answer...",
  "canonical_text": "Atomic canonical claim",
  "word_count": 15
}
```

### Review Object

```json
{
  "claim_id": "model_name_claim_0",
  "verdict": "CORRECT",
  "reason": "Brief justification",
  "evidence_needed": false,
  "confidence": 0.85
}
```

---

## Rate Limiting

**Default**: 30 requests per minute per IP

**Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1701087600
```

**429 Too Many Requests**:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## CORS

**Allowed Origins** (configurable in `.env`):
```
http://localhost:3000
http://localhost:3001
```

**Allowed Methods**:
```
GET, POST, OPTIONS
```

---

## WebSocket Support (Future)

Real-time pipeline progress updates.

**Endpoint**: `ws://localhost:8000/ws/query`

**Message Format**:
```json
{
  "stage": "stage1",
  "status": "completed",
  "progress": 0.2,
  "message": "Stage 1 completed in 12.3s"
}
```

---

## Client Examples

### Python

```python
import requests

# Submit query
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "What causes climate change?",
        "options": {"use_cache": True}
    }
)

result = response.json()
print(result["final_answer"]["final_answer"])
```

### JavaScript/TypeScript

```javascript
async function submitQuery(query) {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      options: { use_cache: true }
    })
  });
  
  const result = await response.json();
  return result.final_answer.final_answer;
}
```

### cURL

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What causes climate change?",
    "options": {"use_cache": true}
  }'
```

---

## Best Practices

1. **Use Caching**: Enable cache for repeated queries
2. **Set Timeouts**: Use appropriate timeout values for your use case
3. **Handle Errors**: Implement retry logic with exponential backoff
4. **Monitor Health**: Periodically check `/api/health`
5. **Batch Requests**: Don't send more than 10 concurrent requests

---

## OpenAPI Specification

Full OpenAPI/Swagger documentation available at:

```
http://localhost:8000/docs
```

Interactive API explorer available at:

```
http://localhost:8000/redoc
```

---

For pipeline details, see [PIPELINE.md](PIPELINE.md)  
For setup instructions, see [SETUP.md](SETUP.md)
