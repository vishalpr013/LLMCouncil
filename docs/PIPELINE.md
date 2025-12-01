# LLM Council Pipeline Documentation

## Overview

The LLM Council implements a sophisticated multi-stage debate pipeline where multiple AI models collaborate to generate high-quality, fact-checked answers.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER QUERY                            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼────────┐
│  Llama-7B      │      │  GPT-OSS-20B    │
│  (Local)       │      │  (HF API)       │
│  Opinion A     │      │  Opinion B      │
└───────┬────────┘      └────────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
              ┌──────▼──────┐
              │   GPT-J-6B  │
              │ (Paraphrase)│
              │   P₁, P₂    │
              └──────┬──────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼────────┐
│  Mistral-7B    │      │  DeepSeek-7B    │
│  Reviewer A    │      │  Reviewer B     │
│  R₁ verdicts   │      │  R₂ verdicts    │
└───────┬────────┘      └────────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
              ┌──────▼──────┐
              │ Aggregator  │
              │  Consensus  │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │   Gemini    │
              │  Chairman   │
              │ Final Answer│
              └─────────────┘
```

## Stage-by-Stage Breakdown

### Stage 1: First Opinions (A_i)

**Purpose**: Generate initial diverse opinions from different models

**Models**:
- **Llama-7B** (local, quantized): Fast, runs on consumer GPU
- **GPT-OSS-20B** (HF API): Larger model, potentially more knowledgeable

**Execution**: Parallel (async)

**Input**: Raw user query

**Output Format**:
```json
{
  "answer_text": "2-4 sentence answer",
  "claims": ["claim1", "claim2", "claim3"],
  "citations": [{"source": "...", "url": "...", "snippet": "..."}]
}
```

**Key Rules**:
- NO chain-of-thought reasoning
- NO self-identification
- Models don't know other models exist
- Strictly JSON output
- Factual and concise

**Typical Duration**: 10-15 seconds (parallel)

---

### Stage 2: Claim Extraction (P_i)

**Purpose**: Convert natural language answers into canonical atomic claims

**Model**: GPT-J-6B (local, quantized)

**Execution**: Sequential (one answer at a time)

**Input**: Each `answer_text` from Stage-1

**Output Format**:
```json
{
  "claims": [
    "Atomic canonical claim 1 (≤20 words)",
    "Atomic canonical claim 2 (≤20 words)"
  ]
}
```

**Transformation Rules**:
- One fact per claim
- Clear, unambiguous language
- Remove hedging unless factually necessary
- Preserve original meaning
- ≤20 words per claim

**Example**:
```
Original: "Climate change is caused by increased greenhouse gases, 
           mainly from burning fossil fuels, which trap heat."

Canonical Claims:
- "Climate change is caused by increased greenhouse gases."
- "Greenhouse gases mainly come from burning fossil fuels."
- "Greenhouse gases trap heat in the atmosphere."
```

**Typical Duration**: 5-8 seconds total

---

### Stage 3: Peer Review (R_i)

**Purpose**: Independent fact-checking of all claims

**Models**:
- **Mistral-7B-Distill** (Reviewer A)
- **DeepSeek-R1-Distill-7B** (Reviewer B)

**Execution**: Parallel (async)

**Input**: 
- Original user query
- ALL canonical claims (anonymized, no source attribution)

**Output Format**:
```json
{
  "reviews": [
    {
      "claim_id": "llama-7b_claim_0",
      "verdict": "CORRECT",
      "reason": "Brief justification (≤30 words)",
      "evidence_needed": false,
      "confidence": 0.85
    }
  ]
}
```

**Verdict Types**:
- **CORRECT**: Factually accurate and verifiable
- **INCORRECT**: Factually wrong or misleading
- **UNCERTAIN**: Cannot verify with confidence

**Key Rules**:
- Claims are anonymized (reviewers don't know source)
- Each claim judged independently
- NO chain-of-thought
- Evidence-based reasoning
- Confidence score (0.0-1.0)

**Typical Duration**: 8-12 seconds (parallel)

---

### Stage 4: Aggregation

**Purpose**: Synthesize verdicts from multiple reviewers

**Execution**: Synchronous (fast, no model call)

**Logic**:

1. **Supported Claims**: All reviewers say CORRECT OR majority says CORRECT
2. **Rejected Claims**: All reviewers say INCORRECT OR majority says INCORRECT
3. **Uncertain Claims**: All reviewers say UNCERTAIN
4. **Disputed Claims**: No clear majority, reviewers disagree

**Consensus Score Calculation**:
```python
consensus_score = (claims_with_unanimous_verdict) / (total_claims)
```

**Output**:
```json
{
  "total_claims": 12,
  "supported_claims": ["claim1", "claim2", ...],
  "rejected_claims": ["claim7"],
  "disputed_claims": ["claim5"],
  "uncertain_claims": ["claim9", "claim10"],
  "consensus_score": 0.75,
  "evidence_needed_count": 3
}
```

**Typical Duration**: <1 second

---

### Stage 5: Chairman Synthesis

**Purpose**: Generate authoritative final answer based on verified evidence

**Model**: Gemini-1.5-Pro (Google API)

**Execution**: Single API call

**Input**:
- Original query
- All Stage-1 opinions
- All canonical claims
- All reviewer verdicts
- Aggregation summary

**Output Format**:
```json
{
  "final_answer": "Comprehensive 3-6 sentence answer based on supported claims",
  "supporting_claims": ["claim1", "claim2"],
  "uncertain_points": ["point1"],
  "rejected_claims": ["claim7"],
  "citations": [{"source": "...", "url": "..."}],
  "confidence": 0.85,
  "reasoning_summary": "Brief explanation of synthesis process"
}
```

**Synthesis Rules**:
- Use ONLY supported claims
- Acknowledge uncertain points explicitly
- Mention rejected claims if relevant to context
- Balanced and fact-based
- Clear confidence indication

**Typical Duration**: 5-10 seconds

---

## Complete Pipeline Flow Example

### Input Query
```
"What causes climate change?"
```

### Stage 1 Outputs
```
Llama-7B: "Climate change is primarily caused by greenhouse gas emissions..."
GPT-OSS-20B: "The main driver of climate change is the increase in CO2..."
```

### Stage 2 Outputs (Canonical Claims)
```
[llama-7b_claim_0]: "Climate change is caused by greenhouse gas emissions."
[llama-7b_claim_1]: "Greenhouse gases trap heat in the atmosphere."
[gpt-oss_claim_0]: "The main driver of climate change is increased CO2."
[gpt-oss_claim_1]: "CO2 levels have risen due to fossil fuel combustion."
```

### Stage 3 Outputs (Reviews)
```
Reviewer A (Mistral):
  [llama-7b_claim_0]: CORRECT (confidence: 0.95)
  [llama-7b_claim_1]: CORRECT (confidence: 0.90)
  [gpt-oss_claim_0]: CORRECT (confidence: 0.92)
  [gpt-oss_claim_1]: CORRECT (confidence: 0.88)

