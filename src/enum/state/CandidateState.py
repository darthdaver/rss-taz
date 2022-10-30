from enum import Enum

class CandidateState(str, Enum):
    PROCESSED = "PROCESSED"
    QUEUE = "QUEUE"