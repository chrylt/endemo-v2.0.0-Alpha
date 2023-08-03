import os

import pandas as pd

from endemo2.data_analytics.prediction_models import Timeseries, Coef
from endemo2.general.demand_containers import Demand


class FileGenerator(object):
    """
    A tool to more easily generate output files.

    :ivar Input input_manager: A reference to the input_manager that holds all preprocessing.
    :ivar pd.ExcelWriter excel_writer: The excel writer used for writing the file.
    :ivar str current_sheet_name: Keeps track of the current sheet name that new entries (add_entry) will be written to.
    :ivar dict current_out_dict: Keeps the entries that are added.
        When writing the file, these are converted to a table.
    :ivar str out_file_path: The output file path. Mainly used as attribute for debugging.
    """

    # Example usage:
    #    fg = FileGenerator(input_manager, out.xlsx)
    #    with fg
    #        fg.start_sheet("Data")
    #        fg.add_entry("Country", "Belgium")
    #        fg.add_entry("Value", 0.5)
    #        fg.start_sheet("Info")
    #        fg.add_entry("Sources", "[1] ...")
    #        ...

    def __init__(self, input_manager, directory, filename):
        if directory == "":
            if not os.path.exists(input_manager.output_path):
                os.makedirs(input_manager.output_path)
            self.out_file_path = input_manager.output_path / filename
        else:
            if not os.path.exists(input_manager.output_path / directory):
                os.makedirs(input_manager.output_path / directory)
            self.out_file_path = input_manager.output_path / directory / filename

        self.input_manager = input_manager
        self.excel_writer = pd.ExcelWriter(self.out_file_path)
        self.current_sheet_name = ""
        self.current_out_dict = dict()

    def __enter__(self):
        self.current_sheet_name = ""
        self.current_out_dict = dict()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_file()

    def start_sheet(self, name):
        """ Start editing a new sheet with name "name". """
        if self.current_sheet_name != "":
            self.end_sheet()
        self.current_sheet_name = name
        self.current_out_dict = dict()

    def end_sheet(self):
        """ Stop editing current sheet. """
        df_out = pd.DataFrame(self.current_out_dict)
        df_out.to_excel(self.excel_writer, index=False, sheet_name=self.current_sheet_name, float_format="%.12f")
        self.current_sheet_name = ""
        self.current_out_dict = dict()

    def add_entry(self, column_name, value):
        """
        Add an entry to a column. But pay attention! In the end of the sheet, all columns have to have the same length.
        """
        if column_name not in self.current_out_dict.keys():
            self.current_out_dict[column_name] = []
        self.current_out_dict[column_name].append(value)

    def save_file(self):
        """ Save the dictionary that was filled by this object to a file. """
        if self.current_sheet_name != "":
            self.end_sheet()
        self.excel_writer.close()

def shortcut_coef_output(fg: FileGenerator, coef: Coef):
    exp_coef = coef._exp
    lin_coef = coef._lin
    quadr_coef = coef._quadr
    offset = coef._offset

    fg.add_entry("EXP Start Point", "(" + str(exp_coef[0][0]) + ", " + str(exp_coef[0][1]) + ")")
    fg.add_entry("EXP Change Rate", exp_coef[1])
    fg.add_entry("L k0", lin_coef[0])
    fg.add_entry("L k1", lin_coef[1])
    fg.add_entry("Q k0", quadr_coef[0])
    fg.add_entry("Q k1", quadr_coef[1])
    fg.add_entry("Q k2", quadr_coef[2])
    fg.add_entry("Offset", offset)


def shortcut_save_timeseries_print(fg, from_year, to_year, data: [(float, float)]):
    """ To correctly print, when data does potentially not cover every year."""

    i = from_year
    for (year, value) in data:
        if i > year:
            continue
        while i < year:
            fg.add_entry(i, "-")
            i += 1
        fg.add_entry(year, value)
        i += 1

    while i <= to_year:
        fg.add_entry(i, "-")
        i += 1

def shortcut_sc_output(fg, sc):
    fg.add_entry("Electricity [GJ/t]", sc.electricity)
    fg.add_entry("Heat [GJ/t]", sc.heat)
    fg.add_entry("Hydrogen [GJ/t]", sc.hydrogen)
    fg.add_entry("max. subst. of heat with H2 [%]", sc.max_subst_h2)

def shortcut_demand_table(fg: FileGenerator, demand: Demand):
    fg.add_entry("Electricity [TWh]", demand.electricity)
    fg.add_entry("Heat [TWh]", demand.heat.q1 + demand.heat.q2 + demand.heat.q3 + demand.heat.q4)
    fg.add_entry("Hydrogen [TWh]", demand.hydrogen)
    fg.add_entry("Heat Q1 [TWh]", demand.heat.q1)
    fg.add_entry("Heat Q2 [TWh]", demand.heat.q2)
    fg.add_entry("Heat Q3 [TWh]", demand.heat.q3)
    fg.add_entry("Heat Q4 [TWh]", demand.heat.q4)


def generate_timeseries_output(fg: FileGenerator, ts: Timeseries, year_from: int, year_to: int):
    # output coef
    coef = ts.get_coef()
    shortcut_coef_output(fg, coef)

    # output data
    shortcut_save_timeseries_print(fg, year_from, year_to, ts.get_data())



