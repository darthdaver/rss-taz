from src.types.EnergyIndexes import EnergyIndexesInfo

class GlobalIndicators:
    def __init__(self):
        self.__requested = { k: 0 for k in range(0,5001) }
        self.__canceled = { k: 0 for k in range(0,5001) }
        self.__accepted = { k: 0 for k in range(0,5001) }
        self.__not_served = { k: 0 for k in range(0,5001) }
        self.__rejections = { k: 0 for k in range(0,5001) }
        self.__tazs_stats = { k: {} for k in range(0,5001) }

    def get_global_indicators(self) -> EnergyIndexesInfo:
        return {
            "requested": self.__requested,
            "canceled": self.__canceled,
            "accepted": self.__accepted,
            "not_served": self.__not_served,
            "rejections": self.__rejections,
            "taz_stats": self.__tazs_stats
        }

    def received_request(
            self,
            timestamp: float
    ):
        self.__requested[int(timestamp)] += 1

    def accepted_request(
            self,
            timestamp: float
    ):
        self.__accepted[int(timestamp)] += 1

    def canceled_request(
            self,
            timestamp: float
    ):
        self.__canceled[int(timestamp)] += 1

    def request_not_served(
            self,
            timestamp: float
    ):
        self.__not_served[int(timestamp)] += 1

    def rejected(
            self,
            timestamp: float
    ):
        self.__rejections[int(timestamp)] += 1

    def taz_stats(
            self,
            timestamp: float,
            taz_id,
            stats
    ):
        self.__tazs_stats[int(timestamp)][taz_id] = stats