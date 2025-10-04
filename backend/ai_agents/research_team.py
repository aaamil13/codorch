"""Research Team - Multi-agent AI system for research and analysis."""

import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from backend.core.ai_client import get_ai_client


# ============================================================================
# Response Models
# ============================================================================


class ResearchResponse(BaseModel):
    """Research response from WebResearchAgent."""

    market_trends: list[str] = Field(description="Current market trends")
    competitors: list[str] = Field(description="Key competitors or similar solutions")
    technologies: list[str] = Field(description="Relevant technologies and tools")
    insights: list[str] = Field(description="Key insights and observations")
    sources: list[str] = Field(default_factory=list, description="Source references")


class DomainAnalysis(BaseModel):
    """Domain analysis from DomainExpertAgent."""

    technical_feasibility: str = Field(description="Technical feasibility assessment")
    architecture_recommendations: list[str] = Field(description="Architecture and design recommendations")
    best_practices: list[str] = Field(description="Industry best practices")
    risks: list[str] = Field(description="Potential risks and challenges")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")


class AnalysisResult(BaseModel):
    """Analysis result from AnalyzerAgent."""

    summary: str = Field(description="Synthesized summary")
    key_findings: list[dict[str, Any]] = Field(description="Key findings extracted")
    patterns: list[str] = Field(description="Identified patterns")
    recommendations: list[str] = Field(description="Actionable recommendations")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence")


class ResearchSynthesis(BaseModel):
    """Final synthesis from SupervisorAgent."""

    research_summary: str = Field(description="Overall research summary")
    key_insights: list[str] = Field(description="Most important insights")
    findings: list[dict[str, Any]] = Field(description="Structured findings")
    next_steps: list[str] = Field(description="Recommended next steps")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence")


# ============================================================================
# Research Context
# ============================================================================


class ResearchContext(BaseModel):
    """Context for research session."""

    session_id: str
    query: str
    context_summary: Optional[dict[str, Any]] = None
    previous_messages: list[dict[str, str]] = Field(default_factory=list)
    goal_context: Optional[dict[str, Any]] = None
    opportunity_context: Optional[dict[str, Any]] = None


# ============================================================================
# AI Agents
# ============================================================================


class WebResearchAgent:
    """Agent for web research simulation and trend analysis."""

    def __init__(self) -> None:
        """Initialize WebResearchAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-flash"
        self.agent = Agent(
            self.model,
            output_type=ResearchResponse,
            system_prompt="""You are a Web Research Agent specialized in:
- Market trends and industry analysis
- Competitor research
- Technology landscape assessment
- Industry insights and observations

Your task is to simulate web research and provide comprehensive insights based on the query and context provided.
Focus on current trends, relevant technologies, and market dynamics.
""",
        )

    async def research(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchResponse:
        """Conduct web research simulation."""
        prompt = f"""Research Query: {query}

Context:
{json.dumps(context, indent=2) if context else 'No additional context'}

Please provide comprehensive research insights including:
1. Current market trends
2. Key competitors or similar solutions
3. Relevant technologies and tools
4. Important insights and observations
5. Source references (simulated)
"""

        try:
            result = await self.agent.run(prompt)
            return result  # type: ignore
        except Exception as e:
            print(f"WebResearchAgent error: {e}")
            # Return fallback response
            return ResearchResponse(
                market_trends=["Unable to fetch trends"],
                competitors=["Research unavailable"],
                technologies=["Analysis pending"],
                insights=[f"Error: {str(e)}"],
                sources=[],
            )


class DomainExpertAgent:
    """Agent for domain-specific expertise and technical analysis."""

    def __init__(self) -> None:
        """Initialize DomainExpertAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.agent = Agent(
            self.model,
            output_type=DomainAnalysis,
            system_prompt="""You are a Domain Expert Agent with deep technical knowledge in:
- Software architecture and system design
- Technical feasibility assessment
- Best practices and industry standards
- Risk analysis and mitigation

Your task is to provide expert analysis on technical aspects of the query.
Focus on feasibility, architecture, best practices, and potential risks.
""",
        )

    async def analyze(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        research_data: Optional[ResearchResponse] = None,
    ) -> DomainAnalysis:
        """Provide domain expert analysis."""
        prompt = f"""Query: {query}

Context:
{json.dumps(context, indent=2) if context else 'No additional context'}

Research Data:
{research_data.model_dump_json(indent=2) if research_data else 'No research data available'}

Please provide expert analysis including:
1. Technical feasibility assessment
2. Architecture and design recommendations
3. Industry best practices
4. Potential risks and challenges
5. Confidence score (0-1)
"""

        try:
            result = await self.agent.run(prompt)
            return result  # type: ignore
        except Exception as e:
            print(f"DomainExpertAgent error: {e}")
            return DomainAnalysis(
                technical_feasibility="Analysis unavailable",
                architecture_recommendations=["Expert analysis pending"],
                best_practices=["Standard practices apply"],
                risks=[f"Error: {str(e)}"],
                confidence=0.3,
            )


