"""
Domain Classifier Unit Tests

Tests for task domain classification.
"""

import pytest


@pytest.mark.unit
class TestTaskDomain:
    """Tests for TaskDomain enum."""

    def test_has_all_domains(self):
        """TaskDomain should have all expected domains."""
        from orchestration.outer_loop.gather.domain_classifier import TaskDomain

        expected = [
            "CODING",
            "CORRESPONDENCE",
            "RESEARCH",
            "DOCUMENT",
            "SOCIAL",
            "CREATIVE",
            "PERSONAL",
            "PROFESSIONAL",
            "TECHNICAL_OPS",
            "DATA",
            "GENERAL",
        ]

        for domain in expected:
            assert hasattr(TaskDomain, domain)

    def test_domain_values_are_lowercase(self):
        """Domain values should be lowercase."""
        from orchestration.outer_loop.gather.domain_classifier import TaskDomain

        for domain in TaskDomain:
            assert domain.value == domain.value.lower()


@pytest.mark.unit
class TestClassifyDomain:
    """Tests for classify_domain function."""

    def test_returns_tuple(self):
        """classify_domain should return (domain, confidence) tuple."""
        from orchestration.outer_loop.gather.domain_classifier import classify_domain

        result = classify_domain("test query")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_coding_keywords(self):
        """Should classify coding-related queries as CODING."""
        from orchestration.outer_loop.gather.domain_classifier import (
            classify_domain,
            TaskDomain,
        )

        queries = [
            "implement a function to sort arrays",
            "fix the bug in the authentication code",
            "refactor the API endpoint",
            "write unit tests for the module",
            "build a REST API",
        ]

        for query in queries:
            domain, _ = classify_domain(query)
            assert domain == TaskDomain.CODING, f"Failed for: {query}"

    def test_correspondence_keywords(self):
        """Should classify email/message queries as CORRESPONDENCE."""
        from orchestration.outer_loop.gather.domain_classifier import (
            classify_domain,
            TaskDomain,
        )

        queries = [
            "write an email to my manager",
            "draft a reply to John",
            "compose a message",
            "respond to this email with thanks",
        ]

        for query in queries:
            domain, _ = classify_domain(query)
            assert domain == TaskDomain.CORRESPONDENCE, f"Failed for: {query}"

    def test_research_keywords(self):
        """Should classify research queries as RESEARCH."""
        from orchestration.outer_loop.gather.domain_classifier import (
            classify_domain,
            TaskDomain,
        )

        queries = [
            "research best practices for microservices",
            "investigate the performance issue",
            "compare different database options",
            "find out how to implement caching",
        ]

        for query in queries:
            domain, _ = classify_domain(query)
            assert domain == TaskDomain.RESEARCH, f"Failed for: {query}"

    def test_general_fallback(self):
        """Should return GENERAL for unrecognized queries."""
        from orchestration.outer_loop.gather.domain_classifier import (
            classify_domain,
            TaskDomain,
        )

        result, confidence = classify_domain("xyz abc 123")

        assert result == TaskDomain.GENERAL
        assert confidence == 0.3  # Low confidence for fallback

    def test_confidence_range(self):
        """Confidence should be between 0 and 1."""
        from orchestration.outer_loop.gather.domain_classifier import classify_domain

        queries = [
            "implement a complex API with authentication",
            "write",
            "xyz",
            "research the best practices for code review",
        ]

        for query in queries:
            _, confidence = classify_domain(query)
            assert 0.0 <= confidence <= 1.0, f"Bad confidence for: {query}"

    def test_longer_keywords_have_more_weight(self):
        """Multi-word keywords should contribute more to score."""
        from orchestration.outer_loop.gather.domain_classifier import (
            classify_domain,
            TaskDomain,
        )

        # "machine learning" should push toward DATA
        domain, _ = classify_domain("I need to train a machine learning model")

        assert domain == TaskDomain.DATA


@pytest.mark.unit
class TestGetDomainDescription:
    """Tests for get_domain_description function."""

    def test_returns_string(self):
        """Should return a string description."""
        from orchestration.outer_loop.gather.domain_classifier import (
            get_domain_description,
            TaskDomain,
        )

        for domain in TaskDomain:
            desc = get_domain_description(domain)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_descriptions_are_unique(self):
        """Each domain should have a unique description."""
        from orchestration.outer_loop.gather.domain_classifier import (
            get_domain_description,
            TaskDomain,
        )

        descriptions = [get_domain_description(d) for d in TaskDomain]

        assert len(set(descriptions)) == len(descriptions)

    def test_coding_description(self):
        """CODING domain should have appropriate description."""
        from orchestration.outer_loop.gather.domain_classifier import (
            get_domain_description,
            TaskDomain,
        )

        desc = get_domain_description(TaskDomain.CODING)

        assert "software" in desc.lower() or "programming" in desc.lower()
