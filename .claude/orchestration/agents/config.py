"""
Agent Registry and Configuration

Provides centralized configuration for all cognitive agents,
including their metadata, context budgets, and model preferences.
"""

from typing import Dict, Final, List, Optional

# Agent registry with metadata
AGENT_REGISTRY: Final[Dict[str, Dict]] = {
    "clarification": {
        "cognitive_function": "CLARIFICATION",
        "description": "Transform vague inputs into actionable specifications",
        "color": "cyan",
        "model": "sonnet",
    },
    "research": {
        "cognitive_function": "RESEARCH",
        "description": "Systematic information discovery and evaluation",
        "color": "blue",
        "model": "sonnet",
    },
    "analysis": {
        "cognitive_function": "ANALYSIS",
        "description": "Decompose complexity and identify patterns",
        "color": "green",
        "model": "opus",
    },
    "synthesis": {
        "cognitive_function": "SYNTHESIS",
        "description": "Integrate disparate information into coherent designs",
        "color": "magenta",
        "model": "opus",
    },
    "generation": {
        "cognitive_function": "GENERATION",
        "description": "Create artifacts using domain-appropriate creation cycles",
        "color": "yellow",
        "model": "sonnet",
    },
    "validation": {
        "cognitive_function": "VALIDATION",
        "description": "Systematically verify artifacts against criteria",
        "color": "red",
        "model": "sonnet",
    },
    "memory": {
        "cognitive_function": "METACOGNITION",
        "description": "Metacognitive monitor for impasse detection and remediation",
        "color": "purple",
        "model": "haiku",
    },
}


# Backwards compatibility: map old names to new canonical names
AGENT_NAME_ALIASES: Final[Dict[str, str]] = {
    "clarification-agent": "clarification",
    "research-agent": "research",
    "analysis-agent": "analysis",
    "synthesis-agent": "synthesis",
    "generation-agent": "generation",
    "validation-agent": "validation",
    "goal-memory-agent": "memory",
}


# Context budget configuration (based on ACT-R buffer constraints)
AGENT_CONTEXT_BUDGETS: Final[Dict[str, Dict]] = {
    "clarification": {
        "max_input_tokens": 2000,
        "max_output_tokens": 1500,
        "priority_sections": ["task_description", "user_query", "unknowns"],
    },
    "research": {
        "max_input_tokens": 3000,
        "max_output_tokens": 2500,
        "priority_sections": ["research_queries", "unknowns", "constraints"],
    },
    "analysis": {
        "max_input_tokens": 2500,
        "max_output_tokens": 2000,
        "priority_sections": ["research_findings", "constraints", "trade_offs"],
    },
    "synthesis": {
        "max_input_tokens": 3000,
        "max_output_tokens": 2500,
        "priority_sections": ["analysis_output", "constraints", "design_decisions"],
    },
    "generation": {
        "max_input_tokens": 4000,
        "max_output_tokens": 8000,
        "priority_sections": ["specification", "design", "constraints"],
    },
    "validation": {
        "max_input_tokens": 2500,
        "max_output_tokens": 1500,
        "priority_sections": ["artifact", "criteria", "constraints"],
    },
    "memory": {
        "max_input_tokens": 1500,
        "max_output_tokens": 800,
        "priority_sections": ["agent_output_summary", "previous_goal_state"],
    },
}


def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent name to canonical short form.

    Args:
        agent_name: Agent name (may include -agent suffix)

    Returns:
        Canonical agent name
    """
    return AGENT_NAME_ALIASES.get(agent_name, agent_name)


def get_agent_config(agent_name: str) -> Optional[Dict]:
    """
    Get configuration for a specific agent.

    Args:
        agent_name: Agent name

    Returns:
        Agent configuration dict or None if not found
    """
    normalized = normalize_agent_name(agent_name)
    return AGENT_REGISTRY.get(normalized)


def get_agent_budget(agent_name: str) -> Dict:
    """
    Get context budget configuration for an agent.

    Args:
        agent_name: Agent name

    Returns:
        Context budget configuration
    """
    normalized = normalize_agent_name(agent_name)
    return AGENT_CONTEXT_BUDGETS.get(
        normalized,
        {
            "max_input_tokens": 2500,
            "max_output_tokens": 2000,
            "priority_sections": [],
        },
    )


def get_all_agent_names() -> List[str]:
    """
    Get list of all canonical agent names.

    Returns:
        List of agent names
    """
    return list(AGENT_REGISTRY.keys())


def is_valid_agent(agent_name: str) -> bool:
    """
    Check if an agent name is valid.

    Args:
        agent_name: Agent name to check

    Returns:
        True if valid agent
    """
    normalized = normalize_agent_name(agent_name)
    return normalized in AGENT_REGISTRY
