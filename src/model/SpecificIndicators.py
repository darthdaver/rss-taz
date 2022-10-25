from src.types.EnergyIndexes import EnergyIndexesInfo

class SpecificIndicators:
    def __init__(self):
        self.__ride_stats = []

    def get_specific_indicators(self) -> EnergyIndexesInfo:
        return self.__ride_stats

    def ride_stats(
            self,
            stats
    ):
        self.__ride_stats.append(stats)