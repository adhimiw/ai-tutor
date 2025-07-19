"""
Optimization Service for DSPy Modules
Handles systematic optimization of tutoring modules using Google Gemini
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import pickle

import dspy
from loguru import logger


class OptimizationService:
    """
    Service for optimizing DSPy modules using various optimizers
    Focuses on educational effectiveness metrics
    """
    
    def __init__(self):
        self.optimizers = {}
        self.optimization_history = {}
        self.cache_dir = os.getenv("OPTIMIZATION_CACHE_DIR", "./cache")
        self.is_initialized = False
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize optimization service"""
        try:
            # Initialize different optimizers
            self.optimizers = {
                "mipro_v2": dspy.MIPROv2(
                    metric=self._educational_effectiveness_metric,
                    auto="light",  # Use light mode for faster optimization
                    num_threads=4
                ),
                "bootstrap_rs": dspy.BootstrapRS(
                    metric=self._educational_effectiveness_metric,
                    max_bootstrapped_demos=3,
                    max_labeled_demos=3
                ),
                "bootstrap_fewshot": dspy.BootstrapFewShot(
                    metric=self._educational_effectiveness_metric,
                    max_bootstrapped_demos=5
                )
            }
            
            self.is_initialized = True
            logger.info("Optimization service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize optimization service: {e}")
            self.is_initialized = False
            raise
    
    async def optimize_module(self, module_name: str, module: dspy.Module, 
                            training_examples: List[Dict[str, Any]], 
                            metric_name: str = "educational_effectiveness"):
        """
        Optimize a DSPy module using training examples
        
        Args:
            module_name: Name of the module to optimize
            module: DSPy module instance
            training_examples: List of training examples
            metric_name: Metric to optimize for
        """
        
        if not self.is_initialized:
            logger.error("Optimization service not initialized")
            return
        
        try:
            logger.info(f"Starting optimization for module: {module_name}")
            
            # Convert training examples to DSPy format
            trainset = self._convert_to_dspy_examples(training_examples)
            
            if len(trainset) < 5:
                logger.warning(f"Only {len(trainset)} training examples available. Optimization may be limited.")
            
            # Select optimizer based on dataset size and requirements
            optimizer_name = self._select_optimizer(len(trainset), metric_name)
            optimizer = self.optimizers[optimizer_name]
            
            logger.info(f"Using optimizer: {optimizer_name}")
            
            # Run optimization
            start_time = datetime.now()
            optimized_module = optimizer.compile(
                module, 
                trainset=trainset,
                requires_permission_to_run=False
            )
            end_time = datetime.now()
            
            # Save optimized module
            optimization_id = f"{module_name}_{int(start_time.timestamp())}"
            await self._save_optimized_module(optimization_id, optimized_module, {
                "module_name": module_name,
                "optimizer": optimizer_name,
                "training_examples_count": len(trainset),
                "optimization_time": (end_time - start_time).total_seconds(),
                "timestamp": start_time.isoformat()
            })
            
            # Record optimization history
            self.optimization_history[optimization_id] = {
                "module_name": module_name,
                "optimizer": optimizer_name,
                "training_examples": len(trainset),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "status": "completed"
            }
            
            logger.info(f"Optimization completed for {module_name} in {(end_time - start_time).total_seconds():.2f} seconds")
            
            return {
                "optimization_id": optimization_id,
                "optimized_module": optimized_module,
                "optimizer_used": optimizer_name,
                "training_examples_count": len(trainset),
                "optimization_time": (end_time - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing module {module_name}: {e}")
            # Record failed optimization
            if 'optimization_id' in locals():
                self.optimization_history[optimization_id]["status"] = "failed"
                self.optimization_history[optimization_id]["error"] = str(e)
            raise
    
    def _convert_to_dspy_examples(self, training_examples: List[Dict[str, Any]]) -> List[dspy.Example]:
        """Convert training examples to DSPy format"""
        
        dspy_examples = []
        
        for example in training_examples:
            try:
                # Extract input and output fields
                inputs = {}
                outputs = {}
                
                # Common patterns for educational examples
                if "question" in example and "response" in example:
                    inputs["question"] = example["question"]
                    outputs["response"] = example["response"]
                
                if "user_message" in example and "ai_response" in example:
                    inputs["question"] = example["user_message"]
                    outputs["response"] = example["ai_response"]
                
                # Add context if available
                if "context" in example:
                    inputs["context"] = example["context"]
                
                # Add difficulty level if available
                if "difficulty_level" in example:
                    inputs["difficulty_level"] = example["difficulty_level"]
                
                # Add subject if available
                if "subject" in example:
                    inputs["subject"] = example["subject"]
                
                # Create DSPy example
                if inputs and outputs:
                    dspy_example = dspy.Example(**inputs, **outputs).with_inputs(*inputs.keys())
                    dspy_examples.append(dspy_example)
                
            except Exception as e:
                logger.warning(f"Failed to convert training example: {e}")
                continue
        
        logger.info(f"Converted {len(dspy_examples)} training examples to DSPy format")
        return dspy_examples
    
    def _select_optimizer(self, dataset_size: int, metric_name: str) -> str:
        """Select appropriate optimizer based on dataset size and requirements"""
        
        if dataset_size < 10:
            return "bootstrap_fewshot"  # Good for small datasets
        elif dataset_size < 50:
            return "bootstrap_rs"  # Good for medium datasets
        else:
            return "mipro_v2"  # Best for larger datasets
    
    def _educational_effectiveness_metric(self, example, pred, trace=None):
        """
        Educational effectiveness metric for tutoring optimization
        Evaluates how well the AI response helps student learning
        """
        
        try:
            # Extract expected and predicted responses
            expected = example.response if hasattr(example, 'response') else ""
            predicted = pred.response if hasattr(pred, 'response') else str(pred)
            
            if not expected or not predicted:
                return 0.0
            
            # Simple effectiveness scoring based on multiple criteria
            score = 0.0
            
            # 1. Content relevance (basic keyword overlap)
            expected_words = set(expected.lower().split())
            predicted_words = set(predicted.lower().split())
            
            if expected_words:
                overlap_ratio = len(expected_words.intersection(predicted_words)) / len(expected_words)
                score += overlap_ratio * 0.3
            
            # 2. Response completeness (length similarity)
            length_ratio = min(len(predicted), len(expected)) / max(len(predicted), len(expected), 1)
            score += length_ratio * 0.2
            
            # 3. Educational indicators (presence of explanatory elements)
            educational_indicators = [
                "because", "therefore", "for example", "step", "first", "second", "next",
                "explanation", "understand", "concept", "principle", "rule", "method"
            ]
            
            indicator_count = sum(1 for indicator in educational_indicators if indicator in predicted.lower())
            score += min(indicator_count / 5, 1.0) * 0.3
            
            # 4. Structure and clarity (basic checks)
            if len(predicted.split('.')) > 1:  # Multiple sentences
                score += 0.1
            
            if any(char in predicted for char in [':', '-', '•']):  # Structured formatting
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating educational effectiveness metric: {e}")
            return 0.0
    
    async def _save_optimized_module(self, optimization_id: str, module: dspy.Module, metadata: Dict[str, Any]):
        """Save optimized module to cache"""
        
        try:
            # Save module
            module_path = os.path.join(self.cache_dir, f"{optimization_id}_module.pkl")
            with open(module_path, 'wb') as f:
                pickle.dump(module, f)
            
            # Save metadata
            metadata_path = os.path.join(self.cache_dir, f"{optimization_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Saved optimized module: {optimization_id}")
            
        except Exception as e:
            logger.error(f"Error saving optimized module: {e}")
    
    async def load_optimized_module(self, optimization_id: str) -> Optional[dspy.Module]:
        """Load optimized module from cache"""
        
        try:
            module_path = os.path.join(self.cache_dir, f"{optimization_id}_module.pkl")
            
            if os.path.exists(module_path):
                with open(module_path, 'rb') as f:
                    module = pickle.load(f)
                
                logger.debug(f"Loaded optimized module: {optimization_id}")
                return module
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading optimized module: {e}")
            return None
    
    async def get_optimization_history(self) -> Dict[str, Any]:
        """Get optimization history"""
        return self.optimization_history
    
    async def cleanup_old_optimizations(self, days_old: int = 30):
        """Cleanup old optimization cache files"""
        
        try:
            cutoff_timestamp = datetime.now().timestamp() - (days_old * 24 * 3600)
            
            # Clean up optimization history
            to_remove = []
            for opt_id, opt_info in self.optimization_history.items():
                opt_timestamp = datetime.fromisoformat(opt_info["start_time"]).timestamp()
                if opt_timestamp < cutoff_timestamp:
                    to_remove.append(opt_id)
            
            for opt_id in to_remove:
                del self.optimization_history[opt_id]
                
                # Remove cache files
                module_path = os.path.join(self.cache_dir, f"{opt_id}_module.pkl")
                metadata_path = os.path.join(self.cache_dir, f"{opt_id}_metadata.json")
                
                for path in [module_path, metadata_path]:
                    if os.path.exists(path):
                        os.remove(path)
            
            logger.info(f"Cleaned up {len(to_remove)} old optimizations")
            
        except Exception as e:
            logger.error(f"Error during optimization cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization service statistics"""
        
        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(1 for opt in self.optimization_history.values() if opt["status"] == "completed")
        
        return {
            "is_initialized": self.is_initialized,
            "total_optimizations": total_optimizations,
            "successful_optimizations": successful_optimizations,
            "available_optimizers": list(self.optimizers.keys()),
            "cache_directory": self.cache_dir
        }
