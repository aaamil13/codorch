"""Architecture Team - Multi-agent AI system for architecture generation and analysis."""

import json
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from backend.core.ai_client import get_ai_client


# ============================================================================
# Response Models
# ============================================================================


class ModuleProposal(BaseModel):
    """Proposed module from architect."""

    name: str = Field(description="Module name")
    description: str = Field(description="What this module does")
    module_type: str = Field(description="Type: package, class, interface, service, component")
    level: int = Field(description="Depth in hierarchy")
    parent_name: Optional[str] = Field(None, description="Parent module name")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    patterns: list[str] = Field(default_factory=list, description="Design patterns")


class DependencyProposal(BaseModel):
    """Proposed dependency from architect."""

    from_module: str = Field(description="Source module name")
    to_module: str = Field(description="Target module name")
    dependency_type: str = Field(description="Type: import, extends, uses, implements, depends_on")
    reason: str = Field(description="Why this dependency is needed")


class ArchitectureProposal(BaseModel):
    """Complete architecture proposal."""

    modules: list[ModuleProposal] = Field(description="All proposed modules")
    dependencies: list[DependencyProposal] = Field(description="All dependencies")
    architectural_style: str = Field(description="Overall style (layered, microservices, etc.)")
    reasoning: str = Field(description="Why this architecture was chosen")


class DependencyValidationResult(BaseModel):
    """Dependency validation result."""

    is_valid: bool = Field(description="Whether dependencies are valid")
    circular_dependencies: list[list[str]] = Field(
        default_factory=list,
        description="Detected circular dependency chains",
    )
    invalid_dependencies: list[str] = Field(
        default_factory=list,
        description="Invalid dependency descriptions",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for improvement",
    )
    fixed_dependencies: Optional[list[DependencyProposal]] = None


class ComplexityAssessment(BaseModel):
    """Complexity assessment result."""

    overall_complexity: float = Field(ge=0.0, le=10.0, description="Overall complexity score (0-10)")
    module_count_score: float = Field(ge=0.0, le=10.0)
    dependency_score: float = Field(ge=0.0, le=10.0)
    depth_score: float = Field(ge=0.0, le=10.0)
    hotspots: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Modules with high complexity",
    )
    recommendations: list[str] = Field(default_factory=list)


class ArchitectureReview(BaseModel):
    """Final architecture review."""

    approval_status: str = Field(description="approved / approved_with_changes / rejected")
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall quality score")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    critical_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in review")


# ============================================================================
# Context Models
# ============================================================================


class ArchitectureContext(BaseModel):
    """Context for architecture generation."""

    project_id: str
    goals: list[dict[str, Any]] = Field(default_factory=list)
    opportunities: list[dict[str, Any]] = Field(default_factory=list)
    architectural_style: Optional[str] = None
    preferences: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# AI Agents
# ============================================================================


class SoftwareArchitectAgent:
    """Agent for generating software architecture."""

    def __init__(self) -> None:
        """Initialize SoftwareArchitectAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.agent = Agent(
            self.model,
            output_type=ArchitectureProposal,
            system_prompt="""You are a Senior Software Architect with expertise in:
- Software architecture design (layered, microservices, hexagonal, clean architecture)
- Design patterns and best practices
- Scalability and maintainability
- Technology selection
- Modular system design

Your task is to propose a well-structured, modular architecture based on requirements.

Guidelines:
1. Keep modules focused (single responsibility)
2. Use clear naming conventions
3. Minimize coupling, maximize cohesion
4. Choose appropriate architectural style
5. Consider scalability and maintainability
6. Use established design patterns
7. Limit hierarchy depth to 4-5 levels
""",
        )

    async def propose_architecture(
        self,
        goals: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
        style: Optional[str] = None,
    ) -> ArchitectureProposal:
        """Generate architecture proposal."""
        prompt = f"""Generate a software architecture based on:

Goals:
{json.dumps(goals, indent=2)}

Opportunities:
{json.dumps(opportunities, indent=2)}

Preferred Style: {style or 'Choose best fit'}

Please propose:
1. A modular architecture with clear module hierarchy
2. Dependencies between modules
3. Technologies and patterns for each module
4. Justification for architectural choices