class AnalyzerAgent:
    """Agent for data synthesis and pattern recognition."""

    def __init__(self) -> None:
        """Initialize AnalyzerAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.agent = Agent(
            self.model,
            output_type=AnalysisResult,
            system_prompt="""You are an Analyzer Agent specialized in:
- Data synthesis and integration
- Pattern recognition
- Insight extraction
- Recommendation generation

Your task is to analyze all collected information and produce:
- Comprehensive summaries
- Key findings
- Identified patterns
- Actionable recommendations
""",
        )

    async def synthesize(
        self,
        query: str,
        research_data: Optional[ResearchResponse] = None,
        domain_analysis: Optional[DomainAnalysis] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AnalysisResult:
        """Synthesize and analyze all collected data."""
        prompt = f"""Query: {query}

Context:
{json.dumps(context, indent=2) if context else 'No context'}

Research Data:
{research_data.model_dump_json(indent=2) if research_data else 'No research data'}

Domain Analysis:
{domain_analysis.model_dump_json(indent=2) if domain_analysis else 'No domain analysis'}

Please synthesize all information and provide:
1. Comprehensive summary
2. Key findings (structured)
3. Identified patterns
4. Actionable recommendations
5. Overall confidence score
"""

        try:
            result = await self.agent.run(prompt)
            return result  # type: ignore
        except Exception as e:
            print(f"AnalyzerAgent error: {e}")
            return AnalysisResult(
                summary="Analysis unavailable",
                key_findings=[],
                patterns=["Pattern analysis pending"],
                recommendations=["Further analysis needed"],
                confidence=0.3,
            )


class SupervisorAgent:
    """Supervisor agent for coordinating research workflow."""

    def __init__(self) -> None:
        """Initialize SupervisorAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.web_researcher = WebResearchAgent()
        self.domain_expert = DomainExpertAgent()
        self.analyzer = AnalyzerAgent()

        self.agent = Agent(
            self.model,
            output_type=ResearchSynthesis,
            system_prompt="""You are a Supervisor Agent responsible for:
- Coordinating the research workflow
- Synthesizing results from all agents
- Ensuring quality and coherence
- Providing final recommendations

Your task is to produce a comprehensive research synthesis that integrates all agent outputs.
""",
        )

    async def coordinate_research(
        self,
        query: str,
        context: ResearchContext,
    ) -> ResearchSynthesis:
        """Coordinate full research workflow."""
        # Step 1: Web Research
        print(f"🌐 WebResearchAgent: Researching '{query}'...")
        research_data = await self.web_researcher.research(
            query=query,
            context=context.context_summary,
        )

        # Step 2: Domain Expert Analysis
        print(f"🎓 DomainExpertAgent: Analyzing...")
        domain_analysis = await self.domain_expert.analyze(
            query=query,
            context=context.context_summary,
            research_data=research_data,
        )

        # Step 3: Data Synthesis
        print(f"📊 AnalyzerAgent: Synthesizing...")
        analysis_result = await self.analyzer.synthesize(
            query=query,
            research_data=research_data,
            domain_analysis=domain_analysis,
            context=context.context_summary,
        )

        # Step 4: Final Synthesis
        print(f"🎯 SupervisorAgent: Creating final synthesis...")
        synthesis_prompt = f"""Query: {query}

Web Research Results:
{research_data.model_dump_json(indent=2)}

Domain Expert Analysis:
{domain_analysis.model_dump_json(indent=2)}

Analyzer Synthesis:
{analysis_result.model_dump_json(indent=2)}

Context:
{json.dumps(context.model_dump(), indent=2)}

Please provide a comprehensive research synthesis that:
1. Summarizes all research findings
2. Highlights key insights
3. Structures findings by type (technical/market/user/competitor)
4. Recommends next steps
5. Provides overall confidence assessment
"""

        try:
            result = await self.agent.run(synthesis_prompt)
            return result  # type: ignore
        except Exception as e:
            print(f"SupervisorAgent error: {e}")
            # Fallback synthesis
            return ResearchSynthesis(
                research_summary=analysis_result.summary,
                key_insights=analysis_result.patterns[:5],
                findings=[
                    {
                        "type": "technical",
                        "title": "Technical Analysis",
                        "description": domain_analysis.technical_feasibility,
                        "confidence": domain_analysis.confidence,
                    }
                ],
                next_steps=analysis_result.recommendations[:3],
                confidence=0.6,
            )


# ============================================================================
# Research Team Coordinator
# ============================================================================


class ResearchTeam:
    """Coordinates the entire research team."""

    def __init__(self) -> None:
        """Initialize Research Team."""
        self.supervisor = SupervisorAgent()

    async def conduct_research(
        self,
        query: str,
        session_id: str,
        context_summary: Optional[dict[str, Any]] = None,
        previous_messages: Optional[list[dict[str, str]]] = None,
    ) -> ResearchSynthesis:
        """Conduct full research with all agents."""
        context = ResearchContext(
            session_id=session_id,
            query=query,
            context_summary=context_summary,
            previous_messages=previous_messages or [],
        )

        return await self.supervisor.coordinate_research(query=query, context=context)
