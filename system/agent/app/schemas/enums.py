from enum import Enum

class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    APPLICATION = "application"
    INFRA = "infrastructure"
    SECURITY = "security"
    DATABASE = "database"
    NETWORK = "network"
    UNKNOWN = "unknown"

class SignalType(str, Enum):
    FAILURE = "failure"
    DEGRADATION = "degradation"
    NOISE = "noise"

