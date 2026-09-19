"""
Execution Trace Tracking for the SatQuery Central Orchestrator.

Provides transparent recording of:
- User query interpretation
- Agent selection and reasoning
- Validation & dependency-ordered execution steps
- Execution timings & error auditing
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .schemas import ExecutionTrace, ExecutionStepTrace, AgentType


class TraceManager:
    """Manages the execution trace lifecycle for a single orchestration query."""

    def __init__(self, query: str):
        self.request_id = f"satquery-req-{uuid.uuid4().hex[:8]}"
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.user_query = query
        self.detected_intent = "Analyzing..."
        self.selected_agents: List[AgentType] = []
        self.selection_reasoning = ""
        self.execution_order: List[List[AgentType]] = []
        self.steps: List[ExecutionStepTrace] = []
        self.errors: List[str] = []
        self._start_time = time.time()
        self._step_counter = 1

    def set_plan(
        self,
        intent: str,
        selected_agents: List[AgentType],
        selection_reasoning: str,
        execution_order: List[List[AgentType]],
    ):
        """Records the parsed query plan."""
        self.detected_intent = intent
        self.selected_agents = selected_agents
        self.selection_reasoning = selection_reasoning
        self.execution_order = execution_order

    def add_step(
        self,
        name: str,
        description: str,
        status: str = "completed",
        duration_seconds: float = 0.0,
        details: Optional[Dict[str, Any]] = None,
    ) -> ExecutionStepTrace:
        """Appends a new checkpoint to the execution trace."""
        step = ExecutionStepTrace(
            step=self._step_counter,
            name=name,
            description=description,
            status=status,
            duration_seconds=round(duration_seconds, 3),
            details=details or {},
        )
        self.steps.append(step)
        self._step_counter += 1
        return step

    def record_error(self, error_message: str):
        """Logs an error encountered during execution."""
        self.errors.append(error_message)

    def finalize(self) -> ExecutionTrace:
        """Builds and returns the finalized execution trace."""
        total_duration = time.time() - self._start_time
        return ExecutionTrace(
            request_id=self.request_id,
            timestamp=self.timestamp,
            user_query=self.user_query,
            detected_intent=self.detected_intent,
            selected_agents=self.selected_agents,
            selection_reasoning=self.selection_reasoning,
            execution_order=self.execution_order,
            steps=self.steps,
            total_duration_seconds=round(total_duration, 3),
            errors=self.errors,
        )
