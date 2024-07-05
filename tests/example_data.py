from typing import Any

A3_MESSAGE: dict[str, Any] = {
    "command": "EVENT_APC_STATE",
    "payload": {
        "cookerId": "anova random-id",
        "type": "a3",
        "state": {
            "firmwareVersion": "ver 5.5.1",
            "isCooking": True,
            "currentTemperature": 96.1,
            "targetTemperature": 96.1,
            "timerInSeconds": 840,
            "unit": "f",
            "isTimerRunning": True,
            "isSpeakerOn": True,
            "isAlarmActive": False,
            "currentJobID": "random_job_id",
            "currentJob": {
                "jobType": "manual_cook",
                "jobStage": "cooking",
                "targetTemperature": 96.1,
                "timerLength": 840,
                "tempUnit": "f",
                "thresholdTemperature": 40,
                "thresholdTemperatureUnit": "f",
            },
            "isKeepingWarm": False,
            "isCheckingTemperatureForIceBath": False,
            "isMonitoringIcebath": False,
            "isConnected": True,
        },
    },
}

A4_MESSAGE: dict[str, Any] = {
    "command": "EVENT_APC_STATE",
    "payload": {
        "cookerId": "XXXXXXXX",
        "type": "a4",
        "state": {
            "boot-id": "43435004281963",
            "job": {
                "cook-time-seconds": 0,
                "id": "98827197488379",
                "mode": "COOK",
                "ota-url": "",
                "target-temperature": 66.11,
                "temperature-unit": "F",
            },
            "job-status": {
                "cook-time-remaining": 0,
                "job-start-systick": 1553,
                "provisioning-pairing-code": 0,
                "state": "COOKING",
                "state-change-systick": 1553,
            },
            "network-info": {
                "bssid": "XXXXXXXX",
                "connection-status": "connected-station",
                "is-provisioning": False,
                "mac-address": "XXXXXXXX",
                "mode": "station",
                "security-type": "WPA2",
                "ssid": "XXXXXXXX",
            },
            "pin-info": {
                "device-safe": 0,
                "water-leak": 0,
                "water-level-critical": 0,
                "water-temp-too-high": 0,
            },
            "system-info-3220": {
                "firmware-version": "1.4.4",
                "firmware-version-raw": "VM176_A_01.04.04",
                "largest-free-heap-size": 28008,
                "stack-low-level": 180,
                "stack-low-task": 7,
                "systick": 15315965,
                "total-free-heap-size": 28688,
            },
            "system-info-nxp": {"version-string": "VM171_A_01.04.04"},
            "temperature-info": {
                "heater-temperature": 66.74,
                "triac-temperature": 54.99,
                "water-temperature": 66.09,
            },
        },
    },
}

A6_MESSAGE: dict[str, Any] = {
    "command": "EVENT_APC_STATE",
    "payload": {
        "cookerId": "a6_device",
        "type": "a6",
        "state": {
            "version": 1,
            "updatedTimestamp": "2024-06-13T03:11:31Z",
            "systemInfo": {
                "deviceId": "a6_device",
                "online": True,
                "firmwareVersion": "01.01.12",
                "releaseTrack": "production",
                "firmwareUpdatedTimestamp": "2024-05-20T04:40:01Z",
                "lastConnectedTimestamp": "2024-06-13T01:34:31Z",
                "lastDisconnectedTimestamp": "2024-06-09T13:31:09Z",
                "hardwareVersion": "1.0.0",
                "triacsFailed": False,
            },
            "state": {
                "mode": "idle",
                "temperatureUnit": "C",
                "processedCommandIds": [
                    "cd442f58-2b8f-42bb-9e17-17d0be83005f",
                    "7bef2615-84e6-4736-bb9e-4ed2bc94c545",
                    "91d01cba-de6c-40b4-9562-5c8b1e500cc4",
                    "d52e0f5b-09af-4160-860a-5c48fa08ddd5",
                    "d00ac964-d304-4fdf-9a0d-bf175bc7dc8f",
                    "2426cd8d-e930-4f56-8edf-19032a6fff56",
                    "ebcf91ee-c385-4612-8fab-675d4541e57c",
                    "e038b103-61d3-4612-b20a-d73ee1e3e5df",
                    "526596ec-592b-4c47-bb70-a3cf9bdf75a4",
                    "84b3af5c-c31a-477c-9160-bd64caa32851",
                ],
                "resumeAfterPowerInterruption": False,
            },
            "nodes": {
                "lowWater": {"warning": False, "empty": False},
                "waterTemperatureSensor": {
                    "current": {"celsius": 24.72},
                    "setpoint": {"celsius": 57.2},
                    "enabled": True,
                },
                "timer": {"mode": "idle", "initial": 7200},
            },
            "metadata": {},
        },
    },
}

