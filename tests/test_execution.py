import pytest
from pydantic import ValidationError
from app.execution.base import ResourceLimits
from app.execution.docker_engine import DockerExecutionEngine


def test_resource_limits_validation():
    limits = ResourceLimits(
        max_memory_mb=256,
        cpu_quota=0.5,
        max_execution_time_seconds=10,
        allow_network=False,
        max_processes=32,
    )
    assert limits.max_memory_mb == 256
    assert limits.allow_network is False

    with pytest.raises(ValidationError):
        ResourceLimits(max_memory_mb=32)


def test_execution_engine_provision_and_command():
    engine = DockerExecutionEngine(enable_docker=False)
    session_id = "test-session-123456"

    # 1. Provision container
    info = engine.provision_container(
        session_id=session_id,
        limits=ResourceLimits(max_memory_mb=512, cpu_quota=0.5),
    )
    assert info.session_id == session_id
    assert info.resource_limits.max_memory_mb == 512
    assert info.container_id is not None

    # 2. Execute echo command
    res_echo = engine.execute_command(
        container_id=info.container_id,
        command="echo 'Vivoki Execution Engine'",
    )
    assert res_echo.exit_code == 0
    assert "Vivoki Execution Engine" in res_echo.stdout
    assert res_echo.timed_out is False

    # 3. Execute test command
    res_test = engine.execute_command(
        container_id=info.container_id,
        command="pytest",
    )
    assert res_test.exit_code == 0
    assert "PASSED" in res_test.stdout

    # 4. Cleanup container
    cleaned = engine.cleanup_container(info.container_id)
    assert cleaned is True
