"""Validation pipeline for pre-code-generation checks."""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.architecture.service import ArchitectureService
from backend.modules.requirements.service import RequirementsService
from backend.modules.code_generation.schemas import PreGenerationValidation, ValidationCheck


class ValidationPipeline:
    """Pre-generation validation pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.arch_service = ArchitectureService(session)
        self.req_service = RequirementsService(session)

    async def validate_project_readiness(self, project_id: UUID) -> PreGenerationValidation:
        """Validate if project is ready for code generation."""
        checks = []

        # Check 1: Architecture Completeness
        arch_check = await self._validate_architecture(project_id)
        checks.append(arch_check)

        # Check 2: Requirements Quality
        req_check = await self._validate_requirements(project_id)
        checks.append(req_check)

        # Check 3: Dependencies
        dep_check = await self._validate_dependencies(project_id)
        checks.append(dep_check)

        # Check 4: Technology Stack
        tech_check = await self._validate_technology_stack(project_id)
        checks.append(tech_check)

        # Calculate overall readiness
        architecture_completeness = arch_check.score * 10
        requirements_clarity = req_check.score * 10
        overall_readiness = sum(c.score for c in checks) / len(checks) * 10

        # Determine if can proceed
        can_proceed = (
            all(c.passed for c in checks)
            and architecture_completeness >= 90
            and requirements_clarity >= 90
            and overall_readiness >= 85
        )

        blocking_issues = []
        for check in checks:
            if not check.passed:
                blocking_issues.extend(check.issues)

        return PreGenerationValidation(
            architecture_completeness=architecture_completeness,
            requirements_clarity=requirements_clarity,
            dependencies_resolved=dep_check.passed,
            circular_dependencies=not dep_check.passed,
            overall_readiness=overall_readiness,
            checks=checks,
            can_proceed=can_proceed,
            blocking_issues=blocking_issues,
        )

    async def _validate_architecture(self, project_id: UUID) -> ValidationCheck:
        """Validate architecture is complete."""
        modules = await self.arch_service.list_modules(project_id)
        validation = await self.arch_service.validate_architecture(project_id)

        issues = []
        if len(modules) == 0:
            issues.append("No architecture modules defined")

        approved_count = sum(1 for m in modules if m.status == "approved")
        approval_rate = (approved_count / len(modules) * 100) if modules else 0

        if approval_rate < 80:
            issues.append(f"Only {approval_rate:.0f}% of modules are approved (need 80%)")

        if not validation.is_valid:
            issues.append("Architecture has validation errors")

        passed = len(issues) == 0 and len(modules) > 0
        score = min(10.0, (approved_count / max(1, len(modules))) * 10)

        return ValidationCheck(
            check_name="Architecture Completeness",
            passed=passed,
            score=score,
            message=f"{len(modules)} modules, {approved_count} approved",
            issues=issues,
        )

    async def _validate_requirements(self, project_id: UUID) -> ValidationCheck:
        """Validate requirements are clear and approved."""
        requirements = await self.req_service.list_requirements(project_id)
        summary = await self.req_service.get_requirements_summary(project_id)

        issues = []
        if len(requirements) == 0:
            issues.append("No requirements defined")

        approved_count = sum(1 for r in requirements if r.status == "approved")
        approval_rate = (approved_count / len(requirements) * 100) if requirements else 0

        if approval_rate < 80:
            issues.append(f"Only {approval_rate:.0f}% of requirements approved (need 80%)")

        if summary.validation_coverage < 90:
            issues.append(f"Only {summary.validation_coverage:.0f}% validated (need 90%)")

        passed = len(issues) == 0
        score = min(10.0, (approved_count / max(1, len(requirements))) * 10)

        return ValidationCheck(
            check_name="Requirements Quality",
            passed=passed,
            score=score,
            message=f"{len(requirements)} requirements, {approved_count} approved",
            issues=issues,
        )

    async def _validate_dependencies(self, project_id: UUID) -> ValidationCheck:
        """Validate all dependencies are resolved."""
        validation = await self.arch_service.validate_architecture(project_id)

        issues = []
        if not validation.is_valid:
            for issue in validation.issues:
                if issue.severity == "critical":
                    issues.append(f"{issue.type}: {issue.message}")

        circular = any("circular" in issue.type.lower() for issue in validation.issues)

        passed = validation.is_valid and not circular
        score = 10.0 if passed else 5.0

        return ValidationCheck(
            check_name="Dependencies Resolved",
            passed=passed,
            score=score,
            message="All dependencies valid" if passed else "Dependency issues found",
            issues=issues,
        )

    async def _validate_technology_stack(self, project_id: UUID) -> ValidationCheck:
        """Validate technology stack is selected."""
        technologies = await self.req_service.list_technology_recommendations(project_id)

        issues = []
        if len(technologies) == 0:
            issues.append("No technology stack selected")

        accepted_count = sum(1 for t in technologies if t.status == "accepted")

        if accepted_count < 3:
            issues.append(f"Only {accepted_count} technologies accepted (recommend at least 3)")

        passed = accepted_count >= 3
        score = min(10.0, accepted_count / 3 * 10)

        return ValidationCheck(
            check_name="Technology Stack",
            passed=passed,
            score=score,
            message=f"{accepted_count} technologies accepted",
            issues=issues,
        )