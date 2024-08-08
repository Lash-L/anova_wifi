import aiohttp

from anova_wifi import AnovaApi


async def test_can_create() -> None:
    AnovaApi(aiohttp.ClientSession(), "", "")
