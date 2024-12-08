# Endemo v2.0.0 Alpha

**Endemo** is a Python-based energy demand forecasting model. It uses historical data and various regression methods (linear, quadratic, and custom quadratic with offset) to estimate future energy demand across multiple sectors (households, industry, transport, etc.). By breaking down the estimation into distinct sectors and subsectors, Endemo aims to produce more accurate forecasts of overall useful energy demand.

This repository is a ground-up rework of the original model [endemo](https://github.com/tum-ens/endemo/tree/main). It has been incorporated in the main repository [here](https://github.com/tum-ens/endemo/tree/endemo-v2).

## Key Features

- **Sector-Specific Modeling:** Each sector and subsector (e.g., steel production, household heating, transport types) is estimated separately for higher accuracy.
- **Data-Driven Forecasts:** Uses historical input data from Excel files and applies regression techniques to project future trends.
- **Flexible Regression Approaches:** Supports linear, standard quadratic, and custom quadratic-with-offset regressions.
- **Configurable Outputs:** Produces forecasts stored in Excel format. Plots and visualizations of input data and resulting forecasts can be optionally generated.
- **Structured Results:** Outputs are typically organized by sector, subsector, and estimation type (population, GDP, product output, heating demand, etc.).

## Project Structure

The model’s workflow involves reading input data, preprocessing and filtering instances, applying regression-based estimations, and consolidating the results. The included images illustrate how data, filters, and parameters flow through the model’s layers.

### High-Level Flow

1. **Input & Settings:** Load input Excel files and configuration parameters.
2. **Preprocessing:** Process and group data. Extract coefficients and define country groups.
3. **Instance Filters & Model Setup:** Apply sector, country, and product filters, then run the model scenarios.
4. **Forecasting & Output:** Run regression estimates, produce forecast data, and (optionally) generate plots.

![Slide27](https://github.com/user-attachments/assets/1c5a97a0-5d65-4e3b-9ed2-eeb0c8425c3b)
![Slide24](https://github.com/user-attachments/assets/0a68f3e8-2544-4100-8fd3-2a9266340bb2)

## Documentation

Detailed documentation of the source code is located in `docs/_build/html/index.html`. Open this file in a web browser for full API references and usage guidelines.

For frequent use, consider bookmarking the documentation page.

## Installation

**Recommended:** Use Anaconda or Mamba for managing the Python environment.  
**Python Version:** 3.10 recommended.

### Using Anaconda/Mamba (Recommended)

1. Install [Anaconda](http://continuum.io/downloads) or [Mamba](https://github.com/conda-forge/miniforge#mambaforge) (64-bit preferred).
2. Download the `endemo-env.yml` environment file from this repository.
3. Open a new terminal and run:
   ```bash
   conda env create -f endemo-env.yml
   conda activate endemo
   ```
4. If needed, initialize conda:
   ```bash
   conda init
   ```

### Manual Installation

If not using Anaconda/Mamba, install packages listed in `endemo-env.yml` manually. Ensure compatibility with Python 3.10 if possible.

## Getting Started

1. Navigate to the directory where you cloned or downloaded Endemo.
2. Run:
   ```bash
   python main.py
   ```
3. The results, including output Excel files (and optionally generated plots), will be stored in the `output` directory.

## Contributing

For developers, we recommend using Git with SSH keys for secure access.  
[Git Installation](http://git-scm.com/) instructions and [SSH key setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) are available on the official GitHub documentation.

For pull requests, please ensure code quality, include tests where applicable, and update documentation as needed.

---

This revised README gives a clearer, more direct overview of the project's purpose, features, installation steps, usage instructions, and structure. It also highlights the input/output formats and how to access documentation for further details.
