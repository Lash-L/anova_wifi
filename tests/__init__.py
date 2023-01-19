from typing import Any, Iterator
from unittest.mock import AsyncMock


class MockResponse:
    def __init__(self, json_data, status_code, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.json_data = json_data
        self.status_code = status_code

    def __await__(self):
        return MockResponse(json_data=self.json_data,status_code=self.status_code)

    async def json(self):
        return self.json_data
