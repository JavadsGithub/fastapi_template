# tests/abac_tests.py

import pytest


@pytest.mark.asyncio
async def test_admin_can_delete_any_product(test_data, get_token, test_client):
    token = get_token("admin_user")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.delete(
        "/api/v1/auth/delete-product/1", headers=headers
    )
    assert response.status_code == 200
    response = await test_client.delete(
        "/api/v1/auth/delete-product/2", headers=headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_seller_can_delete_own_products(test_data, get_token, test_client):
    token = get_token("seller_ali")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.delete(
        "/api/v1/auth/delete-product/1", headers=headers
    )
    assert response.status_code == 200
    response = await test_client.delete(
        "/api/v1/auth/delete-product/2", headers=headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_buyer_cannot_delete_any_product(test_data, get_token, test_client):
    token = get_token("buyer_reza")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.delete(
        "/api/v1/auth/delete-product/1", headers=headers
    )
    assert response.status_code == 403
    response = await test_client.delete(
        "/api/v1/auth/delete-product/2", headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_download_any_product(test_data, get_token, test_client):
    token = get_token("admin_user")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/v1/auth/download-product/1", headers=headers)
    assert response.status_code == 200
    response = await test_client.get("/api/v1/auth/download-product/2", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_seller_can_download_private_product(test_data, get_token, test_client):
    token = get_token("seller_ali")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/v1/auth/download-product/1", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_seller_can_download_public_product(test_data, get_token, test_client):
    token = get_token("seller_ali")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/v1/auth/download-product/2", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_buyer_can_download_purchased_and_public_products(
    test_data, get_token, test_client
):
    token = get_token("buyer_reza")
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/v1/auth/download-product/1", headers=headers)
    assert response.status_code == 200
    response = await test_client.get("/api/v1/auth/download-product/2", headers=headers)
    assert response.status_code == 200
