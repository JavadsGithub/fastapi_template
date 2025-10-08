# tests/test_abac_policies.py
import pytest
from types import SimpleNamespace
from app.auth.engine import ABACEngine

abac = ABACEngine()

def make_user(id=1, roles=None, purchased=None):
    return SimpleNamespace(
        id=id,
        roles=roles or [],
        purchased_product_ids=purchased or []
    )

def make_product(id=10, owner_id=2, is_public=False):
    return SimpleNamespace(
        id=id,
        owner_id=owner_id,
        is_public=is_public,
        price=50
    )

def test_admin_can_delete_any_product():
    user = make_user(id=99, roles=["admin"])
    product = make_product(id=1, owner_id=2)
    allowed, reason = abac.evaluate("delete_product", user, product, {"hour": 2})
    assert allowed is True
    assert reason == "user_is_admin"

def test_owner_can_delete_in_allowed_hours():
    user = make_user(id=2, roles=[])
    product = make_product(id=5, owner_id=2)
    allowed, reason = abac.evaluate("delete_product", user, product, {"hour": 10})
    assert allowed is True
    assert reason == "owner_and_time_ok"

def test_owner_cannot_delete_outside_hours():
    user = make_user(id=2)
    product = make_product(id=5, owner_id=2)
    allowed, reason = abac.evaluate("delete_product", user, product, {"hour": 23})
    assert allowed is False
    assert reason == "owner_but_out_of_allowed_hours"

def test_buyer_can_download_if_purchased():
    user = make_user(id=7, purchased=[11,12])
    product = make_product(id=11, owner_id=3)
    allowed, reason = abac.evaluate("download_product", user, product, {"hour": 15})
    assert allowed is True
    assert reason == "user_purchased"

def test_public_product_downloadable_by_anyone():
    user = make_user(id=100)
    product = make_product(id=20, is_public=True)
    allowed, reason = abac.evaluate("download_product", user, product, {"hour": 5})
    assert allowed is True
    assert reason == "resource_is_public"

def test_not_purchased_cannot_download():
    user = make_user(id=8, purchased=[])
    product = make_product(id=99, is_public=False)
    allowed, reason = abac.evaluate("download_product", user, product, {"hour": 12})
    assert allowed is False
    assert reason == "not_purchased_or_public"
