"""
Types and enumerations for the CLOUD-M7 provenance schema.
"""

from enum import Enum


class TierType(str, Enum):
    """Distributed tier classifications for CLOUD-M7."""
    EDGE = "Edge"
    FOG = "Fog"
    CLOUD = "Cloud"


class EventType(str, Enum):
    """Forensic event types across heterogeneous multi-tier systems."""
    PROCESS = "Process"
    FILE = "File"
    SOCKET = "Socket"
    API = "API"


class ActionType(str, Enum):
    """Granular action type associated with provenance events."""
    # Process actions
    EXEC = "exec"
    FORK = "fork"
    EXIT = "exit"
    
    # File actions
    READ = "read"
    WRITE = "write"
    MODIFY = "modify"
    DELETE = "delete"
    
    # Socket actions
    CONNECT = "connect"
    ACCEPT = "accept"
    SEND = "send"
    RECEIVE = "receive"
    
    # Cloud / API actions
    AUTH_LOGIN = "auth_login"
    TOKEN_GENERATE = "token_generate"
    QUERY_DB = "query_db"
    EXFIL_DATA = "exfil_data"
