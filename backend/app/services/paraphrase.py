"""
Paraphrase service for claim extraction
Uses GPT-J-6B to convert answers into canonical claims
"""

import json
from typing import List, Dict, Any
from app.services.local_models import GPTJ6BRunner
from app.prompts.paraphrase import get_paraphrase_llama_prompt
from app.utils.logger import logger
from app.utils.error_handler import ValidationError


class ParaphraseService:
    """Service for extracting canonical claims from answers"""
    
    def __init__(self):
        self.runner = GPTJ6BRunner()
    
    async def extract_claims(
        self,
        model_name: str,
        answer_text: str
    ) -> List[Dict[str, Any]]:
        """
        Extract canonical claims from an answer
        
        Args:
            model_name: Source model name (for tracking)
            answer_text: Original answer text
            
        Returns:
            List of paraphrased claim dicts
        """
        try:
            logger.debug(f"Extracting claims from {model_name}")
            
            # Generate prompt
            prompt = get_paraphrase_llama_prompt(answer_text)
            
            # Call model
            response = await self.runner.generate(prompt)
            
            # Parse JSON response
            try:
                parsed = self._parse_response(response)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse paraphrase response, attempting cleanup: {str(e)}")
                parsed = self._clean_and_parse(response)
            
            # Validate structure
            if "claims" not in parsed or not isinstance(parsed["claims"], list):
                raise ValidationError("Invalid paraphrase response structure")
            
            # Format claims with IDs
            claims = []
            for idx, claim_text in enumerate(parsed["claims"]):
                if claim_text and isinstance(claim_text, str):
                    claims.append({
                        "claim_id": f"{model_name.lower()}_claim_{idx}",
                        "original_model": model_name,
                        "original_text": answer_text,
                        "canonical_text": claim_text.strip(),
                        "word_count": len(claim_text.split())
                    })
            
            logger.info(f"Extracted {len(claims)} claims from {model_name}")
            return claims
            
        except Exception as e:
            logger.error(f"Paraphrase failed for {model_name}: {str(e)}")
            
            # Fallback: split answer into sentences
            return self._fallback_extraction(model_name, answer_text)
    
    def _parse_response(self, response: str) -> dict:
        """Parse JSON response"""
        # Try to extract JSON from response
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
    
    def _fallback_extraction(self, model_name: str, answer_text: str) -> List[Dict[str, Any]]:
        """Fallback: split answer into sentences"""
        logger.warning(f"Using fallback claim extraction for {model_name}")
        
        # Simple sentence splitting
        sentences = [s.strip() for s in answer_text.split('.') if s.strip()]
        
        claims = []
        for idx, sentence in enumerate(sentences[:5]):  # Max 5 claims
            if len(sentence) > 10:  # Minimum length
                claims.append({
                    "claim_id": f"{model_name.lower()}_claim_{idx}",
                    "original_model": model_name,
                    "original_text": answer_text,
                    "canonical_text": sentence + ".",
                    "word_count": len(sentence.split())
                })
        
        return claims
    
    async def close(self):
        """Cleanup resources"""
        await self.runner.close()
