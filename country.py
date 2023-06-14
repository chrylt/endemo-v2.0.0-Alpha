import warnings

import industry_sector
import input
import output
import prediction_models
import sector


class Country:
    _name: str
    _abbreviations: [str]  # not implemented yet
    _population: prediction_models.PredictedTimeseries
    _gdp: prediction_models.TimeStepSequence
    _sectors: dict[sector.SectorIdentifier, sector.Sector]

    def __init__(self, name: str, input_manager: input.Input):
        self._name = name
        self._sectors = dict()

        # fill abbreviations
        self._abbreviations = input_manager.general_input.abbreviations[self._name]

        # create population timeseries
        self._population = \
            prediction_models.PredictedTimeseries(
                historical_data=input_manager.general_input.population[self._name].historical,
                prediction_data=input_manager.general_input.population[self._name].prognosis)

        # create gdp timeseries
        self._gdp = prediction_models.TimeStepSequence(
            historical_data=input_manager.general_input.gdp[self._name].historical,
            progression_data=input_manager.general_input.gdp[self._name].prognosis)

        # create sectors and pass on required data
        active_sectors = input_manager.ctrl.general_settings.get_active_sectors()

        if "industry" in active_sectors:
            self._sectors[sector.SectorIdentifier.INDUSTRY] = \
                industry_sector.Industry(self._name, self._population, self._gdp, input_manager)

        # TODO: add other sectors

        # create warnings
        if not self._abbreviations:
            warnings.warn("Country " + self._name + " has an empty list of Abbreviations.")
        if not self._population.get_data():
            warnings.warn("Country " + self._name + " has an empty list of historical Population.")
        if not self._population.get_prediction_raw():
            warnings.warn("Country " + self._name + " has an empty list of prediction for Population.")
        if not self._gdp.get_historical_data_raw():
            warnings.warn("Country " + self._name + " has an empty list of historical gdp.")
        if not self._gdp.get_interval_change_rate_raw():
            warnings.warn("Country " + self._name + " has an empty list of interval_changeRate for gdp.")

    def calculate_total_demand(self, year: int) -> output.Demand:
        total_demand = output.Demand()

        for sector_name, obj_sector in self._sectors.items():
            total_demand.add(obj_sector.calculate_total_demand(year))

        return total_demand

    def get_name(self):
        return self._name

    def get_population(self):
        return self._population

    def get_gdp(self):
        return self._gdp

    def get_sector(self, sector_id: sector.SectorIdentifier):
        return self._sectors[sector_id]
