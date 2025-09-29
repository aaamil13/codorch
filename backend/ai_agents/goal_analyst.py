"""Goal Analyst AI Agent using Pydantic AI."""

from typing import Optional

from pydantic import BaseModel, Field

from backend.core.ai_client import get_ai_client, get_advanced_ai_client
from backend.core.config import settings


class GoalAnalysisResult(BaseModel):
    """Result of goal analysis."""

    is_smart_compliant: bool = Field(..., description="Whether goal meets SMART criteria")
    specific_feedback: str = Field(..., description="Feedback on specificity")
    measurable_feedback: str = Field(..., description="Feedback on measurability")
    achievable_feedback: str = Field(..., description="Feedback on achievability")
    relevant_feedback: str = Field(..., description="Feedback on relevance")
    time_bound_feedback: str = Field(..., description="Feedback on time constraints")
    overall_feedback: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class MetricSuggestion(BaseModel):
    """Suggested metric for goal."""

    name: str
    description: str
    target_value: Optional[float] = None
    unit: Optional[str] = None


class SubgoalSuggestion(BaseModel):
    """Suggested subgoal."""

    title: str
    description: str
    priority: str
    estimated_duration: Optional[str] = None


class GoalAnalystAgent:
    """
    AI Agent for analyzing and improving goals.

    Uses AI to validate SMART criteria and provide actionable feedback.
    """

    def __init__(self, use_advanced_model: bool = False) -> None:
        """Initialize agent."""
        if use_advanced_model:
            self.ai_client = get_advanced_ai_client()
        else:
            self.ai_client = get_ai_client()

    async def analyze_goal(
        self,
        title: str,
        description: Optional[str],
        category: Optional[str],
        target_date: Optional[str],
    ) -> GoalAnalysisResult:
        """
        Analyze goal for SMART compliance.

        Args:
            title: Goal title
            description: Goal description
            category: Goal category
            target_date: Target completion date

        Returns:
            Analysis result with feedback and suggestions
        """
        system_prompt = """You are an expert business goal analyst specializing in SMART goal methodology.

Analyze goals for:
- Specific: Is the goal clear and unambiguous?
- Measurable: Can progress be measured?
- Achievable: Is it realistic given typical constraints?
- Relevant: Does it align with business objectives?
- Time-bound: Is there a clear timeline?

Provide constructive, actionable feedback."""

        user_message = f"""Analyze this business goal:

Title: {title}
Description: {description or "Not provided"}
Category: {category or "Not specified"}
Target Date: {target_date or "Not specified"}

Provide:
1. Feedback on each SMART criterion
2. Overall assessment (is it SMART compliant?)
3. Specific suggestions for improvement
4. Strengths and weaknesses
5. Keep feedback concise and actionable"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=0.3, max_tokens=1500
            )

            content = self.ai_client.extract_text_from_completion(response)

            # Parse AI response (simple parsing)
            return self._parse_analysis_response(content)

        except Exception as e:
            # Fallback response
            return GoalAnalysisResult(
                is_smart_compliant=False,
                specific_feedback="Unable to analyze due to error",
                measurable_feedback="Unable to analyze due to error",
                achievable_feedback="Unable to analyze due to error",
                relevant_feedback="Unable to analyze due to error",
                time_bound_feedback="Unable to analyze due to error",
                overall_feedback=[f"Error during analysis: {str(e)}"],
                suggestions=["Please check the goal details and try again"],
                strengths=[],
                weaknesses=[],
            )

    def _parse_analysis_response(self, content: str) -> GoalAnalysisResult:
        """Parse AI response into structured format."""
        # Simple parsing logic
        lines = content.strip().split("\n")

        result = GoalAnalysisResult(
            is_smart_compliant="smart compliant" in content.lower()
            or "meets smart" in content.lower(),
            specific_feedback=self._extract_criterion_feedback(content, "specific"),
            measurable_feedback=self._extract_criterion_feedback(content, "measurable"),
            achievable_feedback=self._extract_criterion_feedback(content, "achievable"),
            relevant_feedback=self._extract_criterion_feedback(content, "relevant"),
            time_bound_feedback=self._extract_criterion_feedback(content, "time"),
            overall_feedback=[line.strip("- ") for line in lines if line.strip().startswith("-")][
                :3
            ],
            suggestions=self._extract_section(content, "suggestion"),
            strengths=self._extract_section(content, "strength"),
            weaknesses=self._extract_section(content, "weakness"),
        )

        return result

    def _extract_criterion_feedback(self, content: str, criterion: str) -> str:
        """Extract feedback for specific SMART criterion."""
        lines = content.lower().split("\n")
        for i, line in enumerate(lines):
            if criterion in line and ":" in line:
                # Get the feedback part
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()
                # Try next line
                if i + 1 < len(lines):
                    return lines[i + 1].strip()

        return f"{criterion.capitalize()} criterion needs review"

    def _extract_section(self, content: str, section_name: str) -> list[str]:
        """Extract list items from a section."""
        items = []
        lines = content.split("\n")
        in_section = False

        for line in lines:
            line_lower = line.lower()
            if section_name in line_lower:
                in_section = True
                continue

            if in_section:
                if line.strip().startswith("-") or line.strip().startswith("•"):
                    items.append(line.strip("- •").strip())
                elif line.strip() and not line[0].isalpha():
                    continue
                elif items and line.strip():  # New section
                    break

        return items[:5]  # Limit to 5 items

    async def suggest_metrics(
        self, title: str, description: Optional[str], category: Optional[str]
    ) -> list[MetricSuggestion]:
        """
        Suggest relevant metrics for goal.

        Args:
            title: Goal title
            description: Goal description
            category: Goal category

        Returns:
            List of suggested metrics
        """
        system_prompt = """You are an expert in defining business metrics and KPIs.
