"""
Tests for the bulk download endpoint.
"""

import pytest
from rest_framework.test import APIClient

from core import factories

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("reach", argvalues=["public", "restricted", "authenticated"])
def test_api_items_bulk_download_anonymous(reach):
    """Anonymous (non-connected user) can't perform a bulk download"""

    item = factories.ItemFactory(link_reach=reach)
    client = APIClient()

    response = client.post(
        "/api/v1.0/items/downloads/",
        data={"ids": [item.id]},
        format="json",
    )

    assert response.status_code == 401


def test_api_items_bulk_download_authenticated():
    """An authenticated user can perform a bulk download"""

    item = factories.ItemFactory(link_reach="authenticated")
    user = factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/items/downloads/",
        data={"ids": [item.id]},
        format="json",
    )

    assert response.status_code == 200


def test_api_items_bulk_download_restricted_item():
    """An authenticated user can't perform a bulk download on an item created by another user"""

    other_user_item = factories.ItemFactory(link_reach="restricted")
    user = factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/items/downloads/",
        data={"ids": [other_user_item.id]},
        format="json",
    )

    assert response.status_code == 404


def test_api_items_bulk_download_mixed_items():
    """Only the items the user can read are kept"""

    other_user_item = factories.ItemFactory(link_reach="restricted")
    allowed_item = factories.ItemFactory(link_reach="authenticated")
    user = factories.UserFactory()
    client = APIClient()
    client.force_login(user)

    response = client.post(
        "/api/v1.0/items/downloads/",
        data={"ids": [other_user_item.id, allowed_item.id]},
        format="json",
    )

    data_json = response.json()

    assert response.status_code == 200

    response_ids = data_json["ids"]

    assert str(other_user_item.id) not in response_ids
    assert str(allowed_item.id) in response_ids
