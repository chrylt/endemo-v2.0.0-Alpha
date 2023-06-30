from __future__ import annotations

from collections import namedtuple
from enum import Enum

import numpy as np
import pandas as pd

ProductSettings = namedtuple("ProductSettings", ("active", "manual_exp_change_rate", "perc_used"))


class ForecastMethod(Enum):
    """
    The ForecastMethod indicates the preferred way to extrapolate historical data.
    """
    LINEAR = 0
    QUADRATIC = 1
    EXPONENTIAL = 2


class ControlParameters:
    """
    The ControlParameter class holds the data given by the Set_and_Control_Parameters.xlsx file.
    It is split in general settings, and settings for each sector, indicating non-overlapping parameters for our model.
    """
    general_settings: GeneralSettings
    industry_settings: IndustrySettings

    def __init__(self, general_settings: GeneralSettings, industry_settings: IndustrySettings):
        self.general_settings = general_settings
        self.industry_settings = industry_settings


class IndustrySettings:
    """
    The IndustrySettings contain the parameters for the model given in Set_and_Control_Parameters.xlsx in the
    IND_general and IND_subsectors sheets.
    """
    forecast_map = dict({"Trend": ForecastMethod.LINEAR, "U-shape": ForecastMethod.QUADRATIC,
                         "Exponential": ForecastMethod.EXPONENTIAL})

    forecast_method: ForecastMethod
    time_trend_model_activation_quadratic: bool
    production_quantity_calc_per_capita: bool
    trend_calc_for_spec: bool
    h2_subst_of_heat: float
    nuts2_used_for_calculation: bool
    skip_years: [int]
    last_available_year: int
    product_settings: dict[str, ProductSettings]
    active_product_names: []
    rest_sector_growth_rate: float

    def __init__(self, ex_general: pd.DataFrame, ex_subsectors: pd.DataFrame):
        self.product_settings = dict()
        self.active_product_names = []
        forecast_method_string = ex_general[ex_general["Parameter"] == "Forecast method"].get("Value").iloc[0]
        self.forecast_method = IndustrySettings.forecast_map[forecast_method_string]

        self.time_trend_model_activation_quadratic = \
            ex_general[ex_general["Parameter"] == "Time trend model activation for U-shape method"].get("Value").iloc[0]

        self.production_quantity_calc_per_capita = \
            ex_general[ex_general["Parameter"] == "Production quantity calculated per capita"].get("Value").iloc[0]

        self.trend_calc_for_spec = \
            ex_general[ex_general["Parameter"] == "Trend calculation for specific energy requirements"].get(
                "Value").iloc[0]

        self.h2_subst_of_heat = \
            ex_general[ex_general["Parameter"] == "H2 substitution of heat"].get("Value").iloc[0]

        self.nuts2_used_for_calculation = \
            ex_general[ex_general["Parameter"] == "NUTS2 distribution based on installed industrial capacity"].get(
                "Value").iloc[0]

        skip_years_string = str(ex_general[ex_general["Parameter"] == "Skip years"].get("Value").iloc[0])
        self.skip_years = [int(i) for i in skip_years_string.split(",")]

        self.last_available_year = \
            ex_general[ex_general["Parameter"] == "Last available year"].get("Value").iloc[0]

        self.rest_sector_growth_rate = \
            ex_subsectors[ex_subsectors["Subsectors"] == "unspecified industry"].get(
                "Parameter: production quantity change in %/year").iloc[0]

        product_list = ex_subsectors.get("Subsectors")

        for product in product_list:
            active = \
                ex_subsectors[ex_subsectors["Subsectors"] == product].get(
                    "Active subsectors").iloc[0]
            prod_quant_change = \
                ex_subsectors[ex_subsectors["Subsectors"] == product].get(
                    "Parameter: production quantity change in %/year").iloc[0]
            sub_perc_used_string = \
                ex_subsectors[ex_subsectors["Subsectors"] == product].get(
                    "Parameter: technology substitution in %").iloc[0]
            try:
                sub_perc_used_float = float(sub_perc_used_string)
                sub_perc_used = sub_perc_used_float / 100
            except ValueError:
                sub_perc_used = 1

            self.product_settings[product] = ProductSettings(active, prod_quant_change, sub_perc_used)

            if self.product_settings[product].active:
                self.active_product_names.append(product)


class GeneralSettings:
    """
    The GeneralSettings contain the parameters for the model given in Set_and_Control_Parameters.xlsx in the
    GeneralSettings and Countries sheets.
    """
    _sectors_active_values: dict
    _parameter_values: dict

    target_year: int
    recognized_countries: [str]
    active_countries: [str]

    nuts2_version: int

    def __init__(self, ex_general: pd.DataFrame, ex_country: pd.DataFrame):
        self._sectors_active_values = dict()
        self._parameter_values = dict()
        self.target_year = int(ex_general[ex_general["Parameter"] == "Forecast year"].get("Value").iloc[0])
        self.recognized_countries = ex_country.get("Country")
        self.active_countries = ex_country[ex_country["Active"] == 1].get("Country")
        self.nuts2_version = int(ex_general[ex_general["Parameter"] == "NUTS2 classification"].get("Value").iloc[0])

        rows_it = pd.DataFrame(ex_general).itertuples()
        for row in rows_it:
            if row.Parameter.startswith('Sector: '):
                self._sectors_active_values[row.Parameter.removeprefix('Sector: ')] = row.Value
            else:
                self._parameter_values[row.Parameter] = row.Value

    def __str__(self):
        return ("sectors_active_values: " + str(self._sectors_active_values) + "\n" +
                "parameter_values: " + str(self._parameter_values))

    def get_active_sectors(self):
        # returns a list of sectors activated for calculation
        return [sector for (sector, isActive) in self._sectors_active_values.items() if isActive]

    def get_parameter(self, name: str):
        # return the parameter value by parameter name with meaningful error message
        try:
            return self._parameter_values[name]
        except KeyError:
            KeyError(
                "Parameter name not found. Does the parameter access string in the code match a parameter in the Set_and_Control_Parameters.xlsx input table?")
