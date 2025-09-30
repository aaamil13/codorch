"""AI Agents for Requirements Module (Module 5)."""

from pydantic import BaseModel, Field
from pydantic_ai import Agent


# ============================================================================
# Output Models
# ============================================================================


class RequirementAnalysis(BaseModel):
    """Analysis result from RequirementsAnalystAgent."""

    completeness_score: float = Field(ge=0.0, le=10.0)
    clarity_score: float = Field(ge=0.0, le=10.0)
    consistency_score: float = Field(ge=0.0, le=10.0)
    feasibility_score: float = Field(ge=0.0, le=10.0)
    issues: list[dict[str, str]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    improved_description: str = Field(default="")
    recommended_acceptance_criteria: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Validation result from RequirementsValidatorAgent."""

    is_valid: bool
    overall_score: float = Field(ge=0.0, le=10.0)
    critical_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TechnologyRecommendations(BaseModel):
    """Technology recommendations from TechnologyAdvisorAgent."""

    recommendations: list[dict[str, any]] = Field(default_factory=list)
    reasoning: str
    alternatives_considered: list[str] = Field(default_factory=list)


# ============================================================================
# AI Agents
# ============================================================================


# Requirements Analyst Agent
requirements_analyst_agent = Agent(
    "google-gla:gemini-2.0-flash-001",
    result_type=RequirementAnalysis,
    system_prompt="""You are an expert Requirements Analyst specializing in software requirements engineering.

Your responsibilities:
1. Analyze requirement completeness - check if all necessary information is present
2. Evaluate clarity - ensure requirements are unambiguous and understandable
3. Check consistency - verify requirements don't contradict each other
4. Assess feasibility - determine if requirements are technically achievable
5. Identify issues and provide actionable suggestions
6. Generate acceptance criteria when missing

Scoring Guidelines:
- Completeness (0-10): Has all necessary details (what, why, who, constraints)
- Clarity (0-10): Clear, unambiguous, no vague terms
- Consistency (0-10): Doesn't contradict other requirements or itself
- Feasibility (0-10): Technically possible with reasonable effort

For each issue, provide:
- Type: completeness/clarity/consistency/feasibility
- Severity: critical/warning/info
- Message: Clear description of the issue
- Suggestion: Specific actionable recommendation

Be thorough but constructive. Focus on helping improve the requirement.""",
)


# Requirements Validator Agent
requirements_validator_agent = Agent(
    "google-gla:gemini-2.0-flash-001",
    result_type=ValidationResult,
    system_prompt="""You are a Requirements Validation Expert responsible for final quality checks.

Your responsibilities:
1. Perform comprehensive validation of requirements
2. Identify critical issues that must be fixed before approval
3. Flag warnings that should be addressed
4. Provide recommendations for improvement
5. Make final pass/fail decision

Validation Criteria:
- Overall score >= 7.0 to pass
- No critical issues for approval
- Must have clear acceptance criteria
- Must be testable and verifiable
- Must have sufficient detail for implementation

Critical Issues (fail validation):
- Missing essential information
- Contradictory requirements
- Technically impossible requirements
- Security vulnerabilities
- Missing acceptance criteria for functional requirements

Warnings (pass but recommend fixing):
- Vague language
- Missing edge cases
- Performance concerns not specified
- Missing non-functional requirements

Be strict but fair. Safety and quality are paramount.""",
)


# Technology Advisor Agent
technology_advisor_agent = Agent(
    "google-gla:gemini-2.0-flash-001",
    result_type=TechnologyRecommendations,
    system_prompt="""You are a Technology Advisor specializing in recommending suitable technologies for software requirements.

Your responsibilities:
1. Analyze requirements to understand technical needs
2. Recommend appropriate technologies (languages, frameworks, libraries, databases, tools)
3. Provide suitability scores (0-10) with reasoning
4. Consider popularity, learning curve, and ecosystem
5. Suggest alternatives with pros/cons
6. Ensure recommendations are practical and well-supported

Recommendation Format:
{
    "technology_type": "framework|library|database|language|tool",
    "name": "Technology name",
    "version": "Recommended version",
    "suitability_score": 0-10,
    "reasoning": "Why this technology fits",
    "popularity_score": 0-10,
    "learning_curve_score": 0-10 (higher = easier),
    "pros": ["advantage 1", "advantage 2"],
    "cons": ["limitation 1", "limitation 2"]
}

Consider:
- Requirement complexity and scale
- Team expertise (assume intermediate level if not specified)
- Project timeline
- Maintenance and long-term support
- Community and ecosystem
- Performance requirements
- Security considerations

Be pragmatic. Recommend proven, well-supported technologies over bleeding-edge.""",
)


# ============================================================================
# Helper Functions
# ============================================================================


async def analyze_requirement(
    requirement_title: str,
    requirement_description: str,
    requirement_type: str,
    acceptance_criteria: list[str],
) -> RequirementAnalysis:
    """Analyze requirement quality."""
    context = f"""
Requirement Type: {requirement_type}
Title: {requirement_title}
Description: {requirement_description}
Current Acceptance Criteria: {', '.join(acceptance_criteria) if acceptance_criteria else 'None'}

Analyze this requirement thoroughly and provide detailed feedback.
"""
    
    result = await requirements_analyst_agent.run(context)
    return result.data


async def validate_requirement_quality(
    requirement_title: str,
    requirement_description: str,
    requirement_type: str,
    analysis: RequirementAnalysis,
) -> ValidationResult:
    """Validate requirement is ready for approval."""
    context = f"""
Requirement Type: {requirement_type}
Title: {requirement_title}
Description: {requirement_description}

Previous Analysis:
- Completeness Score: {analysis.completeness_score}/10
- Clarity Score: {analysis.clarity_score}/10
- Consistency Score: {analysis.consistency_score}/10
- Feasibility Score: {analysis.feasibility_score}/10
- Issues Found: {len(analysis.issues)}

Perform final validation and determine if this requirement is ready for approval.
"""
    
    result = await requirements_validator_agent.run(context)
    return result.data


async def recommend_technologies(
    requirements_summary: str,
    module_context: str,
    preferences: dict,
) -> TechnologyRecommendations:
    """Get technology recommendations based on requirements."""
    prefs_str = ", ".join([f"{k}: {v}" for k, v in preferences.items()]) if preferences else "None specified"
    
    context = f"""
Module Context: {module_context}

Requirements Summary:
{requirements_summary}

User Preferences: {prefs_str}

Analyze the requirements and recommend appropriate technologies for implementation.
Provide at least 3-5 recommendations covering different technology categories.
"""
    
    result = await technology_advisor_agent.run(context)
    return result.data


# ============================================================================
# Requirements Team (Coordinator)
# ============================================================================


class RequirementsTeam:
    """Coordinator for Requirements AI team."""

    @staticmethod
    async def full_analysis_workflow(
        requirement_title: str,
        requirement_description: str,
        requirement_type: str,
        acceptance_criteria: list[str],
    ) -> dict:
        """Run complete analysis workflow."""
        # Step 1: Analyze
        analysis = await analyze_requirement(
            requirement_title,
            requirement_description,
            requirement_type,
            acceptance_criteria,
        )

        # Step 2: Validate
        validation = await validate_requirement_quality(
            requirement_title,
            requirement_description,
            requirement_type,
            analysis,
        )

        return {
            "analysis": analysis,
            "validation": validation,
            "overall_score": (
                analysis.completeness_score
                + analysis.clarity_score
                + analysis.consistency_score
                + analysis.feasibility_score
            )
            / 4,
            "is_ready_for_approval": validation.is_valid,
        }

    @staticmethod
    async def technology_recommendation_workflow(
        project_requirements: list[dict],
        module_name: str,
        preferences: dict,
    ) -> TechnologyRecommendations:
        """Generate technology recommendations."""
        # Build summary
        summary_parts = []
        for req in project_requirements:
            summary_parts.append(f"- [{req['type']}] {req['title']}: {req['description'][:100]}")

        requirements_summary = "\n".join(summary_parts[:10])  # Limit to 10 requirements

        module_context = f"Module: {module_name}, Total Requirements: {len(project_requirements)}"

        return await recommend_technologies(
            requirements_summary,
            module_context,
            preferences,
        )