Suggest 3-5 relevant, measurable metrics for the given goal."""

        user_message = f"""Suggest metrics for this goal:

Title: {title}
Description: {description or "Not provided"}
Category: {category or "Not specified"}

Provide 3-5 specific, measurable metrics with:
- Metric name
- Description
- Target value (if applicable)
- Unit of measurement"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=0.4, max_tokens=800
            )

            content = self.ai_client.extract_text_from_completion(response)
            return self._parse_metrics(content)

        except Exception:
            # Fallback metrics
            return [
                MetricSuggestion(
                    name="Progress Percentage",
                    description="Overall completion percentage",
                    target_value=100.0,
                    unit="%",
                )
            ]

    def _parse_metrics(self, content: str) -> list[MetricSuggestion]:
        """Parse metrics from AI response."""
        # Simple parsing
        metrics = []
        lines = content.split("\n")

        current_metric = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("-") or line.startswith("•") or line[0].isdigit():
                # New metric
                if current_metric:
                    metrics.append(current_metric)
                metric_text = line.strip("- •0123456789. ")
                current_metric = MetricSuggestion(
                    name=metric_text[:50],
                    description=metric_text,
                )

        if current_metric:
            metrics.append(current_metric)

        return metrics[:5]

    async def decompose_goal(
        self, title: str, description: Optional[str], num_subgoals: int = 3
    ) -> list[SubgoalSuggestion]:
        """
        Decompose goal into subgoals.

        Args:
            title: Goal title
            description: Goal description
            num_subgoals: Number of subgoals to generate

        Returns:
            List of suggested subgoals
        """
        system_prompt = """You are an expert in breaking down complex goals into actionable subgoals.
Create logical, sequential subgoals that lead to achieving the main goal."""

        user_message = f"""Break down this goal into {num_subgoals} subgoals:

Main Goal: {title}
Description: {description or "Not provided"}

For each subgoal provide:
- Title (clear, specific)
- Description (detailed)
- Priority (high, medium, low)
- Estimated duration"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=0.5, max_tokens=1200
            )

            content = self.ai_client.extract_text_from_completion(response)
            return self._parse_subgoals(content)

        except Exception:
            # Fallback
            return [
                SubgoalSuggestion(
                    title=f"Subgoal for: {title}",
                    description="Define specific steps to achieve this goal",
                    priority="medium",
                )
            ]

    def _parse_subgoals(self, content: str) -> list[SubgoalSuggestion]:
        """Parse subgoals from AI response."""
        # Simple parsing
        subgoals = []
        lines = content.split("\n")

        current_subgoal = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if (
                line.startswith("-")
                or line.startswith("•")
                or (line[0].isdigit() and "." in line[:3])
            ):
                # New subgoal
                if current_subgoal:
                    subgoals.append(current_subgoal)

                title_text = line.strip("- •0123456789. ")
                current_subgoal = SubgoalSuggestion(
                    title=title_text[:100],
                    description=title_text,
                    priority="medium",
                )

        if current_subgoal:
            subgoals.append(current_subgoal)

        return subgoals[:5]
