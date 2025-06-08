import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_crud_demo(async_client: AsyncClient):
    # --- Create ---
    create_payload = {
        "name": "조회 테스트",
        "content": "내용입니다",
        "test": "필드"
    }
    create_res = await async_client.post("/demo/", json=create_payload)
    assert create_res.status_code == 201
    body = create_res.json()
    assert body["status"] == "CREATED"
    assert "detail" in body
    demo_id = body["detail"]["id"]

    # --- Read ---
    get_res = await async_client.get(f"/demo/{demo_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["name"] == "조회 테스트"
    assert data["content"] == "내용입니다"
    assert data["test"] == "필드"

    # --- Update ---
    update_payload = {
        "name": "수정된 이름",
        "content": "수정된 내용",
        "test": "수정된 필드"
    }
    update_res = await async_client.put(f"/demo/{demo_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "OK"
    assert update_res.json()["detail"] is None or update_res.json()["detail"] == {}

    # --- Read Again ---
    updated_res = await async_client.get(f"/demo/{demo_id}")
    assert updated_res.status_code == 200
    updated = updated_res.json()
    assert updated["name"] == "수정된 이름"
    assert updated["content"] == "수정된 내용"
    assert updated["test"] == "수정된 필드"

    # --- Delete ---
    delete_res = await async_client.delete(f"/demo/{demo_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "OK"
    assert delete_res.json()["detail"] is None or delete_res.json()["detail"] == {}

    # --- Read After Delete ---
    res_check = await async_client.get(f"/demo/{demo_id}")
    assert res_check.status_code == 404
    assert res_check.json()["status"] == "NOT_FOUND"
    assert "demo_id" in res_check.json()["detail"]