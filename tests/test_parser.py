import aiohttp
import pytest

from anova_wifi import AnovaApi

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_can_create() -> None:
    AnovaApi(aiohttp.ClientSession(), "", "")


async def test_can_create_with_personal_access_token() -> None:
    AnovaApi(aiohttp.ClientSession(), personal_access_token="anova-abc123")


async def test_requires_credentials() -> None:
    with pytest.raises(ValueError):
        AnovaApi(aiohttp.ClientSession())


async def test_rejects_both_pat_and_username_password() -> None:
    with pytest.raises(ValueError):
        AnovaApi(
            aiohttp.ClientSession(),
            "user",
            "pass",
            personal_access_token="anova-abc123",
        )


async def test_rejects_username_without_password() -> None:
    with pytest.raises(ValueError):
        AnovaApi(aiohttp.ClientSession(), username="user")


async def test_authenticate_with_personal_access_token_skips_firebase() -> None:
    api = AnovaApi(aiohttp.ClientSession(), personal_access_token="anova-abc123")

    result = await api.authenticate()

    assert result is True
    assert api.jwt == "anova-abc123"
    assert api._firebase_jwt == "anova-abc123"
