from unittest.mock import AsyncMock

import pytest

from anova_wifi.websocket_handler import (
    WEBSOCKET_HEARTBEAT_SECONDS,
    AnovaWebsocketHandler,
)


@pytest.mark.asyncio
async def test_connect_passes_heartbeat_to_ws_connect() -> None:
    """Without a heartbeat, aiohttp can't detect a silently dead connection."""
    session = AsyncMock()
    handler = AnovaWebsocketHandler(
        firebase_jwt="firebase_jwt", jwt="jwt", session=session
    )

    await handler.connect()

    session.ws_connect.assert_awaited_once_with(
        handler.url, heartbeat=WEBSOCKET_HEARTBEAT_SECONDS
    )
