"""
This module contains all things shared by the different preprocessing stages.
"""

from endemo2.preprocessing.preproccessing_step_two import GroupManager
from input.input import Input
from endemo2.preprocessing import preprocessing_step_one as pp1


class Preprocessor:
    """
    The preprocessor controls the execution of the different preprocessing stages.
    """

    def __init__(self, input_manager: Input):

        self.countries_pp = dict[str, pp1.CountryPreprocessed]()

        # preprocess stage 1
        for country_name in input_manager.ctrl.general_settings.active_countries:
            self.countries_pp[country_name] = pp1.CountryPreprocessed(country_name, input_manager)
            
        # preprocess stage 2
        self.group_manager = GroupManager(input_manager, self.countries_pp)

