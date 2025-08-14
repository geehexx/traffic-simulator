"""MCP tools for prompt management and optimization."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from ..config import MCPConfig
from ..logging_util import MCPLogger
from ..security import SecurityManager
from .schemas import (
    PromptInput,
    PromptMode,
    MetaOptimizerConfig,
)
from .registry import PromptRegistryManager
from .meta_optimizer import MetaOptimizer
from .dspy_modules import PromptExecutor


class PromptTools:
    """MCP tools for prompt management and optimization."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize prompt tools."""
        self.config = config
        self.logger = logger
        self.security = security

        # Initialize prompt management components
        self.registry_manager = PromptRegistryManager(
            registry_path=config.repo_path / "runs" / "prompts"
        )
        self.meta_optimizer = MetaOptimizer(
            registry_manager=self.registry_manager, config=MetaOptimizerConfig()
        )
        self.prompt_executor = PromptExecutor()

    def execute_prompt(
        self,
        mode: str,
        repo_metadata: Optional[Dict[str, Any]] = None,
        git_signals: Optional[Dict[str, Any]] = None,
        change_inventory: Optional[List[str]] = None,
        chat_decisions: Optional[List[str]] = None,
        style_guide: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a prompt with structured input and output."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Create structured input
            input_data = PromptInput(
                mode=prompt_mode,
                repo_metadata=repo_metadata or {},
                git_signals=git_signals or {},
                change_inventory=change_inventory or [],
                chat_decisions=chat_decisions or [],
                style_guide=style_guide or {},
                constraints=constraints or {},
                context=context or {},
            )

            # Execute prompt
            output = self.prompt_executor.forward(input_data)

            result = {
                "success": output.success,
                "mode": output.mode.value,
                "artifacts": output.artifacts,
                "diffs": output.diffs,
                "coverage_decisions": output.coverage_decisions,
                "consolidation_map": output.consolidation_map,
                "questions": output.questions,
                "commit_message": output.commit_message,
                "execution_time": output.execution_time,
                "summary": f"Prompt execution: {'✓' if output.success else '✗'}, "
                f"Artifacts: {len(output.artifacts)}, "
                f"Time: {output.execution_time:.2f}s",
            }

            if output.error:
                result["error"] = output.error

            if output.quality_scores:
                result["quality_scores"] = {
                    "pdqi_9_score": output.quality_scores.pdqi_9_score,
                    "rgs_score": output.quality_scores.rgs_score,
                    "stability_index": output.quality_scores.stability_index,
                    "idempotency_score": output.quality_scores.idempotency_score,
                    "duplication_score": output.quality_scores.duplication_score,
                    "link_integrity_score": output.quality_scores.link_integrity_score,
                    "overall_score": output.quality_scores.overall_score,
                }

            duration = time.time() - start_time
            self.logger.log_operation(
                "prompt",
                "execute",
                {"mode": mode, "input_data": input_data.model_dump()},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to execute prompt: {e}"
            self.logger.log_operation(
                "prompt", "execute", {"mode": mode}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def register_prompt(
        self,
        content: str,
        mode: str,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Register a new prompt in the registry."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Register prompt
            prompt_id = self.registry_manager.register_prompt(
                content=content, mode=prompt_mode, parameters=parameters, metadata=metadata
            )

            result = {
                "success": True,
                "prompt_id": prompt_id,
                "mode": mode,
                "summary": f"Prompt registered: {prompt_id}",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "prompt",
                "register",
                {"mode": mode, "content_length": len(content)},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to register prompt: {e}"
            self.logger.log_operation(
                "prompt", "register", {"mode": mode}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def get_active_prompt(self, mode: str) -> Dict[str, Any]:
        """Get the active prompt for a mode."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Get active prompt
            active_prompt = self.registry_manager.get_active_prompt(prompt_mode)

            if not active_prompt:
                return {
                    "success": False,
                    "error": f"No active prompt found for mode: {mode}",
                    "mode": mode,
                }

            result = {
                "success": True,
                "prompt_id": active_prompt.id,
                "content": active_prompt.content,
                "parameters": active_prompt.parameters,
                "metadata": active_prompt.metadata,
                "created_at": active_prompt.created_at.isoformat(),
                "mode": mode,
                "summary": f"Active prompt: {active_prompt.id}",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "prompt", "get_active", {"mode": mode}, result, duration=duration
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get active prompt: {e}"
            self.logger.log_operation(
                "prompt", "get_active", {"mode": mode}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def optimize_prompts(
        self,
        mode: str,
        auto_apply: bool = False,
        test_inputs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Optimize prompts for a specific mode."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Convert test inputs if provided
            structured_test_inputs = None
            if test_inputs:
                structured_test_inputs = []
                for test_input in test_inputs:
                    structured_input = PromptInput(
                        mode=prompt_mode,
                        repo_metadata=test_input.get("repo_metadata", {}),
                        git_signals=test_input.get("git_signals", {}),
                        change_inventory=test_input.get("change_inventory", []),
                        chat_decisions=test_input.get("chat_decisions", []),
                        style_guide=test_input.get("style_guide", {}),
                        constraints=test_input.get("constraints", {}),
                        context=test_input.get("context", {}),
                    )
                    structured_test_inputs.append(structured_input)

            # Run optimization
            optimization_result = self.meta_optimizer.optimize_prompts(
                mode=prompt_mode, test_inputs=structured_test_inputs
            )

            # Apply if requested
            applied = False
            if auto_apply and optimization_result.winner_candidate:
                applied = self.meta_optimizer.apply_optimization(
                    optimization_result, prompt_mode, auto_apply=True
                )

            result = {
                "success": True,
                "mode": mode,
                "candidates_generated": len(optimization_result.evaluation_results),
                "winner_candidate": {
                    "id": optimization_result.winner_candidate.id
                    if optimization_result.winner_candidate
                    else None,
                    "content": optimization_result.winner_candidate.content
                    if optimization_result.winner_candidate
                    else None,
                },
                "improvement_metrics": optimization_result.improvement_metrics,
                "applied": applied,
                "suggestions": optimization_result.next_optimization_suggestions,
                "summary": f"Optimization completed: {len(optimization_result.evaluation_results)} candidates evaluated",
            }

            if optimization_result.winner_candidate:
                result["winner_quality_scores"] = {
                    "overall_score": optimization_result.winner_candidate.metadata.get(
                        "overall_score", 0
                    ),
                    "stability_index": optimization_result.winner_candidate.metadata.get(
                        "stability_index", 0
                    ),
                }

            duration = time.time() - start_time
            self.logger.log_operation(
                "prompt",
                "optimize",
                {"mode": mode, "auto_apply": auto_apply},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to optimize prompts: {e}"
            self.logger.log_operation(
                "prompt", "optimize", {"mode": mode}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def list_prompts(self, mode: Optional[str] = None) -> Dict[str, Any]:
        """List prompts in the registry."""
        start_time = time.time()

        try:
            # Validate mode if provided
            prompt_mode = None
            if mode:
                try:
                    prompt_mode = PromptMode(mode)
                except ValueError:
                    raise ValueError(
                        f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                    )

            # Get prompts
            prompts = self.registry_manager.list_prompts(prompt_mode)

            result = {
                "success": True,
                "prompts": [
                    {
                        "id": prompt.id,
                        "content": prompt.content[:200] + "..."
                        if len(prompt.content) > 200
                        else prompt.content,
                        "parameters": prompt.parameters,
                        "metadata": prompt.metadata,
                        "created_at": prompt.created_at.isoformat(),
                    }
                    for prompt in prompts
                ],
                "total_count": len(prompts),
                "mode_filter": mode,
                "summary": f"Found {len(prompts)} prompts",
            }

            duration = time.time() - start_time
            self.logger.log_operation("prompt", "list", {"mode": mode}, result, duration=duration)

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to list prompts: {e}"
            self.logger.log_operation(
                "prompt", "list", {"mode": mode}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        start_time = time.time()

        try:
            stats = self.meta_optimizer.get_optimization_stats()
            history = self.meta_optimizer.get_optimization_history()
            registry_stats = self.registry_manager.get_registry_stats()

            result = {
                "success": True,
                "optimization_stats": stats,
                "optimization_history": history,
                "registry_stats": registry_stats,
                "summary": f"Optimization stats: {stats.get('total_optimizations', 0)} total optimizations",
            }

            duration = time.time() - start_time
            self.logger.log_operation("prompt", "get_stats", {}, result, duration=duration)

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get optimization stats: {e}"
            self.logger.log_operation("prompt", "get_stats", {}, error=error_msg, duration=duration)
            raise RuntimeError(error_msg)
