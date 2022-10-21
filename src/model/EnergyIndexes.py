from src.types.EnergyIndexes import EnergyIndexesInfo

class EnergyIndexes:
    def __init__(self):
        self.__requested = { k: 0 for k in range(0,5001)}
        self.__canceled = { k: 0 for k in range(0,5001)}
        self.__accepted = { k: 0 for k in range(0,5001)}
        self.__not_served = { k: 0 for k in range(0,5001)}
        self.__overhead = { k: [] for k in range(0,5001)}
        self.__price_fluctuation = { k: [] for k in range(0,5001)}

    def get_energy_indexes(self) -> EnergyIndexesInfo:
        return {
            "requested": self.__requested,
            "canceled": self.__canceled,
            "accepted": self.__accepted,
            "not_served": self.__not_served,
            "overhead": self.__overhead,
            "price_fluctuation": self.__price_fluctuation
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

    def compute_ovehead(
            self,
            timestamp_end: float,
            timestamp_request: float,
            estimated_ride_time: float
    ):
        overhead = ((timestamp_end - timestamp_request) - estimated_ride_time) / estimated_ride_time
        self.__overhead[int(timestamp_end)].append(overhead)

    def compute_price_fluctuation(
            self,
            timestamp: float,
            actual_price: float,
            estimated_price: float
    ):
        price_fluctuation = abs(actual_price - estimated_price) / estimated_price
        self.__price_fluctuation[int(timestamp)].append(price_fluctuation)
