"""
Reviewer service for peer review stage
Uses Mistral-7B and DeepSeek-7B to evaluate claims
"""

import json
from typing import List, Dict, Any
from app.services.local_models import Mistral7BRunner, DeepSeek7BRunner
from app.prompts.reviewer import get_reviewer_llama_prompt
from app.models.schemas import Verdict
from app.utils.logger import logger
from app.utils.error_handler import ValidationError


class ReviewerService:
    """Service for peer reviewing claims"""
    
    def __init__(self):
        self.reviewer_a = Mistral7BRunner()
        self.reviewer_b = DeepSeek7BRunner()
    
    async def review_claims(
        self,
        reviewer_name: str,
        query: str,
        claims: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Review claims with specified reviewer
        
        Args:
            reviewer_name: "Reviewer_A" or "Reviewer_B"
            query: Original user query
            claims: List of canonical claims to review
            
        Returns:
            Reviewer verdict dict
        """
        try:
            logger.debug(f"{reviewer_name} reviewing {len(claims)} claims")
            
            # Select reviewer
            runner = self.reviewer_a if reviewer_name == "Reviewer_A" else self.reviewer_b
            
            # Generate prompt
            prompt = get_reviewer_llama_prompt(query, claims)
            
            # Call model
            response = await runner.generate(prompt)
            
            # Parse JSON response
            try:
                parsed = self._parse_response(response)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse reviewer response, attempting cleanup: {str(e)}")
                parsed = self._clean_and_parse(response)
            
            # Validate structure
            if "reviews" not in parsed or not isinstance(parsed["reviews"], list):
                raise ValidationError("Invalid reviewer response structure")
            
            # Format reviews
            reviews = []
            for review in parsed["reviews"]:
                if self._validate_review(review):
                    reviews.append({
                        "claim_id": review["claim_id"],
                        "verdict": review["verdict"].upper(),
                        "reason": review["reason"],
                        "evidence_needed": review.get("evidence_needed", False),
                        "confidence": float(review.get("confidence", 0.5))
                    })
            
            verdict = {
                "reviewer_name": reviewer_name,
                "reviews": reviews,
                "metadata": {
                    "total_reviewed": len(reviews),
                    "model": runner.model_name
                }
            }
            
            logger.info(f"{reviewer_name} completed {len(reviews)} reviews")
            return verdict
            
        except Exception as e:
            logger.error(f"Review failed for {reviewer_name}: {str(e)}")
            
            # Fallback: mark all as uncertain
            return self._fallback_reviews(reviewer_name, claims)
    
    def _validate_review(self, review: dict) -> bool:
        """Validate review structure"""
        required_fields = ["claim_id", "verdict", "reason"]
        
        if not all(field in review for field in required_fields):
            return False
        
        if review["verdict"].upper() not in ["CORRECT", "INCORRECT", "UNCERTAIN"]:
            return False
        
        return True
    
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
    
    def _fallback_reviews(self, reviewer_name: str, claims: List[Dict]) -> Dict[str, Any]:
        """Fallback: mark all as uncertain"""
        logger.warning(f"Using fallback reviews for {reviewer_name}")
        
        reviews = []
        for claim in claims:
            reviews.append({
                "claim_id": claim["claim_id"],
                "verdict": "UNCERTAIN",
                "reason": "Unable to verify due to reviewer error",
                "evidence_needed": True,
                "confidence": 0.3
            })
        
        return {
            "reviewer_name": reviewer_name,
            "reviews": reviews,
            "metadata": {
                "total_reviewed": len(reviews),
                "fallback": True
            }
        }
    
    async def close(self):
        """Cleanup resources"""
        await self.reviewer_a.close()
        await self.reviewer_b.close()
