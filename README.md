# Remote Sensing Landuse
This repository, specifically this branch, was used in the completion of my Master's Thesis entitled "Evaluation of climate risks on satellite-detected morphological slums of 10 municipalities" under the Global Urban Climate Studies Laboratory at Tokyo Institute of Technology. This uses Landsat 8 bands and ESA WorldCover 2021 data to cluster urban build-up pixels of morphological slums in the given study areas. The shapefiles of the slum zones were kindly provided by Dr. Dana Thomson and her team found here: https://github.com/hazemmahmoud88/KnowYourCity-data-for-research.

Next, CMORPH precipitation data and WRF simulations were used to calculate the potential extreme climate hazard values for each morphological slum cluster. Finally, the overall climate risk of each of the study areas were evaluated using the variables stated in my thesis, forming the risk equation.

Note: the files and processes concerning IIC are not used in my final pipeline, but were used as the foundation based on the work of David Winderl in our lab. You can see more about this in the main branch.
## Setup
First, you have to clone the repository and create a conda environment on your machine ensuring the appropriate python version. The dependencies are stored in the yml file. Prior to utilizing the pipeline formed in this repository, you need to have registered in Google Earth Engine and Terra Catalogue. Run the commands below and prepare which satellite images you want to download.
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

## General Pipeline
An outline of the process done to complete my thesis is provided here.
1. Setup repository and select your data
2. Download appropriate satellite images through dl_landcover.py and dl_landsat.py
3. Process these images in clustering_slums.ipynb and cluster the raster files based on your specifications.
4. Process the resulting morphological slum clusters in QGIS for easier visualization. Flow for this is specified in the compilation of QGIS files ran on my local machine, not in this repository.
5. Download the CMORPH precipitation dataset through webscraping found in cmorph_downloader.ipynb/py
6. Load the data in the hazard_analysis.ipynb to get the IDF values and UTCI from WRF simulations.
7. Calculate Risk values of each study area through risk_evaluation.ipynb.
8. slum_statistics.ipynb and wrf_results_extract.ipynb are used for supplementary data processing.

## Repository Structure
Brief explanations on each file is provided here along with notes on how to use them for future studies.

### clustering_slums.ipynb
This notebook is responsible for running the actual clustering algorithm to detect morphological slums using satellite data.

Key Tasks:
- Load preprocessed Landsat 8 and ESA WorldCover images.
- Preprocess the satellite bands and calculate information such as NDVI and Water index.
- Apply clustering algorithm (e.g., Bisecting KMeans) on urban build-up pixels to determine which cluster corresponds to the morphological slums.
- Visualize results on maps and download them as raster files.

Notes:
- Pipeline follows from top to bottom, just make sure to specify the correct files and bands you are interested in. Follow the IMAGE_RAW variable to understand the flow.
- Specify the k value and BANDS_USED for the clustering. You can cluster to a higher level of a particular cluster (hierarchial clustering) following the IMAGE_MAP_SLUM variable.

### cmorph_downloader.ipynb/py
CMORPH is a precipitation dataset derived from satellite observations. This file handles the web scraping of the 30min 8km resolution dataset. You can modify the time frame you wish to download. Notebook and script versions are available for convenience.

### dl_landcover.py
A script for downloading ESA WorldCover land cover data, which provides a global land use classification with a 10m resolution. This data is critical for classifying urban vs. non-urban pixels.

How to use:
Ensure your terracatalogue authentication is successful. Note that there are cases where Catalogue.authenticate() does not work, and you might need to use authenticate_non_interactive instead. 

Next, change the coords variable in main to the center point of your study area, then change the data folder name respectively.

### dl_landsat.py
This script downloads Landsat 8 satellite images. It provides multi-spectral data, which is used to analyze urban zones and detect morphological slums based on their spectral characteristics.

How to use:
There is a global LANDSAT_8 variable that determines which collection to download from. Refer to the earth engine catalog.
The bands are selected in the apply_scale_factors method.

To download the images, you first need to authenticate your earth engine credentials, then you need to make a Google Drive folder with the same name as the folder name specified in main. Make sure this folder is publicly accessible and editable for the program to store the files properly. After running export_to_drive for the images, export_to_numpy transforms them into numpy arrays suitable for analysis.

Lastly, specify the range of years, coordinates and band_list of your study area you want to analyze.

### hazard_analysis.ipynb
This notebook performs an analysis of extreme climate hazards in the study areas. The hazard values used in the master's thesis' Risk Equations are directly taken from here.

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
This notebook is dedicated to generating statistical summaries of the slum areas identified through clustering. The histogram files were processed in QGIS to provide the values for each cluster in the respective study areas.

Key tasks:
- Extracting demographic and spatial statistics related to slum areas.
- Aggregating the cluster outputs to provide a quantitative overview of the slum zones.

### wrf_results_extract.ipynb
This notebook deals with the Weather Research and Forecasting (WRF) model. The WRF model is commonly used for weather prediction and climate modeling. This notebook extracts and analyzes the results from a WRF simulation for the study areas.

Key tasks:
- Loading and extracting relevant meteorological data from WRF output files.
- Performing spatial and temporal analysis of climate factors (temperature, rainfall) affecting the morphological slums.
- Comparing model results with observed data to validate predictions or generate insights.
