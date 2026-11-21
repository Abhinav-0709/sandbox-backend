import pytest
from pydantic import ValidationError
from app.services.environment_service import bump_semver, DEFAULT_ENVIRONMENTS
from app.schemas.environment import CreateEnvironmentRequest


def test_semver_bumping_rules():
    assert bump_semver("1.0.0", "patch") == "1.0.1"
    assert bump_semver("1.0.0", "minor") == "1.1.0"
    assert bump_semver("1.0.0", "major") == "2.0.0"
    assert bump_semver("2.4.1", "minor") == "2.5.0"
    assert bump_semver("2.4.1", "patch") == "2.4.2"
    assert bump_semver("2.4.1", "major") == "3.0.0"


def test_default_environments_schema_integrity():
    assert len(DEFAULT_ENVIRONMENTS) >= 3
    slugs = [e["slug"] for e in DEFAULT_ENVIRONMENTS]
    assert "finance-ap-reconciliation" in slugs
    assert "hr-candidate-screening" in slugs
    assert "sde-bug-triage" in slugs

    for env in DEFAULT_ENVIRONMENTS:
        assert "config" in env
        assert "starter_workspace_state" in env["config"]
        assert "evaluation_rules" in env
        assert env["estimated_minutes"] >= 15


def test_create_environment_validation_rejects_invalid_slug():
    # Slug with spaces or uppercase must fail validation
    with pytest.raises(ValidationError):
        CreateEnvironmentRequest(
            slug="Invalid Slug With Spaces",
            title="Invalid Environment",
            category="finance",
            department="Finance",
            role_title="Specialist",
        )

    # Valid slug passes
    valid = CreateEnvironmentRequest(
        slug="sales-pipeline-audit",
        title="Sales Pipeline Audit",
        category="sales",
        department="Sales Operations",
        role_title="Sales Analyst",
    )
    assert valid.slug == "sales-pipeline-audit"


