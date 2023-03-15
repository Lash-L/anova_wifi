class AnovaException(Exception):
    pass


class AnovaOffline(AnovaException):
    pass


class InvalidLogin(AnovaException):
    pass


class NoDevicesFound(AnovaException):
    pass
