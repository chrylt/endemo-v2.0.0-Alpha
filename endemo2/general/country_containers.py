from __future__ import annotations

import enum
import warnings
from typing import Any, Union

from endemo2.utility import utility as uty
from endemo2.utility import prediction_models as pm
from endemo2.general import demand_containers as ctn
from endemo2.utility.prediction_models import Timeseries


class GroupType(enum.Enum):
    SEPARATE = 0
    JOINED = 1
    JOINED_DIVERSIFIED = 2
    EMPTY = 3


class Population:
    """
    Holds information about a countries' population. Contains per-country data, as well as nuts2 data

    :ivar DataManualPrediction country_level_population: The object containing population information and predictions
        on a country level.
    :ivar NutsRegion nuts2: The root of the Nuts2 Tree for a country.
    :ivar bool nuts2_used: Decides, which type of population should be used for getters.
    """

    def __init__(self, country_level_population: pm.DataManualPrediction, nuts2: NutsRegion, nuts2_used: bool = False):
        self.country_level_population = country_level_population
        self.nuts2 = nuts2
        self.nuts2_used = nuts2_used

    def get_data(self) -> [(float, float)]:
        """
        Getter for data based on whether nuts2_used is true or not.

        :return: Nuts2 population data if nuts2_used is true, otherwise country level data.
        """
        if self.nuts2_used and self.nuts2:
            return self.nuts2.get_historical_data()
        else:
            return self.country_level_population.get_data()

    def get_country_historical_data(self) -> [(float, float)]:
        """ Getter for the country-level historical data. """
        return self.country_level_population.get_data()

    def get_prog(self, year: int) -> float:
        """
        Getter for population prognosis based on whether nuts2_used is true or not.

        :return: Nuts2 population prognosis if nuts2_used is true, otherwise country level data.
        """
        if self.nuts2_used and self.nuts2:
            return self.nuts2.get_pop_prog(year)
        else:
            return self.country_level_population.get_prog(year)

    def get_country_prog(self, year: int) -> float:
        """ Getter for the country-level prognosis. """
        return self.country_level_population.get_prog(year)

    def get_nuts2_prog(self, year: int) -> float:
        """ Getter for the nuts2 prognosis. """
        return self.nuts2.get_pop_prog(year)

    def get_nuts2_root(self) -> NutsRegion:
        """ Getter for the nuts2 regions root node object. """
        return self.nuts2


class NutsRegion:
    """
    Represents one NUTS Region according to individual codes.

    Generally, NUTS Regions are build as a tree structure to include sub-regions as child nodes and have NUTS2 regions
        as leafs.

    :ivar str region_name: The NUTS tag of the region. For example: DE, DE1, DE11, ...
    """
    def __init__(self, region_name: str):
        self.region_name = region_name


class NutsRegionLeaf(NutsRegion):
    """
    Represents one NUTS2 Region according to individual codes. It is the leaf of the NUTS tree.

    :ivar str region_name: The NUTS tag of the region. For example: DE, DE1, DE11, ...
    :ivar dict[str, NutsRegion] _subregions: The child regions, accessible per NUTS tag. For DE: {DE1 -> .., DE2 -> ..}
    :ivar DataAnalyzer _ts_population: The timeseries for the value the tree is associated with.
    :ivar [(float, float)] _population_historical: The historical population for this region.
        Should only be filled for leaf nodes.
    """
    def __init__(self, region_name: str, data: Any):
        super().__init__(region_name)
        self.data = data

    def __str__(self):
        return "[leaf: " + self.region_name + "]"

    def get(self):
        return self.data


