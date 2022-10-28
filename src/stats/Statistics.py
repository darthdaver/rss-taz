from src.stats.GlobalIndicators import GlobalIndicators
from src.stats.SpecificIndicators import SpecificIndicators
from src.stats.DriversStatistics import DriversStatistics
from src.stats.SimulatorPerformance import SimulatorPerformance


class Statistics:
    def __init__(self):
        self.global_indicators = GlobalIndicators()
        self.specific_indicators = SpecificIndicators()
        self.drivers_stats = DriversStatistics()
        self.simulator_performances = SimulatorPerformance()

    def export_statistics(self):
        self.global_indicators.export_global_indicators()
        self.specific_indicators.export_specific_indicators()
        self.simulator_performances.export_simulator_performances()