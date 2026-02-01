"""
Unit tests for outer_loop/verify/question_aggregator.py

Tests the question bubble-up handler that aggregates questions
from inner loop phases for user clarification.
"""

import json
from pathlib import Path
from typing import List

import pytest


@pytest.fixture
def sample_memory_content_with_questions() -> str:
    """Memory file content with questions in Section 4."""
    return """# Agent Output: generation

## Section 0: Context Loaded
```json
{"verification_status": "PASSED"}
```

## Section 1: Step Overview
Did some work.

## Section 2: Johari Summary
```json
{"open": "info", "hidden": "", "blind": "", "unknown": ""}
```

## Section 3: Downstream Directives
Next agent: validation

## Section 4: User Questions
```json
{
  "clarification_required": true,
  "questions": [
    {
      "id": "Q1",
      "priority": "P0",
      "question": "Should we use REST or GraphQL?",
      "context": "API design decision",
      "options": ["REST", "GraphQL"],
      "discovered_by": "generation",
      "discovery_phase": "inner_loop"
    }
  ],
  "blocking": true
}
```
"""


@pytest.fixture
def sample_memory_content_no_questions() -> str:
    """Memory file content without questions."""
    return """# Agent Output: analysis

## Section 0: Context Loaded
```json
{"verification_status": "PASSED"}
```

## Section 1: Step Overview
Analysis complete.

## Section 2: Johari Summary
```json
{"open": "info", "hidden": "", "blind": "", "unknown": ""}
```

## Section 3: Downstream Directives
Next agent: synthesis

## Section 4: User Questions
```json
{
  "clarification_required": false,
  "questions": [],
  "blocking": false
}
```
"""


@pytest.fixture
def sample_memory_with_p1_questions() -> str:
    """Memory file with P1 priority questions (non-blocking)."""
    return """# Agent Output: research

## Section 4: User Questions
```json
{
  "clarification_required": true,
  "questions": [
    {
      "id": "Q2",
      "priority": "P1",
      "question": "Preferred testing framework?",
      "context": "Testing decision",
      "options": ["pytest", "unittest"],
      "discovered_by": "research",
      "discovery_phase": "inner_loop"
    }
  ],
  "blocking": false
}
```
"""


class TestQuestionAggregatorImport:
    """Tests for question aggregator module import."""

    @pytest.mark.unit
    def test_question_aggregator_exists(self):
        """QuestionAggregator should be importable."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        assert QuestionAggregator is not None

    @pytest.mark.unit
    def test_question_bubble_up_dataclass_exists(self):
        """QuestionBubbleUp dataclass should be importable."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionBubbleUp,
        )

        assert QuestionBubbleUp is not None

    @pytest.mark.unit
    def test_question_aggregator_aggregate_method(self):
        """QuestionAggregator should have aggregate() method."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        assert hasattr(QuestionAggregator, "aggregate")


class TestQuestionBubbleUpDataclass:
    """Tests for QuestionBubbleUp dataclass."""

    @pytest.mark.unit
    def test_question_bubble_up_has_clarification_required(self):
        """QuestionBubbleUp should have clarification_required field."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionBubbleUp,
            Question,
        )

        bubble_up = QuestionBubbleUp(
            clarification_required=True,
            questions=[],
            blocking=False,
        )
        assert bubble_up.clarification_required is True

    @pytest.mark.unit
    def test_question_bubble_up_has_questions(self):
        """QuestionBubbleUp should have questions field."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionBubbleUp,
            Question,
        )

        question = Question(
            id="Q1",
            priority="P0",
            question="Test?",
            context="Test context",
            options=[],
            discovered_by="test",
            discovery_phase="test",
        )
        bubble_up = QuestionBubbleUp(
            clarification_required=True,
            questions=[question],
            blocking=True,
        )
        assert len(bubble_up.questions) == 1

    @pytest.mark.unit
    def test_question_bubble_up_has_blocking(self):
        """QuestionBubbleUp should have blocking field."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionBubbleUp,
        )

        bubble_up = QuestionBubbleUp(
            clarification_required=False,
            questions=[],
            blocking=False,
        )
        assert bubble_up.blocking is False


