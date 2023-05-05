import asyncio
import json
import logging
import time
import typing
from typing import Tuple

import aiohttp

from anova_wifi.exceptions import AnovaException, InvalidLogin, NoDevicesFound
from anova_wifi.precission_cooker import AnovaPrecisionCooker

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
        existing_devices: list[AnovaPrecisionCooker] | None = None,
    ) -> None:
        """Creates an anova api class"""
        if existing_devices is None:
            existing_devices = []
        self.session = session
        self.username = username
        self.password = password
        self.jwt: str | None = None
        self._firebase_jwt: str | None = None
        self.existing_devices = existing_devices

    async def authenticate(self) -> bool:
        """Auth with Firebase server"""
        # Code loving yoinked from https://github.com/ammarzuberi/pyanova-api/blob/master/anova/AnovaCooker.py
        firebase_req_data = {
            "email": self.username,
            "password": self.password,
            "returnSecureToken": True,
        }

        firebase_req = await self.session.post(
            f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={ANOVA_FIREBASE_KEY}",
            json=firebase_req_data,
        )
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

    async def get_devices(self) -> typing.List[AnovaPrecisionCooker]:
        """Get all devices by connecting to anova websocket"""
        if self._firebase_jwt is None or self.jwt is None:
            raise AnovaException("Cannot get devices without first authenticating")
        url = f"https://devices.anovaculinary.io/?token={self._firebase_jwt}&supportedAccessories=APC&platform=android"
        user_devices = []
        timeout = time.time() + 5  # 5 seconds from now

        existing_devices_keys = [d.device_key for d in self.existing_devices]
        async with self.session.ws_connect(url) as ws:
            _LOGGER.debug("looking for devices for 5 seconds...")
            while time.time() < timeout:
                try:
                    msg = await ws.receive(4.5)
                except asyncio.TimeoutError:
                    raise NoDevicesFound("Found no devices on websocket")
                # Filter messages based on the "command" field
                data = json.loads(msg.data)
                _LOGGER.debug("Found message %s", data)
                if data.get("command") == "EVENT_APC_WIFI_VERSION":
                    _LOGGER.debug("Found Event APC WIFI")
                    payload = data.get("payload")
                    devices: typing.List[Tuple[str, str]] = [
                        (d["cookerId"], d["type"])
                        for d in payload
                        if d["cookerId"] not in existing_devices_keys
                    ]
                    for device in devices:
                        _LOGGER.debug("Found device %s", device[0])
                        user_devices.append(
                            AnovaPrecisionCooker(
                                self.session, device[0], device[1], self.jwt
                            )
                        )
        if len(user_devices) == 0:
            raise NoDevicesFound("Found no devices on the websocket")
        self.existing_devices = self.existing_devices + user_devices
        return user_devices
