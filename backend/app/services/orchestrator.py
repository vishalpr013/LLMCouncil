"""
Pipeline orchestrator - coordinates the entire multi-model debate process
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.local_models import Llama7BRunner
from app.services.remote_models import get_hf_client, get_gemini_client
from app.services.paraphrase import ParaphraseService
from app.services.reviewers import ReviewerService
from app.services.aggregator import AggregatorService
from app.services.chairman import ChairmanService
from app.prompts.stage1 import get_stage1_llama_prompt, get_stage1_hf_prompt
from app.utils.cache import get_cache
from app.utils.logger import logger, log_stage, log_model_call
from app.utils.error_handler import PipelineError


class PipelineOrchestrator:
    """
    Main orchestrator for the multi-model debate pipeline
    
    Pipeline stages:
    1. Stage-1: Parallel first opinions (Llama-7B + GPT-OSS-20B)
    2. Paraphrase: Claim extraction (GPT-J-6B)
    3. Review: Peer review (Mistral-7B + DeepSeek-7B)
    4. Aggregation: Combine verdicts
    5. Chairman: Final synthesis (Gemini)
    """
    
    def __init__(self):
        self.cache = get_cache()
        
        # Initialize services
        self.llama_runner = Llama7BRunner()
        self.hf_client = get_hf_client()
        self.gemini_client = get_gemini_client()
        
        self.paraphrase_service = ParaphraseService()
        self.reviewer_service = ReviewerService()
        self.aggregator_service = AggregatorService()
        self.chairman_service = ChairmanService()
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "cache_hits": 0,
            "total_processing_time": 0.0
        }
        
        logger.info("Pipeline orchestrator initialized")
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing pipeline components...")
        # Components are initialized lazily
        logger.info("Pipeline ready")
    
    async def run_pipeline(
        self,
        query: str,
        options: Optional[Dict] = None,
        request_id: str = ""
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline
        
        Args:
            query: User query
            options: Optional query options
            request_id: Request tracking ID
            
        Returns:
            Complete pipeline result
        """
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        options = options or {}
        stage_timings = {}
        
        try:
            # Check cache
            if options.get("use_cache", True):
                cached = self.cache.get(query, options)
                if cached:
                    self.stats["cache_hits"] += 1
                    logger.info(f"[{request_id}] Returning cached response")
                    return cached
            
            # Stage 1: First Opinions
            log_stage(request_id, "Stage-1", "started")
            stage1_start = time.time()
            stage1_opinions = await self._run_stage1(query, request_id, options)
            stage1_time = time.time() - stage1_start
            stage_timings["stage1"] = stage1_time
            log_stage(request_id, "Stage-1", "completed", stage1_time)
            
            # Stage 2: Paraphrase/Claim Extraction
            log_stage(request_id, "Paraphrase", "started")
            paraphrase_start = time.time()
            paraphrased_claims = await self._run_paraphrase(stage1_opinions, request_id)
            paraphrase_time = time.time() - paraphrase_start
            stage_timings["paraphrase"] = paraphrase_time
            log_stage(request_id, "Paraphrase", "completed", paraphrase_time)
            
            # Stage 3: Peer Review
            log_stage(request_id, "Review", "started")
            review_start = time.time()
            reviewer_verdicts = await self._run_review(query, paraphrased_claims, request_id, options)
            review_time = time.time() - review_start
            stage_timings["review"] = review_time
            log_stage(request_id, "Review", "completed", review_time)
            
            # Stage 4: Aggregation
            log_stage(request_id, "Aggregation", "started")
            agg_start = time.time()
            aggregation = self._run_aggregation(paraphrased_claims, reviewer_verdicts)
            agg_time = time.time() - agg_start
            stage_timings["aggregation"] = agg_time
            log_stage(request_id, "Aggregation", "completed", agg_time)
            
            # Stage 5: Chairman Synthesis
            log_stage(request_id, "Chairman", "started")
            chairman_start = time.time()
            final_answer = await self._run_chairman(
                query, stage1_opinions, paraphrased_claims, 
                reviewer_verdicts, aggregation, request_id
            )
            chairman_time = time.time() - chairman_start
            stage_timings["chairman"] = chairman_time
            log_stage(request_id, "Chairman", "completed", chairman_time)
            
            # Build complete response
            processing_time = time.time() - start_time
            
            result = {
                "query": query,
                "stage1_opinions": stage1_opinions,
                "paraphrased_claims": paraphrased_claims,
                "reviewer_verdicts": reviewer_verdicts,
                "aggregation": aggregation,
                "final_answer": final_answer,
                "metadata": {
                    "request_id": request_id,
                    "processing_time": processing_time,
                    "models_used": self._get_models_used(),
                    "cache_hit": False,
                    "errors": [],
                    "warnings": [],
                    "stage_timings": stage_timings,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Cache result
            if options.get("use_cache", True):
                self.cache.set(query, result, options)
            
            self.stats["successful_queries"] += 1
            self.stats["total_processing_time"] += processing_time
            
            return result
            
        except Exception as e:
            self.stats["failed_queries"] += 1
            logger.error(f"[{request_id}] Pipeline failed: {str(e)}")
            raise PipelineError(f"Pipeline execution failed: {str(e)}")
    
    async def _run_stage1(
        self,
        query: str,
        request_id: str,
        options: Dict
    ) -> List[Dict[str, Any]]:
        """Run Stage-1: parallel first opinions"""
        
        tasks = []
        
        # Llama-7B (local)
        if settings.enable_stage1_llama:
            tasks.append(self._call_llama7b(query, request_id))
        
        # HF API (remote)
        if settings.enable_stage1_hf:
            tasks.append(self._call_hf_model(query, request_id))
        
        # Run in parallel if enabled
        if options.get("enable_parallel", True) and settings.enable_parallel_stage1:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for task in tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    results.append(e)
        
        # Process results
        opinions = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Stage-1 model failed: {str(result)}")
                if not options.get("skip_failed_models", True):
                    raise result
            elif result:
                opinions.append(result)
        
        if not opinions:
            raise PipelineError("All Stage-1 models failed")
        
        return opinions
    
    async def _call_llama7b(self, query: str, request_id: str) -> Dict[str, Any]:
        """Call Llama-7B for first opinion"""
        start_time = time.time()
        
        try:
            prompt = get_stage1_llama_prompt(query)
            response = await self.llama_runner.generate(prompt)
            
            # Parse JSON response
            parsed = self._parse_stage1_response(response, "Llama-7B")
            
            duration = time.time() - start_time
            log_model_call(request_id, "Llama-7B", "success", duration)
            
            return parsed
            
        except Exception as e:
            duration = time.time() - start_time
            log_model_call(request_id, "Llama-7B", "failed", duration)
            raise
    
    async def _call_hf_model(self, query: str, request_id: str) -> Dict[str, Any]:
        """Call Hugging Face model for first opinion"""
        start_time = time.time()
        
        try:
            prompt = get_stage1_hf_prompt(query)
            response = await self.hf_client.generate(prompt)
            
            # Parse JSON response
            parsed = self._parse_stage1_response(response, "GPT-OSS-20B")
            
            duration = time.time() - start_time
            log_model_call(request_id, "GPT-OSS-20B", "success", duration)
            
            return parsed
            
        except Exception as e:
            duration = time.time() - start_time
            log_model_call(request_id, "GPT-OSS-20B", "failed", duration)
            raise
    
    def _parse_stage1_response(self, response: str, model_name: str) -> Dict[str, Any]:
        """Parse Stage-1 JSON response"""
        try:
            # Extract JSON
            response = response.strip()
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                parsed = json.loads(json_str)
            else:
                raise ValueError("No JSON found")
            
            # Format opinion
            return {
                "model_name": model_name,
                "answer_text": parsed.get("answer_text", ""),
                "claims": parsed.get("claims", []),
                "citations": parsed.get("citations", []),
                "metadata": {}
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse {model_name} response: {str(e)}")
            # Fallback: use raw response as answer
            return {
                "model_name": model_name,
                "answer_text": response[:500],
                "claims": [],
                "citations": [],
                "metadata": {"parse_error": True}
            }
    
    async def _run_paraphrase(
        self,
        stage1_opinions: List[Dict],
        request_id: str
    ) -> List[Dict[str, Any]]:
        """Run paraphrase stage to extract canonical claims"""
        
        all_claims = []
        
        for opinion in stage1_opinions:
            try:
                claims = await self.paraphrase_service.extract_claims(
                    model_name=opinion["model_name"],
                    answer_text=opinion["answer_text"]
                )
                all_claims.extend(claims)
            except Exception as e:
                logger.warning(f"Paraphrase failed for {opinion['model_name']}: {str(e)}")
        
        return all_claims
    
    async def _run_review(
        self,
        query: str,
        claims: List[Dict],
        request_id: str,
        options: Dict
    ) -> List[Dict[str, Any]]:
        """Run peer review stage"""
        
        tasks = []
        
        # Reviewer A (Mistral)
        if settings.enable_reviewer_a:
            tasks.append(
                self.reviewer_service.review_claims("Reviewer_A", query, claims)
            )
        
        # Reviewer B (DeepSeek)
        if settings.enable_reviewer_b:
            tasks.append(
                self.reviewer_service.review_claims("Reviewer_B", query, claims)
            )
        
        # Run in parallel if enabled
        if options.get("enable_parallel", True) and settings.enable_parallel_reviewers:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for task in tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    results.append(e)
        
        # Process results
        verdicts = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Reviewer failed: {str(result)}")
                if not options.get("skip_failed_models", True):
                    raise result
            elif result:
                verdicts.append(result)
        
        if not verdicts:
            raise PipelineError("All reviewers failed")
        
        return verdicts
    
    def _run_aggregation(
        self,
        claims: List[Dict],
        verdicts: List[Dict]
    ) -> Dict[str, Any]:
        """Run aggregation stage"""
        return self.aggregator_service.aggregate(claims, verdicts)
    
    async def _run_chairman(
        self,
        query: str,
        stage1_opinions: List[Dict],
        claims: List[Dict],
        verdicts: List[Dict],
        aggregation: Dict,
        request_id: str
    ) -> Dict[str, Any]:
        """Run chairman synthesis stage"""
        
        if not settings.enable_chairman:
            return self._fallback_chairman(aggregation)
        
        return await self.chairman_service.synthesize(
            query=query,
            stage1_opinions=stage1_opinions,
            paraphrased_claims=claims,
            reviewer_verdicts=verdicts,
            aggregation=aggregation
        )
    
    def _fallback_chairman(self, aggregation: Dict) -> Dict[str, Any]:
        """Fallback chairman if Gemini unavailable"""
        supported = aggregation.get("supported_claims", [])
        
        return {
            "final_answer": " ".join(supported[:3]) if supported else "Unable to synthesize answer.",
            "supporting_claims": supported[:5],
            "uncertain_points": aggregation.get("uncertain_claims", [])[:3],
            "rejected_claims": aggregation.get("rejected_claims", [])[:3],
            "citations": [],
            "confidence": 0.5,
            "reasoning_summary": "Fallback synthesis (Chairman unavailable)"
        }
    
    def _get_models_used(self) -> List[str]:
        """Get list of models used in pipeline"""
        models = []
        
        if settings.enable_stage1_llama:
            models.append("Llama-7B")
        if settings.enable_stage1_hf:
            models.append("GPT-OSS-20B")
        
        models.append("GPT-J-6B")
        
        if settings.enable_reviewer_a:
            models.append("Mistral-7B")
        if settings.enable_reviewer_b:
            models.append("DeepSeek-7B")
        
        if settings.enable_chairman:
            models.append("Gemini-1.5-Pro")
        
        return models
    
    async def check_health(self) -> Dict[str, Any]:
        """Check health of all models"""
        
        health_checks = {
            "llama_7b": self.llama_runner.health_check(),
            "gptj_6b": self.paraphrase_service.runner.health_check(),
            "mistral_7b": self.reviewer_service.reviewer_a.health_check(),
            "deepseek_7b": self.reviewer_service.reviewer_b.health_check(),
            "hf_api": self.hf_client.health_check(),
            "gemini_api": self.gemini_client.health_check()
        }
        
        results = await asyncio.gather(*health_checks.values(), return_exceptions=True)
        
        status_map = {}
        for (name, _), result in zip(health_checks.items(), results):
            if isinstance(result, Exception):
                status_map[name] = "offline"
            else:
                status_map[name] = "online" if result else "offline"
        
        # Determine overall status
        online_count = sum(1 for s in status_map.values() if s == "online")
        total_count = len(status_map)
        
        if online_count == total_count:
            overall = "healthy"
        elif online_count >= total_count / 2:
            overall = "degraded"
        else:
            overall = "unhealthy"
        
        return {
            "status": overall,
            "models": status_map,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        avg_time = (
            self.stats["total_processing_time"] / self.stats["successful_queries"]
            if self.stats["successful_queries"] > 0
            else 0.0
        )
        
        return {
            "total_queries": self.stats["total_queries"],
            "successful_queries": self.stats["successful_queries"],
            "failed_queries": self.stats["failed_queries"],
            "cache_hits": self.stats["cache_hits"],
            "average_processing_time": round(avg_time, 2),
            "cache_stats": self.cache.get_stats()
        }
    
    async def clear_cache(self):
        """Clear response cache"""
        self.cache.clear()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up pipeline resources...")
        
        await self.llama_runner.close()
        await self.hf_client.close()
        await self.paraphrase_service.close()
        await self.reviewer_service.close()
        
        logger.info("Cleanup completed")