class NutsRegionNode(NutsRegion):
    """
    Represents one NUTS Region according to individual codes. Not a NUTS2 region, but a node in the tree.

    :ivar str region_name: The NUTS tag of the region. For example: DE, DE1, DE11, ...
    :ivar dict[str, NutsRegion] _subregions: The child regions, accessible per NUTS tag. For DE: {DE1 -> .., DE2 -> ..}
    """

    def __init__(self, region_name: str):
        super().__init__(region_name)
        self._sub_regions = dict[str, Union[NutsRegionNode, NutsRegionLeaf]]()

    def __str__(self):
        out = "[root: " + self.region_name + ", children: "
        for key, value in self._sub_regions.items():
            out += key + ", "
        out += "]"
        for _, child in self._sub_regions.items():
            out += str(child)
        return out

    def get_region_name(self):
        """ Getter for the region_name. """
        return self.region_name

    def add_leaf_region(self, nuts2region_obj: NutsRegionLeaf) -> None:
        """
        Traverses the NUTS Tree recursively to insert region node.

        :param nuts2region_obj: The NutsRegion object to insert into the tree
        """
        if len(self.region_name) + 1 is len(nuts2region_obj.region_name):
            # region is direct subregion
            self._sub_regions[nuts2region_obj.region_name] = nuts2region_obj
        elif len(self.region_name) + 1 < len(nuts2region_obj.region_name):
            # region is a subregion of a subregion, search for right one to insert
            for key, value in self._sub_regions.items():
                if nuts2region_obj.region_name.startswith(key):
                    # found parent region
                    self._sub_regions[key].add_leaf_region(nuts2region_obj)
                    return
            # found no region, create in-between
            new_inbetween_region_name = nuts2region_obj.region_name[:len(self.region_name)+1]
            new_inbetween_obj = NutsRegionNode(new_inbetween_region_name)
            new_inbetween_obj.add_leaf_region(nuts2region_obj)
            self._sub_regions[new_inbetween_region_name] = new_inbetween_obj

    def get_historical_data(self) -> [(float, float)]:
        """
        Get historical data or sum over subregions if not available.

        :return: The historical population amount for this region.
        """
        if self._population_historical is None:
            subregion_objs = list(self._sub_regions.values())
            result = subregion_objs[0].get_historical_data()
            for subregion_obj in subregion_objs[1:]:
                result = list(uty._zip_on_x_generator(result, subregion_obj.get_historical_data()))
                result = [(x1, y1 + y2) for ((x1, y1), (x2, y2)) in result]
            self._population_historical = result
        return self._population_historical

    def get_pop_his_year(self, year: int) -> float:
        """
        Get the historical population of self for a certain year.

        :param year: The target year.
        :return: The population amount of a certain year, as recorded in historical data.
        """
        if self._population_historical is not None:
            for (y, a) in self._population_historical:
                if y == year:
                    return a
        else:
            result = 0
            for subregion in self._sub_regions.values():
                result += subregion.get_pop_his_year(year)
            return result

    def get_pop_prog(self, year: int) -> float:
        """
        Recursively calculate and sum up the prognosis for all leaf regions.

        :param year: The year the prognosis should be done for.
        :return: The population amount prognosis for this region.
        """
        result = 0
        if len(self._sub_regions) != 0:
            for subregion in self._sub_regions.values():
                result += subregion.get_pop_prog(year)
            return result
        else:
            return self._ts_population.get_prog(year)

    def get_pop(self, year: int) -> float:
        """
        Get the amount of population in a certain year. Uses historical data when available, else does a prognosis.

        :param year: The target year.
        :return: The amount of population in a certain year, historical or prognosis.
        """
        result = 0
        if len(self._sub_regions) != 0:
            for subregion in self._sub_regions.values():
                result += subregion.get_pop(year)
            return result
        else:
            return self._ts_population.get_value(year)

    def get_node(self, region_code: str) -> NutsRegion:
        """
        Traverse tree and find the node with region code.

        :param region_code: The region code of the node to find.
        :return: The NutsRegion object of the region with region_code.
        """
        if len(self.region_name) + 1 is len(region_code):
            # region is direct subregion
            return self._sub_regions[region_code]
        elif len(self.region_name) + 1 < len(region_code):
            # region is a subregion of a subregion, search for right one to insert
            for key, value in self._sub_regions.items():
                if region_code.startswith(key):
                    # found parent region
                    return self._sub_regions[key].get_node(region_code)

    def get_nodes_dfs(self) -> [NutsRegion]:
        """
        Get a list of all nodes in Depth-First-Search order.

        :return: The list of nodes in DFS-order.
        """
        if len(self._sub_regions) == 0:
            # leaf node, return only self
            return [self]
        else:
            # recursively return this node and all children
            nodes = [self]
            for subregion in self._sub_regions.values():
                nodes += subregion.get_nodes_dfs()
            return nodes

    def get_all_leaf_nodes(self) -> [NutsRegion]:
        """
        Get a list of all leaf nodes order.

        :return: The list of leaf nodes.
        """
        if len(self._sub_regions) == 0:
            # leaf node, return only self
            return [self]
        else:
            # recursively return this node and all children
            nodes = []
            for subregion in self._sub_regions.values():
                nodes += subregion.get_all_leaf_nodes()
            return nodes

    def get_pop_perc_of_subregion_in_year(self, region_obj: NutsRegion, year: int):
        """
        Calculate the percentage of the population proportion in given subregion.
        The population of self denotes 100%.

        :param NutsRegion region_obj: Region object of the subregion which population proportion should be used.
        :param year: Year the population proportion should be calculated for.
        :return: The percentage of subregion population that makes up population of self.
        """
        sub_pop_amount = region_obj.get_pop(year)
        self_pop_amount = self.get_pop(year)
        return sub_pop_amount / self_pop_amount