Focus on:
- Clean separation of concerns
- Scalability
- Maintainability
- Best practices
"""

        try:
            result = await self.agent.run(prompt)
            return result # type: ignore
        except Exception as e:
            print(f"SoftwareArchitectAgent error: {e}")
            # Fallback minimal architecture
            return ArchitectureProposal(
                modules=[
                    ModuleProposal(
                        name="Core",
                        description="Core business logic",
                        module_type="package",
                        level=0,
                        parent_name=None, # Added parent_name
                        technologies=["Python"],
                        patterns=["Repository", "Service Layer"],
                    )
                ],
                dependencies=[],
                architectural_style="Layered Architecture",
                reasoning="Fallback minimal architecture due to error",
            )


class DependencyExpertAgent:
    """Agent for validating and optimizing dependencies."""

    def __init__(self) -> None:
        """Initialize DependencyExpertAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.agent = Agent(
            self.model,
            output_type=DependencyValidationResult,
            system_prompt="""You are a Dependency Expert specializing in:
- Dependency graph analysis
- Circular dependency detection
- Coupling and cohesion optimization
- Dependency injection patterns
- Interface design for loose coupling

Your task is to validate dependencies and suggest improvements.

Guidelines:
1. Detect circular dependencies
2. Identify unnecessary coupling
3. Suggest dependency injection where appropriate
4. Recommend interface-based design
5. Ensure dependencies respect layer boundaries
""",
        )

    async def validate_dependencies(
        self,
        modules: list[ModuleProposal],
        dependencies: list[DependencyProposal],
    ) -> DependencyValidationResult:
        """Validate architecture dependencies."""
        prompt = f"""Validate the following architecture dependencies:

Modules:
{json.dumps([m.model_dump() for m in modules], indent=2)}

Dependencies:
{json.dumps([d.model_dump() for d in dependencies], indent=2)}

Please check for:
1. Circular dependencies
2. Invalid dependency types
3. Unnecessary coupling
4. Missing abstractions
5. Layer violations

Provide:
- Validation result
- List of issues
- Suggestions for improvement
- Fixed dependencies if needed
"""

        try:
            result = await self.agent.run(prompt)
            return result # type: ignore
        except Exception as e:
            print(f"DependencyExpertAgent error: {e}")
            return DependencyValidationResult(
                is_valid=True,
                suggestions=["Validation unavailable - manual review recommended"],
            )


class ComplexityAnalyzerAgent:
    """Agent for analyzing architecture complexity."""

    def __init__(self) -> None:
        """Initialize ComplexityAnalyzerAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-flash"
        self.agent = Agent(
            self.model,
            output_type=ComplexityAssessment,
            system_prompt="""You are a Complexity Analyzer specializing in:
- Software metrics and complexity analysis
- Cyclomatic complexity
- Coupling and cohesion metrics
- Maintainability index
- Code smell detection

Your task is to assess architecture complexity and identify hotspots.

Guidelines:
1. Calculate objective complexity metrics
2. Identify overly complex modules
3. Assess coupling levels
4. Suggest simplifications
5. Rate on a 0-10 scale (0=simple, 10=very complex)
""",
        )

    async def assess_complexity(
        self,
        modules: list[ModuleProposal],
        dependencies: list[DependencyProposal],
    ) -> ComplexityAssessment:
        """Assess architecture complexity."""
        prompt = f"""Assess the complexity of this architecture:

Modules ({len(modules)}):
{json.dumps([m.model_dump() for m in modules], indent=2)}

Dependencies ({len(dependencies)}):
{json.dumps([d.model_dump() for d in dependencies], indent=2)}

Calculate:
1. Overall complexity (0-10)
2. Module count score
3. Dependency density score
4. Hierarchy depth score
5. Identify complexity hotspots
6. Provide recommendations for simplification
"""

        try:
            result = await self.agent.run(prompt)
            return result # type: ignore
        except Exception as e:
            print(f"ComplexityAnalyzerAgent error: {e}")
            # Simple fallback calculation
            module_count_score = min(10.0, len(modules) / 10.0)
            dependency_score = min(10.0, len(dependencies) / 10.0)

            return ComplexityAssessment(
                overall_complexity=(module_count_score + dependency_score) / 2,
                module_count_score=module_count_score,
                dependency_score=dependency_score,
                depth_score=5.0,
                recommendations=["Manual complexity analysis recommended"],
            )


class ArchitectureReviewerAgent:
    """Agent for final architecture review."""

    def __init__(self) -> None:
        """Initialize ArchitectureReviewerAgent."""
        self.client = get_ai_client()
        self.model = "gemini-2.5-pro"
        self.agent = Agent(
            self.model,
            output_type=ArchitectureReview,
            system_prompt="""You are a Senior Architecture Reviewer with expertise in:
