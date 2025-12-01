"""
Chairman service for final synthesis
Uses Gemini to synthesize final answer from all evidence
"""

import json
from typing import List, Dict, Any
from app.services.remote_models import get_gemini_client
from app.prompts.chairman import get_chairman_gemini_prompt
from app.utils.logger import logger
from app.utils.error_handler import ValidationError


class ChairmanService:
    """Service for final answer synthesis"""
    
    def __init__(self):
        self.client = get_gemini_client()
    
    async def synthesize(
        self,
        query: str,
        stage1_opinions: List[Dict[str, Any]],
        paraphrased_claims: List[Dict[str, Any]],
        reviewer_verdicts: List[Dict[str, Any]],
        aggregation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize final answer from all pipeline data
        
        Args:
            query: Original user query
            stage1_opinions: Stage-1 model outputs
            paraphrased_claims: Canonical claims
            reviewer_verdicts: Reviewer outputs
            aggregation: Aggregated verdicts
            
        Returns:
            Final answer dict
        """
        try:
            logger.debug("Synthesizing final answer with Gemini")
            
            # Generate comprehensive prompt
            prompt = get_chairman_gemini_prompt(
                query=query,
                stage1_opinions=stage1_opinions,
                canonical_claims=paraphrased_claims,
                review_verdicts=reviewer_verdicts,
                aggregation=aggregation
            )
            
            # Call Gemini
            response = await self.client.generate(prompt)
            
            # Parse JSON response
            try:
                parsed = self._parse_response(response)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse chairman response, attempting cleanup: {str(e)}")
                parsed = self._clean_and_parse(response)
            
            # Validate structure
            required_fields = [
                "final_answer",
                "supporting_claims",
                "uncertain_points",
                "rejected_claims",
                "confidence"
            ]
            
            for field in required_fields:
                if field not in parsed:
                    if field == "confidence":
                        parsed[field] = 0.7
                    elif field == "final_answer":
                        raise ValidationError("Missing final_answer in chairman response")
                    else:
                        parsed[field] = []
            
            # Ensure citations is a list
            if "citations" not in parsed:
                parsed["citations"] = []
            
            # Add reasoning summary if missing
            if "reasoning_summary" not in parsed:
                parsed["reasoning_summary"] = "Synthesized based on supported claims and peer review."
            
            # Format final answer
            final_answer = {
                "final_answer": parsed["final_answer"],
                "supporting_claims": parsed["supporting_claims"][:10],  # Limit to 10
                "uncertain_points": parsed["uncertain_points"][:5],
                "rejected_claims": parsed["rejected_claims"][:5],
                "citations": parsed.get("citations", [])[:10],
                "confidence": float(parsed["confidence"]),
                "reasoning_summary": parsed.get("reasoning_summary", "")
            }
            
            logger.info(f"Final answer synthesized (confidence: {final_answer['confidence']:.2f})")
            return final_answer
            
        except Exception as e:
            logger.error(f"Chairman synthesis failed: {str(e)}")
            
            # Fallback: generate simple summary
            return self._fallback_synthesis(query, aggregation)
    
    def _parse_response(self, response: str) -> dict:
        """Parse JSON response"""
        response = response.strip()
        
        # Find JSON object
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
        
        raise json.JSONDecodeError("No JSON object found", response, 0)
    
    def _clean_and_parse(self, response: str) -> dict:
        """Clean response and attempt parsing"""
        # Remove markdown code blocks
        response = response.replace("```json", "").replace("```", "")
        
        # Remove common prefixes
        response = response.replace("Output:", "").replace("Result:", "")
        
        return self._parse_response(response)
    
    def _fallback_synthesis(
        self,
        query: str,
        aggregation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback: simple synthesis from aggregation"""
        logger.warning("Using fallback synthesis")
        
        supported = aggregation.get("supported_claims", [])
        uncertain = aggregation.get("uncertain_claims", [])
        rejected = aggregation.get("rejected_claims", [])
        
        # Generate simple answer
        if supported:
            final_answer = f"Based on verified claims: {' '.join(supported[:3])}"
        else:
            final_answer = "Unable to provide a confident answer due to insufficient verified claims."
        
        return {
            "final_answer": final_answer,
            "supporting_claims": supported[:5],
            "uncertain_points": uncertain[:3],
            "rejected_claims": rejected[:3],
            "citations": [],
            "confidence": 0.5,
            "reasoning_summary": "Fallback synthesis due to chairman error."
        }
