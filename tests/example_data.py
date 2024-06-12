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
