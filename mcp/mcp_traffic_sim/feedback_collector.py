"""User feedback collection system for continuous optimization."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager


class UserFeedback(BaseModel):
    """User feedback data model."""

    feedback_id: str
    prompt_id: str
    user_id: str
    original_prompt: str
    generated_output: str
    feedback_text: str
    quality_rating: float = Field(ge=0.0, le=1.0)
    timestamp: float
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackAnalysis(BaseModel):
    """Analysis of user feedback."""

    feedback_id: str
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    quality_indicators: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    optimization_priority: str = "low"  # low, medium, high, critical
    confidence_score: float = Field(ge=0.0, le=1.0)


class FeedbackCollector:
    """Collect and analyze user feedback for continuous optimization."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize feedback collector."""
        self.config = config
        self.logger = logger
        self.security = security

        # Feedback storage
        self.feedback_storage: List[UserFeedback] = []
        self.feedback_analysis: Dict[str, FeedbackAnalysis] = {}
        self.feedback_aggregates: Dict[str, Dict[str, Any]] = {}

        # Feedback processing
        self.feedback_queue: asyncio.Queue = asyncio.Queue()
        self.processing_tasks: List[asyncio.Task] = []

        # Feedback triggers
        self.optimization_triggers: Dict[str, float] = {
            "quality_threshold": 0.7,
            "sentiment_threshold": -0.3,
            "feedback_volume_threshold": 10,
        }

        # Background processing will be started when needed
        self._background_processing_started = False

    def _start_background_processing(self):
        """Start background feedback processing tasks."""
        # Start feedback processor
        self.processing_tasks.append(asyncio.create_task(self._process_feedback_queue()))

        # Start aggregation processor
        self.processing_tasks.append(asyncio.create_task(self._process_feedback_aggregation()))

        # Start trigger processor
        self.processing_tasks.append(asyncio.create_task(self._process_optimization_triggers()))

    async def collect_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect user feedback for a prompt."""
        # Start background processing if not already started
        if not self._background_processing_started:
            self._start_background_processing()
            self._background_processing_started = True

        try:
            # Create feedback object
            feedback = UserFeedback(
                feedback_id=f"feedback_{int(time.time())}_{len(self.feedback_storage)}",
                prompt_id=feedback_data["prompt_id"],
                user_id=feedback_data.get("user_id", "anonymous"),
                original_prompt=feedback_data["original_prompt"],
                generated_output=feedback_data["generated_output"],
                feedback_text=feedback_data["feedback_text"],
                quality_rating=feedback_data.get("quality_rating", 0.5),
                timestamp=time.time(),
                context=feedback_data.get("context", {}),
                metadata=feedback_data.get("metadata", {}),
            )

            # Store feedback
            self.feedback_storage.append(feedback)

            # Add to processing queue
            await self.feedback_queue.put(feedback)

            # Log feedback collection
            self.logger.log_info(
                f"Collected feedback for {feedback.prompt_id} from {feedback.user_id}"
            )

            return {
                "success": True,
                "feedback_id": feedback.feedback_id,
                "timestamp": feedback.timestamp,
                "queue_position": self.feedback_queue.qsize(),
            }

        except Exception as e:
            self.logger.log_error(f"Error collecting feedback: {e}")
            return {"success": False, "error_message": str(e)}

    async def _process_feedback_queue(self):
        """Process feedback from queue."""
        while True:
            try:
                # Get feedback from queue
                feedback = await self.feedback_queue.get()

                # Analyze feedback
                analysis = await self._analyze_feedback(feedback)
                self.feedback_analysis[feedback.feedback_id] = analysis

                # Update aggregates
                await self._update_feedback_aggregates(feedback, analysis)

                # Check for optimization triggers
                await self._check_optimization_triggers(feedback, analysis)

                # Mark task as done
                self.feedback_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error processing feedback: {e}")

    async def _analyze_feedback(self, feedback: UserFeedback) -> FeedbackAnalysis:
        """Analyze user feedback for optimization insights."""
        # Sentiment analysis (simplified)
        sentiment_score = self._analyze_sentiment(feedback.feedback_text)

        # Quality indicators
        quality_indicators = self._extract_quality_indicators(feedback)

        # Improvement suggestions
        improvement_suggestions = self._extract_improvement_suggestions(feedback)

        # Optimization priority
        optimization_priority = self._calculate_optimization_priority(
            feedback, sentiment_score, quality_indicators
        )

        # Confidence score
        confidence_score = self._calculate_confidence_score(feedback, quality_indicators)

        return FeedbackAnalysis(
            feedback_id=feedback.feedback_id,
            sentiment_score=sentiment_score,
            quality_indicators=quality_indicators,
            improvement_suggestions=improvement_suggestions,
            optimization_priority=optimization_priority,
            confidence_score=confidence_score,
        )

    def _analyze_sentiment(self, feedback_text: str) -> float:
        """Analyze sentiment of feedback text."""
        # Simplified sentiment analysis
        positive_words = [
            "good",
            "great",
            "excellent",
            "perfect",
            "helpful",
            "useful",
            "clear",
            "accurate",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "wrong",
            "confusing",
            "unclear",
            "inaccurate",
            "useless",
        ]

        text_lower = feedback_text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count + negative_count == 0:
            return 0.0

        return (positive_count - negative_count) / (positive_count + negative_count)

    def _extract_quality_indicators(self, feedback: UserFeedback) -> List[str]:
        """Extract quality indicators from feedback."""
        indicators = []

        if feedback.quality_rating >= 0.8:
            indicators.append("high_quality")
        elif feedback.quality_rating <= 0.4:
            indicators.append("low_quality")

        if "clear" in feedback.feedback_text.lower():
            indicators.append("clarity_mentioned")

        if "accurate" in feedback.feedback_text.lower():
            indicators.append("accuracy_mentioned")

        if "helpful" in feedback.feedback_text.lower():
            indicators.append("helpfulness_mentioned")

        if "confusing" in feedback.feedback_text.lower():
            indicators.append("confusion_mentioned")

        return indicators

    def _extract_improvement_suggestions(self, feedback: UserFeedback) -> List[str]:
        """Extract improvement suggestions from feedback."""
        suggestions = []

        feedback_lower = feedback.feedback_text.lower()

        if "more" in feedback_lower:
            suggestions.append("increase_detail")

        if "less" in feedback_lower:
            suggestions.append("reduce_complexity")

        if "example" in feedback_lower:
            suggestions.append("add_examples")

        if "step" in feedback_lower:
            suggestions.append("add_step_by_step")

        return suggestions

    def _calculate_optimization_priority(
        self, feedback: UserFeedback, sentiment_score: float, quality_indicators: List[str]
    ) -> str:
        """Calculate optimization priority based on feedback."""
        # High priority factors
        if feedback.quality_rating <= 0.3:
            return "critical"

        if sentiment_score <= -0.5:
            return "high"

        if "low_quality" in quality_indicators:
            return "high"

        # Medium priority factors
        if feedback.quality_rating <= 0.6:
            return "medium"

        if sentiment_score <= -0.2:
            return "medium"

        # Low priority
        return "low"

    def _calculate_confidence_score(
        self, feedback: UserFeedback, quality_indicators: List[str]
    ) -> float:
        """Calculate confidence score for feedback analysis."""
        confidence = 0.5  # Base confidence

        # Increase confidence for detailed feedback
        if len(feedback.feedback_text) > 50:
            confidence += 0.2

        # Increase confidence for specific quality indicators
        if quality_indicators:
            confidence += 0.1

        # Increase confidence for high/low quality ratings
        if feedback.quality_rating >= 0.8 or feedback.quality_rating <= 0.3:
            confidence += 0.2

        return min(confidence, 1.0)

    async def _update_feedback_aggregates(self, feedback: UserFeedback, analysis: FeedbackAnalysis):
        """Update feedback aggregates for prompt."""
        prompt_id = feedback.prompt_id

        if prompt_id not in self.feedback_aggregates:
            self.feedback_aggregates[prompt_id] = {
                "total_feedback": 0,
                "average_quality": 0.0,
                "average_sentiment": 0.0,
                "optimization_priority": "low",
                "last_updated": time.time(),
                "quality_trend": "stable",
                "feedback_volume": 0,
            }

        aggregate = self.feedback_aggregates[prompt_id]
        aggregate["total_feedback"] += 1

        # Update running averages
        total = aggregate["total_feedback"]
        aggregate["average_quality"] = (
            aggregate["average_quality"] * (total - 1) + feedback.quality_rating
        ) / total
        aggregate["average_sentiment"] = (
            aggregate["average_sentiment"] * (total - 1) + analysis.sentiment_score
        ) / total

        # Update optimization priority
        if analysis.optimization_priority == "critical":
            aggregate["optimization_priority"] = "critical"
        elif (
            analysis.optimization_priority == "high"
            and aggregate["optimization_priority"] != "critical"
        ):
            aggregate["optimization_priority"] = "high"
        elif analysis.optimization_priority == "medium" and aggregate[
            "optimization_priority"
        ] not in ["critical", "high"]:
            aggregate["optimization_priority"] = "medium"

        aggregate["last_updated"] = time.time()
        aggregate["feedback_volume"] = total

    async def _check_optimization_triggers(
        self, feedback: UserFeedback, analysis: FeedbackAnalysis
    ):
        """Check if feedback triggers optimization."""
        prompt_id = feedback.prompt_id

        # Check quality threshold
        if feedback.quality_rating < self.optimization_triggers["quality_threshold"]:
            await self._trigger_optimization(
                prompt_id,
                "quality_threshold",
                {
                    "quality_rating": feedback.quality_rating,
                    "threshold": self.optimization_triggers["quality_threshold"],
                },
            )

        # Check sentiment threshold
        if analysis.sentiment_score < self.optimization_triggers["sentiment_threshold"]:
            await self._trigger_optimization(
                prompt_id,
                "sentiment_threshold",
                {
                    "sentiment_score": analysis.sentiment_score,
                    "threshold": self.optimization_triggers["sentiment_threshold"],
                },
            )

        # Check feedback volume threshold
        if prompt_id in self.feedback_aggregates:
            aggregate = self.feedback_aggregates[prompt_id]
            if (
                aggregate["feedback_volume"]
                >= self.optimization_triggers["feedback_volume_threshold"]
            ):
                await self._trigger_optimization(
                    prompt_id,
                    "feedback_volume",
                    {
                        "feedback_volume": aggregate["feedback_volume"],
                        "threshold": self.optimization_triggers["feedback_volume_threshold"],
                    },
                )

    async def _trigger_optimization(
        self, prompt_id: str, trigger_type: str, trigger_data: Dict[str, Any]
    ):
        """Trigger optimization based on feedback."""
        optimization_trigger = {
            "prompt_id": prompt_id,
            "trigger_type": trigger_type,
            "trigger_data": trigger_data,
            "timestamp": time.time(),
            "priority": self._get_trigger_priority(trigger_type),
        }

        # Log optimization trigger
        self.logger.log_info(f"Optimization triggered for {prompt_id}: {trigger_type}")

        # Store trigger for processing
        # In real implementation, this would trigger actual optimization
        self.logger.log_optimization_trigger(optimization_trigger)

    def _get_trigger_priority(self, trigger_type: str) -> str:
        """Get priority for optimization trigger."""
        priority_map = {
            "quality_threshold": "high",
            "sentiment_threshold": "medium",
            "feedback_volume": "low",
        }
        return priority_map.get(trigger_type, "low")

    async def _process_feedback_aggregation(self):
        """Process feedback aggregation periodically."""
        while True:
            try:
                # Update quality trends
                await self._update_quality_trends()

                # Clean up old feedback
                await self._cleanup_old_feedback()

                # Wait before next aggregation
                await asyncio.sleep(3600)  # Every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error in feedback aggregation: {e}")

    async def _update_quality_trends(self):
        """Update quality trends for all prompts."""
        for prompt_id, aggregate in self.feedback_aggregates.items():
            # Get recent feedback for this prompt
            recent_feedback = [
                f
                for f in self.feedback_storage
                if f.prompt_id == prompt_id and time.time() - f.timestamp < 86400  # Last 24 hours
            ]

            if len(recent_feedback) >= 3:
                # Calculate trend
                recent_quality = [f.quality_rating for f in recent_feedback[-3:]]
                older_quality = (
                    [f.quality_rating for f in recent_feedback[:-3]]
                    if len(recent_feedback) > 3
                    else recent_quality
                )

                recent_avg = sum(recent_quality) / len(recent_quality)
                older_avg = sum(older_quality) / len(older_quality) if older_quality else recent_avg

                if recent_avg > older_avg * 1.05:
                    aggregate["quality_trend"] = "improving"
                elif recent_avg < older_avg * 0.95:
                    aggregate["quality_trend"] = "declining"
                else:
                    aggregate["quality_trend"] = "stable"

    async def _cleanup_old_feedback(self):
        """Clean up old feedback data."""
        cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days ago

        # Remove old feedback
        self.feedback_storage = [f for f in self.feedback_storage if f.timestamp > cutoff_time]

        # Remove old analysis
        old_analysis_ids = [
            fid
            for fid, analysis in self.feedback_analysis.items()
            if analysis.feedback_id not in [f.feedback_id for f in self.feedback_storage]
        ]
        for fid in old_analysis_ids:
            del self.feedback_analysis[fid]

    async def _process_optimization_triggers(self):
        """Process optimization triggers periodically."""
        while True:
            try:
                # Check for accumulated triggers
                await self._process_accumulated_triggers()

                # Wait before next check
                await asyncio.sleep(300)  # Every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error processing optimization triggers: {e}")

    async def _process_accumulated_triggers(self):
        """Process accumulated optimization triggers."""
        # This would implement actual optimization triggering
        # For now, just log the processing
        self.logger.log_info("Processing accumulated optimization triggers")

    async def get_feedback_summary(self, prompt_id: Optional[str] = None) -> Dict[str, Any]:
        """Get feedback summary for prompt or all prompts."""
        try:
            if prompt_id:
                # Get feedback for specific prompt
                prompt_feedback = [f for f in self.feedback_storage if f.prompt_id == prompt_id]
                prompt_analysis = [
                    a
                    for a in self.feedback_analysis.values()
                    if a.feedback_id in [f.feedback_id for f in prompt_feedback]
                ]

                if prompt_id in self.feedback_aggregates:
                    aggregate = self.feedback_aggregates[prompt_id]
                else:
                    aggregate = {
                        "total_feedback": 0,
                        "average_quality": 0.0,
                        "average_sentiment": 0.0,
                        "optimization_priority": "low",
                    }

                return {
                    "success": True,
                    "prompt_id": prompt_id,
                    "feedback_count": len(prompt_feedback),
                    "aggregate": aggregate,
                    "recent_feedback": [
                        {
                            "feedback_id": f.feedback_id,
                            "quality_rating": f.quality_rating,
                            "sentiment_score": next(
                                (
                                    a.sentiment_score
                                    for a in prompt_analysis
                                    if a.feedback_id == f.feedback_id
                                ),
                                0.0,
                            ),
                            "timestamp": f.timestamp,
                        }
                        for f in prompt_feedback[-10:]  # Last 10 feedback items
                    ],
                }
            else:
                # Get feedback for all prompts
                return {
                    "success": True,
                    "total_feedback": len(self.feedback_storage),
                    "prompts_with_feedback": len(self.feedback_aggregates),
                    "aggregates": self.feedback_aggregates,
                    "recent_activity": [
                        {
                            "prompt_id": f.prompt_id,
                            "feedback_id": f.feedback_id,
                            "quality_rating": f.quality_rating,
                            "timestamp": f.timestamp,
                        }
                        for f in self.feedback_storage[-20:]  # Last 20 feedback items
                    ],
                }

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def shutdown(self):
        """Shutdown feedback collector."""
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        self.logger.log_info("Feedback collector shutdown complete")