class TestQuestionAggregatorExtraction:
    """Tests for question extraction from memory files."""

    @pytest.mark.unit
    def test_extracts_questions_from_memory(
        self, tmp_path, sample_memory_content_with_questions
    ):
        """Should extract questions from memory file Section 4."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-gen-memory.md"
        memory_file.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.clarification_required is True
        assert len(result.questions) == 1
        assert result.questions[0].id == "Q1"

    @pytest.mark.unit
    def test_handles_no_questions(self, tmp_path, sample_memory_content_no_questions):
        """Should handle memory files with no questions."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-analysis-memory.md"
        memory_file.write_text(sample_memory_content_no_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.clarification_required is False
        assert len(result.questions) == 0

    @pytest.mark.unit
    def test_handles_empty_file_list(self):
        """Should handle empty memory file list."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([], task_id="test")

        assert result.clarification_required is False
        assert len(result.questions) == 0


class TestQuestionAggregatorDeduplication:
    """Tests for question deduplication."""

    @pytest.mark.unit
    def test_deduplicates_same_question(
        self, tmp_path, sample_memory_content_with_questions
    ):
        """Same question from multiple phases should result in single entry."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        # Create two memory files with same question
        memory1 = tmp_path / "test-gen1-memory.md"
        memory1.write_text(sample_memory_content_with_questions)

        memory2 = tmp_path / "test-gen2-memory.md"
        memory2.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory1, memory2], task_id="test")

        # Should deduplicate based on question ID
        assert len(result.questions) == 1

    @pytest.mark.unit
    def test_keeps_different_questions(
        self,
        tmp_path,
        sample_memory_content_with_questions,
        sample_memory_with_p1_questions,
    ):
        """Different questions should all be kept."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory1 = tmp_path / "test-gen-memory.md"
        memory1.write_text(sample_memory_content_with_questions)

        memory2 = tmp_path / "test-research-memory.md"
        memory2.write_text(sample_memory_with_p1_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory1, memory2], task_id="test")

        assert len(result.questions) == 2


class TestQuestionAggregatorPrioritization:
    """Tests for question priority handling."""

    @pytest.mark.unit
    def test_p0_questions_sorted_first(
        self,
        tmp_path,
        sample_memory_content_with_questions,
        sample_memory_with_p1_questions,
    ):
        """P0 questions should be sorted before P1/P2."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        # P1 question file first
        memory1 = tmp_path / "test-research-memory.md"
        memory1.write_text(sample_memory_with_p1_questions)

        # P0 question file second
        memory2 = tmp_path / "test-gen-memory.md"
        memory2.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory1, memory2], task_id="test")

        # P0 should be first regardless of file order
        assert result.questions[0].priority == "P0"
        assert result.questions[1].priority == "P1"

    @pytest.mark.unit
    def test_p0_question_sets_blocking_true(
        self, tmp_path, sample_memory_content_with_questions
    ):
        """Any P0 question should set blocking=true."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-gen-memory.md"
        memory_file.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.blocking is True

    @pytest.mark.unit
    def test_only_p1_p2_questions_not_blocking(
        self, tmp_path, sample_memory_with_p1_questions
    ):
        """P1/P2 only questions should set blocking=false."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-research-memory.md"
        memory_file.write_text(sample_memory_with_p1_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.blocking is False


class TestQuestionAggregatorContextPreservation:
    """Tests for preserving question context."""

    @pytest.mark.unit
    def test_preserves_discovered_by(
        self, tmp_path, sample_memory_content_with_questions
    ):
        """Should preserve discovered_by field."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-gen-memory.md"
        memory_file.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.questions[0].discovered_by == "generation"

    @pytest.mark.unit
    def test_preserves_discovery_phase(
        self, tmp_path, sample_memory_content_with_questions
    ):
        """Should preserve discovery_phase field."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-gen-memory.md"
        memory_file.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.questions[0].discovery_phase == "inner_loop"

    @pytest.mark.unit
    def test_preserves_options(self, tmp_path, sample_memory_content_with_questions):
        """Should preserve options list."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        memory_file = tmp_path / "test-gen-memory.md"
        memory_file.write_text(sample_memory_content_with_questions)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.questions[0].options == ["REST", "GraphQL"]


class TestQuestionAggregatorEdgeCases:
    """Tests for edge cases in question aggregation."""

    @pytest.mark.unit
    def test_handles_malformed_json(self, tmp_path):
        """Should handle malformed JSON in Section 4."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        malformed_content = """# Agent Output: test

## Section 4: User Questions
```json
{not valid json}
```
"""
        memory_file = tmp_path / "test-memory.md"
        memory_file.write_text(malformed_content)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        # Should handle gracefully, not crash
        assert result.clarification_required is False
        assert len(result.questions) == 0

    @pytest.mark.unit
    def test_handles_missing_section_4(self, tmp_path):
        """Should handle memory files without Section 4."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        content_no_section_4 = """# Agent Output: test

## Section 1: Step Overview
Did work.

## Section 3: Downstream Directives
Next agent.
"""
        memory_file = tmp_path / "test-memory.md"
        memory_file.write_text(content_no_section_4)

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([memory_file], task_id="test")

        assert result.clarification_required is False
        assert len(result.questions) == 0

    @pytest.mark.unit
    def test_handles_nonexistent_file(self, tmp_path):
        """Should handle nonexistent memory files."""
        from orchestration.outer_loop.verify.question_aggregator import (
            QuestionAggregator,
        )

        nonexistent = tmp_path / "does-not-exist.md"

        aggregator = QuestionAggregator()
        result = aggregator.aggregate([nonexistent], task_id="test")

        # Should handle gracefully
        assert result.clarification_required is False
