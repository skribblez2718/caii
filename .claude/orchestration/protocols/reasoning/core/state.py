"""
state.py
========

JSON-based state management for the Mandatory Reasoning Protocol.

This module handles:
- Creating and persisting protocol state
- Tracking step outputs (orchestrator responses)
- Managing routing decisions
- Routing validation loop iteration tracking
- Session lifecycle

State is stored separately from the memory protocol (which handles
inter-agent communication). This state tracks orchestration progress.

Routing Validation Loop:
    Steps 4-8 form a validation loop (max 3 iterations).
    Step 4 produces preliminary routing; Steps 5-8 validate.
    If contradiction detected at Step 8, loop back to Step 4.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, Dict, List, Union

# Path setup - navigate to protocols directory for fully-qualified imports
# This prevents collision between reasoning/config and skill/config
_CORE_DIR = Path(__file__).resolve().parent
_REASONING_ROOT = _CORE_DIR.parent
_PROTOCOLS_DIR = _REASONING_ROOT.parent
if str(_PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTOCOLS_DIR))

from reasoning.config.config import (
    STATE_DIR,
    PROTOCOL_NAME,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    STEP_NAMES,
    get_state_file_path,
)
from reasoning.core.fsm import ReasoningFSM, ReasoningState


class ProtocolState:
    """
    Manages the state of a Mandatory Reasoning Protocol execution.

    This class handles:
    - Session initialization
    - Step progression tracking
    - Output capture (orchestrator responses to each step)
    - Routing decision storage
    - State persistence to JSON

    The state is separate from the memory protocol - this tracks
    orchestration progress, not inter-agent communication.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        user_query: str = "",
        fsm: Optional[ReasoningFSM] = None,
    ):
        """
        Initialize protocol state.

        Args:
            session_id: Unique session identifier (generated if not provided)
            user_query: The user's original query
            fsm: FSM instance (created if not provided)
        """
        self.session_id = session_id or self._generate_session_id()
        self.user_query = user_query
        self.query_timestamp = datetime.now(timezone.utc).isoformat()
        self.fsm = fsm or ReasoningFSM()

        # Generic metadata dict for extensibility (e.g., agent sessions)
        self.metadata: Dict[str, Any] = {}

        # Step tracking (keys can be float like 0.5, int like 1-8, or str like "3b")
        self.step_outputs: Dict[Union[float, str], Dict[str, Any]] = {}
        self.step_timestamps: Dict[Union[float, str], Dict[str, str]] = {}

        # Routing validation loop tracking (Steps 4-8)
        self.iteration_count: int = 0  # Current iteration (0 = first pass)
        self.preliminary_routes: List[Dict[str, Any]] = []  # Routes from each iteration
        self.contradiction_detected: bool = False  # Flag for loop-back

        # Final routing decision (set after confident Step 8)
        self.routing_decision: Optional[str] = None
        self.routing_justification: Optional[str] = None

        # Halt state (set if Step 8 detects ambiguity)
        self.halt_reason: Optional[str] = None
        self.clarification_questions: List[str] = []

        # Dispatch tracking (for reliable execution chain)
        # When reasoning completes, store dispatch info so hook can inject it
        self.dispatch_pending: Optional[Dict[str, Any]] = None

        # IDEAL STATE tracking (Phase 1 - The Last Algorithm integration)
        # See: .claude/research/reasoning-protocol-enhancements/
        self.ideal_state: Optional[Dict[str, Any]] = None
        self.ideal_state_iteration: int = 0
        self.ideal_state_max_iterations: int = 5
        self.ideal_state_history: List[Dict[str, Any]] = []

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())[:12]

    @property
    def state_file_path(self) -> Path:
        """Get the path to this session's state file."""
        return get_state_file_path(self.session_id)

    @property
    def current_step(self) -> Optional[float]:
        """Get the current step number (0, 0.5, 1-8)."""
        return self.fsm.get_current_step()

    @property
    def status(self) -> str:
        """Get the current status string."""
        if self.fsm.is_completed():
            return "completed"
        elif self.fsm.is_halted():
            return "halted"
        elif self.fsm.state == ReasoningState.INITIALIZED:
            return "initialized"
        else:
            return "in_progress"

    def start_step(self, step_num: float) -> bool:
        """
        Mark a step as started.

        Args:
            step_num: The step number (0, 0.5, 1-8)

        Returns:
            True if step was started successfully
        """
        target_state = ReasoningFSM.STEP_TO_STATE.get(step_num)
        if not target_state:
            return False

        if self.fsm.transition(target_state):
            self.step_timestamps[step_num] = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": None,
            }
            return True
        return False

    def complete_step(self, step_num: float, output: Dict[str, Any]) -> bool:
        """
        Mark a step as completed and store its output.

        Args:
            step_num: The step number (0, 0.5, 1-8)
            output: The step's output (orchestrator response, extracted data, etc.)

        Returns:
            True if step was completed successfully
        """
        if self.current_step != step_num:
            return False

        self.step_outputs[step_num] = output

        if step_num in self.step_timestamps:
            self.step_timestamps[step_num]["completed_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

        return True

    def add_preliminary_route(self, route: str, justification: str = "") -> None:
        """
        Add a preliminary routing decision from Step 4.

        This is called each time Step 4 produces a routing hypothesis.
        The route is stored for tracking across iterations.

        Args:
            route: The routing decision (e.g., "skill-orchestration", "direct", "meta")
            justification: Reason for the routing decision
        """
        self.preliminary_routes.append({
            "iteration": self.iteration_count,
            "route": route,
            "justification": justification,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def set_final_routing(self, route: str, justification: str = "") -> None:
        """
        Set the FINAL routing decision after confident Step 8.

        This is only called when Step 8 completes confidently (no contradiction).

        Args:
            route: The final routing decision
            justification: Reason for the routing decision
        """
        self.routing_decision = route
        self.routing_justification = justification
        self.contradiction_detected = False

    def trigger_loop_back(self, reason: str = "") -> bool:
        """
        Trigger a loop-back from Step 8 to Step 4.

        Called when contradiction is detected during routing validation.
        Increments iteration count and sets contradiction flag.

        Args:
            reason: Why the loop-back is being triggered

        Returns:
            True if loop-back allowed, False if max iterations reached
        """
        if self.iteration_count >= ReasoningFSM.MAX_ITERATIONS - 1:
            # Max iterations reached, cannot loop back
            return False

        self.iteration_count += 1
        self.contradiction_detected = True

        # Record the loop-back in preliminary routes
        self.preliminary_routes.append({
            "iteration": self.iteration_count,
            "route": None,
            "justification": f"LOOP-BACK: {reason}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return True

    def can_loop_back(self) -> bool:
        """
        Check if another loop-back iteration is allowed.

        Returns:
            True if iteration_count < MAX_ITERATIONS - 1
        """
        return self.iteration_count < ReasoningFSM.MAX_ITERATIONS - 1

    def get_current_preliminary_route(self) -> Optional[str]:
        """
        Get the most recent preliminary route.

        Returns:
            The route from the current iteration, or None
        """
        for pr in reversed(self.preliminary_routes):
            if pr.get("route"):
                return pr["route"]
        return None

    def halt_for_clarification(self, reason: str, questions: List[str]) -> bool:
        """
        Halt the protocol for clarification (Step 8).

        Args:
            reason: Why clarification is needed
            questions: List of clarification questions

        Returns:
            True if halt was successful
        """
        if self.fsm.transition(ReasoningState.HALTED):
            self.halt_reason = reason
            self.clarification_questions = questions
            return True
        return False

    # ==========================================================================
    # IDEAL STATE Methods (Phase 1 - The Last Algorithm integration)
    # ==========================================================================

    def update_ideal_state(self, ideal_state: Dict[str, Any]) -> None:
        """
        Update the IDEAL STATE and record in history.

        Args:
            ideal_state: The IDEAL STATE data structure containing:
                - success_criteria: List of success criteria
                - anti_criteria: List of anti-criteria (things to avoid)
                - success_metrics: List of measurable success metrics
                - completeness_score: Float 0.0-1.0 indicating completeness
                - exit_condition: Description of when IDEAL STATE is sufficient
                - sufficiency: Assessment of whether criteria are sufficient
        """
        # Increment iteration
        self.ideal_state_iteration += 1
        ideal_state["iteration"] = self.ideal_state_iteration

        # Record in history
        self.ideal_state_history.append({
            "iteration": self.ideal_state_iteration,
            "ideal_state": ideal_state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Update current state
        self.ideal_state = ideal_state

    def get_ideal_state_completeness(self) -> float:
        """
        Get the current IDEAL STATE completeness score.

        Returns:
            Completeness score (0.0-1.0) or 0.0 if no IDEAL STATE
        """
        if self.ideal_state:
            return self.ideal_state.get("completeness_score", 0.0)
        return 0.0

    def is_ideal_state_sufficient(self) -> bool:
        """
        Check if IDEAL STATE is sufficient to proceed (>= 95% complete).

        Returns:
            True if completeness >= 0.95 or max iterations reached
        """
        if self.ideal_state_iteration >= self.ideal_state_max_iterations:
            return True  # Hard limit reached
        return self.get_ideal_state_completeness() >= 0.95

    def can_iterate_ideal_state(self) -> bool:
        """
        Check if another IDEAL STATE iteration is allowed.

        Returns:
            True if iteration_count < max_iterations
        """
        return self.ideal_state_iteration < self.ideal_state_max_iterations

    # ==========================================================================
    # Dispatch Tracking Methods (for reliable execution chain)
    # ==========================================================================

    def set_dispatch_pending(
        self,
        route: str,
        directive_command: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Set a pending dispatch to be executed on next user prompt.

        This ensures the execution chain continues even if the dispatcher
        directive print statement isn't processed immediately.

        Args:
            route: The routing decision (skill-orchestration, dynamic-skill-sequencing)
            directive_command: The full command to execute
            context: Optional additional context for dispatch
        """
        self.dispatch_pending = {
            "route": route,
            "session_id": self.session_id,
            "directive_command": directive_command,
            "context": context or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def clear_dispatch_pending(self) -> None:
        """Clear the pending dispatch after it has been handled."""
        self.dispatch_pending = None

    def has_pending_dispatch(self) -> bool:
        """Check if there is a pending dispatch waiting to be executed."""
        return self.dispatch_pending is not None

    def get_dispatch_info(self) -> Optional[Dict[str, Any]]:
        """
        Get the pending dispatch information.

        Returns:
            Dispatch info dict or None if no pending dispatch
        """
        return self.dispatch_pending

    def complete_protocol(self) -> bool:
        """
        Mark the protocol as successfully completed.

        Returns:
            True if completion was successful
        """
        return self.fsm.transition(ReasoningState.COMPLETED)

    def get_step_output(self, step_num: float) -> Optional[Dict[str, Any]]:
        """
        Get the output from a specific step.

        Args:
            step_num: The step number (0, 0.5, 1-8)

        Returns:
            Step output or None if not available
        """
        return self.step_outputs.get(step_num)

    def get_previous_step_output(self) -> Optional[Dict[str, Any]]:
        """
        Get the output from the previous step.

        Returns:
            Previous step's output or None
        """
        current = self.current_step
        if current and current > 1:
            return self.get_step_output(current - 1)
        return None

    def to_dict(self) -> dict:
        """
        Serialize state for JSON storage.

        Returns:
            Dictionary representation of state
        """
        return {
            "schema_version": SCHEMA_VERSION,
            "protocol_name": PROTOCOL_NAME,
            "protocol_version": PROTOCOL_VERSION,
            "session_id": self.session_id,
            "user_query": self.user_query,
            "query_timestamp": self.query_timestamp,
            "status": self.status,
            "fsm": self.fsm.to_dict(),
            "step_outputs": {str(k): v for k, v in self.step_outputs.items()},
            "step_timestamps": {str(k): v for k, v in self.step_timestamps.items()},
            # Generic metadata
            "metadata": self.metadata,
            # Routing validation loop tracking
            "iteration_count": self.iteration_count,
            "preliminary_routes": self.preliminary_routes,
            "contradiction_detected": self.contradiction_detected,
            # Final routing decision
            "routing_decision": self.routing_decision,
            "routing_justification": self.routing_justification,
            "halt_reason": self.halt_reason,
            "clarification_questions": self.clarification_questions,
            # Dispatch tracking
            "dispatch_pending": self.dispatch_pending,
            # IDEAL STATE tracking (Phase 1)
            "ideal_state": self.ideal_state,
            "ideal_state_iteration": self.ideal_state_iteration,
            "ideal_state_max_iterations": self.ideal_state_max_iterations,
            "ideal_state_history": self.ideal_state_history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProtocolState":
        """
        Restore state from JSON data.

        Args:
            data: Dictionary with state data

        Returns:
            Restored ProtocolState instance
        """
        fsm = ReasoningFSM.from_dict(data["fsm"])
        state = cls(
            session_id=data["session_id"],
            user_query=data["user_query"],
            fsm=fsm,
        )
        state.query_timestamp = data["query_timestamp"]
        # Convert keys to appropriate type: int, float (for 0.5), or string (for "3b")
        def convert_step_key(k: str):
            """Convert step key to appropriate type."""
            if k.isdigit():
                return int(k)
            try:
                # Try float conversion for keys like "0.5"
                f = float(k)
                # Only use float if it's actually a non-integer decimal
                if f != int(f):
                    return f
                return int(f)
            except ValueError:
                return k  # Keep as string (e.g., "3b")

        state.step_outputs = {
            convert_step_key(k): v
            for k, v in data.get("step_outputs", {}).items()
        }
        state.step_timestamps = {
            convert_step_key(k): v
            for k, v in data.get("step_timestamps", {}).items()
        }
        # Generic metadata (backwards-compatible default)
        state.metadata = data.get("metadata", {})
        # Routing validation loop tracking
        state.iteration_count = data.get("iteration_count", 0)
        state.preliminary_routes = data.get("preliminary_routes", [])
        state.contradiction_detected = data.get("contradiction_detected", False)
        # Final routing decision
        state.routing_decision = data.get("routing_decision")
        state.routing_justification = data.get("routing_justification")
        state.halt_reason = data.get("halt_reason")
        state.clarification_questions = data.get("clarification_questions", [])
        # Note: Planning fields (plan, plan_status, skip_planning, etc.) were removed.
        # Old state files containing these are handled gracefully - fields are simply ignored.
        # Planning is now handled by Claude Code's built-in EnterPlanMode tool.
        # Dispatch tracking
        state.dispatch_pending = data.get("dispatch_pending")
        # IDEAL STATE tracking (Phase 1 - backwards compatible defaults)
        state.ideal_state = data.get("ideal_state")
        state.ideal_state_iteration = data.get("ideal_state_iteration", 0)
        state.ideal_state_max_iterations = data.get("ideal_state_max_iterations", 5)
        state.ideal_state_history = data.get("ideal_state_history", [])
        return state

    def save(self) -> Path:
        """
        Save state to JSON file.

        Returns:
            Path to the saved state file
        """
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file = self.state_file_path

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        return state_file

    @classmethod
    def load(cls, session_id: str) -> Optional["ProtocolState"]:
        """
        Load state from JSON file.

        Args:
            session_id: The session ID to load

        Returns:
            Restored ProtocolState or None if not found
        """
        state_file = get_state_file_path(session_id)

        if not state_file.exists():
            return None

        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def find_active(cls) -> Optional["ProtocolState"]:
        """
        Find the most recent active (in-progress) protocol state.

        Returns the most recently created in-progress session, based on
        query_timestamp. This ensures we resume the correct session when
        a user provides clarification answers.

        Returns:
            Active ProtocolState or None if none found
        """
        if not STATE_DIR.exists():
            return None

        most_recent: Optional[dict] = None
        most_recent_timestamp: Optional[str] = None

        for state_file in STATE_DIR.glob("reasoning-*.json"):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("status") == "in_progress":
                    timestamp = data.get("query_timestamp", "")
                    if most_recent is None or timestamp > most_recent_timestamp:
                        most_recent = data
                        most_recent_timestamp = timestamp
            except (json.JSONDecodeError, KeyError):
                continue

        if most_recent:
            return cls.from_dict(most_recent)
        return None

    @classmethod
    def find_with_pending_dispatch(cls) -> Optional["ProtocolState"]:
        """
        Find a protocol state that has a pending dispatch to execute.

        This is used by the hook to continue execution chain when
        a dispatch directive was set but not processed immediately.

        Returns:
            ProtocolState with pending dispatch, or None if none found
        """
        if not STATE_DIR.exists():
            return None

        for state_file in STATE_DIR.glob("reasoning-*.json"):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("dispatch_pending") is not None:
                    return cls.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    def __repr__(self) -> str:
        return (
            f"ProtocolState(session_id={self.session_id!r}, "
            f"status={self.status!r}, step={self.current_step})"
        )
