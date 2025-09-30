"""Scoring logic for opportunities."""

from typing import Optional


class OpportunityScorer:
    """
    Scorer for opportunities.

    Evaluates opportunities on multiple dimensions:
    - Feasibility: How realistic is implementation
    - Impact: Potential business impact
    - Innovation: Level of novelty/innovation
    - Resources: Availability of required resources
    """

    @staticmethod
    def score_feasibility(
        description: Optional[str],
        estimated_effort: Optional[str],
        required_resources: Optional[dict],
    ) -> float:
        """
        Score feasibility (0-10).

        Criteria:
        - Has description: +2
        - Effort defined: +3
        - Resources defined: +3
        - Realistic indicators: +2
        """
        score = 5.0  # Base score

        # Has description
        if description and len(description) > 50:
            score += 2.0

        # Effort estimation
        if estimated_effort:
            effort_lower = estimated_effort.lower()
            if any(word in effort_lower for word in ["small", "low", "minimal", "quick"]):
                score += 3.0
            elif any(word in effort_lower for word in ["medium", "moderate"]):
                score += 2.0
            elif any(word in effort_lower for word in ["large", "high", "significant"]):
                score += 1.0

        # Resources defined
        if required_resources and len(required_resources) > 0:
            score += 1.0

        # Realistic indicators in description
        if description:
            desc_lower = description.lower()
            realistic_words = [
                "existing",
                "available",
                "proven",
                "established",
                "current",
                "ready",
            ]
            if any(word in desc_lower for word in realistic_words):
                score += 1.0

        return min(score, 10.0)

    @staticmethod
    def score_impact(
        description: Optional[str], target_market: Optional[str], value_proposition: Optional[str]
    ) -> float:
        """
        Score potential impact (0-10).

        Criteria:
        - Clear value proposition: +4
        - Defined target market: +3
        - Impact words in description: +3
        """
        score = 3.0  # Base score

        # Value proposition
        if value_proposition and len(value_proposition) > 30:
            score += 4.0

        # Target market
        if target_market and len(target_market) > 20:
            score += 3.0

        # Impact indicators
        text = (description or "") + " " + (value_proposition or "")
        impact_words = [
            "revenue",
            "growth",
            "profit",
            "market share",
            "customer",
            "scale",
            "expand",
            "increase",
            "improve",
            "optimize",
        ]
        if any(word in text.lower() for word in impact_words):
            score += 2.0

        return min(score, 10.0)

    @staticmethod
    def score_innovation(
        description: Optional[str], category: Optional[str], value_proposition: Optional[str]
    ) -> float:
        """
        Score innovation level (0-10).

        Criteria:
        - Innovation keywords: +5
        - Unique approach: +3
        - Category novelty: +2
        """
        score = 4.0  # Base score

        text = (description or "") + " " + (value_proposition or "")
        text_lower = text.lower()

        # Innovation keywords
        innovation_words = [
            "new",
            "innovative",
            "novel",
            "unique",
            "disruptive",
            "breakthrough",
            "cutting-edge",
            "revolutionary",
            "first",
            "pioneer",
        ]
        innovation_count = sum(1 for word in innovation_words if word in text_lower)
        score += min(innovation_count * 1.5, 5.0)

        # Technology indicators
        tech_words = ["ai", "ml", "blockchain", "cloud", "automation", "algorithm"]
        if any(word in text_lower for word in tech_words):
            score += 1.0

        return min(score, 10.0)

    @staticmethod
    def score_resources(required_resources: Optional[dict], estimated_effort: Optional[str]) -> float:
        """
        Score resource availability (0-10).

        Criteria:
        - Low resource requirements: +5
        - Clear resource definition: +3
        - Leverages existing resources: +2
        """
        score = 5.0  # Base score

        # Effort level (inverse - lower effort = higher score)
        if estimated_effort:
            effort_lower = estimated_effort.lower()
            if any(word in effort_lower for word in ["small", "low", "minimal"]):
                score += 4.0
            elif any(word in effort_lower for word in ["medium", "moderate"]):
                score += 2.0

        # Resource requirements
        if required_resources:
            num_resources = len(required_resources)
            if num_resources <= 3:
                score += 2.0
            elif num_resources <= 5:
                score += 1.0

        return min(score, 10.0)

    @classmethod
    def calculate_overall_score(
        cls,
        description: Optional[str],
        category: Optional[str],
        target_market: Optional[str],
        value_proposition: Optional[str],
        estimated_effort: Optional[str],
        required_resources: Optional[dict],
    ) -> dict[str, float]:
        """
        Calculate all scores.

        Returns dict with individual scores and overall score.
        """
        feasibility = cls.score_feasibility(description, estimated_effort, required_resources)
        impact = cls.score_impact(description, target_market, value_proposition)
        innovation = cls.score_innovation(description, category, value_proposition)
        resources = cls.score_resources(required_resources, estimated_effort)

        # Weighted average (impact and feasibility more important)
        overall = feasibility * 0.3 + impact * 0.35 + innovation * 0.20 + resources * 0.15

        return {
            "feasibility_score": round(feasibility, 2),
            "impact_score": round(impact, 2),
            "innovation_score": round(innovation, 2),
            "resource_score": round(resources, 2),
            "overall_score": round(overall, 2),
        }
