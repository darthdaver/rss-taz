from enum import Enum


class Request(str, Enum):
    REQUEST_STATE = "state"
    DRIVERS_CANDIDATE = "drivers_candidate"
    AVG_CANDIDATE_DISTANCE = "avg_candidate_distance"
    AVG_CANDIDATE_DURATION = "avg_candidate_duration"
    CANDIDATES_COUNT = "candidates_count"
    REJECTIONS = "rejections"
    CURRENT_CANDIDATE = "current_candidate"
    RESPONSE_COUNT_DOWN = "response_count_down"
    CANDIDATE_ID = "id"
    EXPECTED_DURATION = "expected_duration"
    SEND_REQUEST_BACK_TIMER = "send_request_back_timer"
    COST = "cost"
    CANDIDATE_STATE = "state"
    REQUESTS_SENT = "requests_sent"
