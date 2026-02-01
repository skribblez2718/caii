"""
Question Aggregator

Aggregates questions from inner loop agent memory files for user clarification.
Implements the question bubble-up mechanism.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Question:
    """Individual question from an agent."""

    id: str
    priority: str  # P0, P1, P2
    question: str
    context: str
    options: List[str] = field(default_factory=list)
    discovered_by: str = ""
    discovery_phase: str = ""


@dataclass
class QuestionBubbleUp:
    """Aggregated questions for bubble-up to user."""

    clarification_required: bool
    questions: List[Question] = field(default_factory=list)
    blocking: bool = False


class QuestionAggregator:
    """
    Aggregates questions from inner loop memory files.

    Parses Section 4 (User Questions) from memory files,
    deduplicates, prioritizes (P0 first), and formats for the orchestrator.
    """

    SECTION_4_PATTERN = re.compile(
        r"## Section 4:.*?```json\s*(.*?)\s*```",
        re.DOTALL | re.IGNORECASE,
    )

    def aggregate(  # pylint: disable=unused-argument
        self,
        memory_files: List[Path],
        task_id: str,
    ) -> QuestionBubbleUp:
        """
        Aggregate questions from memory files.

        Args:
            memory_files: List of memory file paths to parse
            task_id: Task ID for context

        Returns:
            QuestionBubbleUp with aggregated questions
        """
        all_questions: List[Question] = []
        seen_ids: set = set()

        for memory_file in memory_files:
            questions = self._extract_questions_from_file(memory_file)
            for question in questions:
                # Deduplicate by question ID
                if question.id not in seen_ids:
                    seen_ids.add(question.id)
                    all_questions.append(question)

        # Sort by priority (P0 first, then P1, then P2)
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        all_questions.sort(key=lambda q: priority_order.get(q.priority, 3))

        # Determine if blocking (any P0 question)
        blocking = any(q.priority == "P0" for q in all_questions)

        return QuestionBubbleUp(
            clarification_required=len(all_questions) > 0,
            questions=all_questions,
            blocking=blocking,
        )

    def _extract_questions_from_file(self, file_path: Path) -> List[Question]:
        """
        Extract questions from a memory file's Section 4.

        Args:
            file_path: Path to memory file

        Returns:
            List of Question objects
        """
        if not file_path.exists():
            return []

        try:
            content = file_path.read_text()
        except (IOError, OSError):
            return []

        # Find Section 4 JSON
        match = self.SECTION_4_PATTERN.search(content)
        if not match:
            return []

        json_str = match.group(1)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return []

        # Parse questions
        questions: List[Question] = []
        if data.get("clarification_required") and "questions" in data:
            for q_data in data["questions"]:
                questions.append(
                    Question(
                        id=q_data.get("id", ""),
                        priority=q_data.get("priority", "P2"),
                        question=q_data.get("question", ""),
                        context=q_data.get("context", ""),
                        options=q_data.get("options", []),
                        discovered_by=q_data.get("discovered_by", ""),
                        discovery_phase=q_data.get("discovery_phase", ""),
                    )
                )

        return questions
