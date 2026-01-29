"""
Unit tests for agents/config.py
"""

import pytest

from orchestration.agents.config import (
    AGENT_REGISTRY,
    AGENT_NAME_ALIASES,
    normalize_agent_name,
    get_agent_config,
    get_agent_budget,
    get_all_agent_names,
    is_valid_agent,
)


class TestAgentRegistry:
    """Tests for AGENT_REGISTRY configuration."""

    def test_all_agents_present(self):
        """All 7 agents should be in registry."""
        expected_agents = [
            "clarification",
            "research",
            "analysis",
            "synthesis",
            "generation",
            "validation",
            "memory",
        ]
        for agent in expected_agents:
            assert agent in AGENT_REGISTRY

    def test_agent_has_required_fields(self):
        """Each agent should have required fields."""
        required_fields = ["cognitive_function", "description", "color", "model"]

        for agent_name, config in AGENT_REGISTRY.items():
            for field in required_fields:
                assert field in config, f"{agent_name} missing {field}"

    def test_model_values_valid(self):
        """Model values should be valid."""
        valid_models = ["sonnet", "opus", "haiku"]

        for agent_name, config in AGENT_REGISTRY.items():
            assert config["model"] in valid_models, f"{agent_name} has invalid model"


class TestNormalizeAgentName:
    """Tests for normalize_agent_name function."""

    def test_canonical_name_unchanged(self):
        """Canonical names should be unchanged."""
        assert normalize_agent_name("research") == "research"
        assert normalize_agent_name("clarification") == "clarification"

    def test_alias_normalized(self):
        """Aliases should be normalized to canonical names."""
        assert normalize_agent_name("research-agent") == "research"
        assert normalize_agent_name("clarification-agent") == "clarification"
        assert normalize_agent_name("goal-memory-agent") == "memory"

    def test_unknown_name_unchanged(self):
        """Unknown names should be unchanged."""
        assert normalize_agent_name("unknown") == "unknown"


class TestGetAgentConfig:
    """Tests for get_agent_config function."""

    def test_valid_agent(self):
        """Should return config for valid agent."""
        config = get_agent_config("research")
        assert config is not None
        assert config["cognitive_function"] == "RESEARCH"

    def test_alias_agent(self):
        """Should return config for alias."""
        config = get_agent_config("research-agent")
        assert config is not None
        assert config["cognitive_function"] == "RESEARCH"

    def test_invalid_agent(self):
        """Should return None for invalid agent."""
        assert get_agent_config("nonexistent") is None


class TestGetAgentBudget:
    """Tests for get_agent_budget function."""

    def test_valid_agent(self):
        """Should return budget for valid agent."""
        budget = get_agent_budget("generation")
        assert budget["max_input_tokens"] == 4000
        assert budget["max_output_tokens"] == 8000

    def test_invalid_agent_gets_default(self):
        """Should return default budget for invalid agent."""
        budget = get_agent_budget("nonexistent")
        assert budget["max_input_tokens"] == 2500
        assert budget["max_output_tokens"] == 2000


class TestGetAllAgentNames:
    """Tests for get_all_agent_names function."""

    def test_returns_all_names(self):
        """Should return all canonical agent names."""
        names = get_all_agent_names()
        assert len(names) == 7
        assert "research" in names
        assert "clarification" in names
        assert "memory" in names


class TestIsValidAgent:
    """Tests for is_valid_agent function."""

    def test_valid_canonical_name(self):
        """Should return True for canonical names."""
        assert is_valid_agent("research") is True
        assert is_valid_agent("clarification") is True

    def test_valid_alias(self):
        """Should return True for aliases."""
        assert is_valid_agent("research-agent") is True
        assert is_valid_agent("goal-memory-agent") is True

    def test_invalid_name(self):
        """Should return False for invalid names."""
        assert is_valid_agent("nonexistent") is False
        assert is_valid_agent("invalid-agent") is False
