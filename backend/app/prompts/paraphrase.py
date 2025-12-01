"""
Paraphrase and claim extraction prompts
"""

PARAPHRASE_SYSTEM_PROMPT = """You are an expert at extracting and reformulating claims into canonical form.
Your task is to convert natural language answers into atomic, canonical claims.

RULES:
1. Each claim must be atomic (single verifiable fact)
2. Each claim must be ≤20 words
3. Use clear, unambiguous language
4. Remove hedging words unless factually necessary
5. Maintain factual accuracy
6. Do NOT add information not present in the original
7. Return ONLY JSON output
"""

PARAPHRASE_USER_PROMPT_TEMPLATE = """Convert the following answer into a list of atomic canonical claims.

Original Answer:
{answer_text}

Extract and reformulate ALL factual claims. Each claim should be:
- Atomic (one fact per claim)
- Clear and unambiguous
- ≤20 words
- Preserving original meaning

Return ONLY valid JSON with this structure:
{{
  "claims": [
    "Canonical claim 1",
    "Canonical claim 2",
    "Canonical claim 3"
  ]
}}

IMPORTANT:
- Return ONLY the JSON object
- No explanations or additional text
- Each claim is a single sentence
- Preserve all facts from the original answer
"""


def get_paraphrase_prompt(answer_text: str) -> str:
    """Generate paraphrase prompt for claim extraction"""
    return PARAPHRASE_USER_PROMPT_TEMPLATE.format(answer_text=answer_text)


def get_paraphrase_llama_prompt(answer_text: str) -> dict:
    """Format for llama.cpp server (GPT-J-6B)"""
    return {
        "prompt": f"{PARAPHRASE_SYSTEM_PROMPT}\n\n{get_paraphrase_prompt(answer_text)}",
        "temperature": 0.5,
        "max_tokens": 512,
        "stop": ["</s>", "Original Answer:", "\n\n\n"],
        "stream": False
    }
