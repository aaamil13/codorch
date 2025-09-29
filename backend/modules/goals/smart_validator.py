"""SMART validation logic for goals."""

from datetime import datetime
from typing import Optional


class SMARTValidator:
    """
    Validator for SMART goals.

    SMART stands for:
    - Specific: Clear and unambiguous
    - Measurable: Can track progress
    - Achievable: Realistic given constraints
    - Relevant: Aligns with objectives
    - Time-bound: Has a deadline
    """

    @staticmethod
    def validate_specific(title: str, description: Optional[str]) -> float:
        """
        Validate if goal is specific.

        Scoring criteria:
        - Has clear title: +3 points
        - Has description: +2 points
        - Description length > 50 chars: +2 points
        - Contains action verbs: +3 points
        """
        score = 0.0

        # Check title
        if title and len(title.strip()) > 0:
            score += 3.0

        # Check description
        if description and len(description.strip()) > 0:
            score += 2.0

            if len(description.strip()) > 50:
                score += 2.0

        # Check for action verbs (simple heuristic)
        action_verbs = [
            "create",
            "build",
            "develop",
            "implement",
            "design",
            "improve",
            "increase",
            "decrease",
            "achieve",
            "deliver",
            "launch",
            "establish",
        ]

        text = (title + " " + (description or "")).lower()
        if any(verb in text for verb in action_verbs):
            score += 3.0

        return min(score, 10.0)

    @staticmethod
    def validate_measurable(
        description: Optional[str], metrics: Optional[dict]
    ) -> float:
        """
        Validate if goal is measurable.

        Scoring criteria:
        - Has metrics defined: +5 points
        - Each metric with target value: +1 point (max 5)
        - Description contains numbers: +2 points
        """
        score = 0.0

        # Check metrics
        if metrics:
            if isinstance(metrics, dict):
                score += 5.0
                # Check for target values in metrics
                if "metrics" in metrics and isinstance(metrics["metrics"], list):
                    for metric in metrics["metrics"][:5]:  # Max 5 metrics
                        if "target_value" in metric and metric["target_value"] is not None:
                            score += 1.0
            elif isinstance(metrics, list) and len(metrics) > 0:
                score += 5.0

        # Check for numbers in description
        if description:
            if any(char.isdigit() for char in description):
                score += 2.0

        return min(score, 10.0)

    @staticmethod
    def validate_achievable(
        description: Optional[str], title: str
    ) -> float:
        """
        Validate if goal is achievable.

        Scoring criteria (heuristic-based):
        - Not overly ambitious words: +4 points
        - Realistic timeframe mentioned: +3 points
        - Incremental approach: +3 points
        """
        score = 5.0  # Base score (assume achievable unless proven otherwise)

        text = (title + " " + (description or "")).lower()

        # Check for overly ambitious words (penalize)
        ambitious_words = ["revolution", "transform completely", "eliminate all", "perfect"]
        if any(word in text for word in ambitious_words):
            score -= 2.0

        # Check for realistic indicators
        realistic_words = [
            "incremental",
            "gradual",
            "step",
            "phase",
            "milestone",
            "iteration",
        ]
        if any(word in text for word in realistic_words):
            score += 3.0

        # Check for resource awareness
        resource_words = ["team", "budget", "time", "resources", "capacity"]
        if any(word in text for word in resource_words):
            score += 2.0

        return min(max(score, 0.0), 10.0)

    @staticmethod
    def validate_relevant(
        title: str, description: Optional[str], category: Optional[str]
    ) -> float:
        """
        Validate if goal is relevant.

        Scoring criteria:
        - Has category: +3 points
        - Description explains why/importance: +4 points
        - Aligns with business terms: +3 points
        """
        score = 5.0  # Base score

        # Check category
        if category and len(category.strip()) > 0:
            score += 3.0

        # Check for reasoning/importance in description
        if description:
            importance_words = [
                "because",
                "important",
                "critical",
                "essential",
                "necessary",
                "key",
                "vital",
                "impact",
                "benefit",
            ]
            if any(word in description.lower() for word in importance_words):
                score += 2.0

        return min(score, 10.0)

    @staticmethod
    def validate_time_bound(target_date: Optional[datetime]) -> float:
        """
        Validate if goal is time-bound.

        Scoring criteria:
        - Has target date: +10 points
        - Target date in future: already validated
        """
        if target_date:
            # Check if date is in the future
            if target_date > datetime.utcnow():
                return 10.0
            else:
                return 5.0  # Has date but it's in the past

        return 0.0

    @classmethod
    def validate_goal(
        cls,
        title: str,
        description: Optional[str],
        category: Optional[str],
        target_date: Optional[datetime],
        metrics: Optional[dict],
    ) -> dict[str, float]:
        """
        Perform full SMART validation.

        Returns dict with all scores.
        """
        specific = cls.validate_specific(title, description)
        measurable = cls.validate_measurable(description, metrics)
        achievable = cls.validate_achievable(description, title)
        relevant = cls.validate_relevant(title, description, category)
        time_bound = cls.validate_time_bound(target_date)

        overall = (specific + measurable + achievable + relevant + time_bound) / 5.0

        return {
            "specific_score": round(specific, 2),
            "measurable_score": round(measurable, 2),
            "achievable_score": round(achievable, 2),
            "relevant_score": round(relevant, 2),
            "time_bound_score": round(time_bound, 2),
            "overall_smart_score": round(overall, 2),
            "is_smart_compliant": overall >= 7.0,  # 70% threshold
        }
