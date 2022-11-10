from src.stats.GlobalIndicators import GlobalIndicators
from src.stats.RidesStatistics import RidesStatistics
from src.stats.SpecificIndicators import SpecificIndicators
from src.stats.DriversStatistics import DriversStatistics
from src.stats.SimulatorPerformance import SimulatorPerformance


class Statistics:
    def __init__(
            self,
            sim_duration: int,
            taz_ids: list[str]
    ):
        self.global_indicators = GlobalIndicators(
            sim_duration,
            taz_ids
        )
        self.specific_indicators = SpecificIndicators(sim_duration)
        self.drivers_stats = DriversStatistics()
        self.ride_stats = RidesStatistics()
        self.simulator_performances = SimulatorPerformance()

    def export_statistics(self):
        self.global_indicators.export_global_indicators()
        self.specific_indicators.export_specific_indicators()
        self.simulator_performances.export_simulator_performances()
