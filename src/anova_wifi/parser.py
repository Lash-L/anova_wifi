import asyncio
import logging

import aiohttp
from aiohttp import ClientConnectorError

from .exceptions import InvalidLogin, LoginUnreachable, NoDevicesFound, WebsocketFailure
from .websocket_handler import AnovaWebsocketHandler

_LOGGER = logging.getLogger(__name__)

# Found here - https://github.com/ammarzuberi/pyanova-api/blob/master/anova/AnovaCooker.py and personally confirmed.
ANOVA_FIREBASE_KEY = "AIzaSyDQiOP2fTR9zvFcag2kSbcmG9zPh6gZhHw"


class AnovaApi:
    """A class to handle communicating with the anova api to get devices"""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        """Creates an anova api class"""
        self.session = session
        self.username = username
        self.password = password
        self.jwt: str | None = None
        self._firebase_jwt: str | None = None
        self.websocket_handler: AnovaWebsocketHandler | None = None

    async def authenticate(self) -> bool:
        """Auth with Firebase server"""
        # Code loving yoinked from https://github.com/ammarzuberi/pyanova-api/blob/master/anova/AnovaCooker.py
        firebase_req_data = {
            "email": self.username,
            "password": self.password,
            "returnSecureToken": True,
        }
        try:
            firebase_req = await self.session.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={ANOVA_FIREBASE_KEY}",
                json=firebase_req_data,
            )
        except ClientConnectorError as err:
            raise LoginUnreachable(
                "Failed to connect to Anova's firebase instance"
            ) from err
        firebase_id_token_json = await firebase_req.json()
        self._firebase_jwt = firebase_id_token_json.get("idToken")

        if not self._firebase_jwt:
            raise InvalidLogin("Could not log in with Google Firebase")

        # Now authenticate with Anova using the Firebase ID token to get the JWT
        anova_auth_req = await self.session.post(
            "https://anovaculinary.io/authenticate",
            json={},
            headers={"firebase-token": self._firebase_jwt},
        )
        jwt_json = await anova_auth_req.json()
        jwt = jwt_json.get("jwt")  # Looks like this JWT is valid for an entire year...

        if not jwt:
            raise InvalidLogin("Could not authenticate with Anova")

        # Set JWT local variable
        self.jwt = jwt

        return True

    async def create_websocket(self) -> None:
        if self._firebase_jwt is None:
            raise WebsocketFailure("Firebase jwt was none.")
        if self.jwt is None:
            raise WebsocketFailure("jwt was none.")
        self.websocket_handler = AnovaWebsocketHandler(
            firebase_jwt=self._firebase_jwt, jwt=self.jwt, session=self.session
        )
        await self.websocket_handler.connect()
        await asyncio.sleep(5)
        if not self.websocket_handler.devices:
            raise NoDevicesFound("No devices were found on the websocket.")

    async def disconnect_websocket(self) -> None:
        if self.websocket_handler is not None:
            await self.websocket_handler.disconnect()
