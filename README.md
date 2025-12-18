
# From Redlining to Today: HOLC Grades and Housing Inequality in the Bay Area

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCB-stat-159-f25/final-group10/main?labpath=Main.ipynb)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17970670.svg)](https://doi.org/10.5281/zenodo.17970670)


## Project Motivation
This project examines whether historical redlining continues to shape housing outcomes decades after discriminatory policies were formally banned. Using Home Owners’ Loan Corporation (HOLC) redlining maps alongside U.S. Census and housing value data, we explore whether neighborhoods and counties with greater historical redlining exposure experienced different housing value trajectories after the 1968 Fair Housing Act. The analysis is exploratory in nature and aims to understand long-run patterns rather than establish definitive causal claims.

---

## Data Sources
- **HOLC Redlining Maps**  
  Mapping Inequality Project (University of Richmond):  
  https://dsl.richmond.edu/panorama/redlining/
- **Housing and Demographic Data**  
  U.S. Census Bureau / American Community Survey (ACS)
- **Supplementary National Data**  
  Federal Reserve Economic Data (FRED):  
  https://fred.stlouisfed.org/tags/series?t=redlining


---

## Analysis Overview
The project consists of 2 main components:
1. **Historical Context**: Time-series exploration of national housing and demographic patterns by HOLC grade.
2. **Bay Area Case Study**: Spatial analysis combining HOLC maps with ACS data for selected Bay Area counties.

The primary outcome of interest is median home value.

---

## Repository Structure

**`data`**: Contains raw and processed datasets used in the analysis

**`figures`**: Contains generated figures, maps, and plots

**`src`**: Contains reusable analysis and modeling functions  

**`Main.ipynb`**: Main project notebook summarizing methods, results, and findings

**`01_holc_timeseries.ipynb`**: National-level HOLC time series exploration  
**`02_holc_redlining_bay_area.ipynb`**: Bay Area HOLC and ACS spatial analysis  
**`03_acs_data_bay_area.ipynb`**: ACS data exploration

**`environment.yml`**: Conda environment file specifying required packages

**`README.md`**: Project overview and instructions for running the analysis


---

## Installation and Setup

### 1. Create the environment
```bash
conda env create -f environment.yml
conda activate redlining-analysis
```
### 2. jupyter lab

## Running the Analysis
1. Ensure all data files are located in the data/ directory.
2. Open notebooks/main_analysis.ipynb.
3. Run all cells from top to bottom to reproduce figures, tables, and results.
4. Generated plots will be saved automatically to the figures/ directory.

## Testing and Reproducibility
Core analytical steps (e.g., difference-in-differences regression) are modularized in src/ to improve reproducibility and clarity. While formal unit testing is limited due to the exploratory nature of the analysis, functions are designed to be reusable and transparent. Re-running the main notebook from a clean environment reproduces all results and figures.

## Notes

This project is exploratory and descriptive. While statistical models are used, results should be interpreted as suggestive patterns rather than definitive causal estimates. The analysis highlights how historical institutional practices may continue to shape present-day housing outcomes despite later policy interventions.
