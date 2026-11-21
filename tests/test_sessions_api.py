import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "Vivoki" in data["name"]


@pytest.mark.asyncio
async def test_list_and_get_environments(client: AsyncClient):
    # 1. List environments
    res = await client.get("/api/v1/sandbox/environments")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    envs = body["data"]
    assert len(envs) >= 3
    slugs = {e["slug"] for e in envs}
    assert "finance-ap-reconciliation" in slugs
    assert "hr-candidate-screening" in slugs
    assert "sde-bug-triage" in slugs

    # 2. Get specific environment
    res_detail = await client.get("/api/v1/sandbox/environments/finance-ap-reconciliation")
    assert res_detail.status_code == 200
    body_detail = res_detail.json()
    assert body_detail["data"]["category"] == "finance"
    assert "starter_workspace_state" in body_detail["data"]["config"]


@pytest.mark.asyncio
async def test_session_lifecycle_and_autosave(client: AsyncClient):
    # 1. Start or resume session
    create_res = await client.post(
        "/api/v1/sandbox/sessions",
        json={"environment_slug": "finance-ap-reconciliation"},
    )
    assert create_res.status_code == 200
    session_data = create_res.json()["data"]
    session_id = session_data["id"]
    assert session_data["status"] == "READY"
    assert session_data["environment_slug"] == "finance-ap-reconciliation"

    # 2. Transition status: READY -> RUNNING
    status_res = await client.patch(
        f"/api/v1/sandbox/sessions/{session_id}/status",
        json={"status": "RUNNING"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["status"] == "RUNNING"

    # 3. Autosave candidate workspace state
    updated_rows = [{"invoiceNo": "INV-8821", "decision": "Partially Approve", "verifiedAmount": 37500}]
    save_res = await client.patch(
        f"/api/v1/sandbox/sessions/{session_id}/workspace",
        json={
            "workspace_state": {"invoiceRows": updated_rows},
            "time_remaining_seconds": 2350,
        },
    )
    assert save_res.status_code == 200
    assert save_res.json()["data"]["time_remaining_seconds"] == 2350

    # 4. Ingest batch of activity events
    events_payload = {
        "events": [
            {"event_type": "spreadsheet.cell_changed", "event_data": {"cell": "E2", "val": 37500}},
            {"event_type": "document.opened", "event_data": {"doc_id": "doc-inv-8821"}},
            {"event_type": "integrity.paste_blocked", "event_data": {"field": "answers.q1"}},
        ]
    }
    event_res = await client.post(
        f"/api/v1/sandbox/sessions/{session_id}/events",
        json=events_payload,
    )
    assert event_res.status_code == 200
    event_body = event_res.json()["data"]
    assert event_body["received_count"] == 3
    assert event_body["latest_sequence_no"] == 3

    # 5. Submit assessment
    submit_res = await client.post(
        f"/api/v1/sandbox/sessions/{session_id}/submit",
        json={
            "workspace_snapshot": {"invoiceRows": updated_rows},
            "answers": {
                "q1DecisionsReasoning": "Three-way matching variance audit",
                "q2DiscountAnalysis": "2% early discount savings of $2,614 CAD on Sigma Precision Tools",
            },
            "integrity_flags": {"pasteCount": 1},
        },
    )
    assert submit_res.status_code == 200
    eval_data = submit_res.json()["data"]
    assert eval_data["session_id"] == session_id
    assert "overall_score" in eval_data
    assert "score_breakdown" in eval_data
    assert eval_data["integrity_audit"]["paste_attempts_count"] == 1

    # 6. Fetch result via GET
    get_res = await client.get(f"/api/v1/sandbox/sessions/{session_id}/result")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == eval_data["id"]
