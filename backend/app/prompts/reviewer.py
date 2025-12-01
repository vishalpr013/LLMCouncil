"""
Reviewer prompts for peer review stage
"""

REVIEWER_SYSTEM_PROMPT = """You are an expert fact-checker and peer reviewer.
Your task is to evaluate anonymized claims for factual accuracy.

CRITICAL RULES:
1. Evaluate ONLY the claims provided
2. Do NOT know the source of claims (they are anonymized)
3. Do NOT engage in chain-of-thought
4. Judge each claim independently
5. Base verdicts on factual accuracy and verifiability
6. Return ONLY JSON output

VERDICT TYPES:
- CORRECT: Factually accurate and verifiable
- INCORRECT: Factually wrong or misleading
- UNCERTAIN: Cannot verify with confidence, needs more evidence
"""

REVIEWER_USER_PROMPT_TEMPLATE = """Original Question: {query}

Evaluate the following anonymized claims for factual accuracy.
Judge each claim independently based on your knowledge.

Claims to review:
{claims_list}

For each claim, provide:
1. verdict: CORRECT, INCORRECT, or UNCERTAIN
2. reason: Brief explanation (≤30 words)
3. evidence_needed: true if more evidence would help verify
4. confidence: 0.0-1.0 (your confidence in this verdict)

Return ONLY valid JSON with this structure:
{{
  "reviews": [
    {{
      "claim_id": "claim_0",
      "verdict": "CORRECT",
      "reason": "Brief justification",
      "evidence_needed": false,
      "confidence": 0.85
    }},
    {{
      "claim_id": "claim_1",
      "verdict": "UNCERTAIN",
      "reason": "Brief justification",
      "evidence_needed": true,
      "confidence": 0.50
    }}
  ]
}}

IMPORTANT:
- Return ONLY the JSON object
- No explanations outside the JSON
- Review ALL claims provided
- Be objective and evidence-based
"""


def format_claims_for_review(claims: list) -> str:
    """Format claims list for reviewer prompt"""
    formatted = []
    for idx, claim in enumerate(claims):
        formatted.append(f"[claim_{idx}]: {claim['canonical_text']}")
    return "\n".join(formatted)


def get_reviewer_prompt(query: str, claims: list) -> str:
    """Generate reviewer prompt"""
    claims_list = format_claims_for_review(claims)
    return REVIEWER_USER_PROMPT_TEMPLATE.format(
        query=query,
        claims_list=claims_list
    )


def get_reviewer_llama_prompt(query: str, claims: list) -> dict:
    """Format for llama.cpp server"""
    return {
        "prompt": f"{REVIEWER_SYSTEM_PROMPT}\n\n{get_reviewer_prompt(query, claims)}",
        "temperature": 0.3,
        "max_tokens": 1024,
        "stop": ["</s>", "Original Question:", "Claims to review:"],
        "stream": False
    }
