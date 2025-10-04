"""AI Agents for Code Generation Module (Module 6)."""

from pydantic import BaseModel, Field
from pydantic_ai import Agent


# ============================================================================
# Output Models
# ============================================================================


class ScaffoldOutput(BaseModel):
    """Scaffold generation output."""

    project_structure: dict[str, list[str]] = Field(default_factory=dict)
    files: list[dict[str, str]] = Field(default_factory=list)
    reasoning: str
    patterns_used: list[str] = Field(default_factory=list)


class CodeOutput(BaseModel):
    """Code implementation output."""

    files: list[dict[str, str]] = Field(default_factory=list)
    implementation_notes: str
    dependencies: list[str] = Field(default_factory=list)


class CodeReviewOutput(BaseModel):
    """Code review output."""

    approved: bool
    overall_score: float = Field(ge=0.0, le=10.0)
    quality_issues: list[str] = Field(default_factory=list)
    security_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TestOutput(BaseModel):
    """Test generation output."""

    test_files: list[dict[str, str]] = Field(default_factory=list)
    coverage_estimate: float = Field(ge=0.0, le=100.0)
    test_types: list[str] = Field(default_factory=list)


# ============================================================================
# AI Agents
# ============================================================================


# Code Generator Agent
def get_code_generator_agent():
    return Agent(
        "google-gla:gemini-2.0-flash-001",
        result_type=CodeOutput,
        system_prompt="""You are an expert Software Engineer specialized in generating production-ready code.

Your responsibilities:
1. Generate clean, maintainable code following best practices
2. Implement all specified requirements accurately
3. Follow architectural patterns and design principles
4. Include proper error handling and logging
5. Write self-documenting code with clear variable names
6. Follow language-specific conventions

Code Quality Standards:
- DRY (Don't Repeat Yourself)
- SOLID principles
- Clean Architecture
- Proper separation of concerns
- Type safety where applicable
- Security best practices

For each file, provide:
- file_path: Full path including filename
- language: Programming language
- content: Complete file content

Generate professional, production-ready code.""",
    )


# Code Reviewer Agent
def get_code_reviewer_agent():
    return Agent(
        "google-gla:gemini-2.0-flash-001",
        result_type=CodeReviewOutput,
        system_prompt="""You are a Senior Code Reviewer responsible for quality assurance.

Review Criteria:
1. Code Quality (0-10)
   - Readability and maintainability
   - Proper naming conventions
   - Code organization
   - Comments and documentation

2. Security (Critical)
   - Input validation
   - SQL injection prevention
   - XSS prevention
   - Authentication/authorization
   - Secrets management

3. Performance
   - Efficient algorithms
   - Database query optimization
   - Memory usage
   - Caching strategies

4. Best Practices
   - Error handling
   - Logging
   - Testing hooks
   - Design patterns

Approval Criteria:
- Overall score >= 7.0
- No critical security issues
- No critical quality issues

Provide specific, actionable feedback.""",
    )


# Test Generator Agent
def get_test_generator_agent():
    return Agent(
        "google-gla:gemini-2.0-flash-001",
        result_type=TestOutput,
        system_prompt="""You are a Test Automation Expert specializing in comprehensive test generation.

Your responsibilities:
1. Generate unit tests for all functions/methods
2. Create integration tests for workflows
3. Cover edge cases and error scenarios
4. Include positive and negative test cases
5. Use appropriate mocking strategies
6. Follow testing best practices

Test Types:
- Unit tests: Individual function testing
- Integration tests: Component interaction
- Edge cases: Boundary conditions, null/empty inputs
- Error cases: Exception handling

Test Coverage Goals:
- Aim for 80%+ code coverage
- Test all critical paths
- Test error handling
- Test validation logic

Generate complete, runnable test files with proper setup/teardown.""",
    )


# ============================================================================
# Helper Functions
# ============================================================================


async def generate_scaffold(
    architecture: dict,
    requirements: list[dict],
    tech_stack: list[dict],
) -> ScaffoldOutput:
    """Generate project scaffold."""
    context = f"""
Architecture:
{architecture}

Requirements Summary:
{requirements[:5]}

Technology Stack:
{tech_stack}

Generate a complete project scaffold with file structure and empty/template files.
"""
    agent = get_code_generator_agent()
    result = await agent.run(context)
    return result.data


async def generate_implementation(
    scaffold: dict,
    requirements: list[dict],
    module_context: str,
) -> CodeOutput:
    """Generate full implementation."""
    context = f"""
Project Scaffold:
{scaffold}

Module: {module_context}

Requirements to Implement:
{requirements}

Generate complete implementation code for all files.
Include proper error handling, validation, and documentation.
"""
    agent = get_code_generator_agent()
    result = await agent.run(context)
    return result.data


async def review_code(
    generated_code: dict,
    requirements: list[dict],
) -> CodeReviewOutput:
    """Review generated code quality."""
    context = f"""
Generated Code:
{generated_code}

Requirements:
{requirements}

Perform comprehensive code review focusing on quality, security, and best practices.
"""
    agent = get_code_reviewer_agent()
    result = await agent.run(context)
    return result.data


async def generate_tests(
    code_files: list[dict],
    language: str,
) -> TestOutput:
    """Generate comprehensive tests."""
    context = f"""
Language: {language}

Code Files to Test:
{code_files[:3]}

Generate comprehensive test suite including unit tests, integration tests, and edge cases.
"""
    agent = get_test_generator_agent()
    result = await agent.run(context)
    return result.data


# ============================================================================
# Code Generation Team
# ============================================================================


class CodeGenerationTeam:
    """Coordinator for code generation workflow."""

    @staticmethod
    async def full_generation_workflow(
        architecture: dict,
        requirements: list[dict],
        tech_stack: list[dict],
        language: str = "python",
    ) -> dict:
        """Run complete code generation workflow."""
        # Step 1: Generate Scaffold
        scaffold = await generate_scaffold(architecture, requirements, tech_stack)

        # Step 2: Generate Implementation
        implementation = await generate_implementation(
            scaffold.model_dump(),
            requirements,
            f"Module implementation in {language}",
        )

        # Step 3: Review Code
        review = await review_code(
            implementation.model_dump(),
            requirements,
        )

        # Step 4: Generate Tests (if code approved)
        tests = None
        if review.approved:
            tests = await generate_tests(
                implementation.files,
                language,
            )

        return {
            "scaffold": scaffold,
            "implementation": implementation,
            "review": review,
            "tests": tests,
            "approved": review.approved,
            "overall_score": review.overall_score,
        }