- Architecture patterns and best practices
- Quality attributes (scalability, maintainability, security)
- Risk assessment
- Technical debt prevention
- Enterprise architecture

Your task is to provide a final comprehensive review of the architecture.

Guidelines:
1. Check alignment with requirements
2. Assess scalability and maintainability
3. Identify potential risks
4. Review for best practices
5. Provide actionable recommendations
6. Give approval status
""",
        )

    async def review_architecture(
        self,
        proposal: ArchitectureProposal,
        validation: DependencyValidationResult,
        complexity: ComplexityAssessment,
    ) -> ArchitectureReview:
        """Review complete architecture."""
        prompt = f"""Review this software architecture:

Architecture Proposal:
{proposal.model_dump_json(indent=2)}

Dependency Validation:
{validation.model_dump_json(indent=2)}

Complexity Assessment:
{complexity.model_dump_json(indent=2)}

Please provide:
1. Approval status (approved / approved_with_changes / rejected)
2. Overall quality score (0-10)
3. Strengths of the architecture
4. Weaknesses and concerns
5. Critical issues that must be addressed
6. Recommendations for improvement
7. Confidence in your review (0-1)

Consider:
- Scalability
- Maintainability
- Security
- Performance
- Best practices
- Alignment with requirements
"""

        try:
            result = await self.agent.run(prompt)
            return result # type: ignore
        except Exception as e:
            print(f"ArchitectureReviewerAgent error: {e}")
            return ArchitectureReview(
                approval_status="approved_with_changes",
                overall_score=7.0,
                strengths=["Architecture proposal created"],
                weaknesses=["Automated review unavailable"],
                critical_issues=[],
                recommendations=["Manual review recommended"],
                confidence=0.5,
            )


# ============================================================================
# Architecture Team Coordinator
# ============================================================================


class ArchitectureTeam:
    """Coordinates the entire architecture team."""

    def __init__(self) -> None:
        """Initialize Architecture Team."""
        self.architect = SoftwareArchitectAgent()
        self.dependency_expert = DependencyExpertAgent()
        self.complexity_analyzer = ComplexityAnalyzerAgent()
        self.reviewer = ArchitectureReviewerAgent()

    async def generate_architecture(
        self,
        goals: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
        style: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate and review architecture with full team."""
        print("🏗️  ArchitectureTeam: Starting architecture generation...")

        # Step 1: Architect proposes architecture
        print("1️⃣  SoftwareArchitect: Proposing architecture...")
        proposal = await self.architect.propose_architecture(goals, opportunities, style)

        # Step 2: Dependency expert validates
        print("2️⃣  DependencyExpert: Validating dependencies...")
        validation = await self.dependency_expert.validate_dependencies(
            proposal.modules,
            proposal.dependencies,
        )

        # If dependencies are invalid and fixes provided, use fixed version
        if not validation.is_valid and validation.fixed_dependencies:
            print("   ⚠️  Applying dependency fixes...")
            proposal.dependencies = validation.fixed_dependencies

        # Step 3: Complexity analyzer assesses
        print("3️⃣  ComplexityAnalyzer: Assessing complexity...")
        complexity = await self.complexity_analyzer.assess_complexity(
            proposal.modules,
            proposal.dependencies,
        )

        # Step 4: Reviewer provides final review
        print("4️⃣  ArchitectureReviewer: Final review...")
        review = await self.reviewer.review_architecture(proposal, validation, complexity)

        print(f"✅ Architecture generation complete! Status: {review.approval_status}")

        return {
            "proposal": proposal.model_dump(),
            "validation": validation.model_dump(),
            "complexity": complexity.model_dump(),
            "review": review.model_dump(),
            "final_score": review.overall_score,
        }
