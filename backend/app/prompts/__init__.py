"""
Stage-1 prompts for first opinions
"""

STAGE1_SYSTEM_PROMPT = """You are an expert AI assistant providing factual, concise answers.
Your task is to answer the user's query accurately and provide supporting claims and citations.

CRITICAL RULES:
1. Do NOT engage in chain-of-thought reasoning
2. Do NOT show your work or thinking process
3. Provide ONLY the structured JSON output
4. Be factual and concise
5. Each claim should be atomic and verifiable
6. Include citations when possible
"""

STAGE1_USER_PROMPT_TEMPLATE = """Answer the following query concisely and factually.

Query: {query}

Return your response as a valid JSON object with this EXACT structure:
{{
  "answer_text": "Your concise answer here (2-4 sentences)",
  "claims": [
    "Atomic factual claim 1",
    "Atomic factual claim 2",
    "Atomic factual claim 3"
  ],
  "citations": [
    {{"source": "Source name", "url": "https://...", "snippet": "Relevant quote"}}
  ]
}}

IMPORTANT:
- answer_text: 2-4 sentences maximum
- claims: 3-7 atomic, verifiable statements
- Each claim should be ≤25 words
- citations: Include if you have reliable sources
- Return ONLY valid JSON, no other text
"""


def get_stage1_prompt(query: str) -> str:
    """Generate complete Stage-1 prompt"""
    return STAGE1_USER_PROMPT_TEMPLATE.format(query=query)


# Llama.cpp compatible format
def get_stage1_llama_prompt(query: str) -> dict:
    """Format for llama.cpp server"""
    return {
        "prompt": f"{STAGE1_SYSTEM_PROMPT}\n\n{get_stage1_prompt(query)}",
        "temperature": 0.7,
        "max_tokens": 1024,
        "stop": ["</s>", "User:", "Query:"],
        "stream": False
    }


# Hugging Face API format
def get_stage1_hf_prompt(query: str) -> dict:
    """Format for Hugging Face Inference API"""
    return {
        "inputs": f"{STAGE1_SYSTEM_PROMPT}\n\n{get_stage1_prompt(query)}",
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }
