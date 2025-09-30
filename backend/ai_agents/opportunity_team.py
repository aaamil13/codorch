"""Opportunity AI Team - Multi-agent system for opportunity generation."""

from typing import Optional

from pydantic import BaseModel, Field

from backend.core.ai_client import get_advanced_ai_client, get_ai_client
from backend.core.config import settings


# Pydantic models for AI responses


class OpportunityIdea(BaseModel):
    """Single opportunity idea."""

    title: str
    description: str
    category: str
    target_market: str
    value_proposition: str
    estimated_effort: str
    estimated_timeline: str
    innovation_level: str
    reasoning: str


class GeneratorResult(BaseModel):
    """Result from idea generator."""

    ideas: list[OpportunityIdea]
    creativity_score: float
    generator_type: str


class AnalysisResult(BaseModel):
    """Result from analyzer."""

    opportunity_id: int
    feasibility_analysis: str
    impact_analysis: str
    risks: list[str]
    strengths: list[str]
    score: float


class SupervisorDecision(BaseModel):
    """Supervisor's final decision."""

    approved_ideas: list[int]
    rejected_ideas: list[int]
    feedback: dict[int, str]
    reasoning: str


# AI Agents


class CreativeIdeaGenerator:
    """
    Creative Idea Generator Agent.

    High temperature, focuses on innovative and bold ideas.
    """

    def __init__(self) -> None:
        """Initialize creative generator."""
        self.ai_client = get_ai_client()
        self.temperature = 0.9  # High creativity

    async def generate_ideas(self, context: str, goal: Optional[str], num_ideas: int = 5) -> GeneratorResult:
        """Generate creative opportunity ideas."""
        system_prompt = """You are a highly creative innovation consultant.

Think boldly and outside the box. Focus on:
- Disruptive approaches
- Blue ocean strategies
- Emerging trends
- Unconventional combinations
- Novel applications

Be creative and ambitious. Feasibility will be checked later."""

        user_message = f"""Generate {num_ideas} creative business opportunities.

Context: {context}
{f"Goal: {goal}" if goal else ""}

For each opportunity provide:
- Title (catchy, clear)
- Description (2-3 sentences)
- Category
- Target market
- Unique value proposition
- Estimated effort (small/medium/large)
- Timeline (weeks/months)
- Innovation level (incremental/moderate/breakthrough)
- Reasoning (why this is a good opportunity)

Focus on CREATIVE and INNOVATIVE ideas."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=self.temperature, max_tokens=2000
            )

            content = self.ai_client.extract_text_from_completion(response)
            ideas = self._parse_ideas(content)

            return GeneratorResult(ideas=ideas, creativity_score=8.5, generator_type="creative")

        except Exception:
            # Fallback
            return GeneratorResult(
                ideas=[
                    OpportunityIdea(
                        title="AI-Powered Solution",
                        description="Innovative AI-based approach",
                        category="technology",
                        target_market="Tech-savvy users",
                        value_proposition="Automation and efficiency",
                        estimated_effort="medium",
                        estimated_timeline="3-6 months",
                        innovation_level="moderate",
                        reasoning="Leverages emerging AI technology",
                    )
                ],
                creativity_score=5.0,
                generator_type="creative",
            )

    def _parse_ideas(self, content: str) -> list[OpportunityIdea]:
        """Parse ideas from AI response (simplified)."""
        # Simple parsing - in production use structured output
        ideas = []
        lines = content.split("\n")

        current_idea = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_idea and "title" in current_idea:
                    ideas.append(
                        OpportunityIdea(
                            title=current_idea.get("title", "Opportunity")[:100],
                            description=current_idea.get("description", "Innovative opportunity")[:500],
                            category=current_idea.get("category", "business")[:50],
                            target_market=current_idea.get("target_market", "General market")[:200],
                            value_proposition=current_idea.get("value_proposition", "Value creation")[:300],
                            estimated_effort=current_idea.get("estimated_effort", "medium")[:50],
                            estimated_timeline=current_idea.get("estimated_timeline", "3 months")[:50],
                            innovation_level=current_idea.get("innovation_level", "moderate")[:50],
                            reasoning=current_idea.get("reasoning", "Strategic opportunity")[:300],
                        )
                    )
                    current_idea = {}

            if ":" in line and len(line) < 200:
                key, value = line.split(":", 1)
                key_lower = key.lower().strip()
                if "title" in key_lower:
                    current_idea["title"] = value.strip()
                elif "description" in key_lower:
                    current_idea["description"] = value.strip()
                elif "category" in key_lower:
                    current_idea["category"] = value.strip()
                elif "market" in key_lower:
                    current_idea["target_market"] = value.strip()
                elif "value" in key_lower or "proposition" in key_lower:
                    current_idea["value_proposition"] = value.strip()
                elif "effort" in key_lower:
                    current_idea["estimated_effort"] = value.strip()
                elif "timeline" in key_lower:
                    current_idea["estimated_timeline"] = value.strip()
                elif "innovation" in key_lower:
                    current_idea["innovation_level"] = value.strip()
                elif "reasoning" in key_lower:
                    current_idea["reasoning"] = value.strip()

        return (
            ideas[:5]
            if ideas
            else [
                OpportunityIdea(
                    title="Generated Opportunity",
                    description="AI-generated opportunity",
                    category="business",
                    target_market="Market segment",
                    value_proposition="Value delivery",
                    estimated_effort="medium",
                    estimated_timeline="3 months",
                    innovation_level="moderate",
                    reasoning="Strategic fit",
                )
            ]
        )


class StructuredIdeaGenerator:
    """
    Structured Idea Generator Agent.

    Lower temperature, focuses on practical and structured ideas.
    """

    def __init__(self) -> None:
        """Initialize structured generator."""
        self.ai_client = get_ai_client()
        self.temperature = 0.5  # Balanced

    async def generate_ideas(self, context: str, goal: Optional[str], num_ideas: int = 5) -> GeneratorResult:
        """Generate structured opportunity ideas."""
        system_prompt = """You are a strategic business consultant.

Focus on:
- Practical and achievable approaches
- Market-validated strategies
- Risk-managed opportunities
- Clear execution paths
- Proven business models

Provide structured, realistic opportunities."""

        user_message = f"""Generate {num_ideas} structured business opportunities.

Context: {context}
{f"Goal: {goal}" if goal else ""}

For each opportunity provide structured details following best practices.
Focus on PRACTICAL and ACHIEVABLE ideas."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=self.temperature, max_tokens=2000
            )

            content = self.ai_client.extract_text_from_completion(response)
            ideas = self._parse_ideas(content)

            return GeneratorResult(ideas=ideas, creativity_score=6.0, generator_type="structured")

        except Exception:
            return GeneratorResult(
                ideas=[],
                creativity_score=5.0,
                generator_type="structured",
            )

    def _parse_ideas(self, content: str) -> list[OpportunityIdea]:
        """Parse ideas from AI response."""
        # Reuse parsing logic from CreativeGenerator
        generator = CreativeIdeaGenerator()
        return generator._parse_ideas(content)


class OpportunityAnalyzer:
    """
    Opportunity Analyzer Agent.

    Analyzes generated opportunities for feasibility and impact.
    """

    def __init__(self) -> None:
        """Initialize analyzer."""
        self.ai_client = get_advanced_ai_client()  # Use advanced model

    async def analyze_opportunity(self, opportunity: OpportunityIdea, opportunity_id: int) -> AnalysisResult:
        """Analyze a single opportunity."""
        system_prompt = """You are an expert business analyst.

Analyze opportunities for:
- Feasibility (technical and market)
- Potential impact (revenue, market, growth)
- Risks and challenges
- Strengths and advantages
- Overall viability score (0-10)

Provide objective, data-driven analysis."""

        user_message = f"""Analyze this opportunity:

Title: {opportunity.title}
Description: {opportunity.description}
Target Market: {opportunity.target_market}
Value Proposition: {opportunity.value_proposition}
Estimated Effort: {opportunity.estimated_effort}
Timeline: {opportunity.estimated_timeline}

Provide:
1. Feasibility analysis
2. Impact analysis
3. Key risks (list)
4. Key strengths (list)
5. Overall score (0-10)"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=0.3, max_tokens=1000
            )

            content = self.ai_client.extract_text_from_completion(response)

            return AnalysisResult(
                opportunity_id=opportunity_id,
                feasibility_analysis=self._extract_section(content, "feasibility"),
                impact_analysis=self._extract_section(content, "impact"),
                risks=self._extract_list(content, "risks"),
                strengths=self._extract_list(content, "strengths"),
                score=self._extract_score(content),
            )

        except Exception:
            return AnalysisResult(
                opportunity_id=opportunity_id,
                feasibility_analysis="Analysis pending",
                impact_analysis="Analysis pending",
                risks=["To be determined"],
                strengths=["To be determined"],
                score=6.0,
            )

    def _extract_section(self, content: str, section: str) -> str:
        """Extract a section from content."""
        lines = content.lower().split("\n")
        for i, line in enumerate(lines):
            if section in line:
                if i + 1 < len(lines):
                    return lines[i + 1].strip()[:500]
        return f"{section.capitalize()} analysis"

    def _extract_list(self, content: str, section: str) -> list[str]:
        """Extract list items from content."""
        items = []
        lines = content.split("\n")
        in_section = False

        for line in lines:
            if section.lower() in line.lower():
                in_section = True
                continue
            if in_section and (line.strip().startswith("-") or line.strip().startswith("•")):
                items.append(line.strip("- •").strip())
            elif in_section and items:
                break

        return items[:5] if items else ["To be determined"]

    def _extract_score(self, content: str) -> float:
        """Extract score from content."""
        # Look for patterns like "score: 8.5" or "8.5/10"
        import re

        matches = re.findall(r"score[:\s]+(\d+\.?\d*)", content.lower())
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                pass

        matches = re.findall(r"(\d+\.?\d*)/10", content)
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                pass

        return 6.5  # Default


class SupervisorAgent:
    """
    Supervisor Agent.

    Makes final decisions on which opportunities to approve.
    """

    def __init__(self) -> None:
        """Initialize supervisor."""
        self.ai_client = get_advanced_ai_client()

    async def review_opportunities(
        self, ideas: list[OpportunityIdea], analyses: list[AnalysisResult]
    ) -> SupervisorDecision:
        """Review and make final decisions."""
        system_prompt = """You are a senior executive making strategic decisions.

