"""
Domain Classifier

Classifies user tasks into domains for appropriate state gathering.
Each domain has specific state requirements and gathering strategies.
"""

from enum import Enum
from typing import List, Tuple


class TaskDomain(Enum):
    """
    Task domain classification.

    Each domain has specific state requirements:
    - CODING: Project structure, git status, dependencies, test coverage
    - CORRESPONDENCE: Draft content, recipient context, thread history, tone
    - RESEARCH: Prior research, sources, knowledge gaps
    - DOCUMENT: Existing content, format requirements, templates
    - SOCIAL: Platform, audience, brand voice, constraints
    - CREATIVE: Style references, constraints, target audience
    - PERSONAL: Personal context, preferences, history
    - PROFESSIONAL: Work context, stakeholders, deadlines
    - TECHNICAL_OPS: System state, configurations, logs
    - DATA: Datasets, schemas, pipelines
    - GENERAL: Fallback for unclassified tasks
    """

    CODING = "coding"
    CORRESPONDENCE = "correspondence"  # Emails, chats, replies
    RESEARCH = "research"
    DOCUMENT = "document"
    SOCIAL = "social"
    CREATIVE = "creative"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    TECHNICAL_OPS = "technical_ops"
    DATA = "data"
    GENERAL = "general"


# Keywords that suggest each domain
DOMAIN_KEYWORDS: dict[TaskDomain, List[str]] = {
    TaskDomain.CODING: [
        "code",
        "implement",
        "function",
        "class",
        "api",
        "endpoint",
        "bug",
        "fix",
        "test",
        "refactor",
        "build",
        "deploy",
        "git",
        "commit",
        "merge",
        "branch",
        "module",
        "package",
        "library",
        "framework",
        "database",
        "query",
        "sql",
        "python",
        "javascript",
        "typescript",
        "rust",
        "go",
        "java",
        "script",
        "cli",
        "backend",
        "frontend",
        "server",
        "client",
    ],
    TaskDomain.CORRESPONDENCE: [
        "email",
        "write to",
        "reply",
        "respond",
        "message",
        "draft",
        "letter",
        "memo",
        "chat",
        "slack",
        "teams",
        "send",
        "cc",
        "bcc",
        "subject line",
        "recipient",
        "dear",
        "sincerely",
        "regards",
        "thanks",
        "follow up",
        "follow-up",
    ],
    TaskDomain.RESEARCH: [
        "research",
        "investigate",
        "explore",
        "find out",
        "learn about",
        "understand",
        "compare",
        "analyze",
        "study",
        "survey",
        "review",
        "best practices",
        "how does",
        "what is",
        "explain",
        "alternatives",
        "options",
        "tradeoffs",
        "trade-offs",
        "pros and cons",
    ],
    TaskDomain.DOCUMENT: [
        "document",
        "documentation",
        "readme",
        "guide",
        "tutorial",
        "manual",
        "spec",
        "specification",
        "wiki",
        "write up",
        "writeup",
        "report",
        "article",
        "blog post",
        "blog",
        "content",
        "markdown",
        "format",
    ],
    TaskDomain.SOCIAL: [
        "tweet",
        "post",
        "social media",
        "linkedin",
        "twitter",
        "facebook",
        "instagram",
        "tiktok",
        "youtube",
        "caption",
        "hashtag",
        "viral",
        "engagement",
        "followers",
        "audience",
        "brand",
    ],
    TaskDomain.CREATIVE: [
        "creative",
        "story",
        "poem",
        "narrative",
        "fiction",
        "design",
        "logo",
        "art",
        "visual",
        "aesthetic",
        "brainstorm",
        "idea",
        "concept",
        "imagination",
        "inspiration",
    ],
    TaskDomain.PERSONAL: [
        "personal",
        "my",
        "i want",
        "i need",
        "help me",
        "advice",
        "recommend",
        "suggestion",
        "opinion",
        "preference",
        "lifestyle",
        "hobby",
        "plan my",
    ],
    TaskDomain.PROFESSIONAL: [
        "professional",
        "work",
        "job",
        "career",
        "meeting",
        "presentation",
        "proposal",
        "client",
        "stakeholder",
        "project",
        "deadline",
        "milestone",
        "deliverable",
        "business",
        "company",
        "team",
        "manager",
    ],
    TaskDomain.TECHNICAL_OPS: [
        "deploy",
        "server",
        "infrastructure",
        "docker",
        "kubernetes",
        "k8s",
        "aws",
        "azure",
        "gcp",
        "cloud",
        "devops",
        "ci/cd",
        "pipeline",
        "monitoring",
        "logs",
        "metrics",
        "alert",
        "incident",
        "troubleshoot",
        "debug",
        "config",
        "configuration",
        "environment",
        "production",
        "staging",
    ],
    TaskDomain.DATA: [
        "data",
        "dataset",
        "csv",
        "json",
        "xml",
        "schema",
        "etl",
        "pipeline",
        "transform",
        "clean",
        "visualize",
        "chart",
        "graph",
        "analytics",
        "statistics",
        "ml",
        "machine learning",
        "model",
        "train",
        "predict",
    ],
}


def classify_domain(user_query: str) -> Tuple[TaskDomain, float]:
    """
    Classify user query into a task domain.

    Uses keyword matching with confidence scoring.
    Returns most likely domain with confidence score.

    Args:
        user_query: The user's task description

    Returns:
        Tuple of (TaskDomain, confidence_score)
        Confidence is 0.0-1.0, higher is more confident
    """
    query_lower = user_query.lower()

    # Score each domain
    scores: dict[TaskDomain, int] = {domain: 0 for domain in TaskDomain}

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                # Longer keywords get more weight
                scores[domain] += len(keyword.split())

    # Find best match
    max_score = max(scores.values())

    if max_score == 0:
        # No keywords matched, return GENERAL with low confidence
        return (TaskDomain.GENERAL, 0.3)

    # Get domain with highest score
    best_domain = max(scores.keys(), key=lambda d: scores[d])

    # Calculate confidence based on score relative to query length
    # More matches relative to query length = higher confidence
    query_words = len(query_lower.split())
    confidence = min(1.0, max_score / (query_words * 0.5))

    return (best_domain, confidence)


def get_domain_description(domain: TaskDomain) -> str:
    """
    Get human-readable description of domain.

    Args:
        domain: The task domain

    Returns:
        Description string for the domain
    """
    descriptions = {
        TaskDomain.CODING: "Software development and programming tasks",
        TaskDomain.CORRESPONDENCE: "Written communication (emails, messages, replies)",
        TaskDomain.RESEARCH: "Information gathering and analysis",
        TaskDomain.DOCUMENT: "Documentation and technical writing",
        TaskDomain.SOCIAL: "Social media content creation",
        TaskDomain.CREATIVE: "Creative and artistic work",
        TaskDomain.PERSONAL: "Personal assistance and advice",
        TaskDomain.PROFESSIONAL: "Professional and business tasks",
        TaskDomain.TECHNICAL_OPS: "DevOps and infrastructure operations",
        TaskDomain.DATA: "Data processing and analysis",
        TaskDomain.GENERAL: "General-purpose task",
    }
    return descriptions.get(domain, "Unknown domain")
