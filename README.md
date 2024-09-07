# Remote Sensing Landuse
This repository was used in the completion of my Master's Thesis entitled "Evaluation of climate risks on satellite-detected morphological slums of 10 municipalities" under the Global Urban Climate Studies Laboratory at Tokyo Institute of Technology. This uses Landsat 8 bands and ESA WorldCover 2021 data to cluster urban build-up pixels of morphological slums in the given study areas. The shapefiles of the slum zones were kindly provided by Dr. Dana Thomson and her team found here: https://github.com/hazemmahmoud88/KnowYourCity-data-for-research.

## Setup

Create a conda enviroment:

```
conda create --name remote-sensing-landuse python=3.8
```

Install the python deps

```
 conda env update --file enviroment.yml
```

Install terracatalogueclient

```
pip install --extra-index-url https://artifactory.vgt.vito.be/api/pypi/python-packages/simple terracatalogueclient 
```
When running the authentication with `Catalogue().authenticate()`, run it in a Jupyter Notebook using the appropriate kernel.

You need to install gcloud in order to run the program in the CLI, see: https://cloud.google.com/cli

## Repository Structure
### dl_landcover.py
A script for downloading ESA WorldCover land cover data, which provides a global land use classification with a 10m resolution. This data is critical for classifying urban vs. non-urban pixels.

### dl_landsat.py
This script downloads Landsat 8 satellite images. It provides multi-spectral data, which is used to analyze urban zones and detect morphological slums based on their spectral characteristics.

### hazard_analysis.ipynb
This notebook performs an analysis of environmental hazards in the study areas. It .

Key tasks:
- Loading CMORPH precipitation dataset. Note that the dataset is very heavy and can take a few hours, running on a strong machine is recommended.
- Utilizing the IDF analysis repository found at https://github.com/MarkusPic/intensity_duration_frequency_analysis to calculate rainfall hazard values of the study areas
- Opens WRF simulation results and calculates UTCI

### risk_evaluation.ipynb
This notebook builds upon the hazard analysis by evaluating the overall risk levels in slum areas. It integrates hazard data with vulnerability and exposure information to assess the risk climate change poses to these areas.

Key tasks:
- Calculation of risk scores based on the hazard severity, assets (population), and the vulnerability levels of slum regions.
- Statistical summaries and interpretation of risk data.

### slum_statistics.ipynb
This notebook is dedicated to generating statistical summaries of the slum areas identified through clustering.

Key tasks:
- Extracting demographic and spatial statistics related to slum areas.
- Aggregating the cluster outputs to provide a quantitative overview of the slum zones.

### wrf_results_extract.ipynb
This notebook deals with the Weather Research and Forecasting (WRF) model. The WRF model is commonly used for weather prediction and climate modeling. This notebook extracts and analyzes the results from a WRF simulation for the study areas.

Key tasks:
- Loading and extracting relevant meteorological data from WRF output files.
- Performing spatial and temporal analysis of climate factors (temperature, rainfall) affecting the morphological slums.
- Comparing model results with observed data to validate predictions or generate insights.