Review opportunities and analyses to decide:
- Which opportunities to approve
- Which to reject
- Provide specific feedback
- Overall strategic reasoning

Be selective and strategic."""

        # Build summary
        summary = "Opportunities for review:\n\n"
        for i, (idea, analysis) in enumerate(zip(ideas, analyses)):
            summary += f"{i+1}. {idea.title}\n"
            summary += f"   Score: {analysis.score}/10\n"
            summary += f"   Feasibility: {analysis.feasibility_analysis[:100]}...\n"
            summary += f"   Impact: {analysis.impact_analysis[:100]}...\n\n"

        user_message = f"""{summary}

Decide which opportunities to:
1. APPROVE (list numbers)
2. REJECT (list numbers)
3. Provide feedback for each
4. Overall strategic reasoning"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self.ai_client.create_completion_with_retry(
                messages=messages, temperature=0.4, max_tokens=1200
            )

            content = self.ai_client.extract_text_from_completion(response)

            # Default: approve ideas with score >= 7.0
            approved = [i for i, a in enumerate(analyses) if a.score >= 7.0]
            rejected = [i for i, a in enumerate(analyses) if a.score < 7.0]

            return SupervisorDecision(
                approved_ideas=approved,
                rejected_ideas=rejected,
                feedback={i: f"Score: {analyses[i].score}" for i in range(len(ideas))},
                reasoning="Selected based on feasibility and impact scores",
            )

        except Exception:
            # Default approval logic
            approved = [i for i, a in enumerate(analyses) if a.score >= 7.0]
            rejected = [i for i in range(len(analyses)) if i not in approved]

            return SupervisorDecision(
                approved_ideas=approved,
                rejected_ideas=rejected,
                feedback={},
                reasoning="Automated approval based on scores",
            )
