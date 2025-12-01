"""
Chairman prompts for final synthesis
"""

CHAIRMAN_SYSTEM_PROMPT = """You are the Chairman of an expert panel synthesizing a final answer.
You have received:
1. Multiple initial opinions from different experts (anonymized)
2. Extracted canonical claims from those opinions
3. Independent peer review verdicts on each claim

Your task is to synthesize a final, authoritative answer based ONLY on:
- Claims marked as CORRECT by reviewers
- Claims with high consensus
- Verifiable facts

CRITICAL RULES:
1. Use ONLY supported claims (marked CORRECT)
2. Acknowledge uncertain points explicitly
3. Mention rejected claims if relevant to context
4. Provide a balanced, fact-based answer
5. Include citations when available
6. Be concise but comprehensive
7. Return ONLY JSON output
"""

CHAIRMAN_USER_PROMPT_TEMPLATE = """Original Query: {query}

=== INITIAL OPINIONS ===
{stage1_opinions}

=== CANONICAL CLAIMS ===
{canonical_claims}

=== PEER REVIEW VERDICTS ===
{review_verdicts}

=== AGGREGATION SUMMARY ===
Total claims: {total_claims}
Supported (CORRECT): {supported_count}
Rejected (INCORRECT): {rejected_count}
Uncertain: {uncertain_count}
Disputed: {disputed_count}
Consensus score: {consensus_score}

=== YOUR TASK ===
Synthesize a final answer to the original query based on the evidence above.

Return ONLY valid JSON with this structure:
{{
  "final_answer": "Your comprehensive final answer (3-6 sentences). Base this ONLY on supported claims. Acknowledge uncertainties.",
  "supporting_claims": [
    "Claim 1 that supports the answer",
    "Claim 2 that supports the answer"
  ],
  "uncertain_points": [
    "Point 1 that needs more evidence",
    "Point 2 that is disputed"
  ],
  "rejected_claims": [
    "Claim 1 that was marked incorrect",
    "Claim 2 that contradicts evidence"
  ],
  "citations": [
    {{"source": "Source name", "url": "https://...", "snippet": "Quote"}}
  ],
  "confidence": 0.85,
  "reasoning_summary": "Brief summary of your reasoning process (2-3 sentences)"
}}

IMPORTANT:
- final_answer: 3-6 sentences, comprehensive but concise
- confidence: 0.0-1.0 based on consensus and evidence quality
- Include ALL categories even if empty lists
- Return ONLY valid JSON, no other text
- Be objective and evidence-based
"""


def format_stage1_opinions(opinions: list) -> str:
    """Format Stage-1 opinions for chairman"""
    formatted = []
    for idx, opinion in enumerate(opinions):
        formatted.append(f"Expert {idx + 1}: {opinion['answer_text']}")
    return "\n".join(formatted)


def format_canonical_claims(claims: list) -> str:
    """Format canonical claims for chairman"""
    formatted = []
    for claim in claims:
        formatted.append(f"- [{claim['claim_id']}] {claim['canonical_text']}")
    return "\n".join(formatted)


def format_review_verdicts(verdicts: list) -> str:
    """Format review verdicts for chairman"""
    formatted = []
    for verdict in verdicts:
        formatted.append(f"\n{verdict['reviewer_name']}:")
        for review in verdict['reviews']:
            formatted.append(
                f"  [{review['claim_id']}] {review['verdict']} "
                f"(confidence: {review['confidence']:.2f}) - {review['reason']}"
            )
    return "\n".join(formatted)


def get_chairman_prompt(
    query: str,
    stage1_opinions: list,
    canonical_claims: list,
    review_verdicts: list,
    aggregation: dict
) -> str:
    """Generate chairman synthesis prompt"""
    return CHAIRMAN_USER_PROMPT_TEMPLATE.format(
        query=query,
        stage1_opinions=format_stage1_opinions(stage1_opinions),
        canonical_claims=format_canonical_claims(canonical_claims),
        review_verdicts=format_review_verdicts(review_verdicts),
        total_claims=aggregation['total_claims'],
        supported_count=len(aggregation['supported_claims']),
        rejected_count=len(aggregation['rejected_claims']),
        uncertain_count=len(aggregation['uncertain_claims']),
        disputed_count=len(aggregation['disputed_claims']),
        consensus_score=aggregation['consensus_score']
    )


def get_chairman_gemini_prompt(
    query: str,
    stage1_opinions: list,
    canonical_claims: list,
    review_verdicts: list,
    aggregation: dict
) -> str:
    """Format for Gemini API"""
    return f"{CHAIRMAN_SYSTEM_PROMPT}\n\n{get_chairman_prompt(query, stage1_opinions, canonical_claims, review_verdicts, aggregation)}"