A7_MESSAGE: dict[str, Any] = {
    "command": "EVENT_APC_STATE",
    "payload": {
        "cookerId": "a7_device",
        "type": "a7",
        "state": {
            "version": 1,
            "updatedTimestamp": "2024-06-13T03:11:47Z",
            "systemInfo": {
                "deviceId": "a7_device",
                "online": True,
                "firmwareVersion": "01.01.12",
                "releaseTrack": "production",
                "firmwareUpdatedTimestamp": "2024-05-20T04:15:07Z",
                "lastConnectedTimestamp": "2024-06-13T02:41:07Z",
                "lastDisconnectedTimestamp": "2024-05-31T05:25:50Z",
                "hardwareVersion": "1.0.0",
                "triacsFailed": False,
            },
            "state": {
                "mode": "idle",
                "temperatureUnit": "C",
                "processedCommandIds": [
                    "7345f32f-090f-4014-935d-a46855c35ca6",
                    "fc3e31da-ddd1-4b82-991e-7b52f767ce42",
                    "84ae5817-76e3-4dac-96d1-0f2a49979629",
                    "a272b1df-baed-45d1-aaa4-9ab59eb3fff5",
                    "9aa0ae14-f32b-4a63-9258-9d86463b89a6",
                    "06d9ea5a-d19e-453a-989c-79158c18bc6e",
                    "eb7ed511-807e-4bc8-ac87-bc0f9c88a605",
                    "1fc21251-f1f6-49f9-8747-533edd79a3c3",
                    "492231e1-c3b3-4750-8e5c-df07fa539477",
                    "47d0f847-b5f4-4072-a22a-311c4e71ebcc",
                ],
                "resumeAfterPowerInterruption": False,
            },
            "nodes": {
                "lowWater": {"warning": False, "empty": False},
                "waterTemperatureSensor": {
                    "current": {"celsius": 25.25},
                    "setpoint": {"celsius": 84.4},
                    "enabled": True,
                },
                "timer": {"mode": "idle", "initial": 36000},
            },
            "metadata": {},
        },
    },
}

A7_COOKING: dict[str, Any] = {
    "command": "EVENT_APC_STATE",
    "payload": {
        "cookerId": "a7_id",
        "type": "a7",
        "state": {
            "cook": {
                "activeStageIndex": 0,
                "stageTransitionPendingUserAction": False,
                "activeStageId": "6b70634f-ed6b-9154-6b30-05e73cec7a4e",
                "stages": [
                    {
                        "do": {
                            "timer": {
                                "entry": {
                                    "conditions": {
                                        "and": {
                                            "nodes.waterTemperatureSensor.current.celsius": {
                                                ">=": 54.17,
                                                "<=": 54.77,
                                            }
                                        }
                                    }
                                },
                                "initial": 0,
                            },
                            "type": "cook",
                            "waterTemperatureSensor": {"setpoint": {"celsius": 54.47}},
                        },
                        "id": "6b70634f-ed6b-9154-6b30-05e73cec7a4e",
                        "entry": {
                            "conditions": {
                                "and": {
                                    "nodes.waterTemperatureSensor.current.celsius": {
                                        "<=": 54.77,
                                        ">=": 54.17,
                                    }
                                }
                            }
                        },
                        "exit": {"conditions": {}},
                        "title": "Cook Stage",
                    }
                ],
                "originSource": "hardware",
                "activeStageStartedTimestamp": "2024-07-05T21:48:29Z",
                "startedTimestamp": "2024-07-05T21:48:29Z",
                "activeStageMode": "running",
                "cookId": "a098de4a-8714-2dd8-1bdc-d067008f2d4f",
            },
            "nodes": {
                "lowWater": {"empty": False, "warning": False},
                "timer": {
                    "mode": "running",
                    "initial": 1200,
                    "startedAtTimestamp": "2024-07-05T21:49:10Z",
                },
                "waterTemperatureSensor": {
                    "enabled": True,
                    "setpoint": {"celsius": 54.46},
                    "current": {"celsius": 55.27},
                },
            },
            "state": {
                "temperatureUnit": "F",
                "resumeAfterPowerInterruption": False,
                "processedCommandIds": [
                    "876cfbc9-03f1-400b-89ec-ef5391270846",
                    "e2e3ce06-45b4-4485-b4fa-9211c082b90d",
                ],
                "mode": "cook",
            },
            "systemInfo": {
                "firmwareVersion": "01.01.25",
                "deviceId": "5yMOd0D2lasOE2U8SkcIcS",
                "lastDisconnectedTimestamp": "2024-07-05T21:47:59Z",
                "triacsFailed": False,
                "releaseTrack": "production",
                "hardwareVersion": "1.0.0",
                "lastConnectedTimestamp": "2024-07-05T21:47:59Z",
                "online": True,
                "firmwareUpdatedTimestamp": "2024-06-07T18:56:03Z",
            },
            "metadata": {},
            "updatedTimestamp": "2024-07-05T21:49:56Z",
            "version": 1,
        },
    },
}
