"""
Agent Chain Module

Provides infrastructure for agent invocation and chaining.
Agents pass context to each other via memory files.
"""

from orchestration.agent_chain.flow import AgentFlow, FlowStep, ContextPattern
from orchestration.agent_chain.state import ChainState
from orchestration.agent_chain.memory import MemoryFile, load_predecessor_context
from orchestration.agent_chain.orchestrator import ChainOrchestrator
from orchestration.agent_chain.invoker import build_agent_invocation_directive
from orchestration.agent_chain.dynamic import create_dynamic_flow

__all__ = [
    "AgentFlow",
    "FlowStep",
    "ContextPattern",
    "ChainState",
    "MemoryFile",
    "load_predecessor_context",
    "ChainOrchestrator",
    "build_agent_invocation_directive",
    "create_dynamic_flow",
]
