"""
Aggregator service for combining reviewer verdicts
"""

from typing import List, Dict, Any
from collections import defaultdict, Counter
from app.utils.logger import logger


class AggregatorService:
    """Service for aggregating reviewer verdicts"""
    
    def aggregate(
        self,
        claims: List[Dict[str, Any]],
        verdicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate verdicts from multiple reviewers
        
        Args:
            claims: List of canonical claims
            verdicts: List of reviewer verdict dicts
            
        Returns:
            Aggregation result dict
        """
        try:
            logger.debug(f"Aggregating verdicts from {len(verdicts)} reviewers")
            
            # Collect all reviews by claim_id
            reviews_by_claim = defaultdict(list)
            
            for verdict in verdicts:
                for review in verdict["reviews"]:
                    reviews_by_claim[review["claim_id"]].append(review)
            
            # Categorize claims
            supported_claims = []
            rejected_claims = []
            disputed_claims = []
            uncertain_claims = []
            evidence_needed_count = 0
            
            # Create claim lookup
            claim_lookup = {c["claim_id"]: c for c in claims}
            
            # Analyze each claim
            for claim_id, reviews in reviews_by_claim.items():
                if claim_id not in claim_lookup:
                    continue
                
                claim_text = claim_lookup[claim_id]["canonical_text"]
                
                # Count verdicts
                verdict_counts = Counter([r["verdict"] for r in reviews])
                
                # Count evidence needed
                if any(r.get("evidence_needed", False) for r in reviews):
                    evidence_needed_count += 1
                
                # Determine category
                correct_count = verdict_counts.get("CORRECT", 0)
                incorrect_count = verdict_counts.get("INCORRECT", 0)
                uncertain_count = verdict_counts.get("UNCERTAIN", 0)
                
                total_reviews = len(reviews)
                
                if correct_count == total_reviews:
                    # All reviewers agree: CORRECT
                    supported_claims.append(claim_text)
                    
                elif incorrect_count == total_reviews:
                    # All reviewers agree: INCORRECT
                    rejected_claims.append(claim_text)
                    
                elif uncertain_count == total_reviews:
                    # All reviewers agree: UNCERTAIN
                    uncertain_claims.append(claim_text)
                    
                elif correct_count > incorrect_count and correct_count > uncertain_count:
                    # Majority says CORRECT
                    supported_claims.append(claim_text)
                    
                elif incorrect_count > correct_count and incorrect_count > uncertain_count:
                    # Majority says INCORRECT
                    rejected_claims.append(claim_text)
                    
                else:
                    # Disputed or no clear majority
                    disputed_claims.append(claim_text)
            
            # Calculate consensus score
            total_claims = len(claims)
            consensus_score = self._calculate_consensus(
                reviews_by_claim,
                total_claims
            )
            
            result = {
                "total_claims": total_claims,
                "supported_claims": supported_claims,
                "rejected_claims": rejected_claims,
                "disputed_claims": disputed_claims,
                "uncertain_claims": uncertain_claims,
                "consensus_score": consensus_score,
                "evidence_needed_count": evidence_needed_count
            }
            
            logger.info(
                f"Aggregation complete: "
                f"{len(supported_claims)} supported, "
                f"{len(rejected_claims)} rejected, "
                f"{len(disputed_claims)} disputed, "
                f"{len(uncertain_claims)} uncertain"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Aggregation failed: {str(e)}")
            raise
    
    def _calculate_consensus(
        self,
        reviews_by_claim: Dict[str, List[Dict]],
        total_claims: int
    ) -> float:
        """
        Calculate consensus score (0.0-1.0)
        
        Higher score = more agreement between reviewers
        """
        if not reviews_by_claim or total_claims == 0:
            return 0.0
        
        agreement_count = 0
        total_comparisons = 0
        
        for claim_id, reviews in reviews_by_claim.items():
            if len(reviews) < 2:
                continue
            
            # Count unanimous verdicts
            verdicts = [r["verdict"] for r in reviews]
            if len(set(verdicts)) == 1:
                agreement_count += 1
            
            total_comparisons += 1
        
        if total_comparisons == 0:
            return 0.5
        
        consensus = agreement_count / total_comparisons
        return round(consensus, 3)