Reviewer B (DeepSeek):
  [llama-7b_claim_0]: CORRECT (confidence: 0.93)
  [llama-7b_claim_1]: CORRECT (confidence: 0.87)
  [gpt-oss_claim_0]: CORRECT (confidence: 0.90)
  [gpt-oss_claim_1]: CORRECT (confidence: 0.85)
```

### Stage 4 Output (Aggregation)
```
Total Claims: 4
Supported: 4 (100%)
Rejected: 0
Uncertain: 0
Disputed: 0
Consensus Score: 1.0 (Strong Consensus)
```

### Stage 5 Output (Final Answer)
```
Final Answer:
"Climate change is primarily caused by greenhouse gas emissions, particularly 
carbon dioxide (CO2). These gases trap heat in the Earth's atmosphere, leading 
to global warming. The main source of increased CO2 levels is the combustion 
of fossil fuels for energy. This process has accelerated significantly since 
the Industrial Revolution."

Supporting Claims: [all 4 claims]
Confidence: 0.92
```

---

## Error Handling & Fallbacks

### Model Failures

**If Stage-1 model fails**:
- Continue with remaining models
- Require at least 1 successful opinion
- Skip failed model in aggregation

**If Paraphrase fails**:
- Fallback: Split answer into sentences
- Use simple sentence-level claims

**If Reviewer fails**:
- Continue with remaining reviewer
- Mark all claims as UNCERTAIN if all reviewers fail

**If Chairman fails**:
- Fallback: Simple concatenation of supported claims
- Lower confidence score

### Timeout Handling

Each stage has configurable timeout:
- Stage-1: 30s per model
- Paraphrase: 15s per answer
- Reviewers: 30s per reviewer
- Chairman: 45s

### Cache Strategy

**Cache Key**: `SHA256(query + options)`

**Cache Hit**:
- Return immediately
- Add `cache_hit: true` to metadata
- Typical response: <100ms

**Cache Miss**:
- Run full pipeline
- Cache result for 1 hour (configurable)

**Cache Invalidation**:
- Manual via `/api/cache/clear`
- Automatic TTL expiration

---

## Performance Optimization

### Parallel Execution

**Enabled by default** for:
- Stage-1 (multiple first opinions)
- Stage-3 (multiple reviewers)

**Benefits**:
- 50% reduction in total time
- Better resource utilization

**Configuration**:
```env
ENABLE_PARALLEL_STAGE1=true
ENABLE_PARALLEL_REVIEWERS=true
```

### GPU Memory Management

**RTX 3050 (6GB)**:
- Load 1 model at a time
- Use Q4_K_M quantization
- 25-35 GPU layers

**RTX 4070 (12GB)**:
- Can load 2 models simultaneously
- Use Q5_K_M quantization
- 40-43 GPU layers

### Latency Breakdown

Typical end-to-end latency (no cache):
```
Stage 1 (parallel):     10-15s
Stage 2 (sequential):    5-8s
Stage 3 (parallel):      8-12s
Stage 4 (sync):          <1s
Stage 5:                 5-10s
─────────────────────────────
Total:                  30-45s
```

With cache hit: <100ms

---

## Design Principles

1. **Anonymity**: No model knows about other models
2. **Independence**: Each stage operates on output of previous stage only
3. **Transparency**: All intermediate outputs visible to user
4. **Evidence-Based**: Final answer based only on verified claims
5. **Graceful Degradation**: System continues even if some models fail
6. **Scalability**: Easy to add more models to any stage

---

## Future Enhancements

- **Dynamic Model Selection**: Choose models based on query type
- **Confidence Calibration**: Machine learning for confidence scores
- **Evidence Retrieval**: Automatic citation fetching
- **Multi-Turn Dialogue**: Follow-up questions
- **Claim Deduplication**: Identify semantically similar claims
- **Explanation Generation**: Detailed reasoning traces

---

For API details, see [API.md](API.md)  
For setup instructions, see [SETUP.md](SETUP.md)
