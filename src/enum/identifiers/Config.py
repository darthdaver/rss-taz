from enum import Enum

class Config(str, Enum):
    PERSONALITY_DISTRIBUTION = "personality_distribution"
    ACCEPTANCE_DISTRIBUTION = "acceptance_distribution"
    ROUTE_LENGTH_DISTRIBUTION = "route_length_distribution"
    TIMER_REMOVE_IDLE_DRIVER = "timer_remove_idle_driver"
    STOP_WORK_DISTRIBUTION = "stop_work_distribution"
    MOVE_DISTRIBUTION = "move_distribution"
    MOVE_DIFF_PROBABILITIES = "move_diff_probabilities"
    CHECKPOINTS = "checkpoints"
    TIME_MOVE_DRIVER = "time_move_driver"
    SIMULATION_DURATION = "simulation_duration"
    TIME_UPDATE_SURGE_MULTIPLIER = "time_update_surge_multiplier"
    CUSTOMER = "customer"
    DRIVER = "driver"
    RIDE = "ride"
