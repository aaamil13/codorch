diff --git a/AI_AGENTS_SPECIFICATION.md b/AI_AGENTS_SPECIFICATION.md
--- a/AI_AGENTS_SPECIFICATION.md
+++ b/AI_AGENTS_SPECIFICATION.md
@@ -0,0 +1,1087 @@
+# AI Agents Specification
+
+## Overview
+
+Тази система използва multi-agent architecture с Pydantic AI за различни типове задачи. Всеки агент има специфична роля, capability и configuration.
+
+---
+
+## Agent Types & Configurations
+
+### 1. Goal Analyst Agent
+
+**Роля**: Анализ и валидация на бизнес цели
+
+```python
+# ai_agents/goal_analyst.py
+
+from pydantic_ai import Agent
+from pydantic import BaseModel, Field
+from typing import List
+
+class GoalAnalysis(BaseModel):
+    is_smart_compliant: bool
+    specific_score: float = Field(ge=0, le=10)
+    measurable_score: float = Field(ge=0, le=10)
+    achievable_score: float = Field(ge=0, le=10)
+    relevant_score: float = Field(ge=0, le=10)
+    time_bound_score: float = Field(ge=0, le=10)
+    overall_score: float
+    feedback: List[str]
+    suggestions: List[str]
+    suggested_metrics: List[dict]
+    suggested_subgoals: List[str]
+
+goal_analyst = Agent(
+    'openai:gpt-4-turbo',
+    result_type=GoalAnalysis,
+    system_prompt="""
+    You are an expert business goal analyst specializing in SMART goal methodology.
+    
+    Analyze goals for:
+    - Specific: Is the goal clear and unambiguous?
+    - Measurable: Can progress be measured?
+    - Achievable: Is it realistic given typical constraints?
+    - Relevant: Does it align with business objectives?
+    - Time-bound: Is there a clear timeline?
+    
+    Provide actionable feedback and concrete suggestions for improvement.
+    Suggest KPIs and metrics that would track progress.
+    Propose logical subgoals if the goal is too broad.
+    """,
+    model_settings={
+        'temperature': 0.3,  # Lower for analytical tasks
+        'max_tokens': 2000
+    }
+)
+
+@goal_analyst.tool
+def fetch_industry_benchmarks(industry: str) -> str:
+    """Fetch typical metrics and benchmarks for industry"""
+    # Implementation
+    return "Industry benchmark data"
+
+@goal_analyst.tool
+def suggest_similar_goals(goal_description: str) -> List[str]:
+    """Find similar successful goals from database"""
+    # Vector search in past successful goals
+    return ["Similar goal 1", "Similar goal 2"]
+```
+
+**Usage Example**:
+```python
+analysis = await goal_analyst.run(
+    f"""Analyze this business goal:
+    
+    Title: {goal.title}
+    Description: {goal.description}
+    Timeline: {goal.timeline}
+    Industry: {goal.industry}
+    """
+)
+```
+
+---
+
+### 2. Opportunity Generator Team
+
+**Роля**: Генериране на бизнес възможности
+
+#### 2.1 Creative Idea Generator
+
+```python
+# ai_agents/idea_generator.py
+
+class OpportunityIdea(BaseModel):
+    title: str
+    description: str
+    target_market: str
+    unique_value_proposition: str
+    initial_approach: str
+    estimated_timeframe: str
+
+class IdeaGeneratorOutput(BaseModel):
+    ideas: List[OpportunityIdea]
+    creativity_score: float
+    diversity_score: float
+
+creative_generator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=IdeaGeneratorOutput,
+    system_prompt="""
+    You are a highly creative innovation consultant specializing in
+    identifying unique business opportunities.
+    
+    Think:
+    - Outside the box
+    - About emerging trends
+    - Blue ocean strategies
+    - Disruptive approaches
+    - Unconventional combinations
+    
+    Generate diverse ideas that span different market segments,
+    business models, and approaches.
+    
+    Be bold and creative - feasibility will be checked later.
+    """,
+    model_settings={
+        'temperature': 0.9,  # High for creativity
+        'top_p': 0.95
+    }
+)
+
+@creative_generator.tool
+def get_trending_technologies() -> List[str]:
+    """Get list of trending technologies"""
+    return ["AI", "Blockchain", "IoT", "AR/VR"]
+
+@creative_generator.tool
+def get_market_gaps(industry: str) -> List[str]:
+    """Identify market gaps"""
+    return ["Gap 1", "Gap 2"]
+```
+
+#### 2.2 Structured Idea Generator
+
+```python
+structured_generator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=IdeaGeneratorOutput,
+    system_prompt="""
+    You are a structured business strategist who generates
+    well-researched, methodical business opportunities.
+    
+    Focus on:
+    - Proven business models
+    - Clear market demand
+    - Competitive advantage
+    - Scalability
+    - Risk mitigation
+    
+    Generate practical, executable ideas based on sound
+    business principles and market analysis.
+    """,
+    model_settings={
+        'temperature': 0.7  # Moderate for structured thinking
+    }
+)
+
+@structured_generator.tool
+def analyze_market_size(target_market: str) -> dict:
+    """Get market size data"""
+    return {"size": "1B USD", "growth": "15% YoY"}
+
+@structured_generator.tool
+def get_competitor_analysis(industry: str) -> List[dict]:
+    """Analyze competitors"""
+    return [{"name": "Competitor 1", "strengths": [], "weaknesses": []}]
+```
+
+#### 2.3 Opportunity Analyzer
+
+```python
+class OpportunityScoring(BaseModel):
+    opportunity_id: str
+    title: str
+    
+    # Scores
+    feasibility_score: float = Field(ge=0, le=10)
+    market_potential_score: float = Field(ge=0, le=10)
+    competitive_advantage_score: float = Field(ge=0, le=10)
+    resource_requirement_score: float = Field(ge=0, le=10)  # Lower is better
+    time_to_market_score: float = Field(ge=0, le=10)
+    innovation_score: float = Field(ge=0, le=10)
+    
+    # Weighted overall
+    overall_score: float
+    
+    # Analysis
+    strengths: List[str]
+    weaknesses: List[str]
+    opportunities_market: List[str]
+    threats: List[str]
+    
+    # Recommendations
+    recommendation: str  # "highly_recommended", "recommended", "consider", "not_recommended"
+    reasoning: str
+    key_success_factors: List[str]
+    main_risks: List[str]
+
+class OpportunityAnalysis(BaseModel):
+    analyzed_opportunities: List[OpportunityScoring]
+    ranked_list: List[str]  # IDs in order of score
+    top_recommendation: str
+    analysis_summary: str
+
+opportunity_analyzer = Agent(
+    'openai:gpt-4-turbo',
+    result_type=OpportunityAnalysis,
+    system_prompt="""
+    You are an expert business analyst who evaluates opportunities
+    using rigorous, data-driven methodology.
+    
+    Evaluate each opportunity on:
+    1. Feasibility - Can it be done with available resources?
+    2. Market Potential - Size and growth of target market
+    3. Competitive Advantage - What makes it unique?
+    4. Resource Requirements - Capital, time, people needed
+    5. Time to Market - How fast can we launch?
+    6. Innovation - How novel is the approach?
+    
+    Perform SWOT analysis for each.
+    Provide clear, justified recommendations.
+    Rank opportunities from best to worst.
+    """,
+    model_settings={
+        'temperature': 0.2  # Low for analytical precision
+    }
+)
+
+@opportunity_analyzer.tool
+def calculate_roi_estimate(
+    revenue_estimate: float,
+    cost_estimate: float,
+    timeframe: str
+) -> dict:
+    """Calculate estimated ROI"""
+    return {"roi": "45%", "break_even": "18 months"}
+
+@opportunity_analyzer.tool  
+def risk_assessment(opportunity: dict) -> dict:
+    """Assess risk factors"""
+    return {"risk_level": "medium", "factors": []}
+```
+
+#### 2.4 Domain Specialist
+
+```python
+class DomainValidation(BaseModel):
+    is_technically_feasible: bool
+    technical_challenges: List[str]
+    required_technologies: List[str]
+    technical_risks: List[str]
+    development_complexity: str  # "low", "medium", "high", "very_high"
+    recommended_approach: str
+    similar_implementations: List[str]
+    confidence: float
+
+domain_specialist = Agent(
+    'openai:gpt-4-turbo',
+    result_type=DomainValidation,
+    system_prompt="""
+    You are a senior technical architect with deep expertise in
+    software development, system design, and technology stacks.
+    
+    For each opportunity, assess:
+    - Technical feasibility
+    - Technology requirements
+    - Development complexity
+    - Potential technical risks
+    - Recommended implementation approach
+    
+    Be realistic about what can be built and maintained.
+    Consider scalability, security, and maintainability.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+
+@domain_specialist.tool
+def check_technology_maturity(tech: str) -> dict:
+    """Check if technology is production-ready"""
+    return {"mature": True, "community": "large", "support": "excellent"}
+
+@domain_specialist.tool
+def estimate_development_time(complexity: str, team_size: int) -> str:
+    """Estimate development timeline"""
+    return "6-9 months"
+```
+
+#### 2.5 Supervisor Agent
+
+```python
+class SupervisorReview(BaseModel):
+    review_status: str  # "approved", "needs_revision", "rejected"
+    quality_score: float
+    completeness_score: float
+    consistency_score: float
+    
+    issues_found: List[str]
+    recommendations: List[str]
+    
+    approved_items: List[str]
+    rejected_items: List[str]
+    items_needing_revision: List[str]
+    
+    final_notes: str
+
+supervisor = Agent(
+    'openai:gpt-4-turbo',
+    result_type=SupervisorReview,
+    system_prompt="""
+    You are a senior project supervisor responsible for quality
+    assurance of AI-generated outputs.
+    
+    Review all work from the team and check for:
+    - Quality: Are outputs well-reasoned and comprehensive?
+    - Completeness: Is all required information present?
+    - Consistency: Do different agents' outputs align?
+    - Accuracy: Are there obvious errors or contradictions?
+    
+    Be thorough but fair. Approve good work, request revisions
+    for fixable issues, reject only if fundamentally flawed.
+    """,
+    model_settings={
+        'temperature': 0.1  # Very low for consistent judgment
+    }
+)
+```
+
+---
+
+### 3. Research Team Agents
+
+#### 3.1 Web Research Agent
+
+```python
+class ResearchFindings(BaseModel):
+    topic: str
+    key_findings: List[str]
+    relevant_data: List[dict]
+    sources: List[str]
+    market_insights: List[str]
+    competitor_intel: List[str]
+    trends_identified: List[str]
+    confidence: float
+
+web_researcher = Agent(
+    'openai:gpt-4-turbo',
+    result_type=ResearchFindings,
+    system_prompt="""
+    You are an expert research analyst who gathers and synthesizes
+    information from various sources.
+    
+    For each research topic:
+    - Find relevant, current information
+    - Identify key trends and patterns
+    - Gather competitive intelligence
+    - Collect market data and statistics
+    - Cite reliable sources
+    
+    Be thorough and objective. Focus on facts and data.
+    """,
+    model_settings={
+        'temperature': 0.4
+    }
+)
+
+@web_researcher.tool
+async def web_search(query: str) -> List[dict]:
+    """Search the web for information"""
+    # Integration with search APIs
+    return [{"title": "...", "url": "...", "snippet": "..."}]
+
+@web_researcher.tool
+async def fetch_market_data(market: str) -> dict:
+    """Fetch market statistics and data"""
+    return {"market_size": "...", "growth_rate": "...", "data": []}
+```
+
+#### 3.2 Domain Knowledge Agent
+
+```python
+class DomainInsights(BaseModel):
+    domain_analysis: str
+    best_practices: List[str]
+    common_pitfalls: List[str]
+    success_patterns: List[str]
+    recommendations: List[str]
+    relevant_frameworks: List[str]
+    expert_insights: List[str]
+
+domain_knowledge_agent = Agent(
+    'openai:gpt-4-turbo',
+    result_type=DomainInsights,
+    system_prompt="""
+    You are a domain expert with deep knowledge across multiple
+    industries and business domains.
+    
+    Provide:
+    - Domain-specific insights and best practices
+    - Common pitfalls and how to avoid them
+    - Proven success patterns
+    - Relevant frameworks and methodologies
+    - Strategic recommendations
+    
+    Draw on your extensive knowledge to provide valuable context.
+    """,
+    model_settings={
+        'temperature': 0.5
+    }
+)
+
+@domain_knowledge_agent.tool
+def retrieve_case_studies(domain: str) -> List[dict]:
+    """Get relevant case studies"""
+    # Vector DB search for similar cases
+    return [{"company": "...", "outcome": "...", "lessons": []}]
+```
+
+#### 3.3 Research Synthesizer
+
+```python
+class ResearchSynthesis(BaseModel):
+    executive_summary: str
+    key_insights: List[str]
+    actionable_recommendations: List[str]
+    data_summary: dict
+    trends_analysis: str
+    risk_factors: List[str]
+    opportunities_identified: List[str]
+    next_steps: List[str]
+    confidence_level: float
+
+research_synthesizer = Agent(
+    'openai:gpt-4-turbo',
+    result_type=ResearchSynthesis,
+    system_prompt="""
+    You are an expert at synthesizing complex research into
+    clear, actionable insights.
+    
+    Take multiple research inputs and:
+    - Create comprehensive executive summary
+    - Extract key insights
+    - Identify patterns and trends
+    - Provide actionable recommendations
+    - Highlight opportunities and risks
+    - Suggest concrete next steps
+    
+    Make the complex simple and accessible.
+    """,
+    model_settings={
+        'temperature': 0.4
+    }
+)
+```
+
+---
+
+### 4. Architecture Team Agents
+
+#### 4.1 Software Architect Agent
+
+```python
+class ArchitectureProposal(BaseModel):
+    architecture_style: str  # microservices, monolith, serverless, etc.
+    
+    modules: List[dict]  # [{name, type, responsibilities, technologies}]
+    layers: List[dict]   # [{name, components}]
+    
+    tech_stack: dict
+    
+    data_flow: str
+    communication_patterns: List[str]
+    
+    scalability_approach: str
+    security_approach: str
+    deployment_strategy: str
+    
+    architectural_patterns: List[str]
+    design_principles: List[str]
+    
+    rationale: str
+    trade_offs: dict
+    
+    diagrams_description: List[dict]
+
+software_architect = Agent(
+    'openai:gpt-4-turbo',
+    result_type=ArchitectureProposal,
+    system_prompt="""
+    You are a principal software architect with 20+ years of experience
+    designing large-scale systems.
+    
+    Design architecture that is:
+    - Scalable and performant
+    - Maintainable and testable
+    - Secure by design
+    - Cost-effective
+    - Technology-appropriate
+    
+    Consider:
+    - System requirements and constraints
+    - Non-functional requirements
+    - Team capabilities
+    - Future growth and evolution
+    
+    Explain your decisions and trade-offs clearly.
+    """,
+    model_settings={
+        'temperature': 0.5
+    }
+)
+
+@software_architect.tool
+def get_architecture_patterns() -> List[dict]:
+    """Get catalog of architecture patterns"""
+    return [
+        {"name": "Microservices", "use_cases": [], "pros": [], "cons": []},
+        {"name": "Event-Driven", "use_cases": [], "pros": [], "cons": []},
+    ]
+
+@software_architect.tool
+def estimate_infrastructure_cost(architecture: dict) -> dict:
+    """Estimate infrastructure costs"""
+    return {"monthly_cost": "5000 USD", "breakdown": {}}
+```
+
+#### 4.2 Architecture Reviewer Agent
+
+```python
+class ArchitectureReview(BaseModel):
+    overall_assessment: str
+    architecture_score: float = Field(ge=0, le=10)
+    
+    strengths: List[str]
+    weaknesses: List[str]
+    concerns: List[str]
+    
+    scalability_assessment: str
+    security_assessment: str
+    maintainability_assessment: str
+    testability_assessment: str
+    
+    recommended_improvements: List[str]
+    critical_issues: List[str]
+    optional_enhancements: List[str]
+    
+    approval_recommendation: str  # "approve", "approve_with_changes", "reject"
+    detailed_feedback: str
+
+architecture_reviewer = Agent(
+    'openai:gpt-4-turbo',
+    result_type=ArchitectureReview,
+    system_prompt="""
+    You are an architecture review expert who evaluates system designs
+    for quality, scalability, and best practices.
+    
+    Review architecture for:
+    - Scalability: Can it handle growth?
+    - Security: Are there vulnerabilities?
+    - Maintainability: Easy to maintain and extend?
+    - Performance: Will it meet performance requirements?
+    - Cost: Is it cost-effective?
+    - Complexity: Is it appropriately complex?
+    
+    Be constructive. Highlight both strengths and areas for improvement.
+    Provide specific, actionable feedback.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+```
+
+#### 4.3 Complexity Analyzer Agent
+
+```python
+class ComplexityAnalysis(BaseModel):
+    overall_complexity_score: float = Field(ge=0, le=100)
+    
+    module_complexity: List[dict]  # Per module breakdown
+    
+    cyclomatic_complexity_estimate: int
+    coupling_score: float
+    cohesion_score: float
+    
+    complexity_hotspots: List[dict]
+    simplification_opportunities: List[str]
+    
+    maintainability_index: float
+    technical_debt_estimate: str
+    
+    recommendations: List[str]
+    
+    risk_assessment: str
+
+complexity_analyzer = Agent(
+    'openai:gpt-4-turbo',
+    result_type=ComplexityAnalysis,
+    system_prompt="""
+    You are a code quality and complexity expert.
+    
+    Analyze architecture for:
+    - Overall system complexity
+    - Module coupling and cohesion
+    - Potential complexity hotspots
+    - Technical debt risks
+    - Maintainability concerns
+    
+    Provide complexity metrics and concrete suggestions for
+    reducing unnecessary complexity.
+    """,
+    model_settings={
+        'temperature': 0.2
+    }
+)
+```
+
+#### 4.4 Dependency Expert Agent
+
+```python
+class DependencyAnalysis(BaseModel):
+    dependency_graph: dict
+    
+    circular_dependencies: List[dict]
+    tight_coupling_areas: List[dict]
+    
+    dependency_health_score: float
+    
+    issues_found: List[dict]
+    warnings: List[str]
+    
+    recommended_changes: List[dict]
+    refactoring_suggestions: List[str]
+    
+    module_independence_scores: dict
+
+dependency_expert = Agent(
+    'openai:gpt-4-turbo',
+    result_type=DependencyAnalysis,
+    system_prompt="""
+    You are an expert in software dependencies and module design.
+    
+    Analyze module dependencies for:
+    - Circular dependencies (anti-pattern)
+    - Tight coupling (risk factor)
+    - Dependency direction (should follow layering)
+    - Module independence
+    
+    Suggest improvements for better module structure.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+```
+
+---
+
+### 5. Requirements Team Agents
+
+#### 5.1 Requirements Analyst Agent
+
+```python
+class RequirementsAnalysis(BaseModel):
+    functional_requirements: List[dict]
+    non_functional_requirements: List[dict]
+    
+    completeness_score: float
+    clarity_score: float
+    testability_score: float
+    
+    missing_requirements: List[str]
+    ambiguous_requirements: List[dict]
+    conflicting_requirements: List[dict]
+    
+    suggested_additions: List[dict]
+    refinement_suggestions: List[dict]
+
+requirements_analyst = Agent(
+    'openai:gpt-4-turbo',
+    result_type=RequirementsAnalysis,
+    system_prompt="""
+    You are a senior requirements engineer.
+    
+    Analyze requirements for:
+    - Completeness: All necessary requirements covered?
+    - Clarity: Are requirements unambiguous?
+    - Testability: Can they be verified?
+    - Consistency: Do they conflict?
+    
+    Suggest improvements and additions.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+```
+
+#### 5.2 Requirements Validator Agent
+
+```python
+class RequirementsValidation(BaseModel):
+    validation_passed: bool
+    validation_score: float
+    
+    validated_requirements: List[str]
+    failed_requirements: List[dict]
+    
+    clarity_issues: List[dict]
+    consistency_issues: List[dict]
+    completeness_gaps: List[str]
+    
+    recommendations: List[str]
+
+requirements_validator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=RequirementsValidation,
+    system_prompt="""
+    You validate requirements against quality criteria.
+    
+    Check each requirement for:
+    - Clear acceptance criteria
+    - No ambiguity
+    - Testable/verifiable
+    - Properly scoped
+    - Non-conflicting
+    
+    Flag issues and provide remediation guidance.
+    """,
+    model_settings={
+        'temperature': 0.2
+    }
+)
+```
+
+#### 5.3 Technology Advisor Agent
+
+```python
+class TechnologyRecommendations(BaseModel):
+    recommended_stack: dict
+    
+    frontend_tech: List[dict]
+    backend_tech: List[dict]
+    database_tech: List[dict]
+    infrastructure_tech: List[dict]
+    devops_tools: List[dict]
+    
+    justifications: dict
+    alternatives: dict
+    
+    learning_curve: dict
+    community_support: dict
+    cost_implications: dict
+    
+    risks: List[str]
+    mitigation_strategies: List[str]
+
+technology_advisor = Agent(
+    'openai:gpt-4-turbo',
+    result_type=TechnologyRecommendations,
+    system_prompt="""
+    You are a technology consultant who recommends appropriate
+    technology stacks based on requirements.
+    
+    Consider:
+    - Project requirements
+    - Team skills
+    - Scalability needs
+    - Budget constraints
+    - Time to market
+    - Community and support
+    - Long-term maintainability
+    
+    Provide well-reasoned recommendations with alternatives.
+    """,
+    model_settings={
+        'temperature': 0.4
+    }
+)
+```
+
+---
+
+### 6. Code Generation Team Agents
+
+#### 6.1 Code Generator Agent
+
+```python
+class GeneratedCode(BaseModel):
+    files: List[dict]  # [{path, content, language}]
+    
+    structure_overview: str
+    key_patterns_used: List[str]
+    
+    setup_instructions: str
+    dependencies: List[str]
+    
+    notes: List[str]
+
+code_generator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=GeneratedCode,
+    system_prompt="""
+    You are an expert software developer who generates clean,
+    well-structured, production-quality code.
+    
+    Generate code that is:
+    - Clean and readable
+    - Well-documented
+    - Follows best practices
+    - Properly structured
+    - Error-handled
+    - Type-safe where applicable
+    
+    Include helpful comments and documentation.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+```
+
+#### 6.2 Code Reviewer Agent
+
+```python
+class CodeReview(BaseModel):
+    overall_quality_score: float
+    
+    code_style_score: float
+    documentation_score: float
+    error_handling_score: float
+    testing_score: float
+    security_score: float
+    
+    issues_found: List[dict]
+    suggestions: List[dict]
+    
+    approve_for_production: bool
+    blocking_issues: List[str]
+    
+    detailed_feedback: str
+
+code_reviewer = Agent(
+    'openai:gpt-4-turbo',
+    result_type=CodeReview,
+    system_prompt="""
+    You are a senior code reviewer who ensures code quality.
+    
+    Review code for:
+    - Code quality and style
+    - Documentation
+    - Error handling
+    - Security vulnerabilities
+    - Performance issues
+    - Best practices
+    
+    Provide constructive, actionable feedback.
+    """,
+    model_settings={
+        'temperature': 0.2
+    }
+)
+```
+
+#### 6.3 Test Generator Agent
+
+```python
+class GeneratedTests(BaseModel):
+    test_files: List[dict]
+    
+    unit_tests_count: int
+    integration_tests_count: int
+    
+    coverage_estimate: float
+    
+    test_patterns_used: List[str]
+    testing_framework: str
+    
+    setup_instructions: str
+
+test_generator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=GeneratedTests,
+    system_prompt="""
+    You are a test automation expert who generates comprehensive tests.
+    
+    Generate:
+    - Unit tests for all functions/methods
+    - Integration tests for workflows
+    - Edge case tests
+    - Error scenario tests
+    
+    Use appropriate testing frameworks and patterns.
+    Aim for high coverage and meaningful assertions.
+    """,
+    model_settings={
+        'temperature': 0.3
+    }
+)
+```
+
+---
+
+## Agent Team Configurations
+
+### Opportunity Generation Team
+
+```python
+opportunity_team = AITeam(
+    name="OpportunityGeneration",
+    agents={
+        "creative_gen": creative_generator,
+        "structured_gen": structured_generator,
+        "analyzer": opportunity_analyzer,
+        "domain_specialist": domain_specialist,
+        "supervisor": supervisor
+    },
+    workflow=opportunity_generation_workflow
+)
+```
+
+### Research Team
+
+```python
+research_team = AITeam(
+    name="Research",
+    agents={
+        "web_researcher": web_researcher,
+        "domain_expert": domain_knowledge_agent,
+        "synthesizer": research_synthesizer,
+        "supervisor": supervisor
+    },
+    workflow=research_workflow
+)
+```
+
+### Architecture Team
+
+```python
+architecture_team = AITeam(
+    name="Architecture",
+    agents={
+        "architect": software_architect,
+        "reviewer": architecture_reviewer,
+        "complexity_analyzer": complexity_analyzer,
+        "dependency_expert": dependency_expert,
+        "supervisor": supervisor
+    },
+    workflow=architecture_generation_workflow
+)
+```
+
+### Code Generation Team
+
+```python
+code_gen_team = AITeam(
+    name="CodeGeneration",
+    agents={
+        "generator": code_generator,
+        "reviewer": code_reviewer,
+        "test_gen": test_generator,
+        "doc_gen": documentation_agent,
+        "supervisor": supervisor
+    },
+    workflow=code_generation_workflow
+)
+```
+
+---
+
+## Cost Management
+
+### Token Usage Tracking
+
+```python
+class TokenTracker:
+    def __init__(self):
+        self.usage = {}
+    
+    def track_agent_call(
+        self,
+        agent_name: str,
+        input_tokens: int,
+        output_tokens: int,
+        cost: float
+    ):
+        if agent_name not in self.usage:
+            self.usage[agent_name] = {
+                "calls": 0,
+                "input_tokens": 0,
+                "output_tokens": 0,
+                "total_cost": 0
+            }
+        
+        self.usage[agent_name]["calls"] += 1
+        self.usage[agent_name]["input_tokens"] += input_tokens
+        self.usage[agent_name]["output_tokens"] += output_tokens
+        self.usage[agent_name]["total_cost"] += cost
+    
+    def get_project_cost(self, project_id: str) -> float:
+        # Query from database
+        pass
+```
+
+### Cost Optimization Strategies
+
+1. **Caching**: Cache AI results for identical inputs
+2. **Batching**: Batch multiple requests when possible
+3. **Model Selection**: Use appropriate model for task (GPT-3.5 for simple, GPT-4 for complex)
+4. **Context Management**: Keep context minimal but sufficient
+5. **Rate Limiting**: Prevent runaway costs
+
+---
+
+## Quality Assurance
+
+### Agent Output Validation
+
+```python
+class AgentOutputValidator:
+    @staticmethod
+    def validate_opportunity_analysis(output: OpportunityAnalysis) -> bool:
+        """Validate opportunity analysis output"""
+        # Check all required fields present
+        # Check scores in valid range
+        # Check reasoning is substantive
+        return True
+    
+    @staticmethod
+    def validate_architecture(output: ArchitectureProposal) -> bool:
+        """Validate architecture proposal"""
+        # Check all modules defined
+        # Check tech stack complete
+        # Check rationale provided
+        return True
+```
+
+### Human-in-the-Loop Checkpoints
+
+Every major AI output requires human approval:
+
+```python
+class HumanApprovalRequired(Exception):
+    pass
+
+async def run_with_approval(
+    agent: Agent,
+    input_data: Any,
+    project_id: str,
+    stage: str
+) -> Any:
+    """Run agent and wait for human approval"""
+    
+    # Run AI agent
+    result = await agent.run(input_data)
+    
+    # Create approval request
+    approval_id = create_approval_request(
+        project_id=project_id,
+        stage=stage,
+        ai_output=result.data
+    )
+    
+    # Wait for approval
+    approved = await wait_for_approval(approval_id)
+    
+    if not approved:
+        raise HumanApprovalRequired(f"Stage {stage} not approved")
+    
+    return result.data
+```
+
+---
+
+Това е пълната спецификация на AI agents. Следва документация за frontend components.