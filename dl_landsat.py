import datetime
import os

import ee
import numpy as np
import gdown
from ee.batch import Export
from osgeo import gdal
from osgeo.gdal import Dataset

LANDSAT_8 = "LANDSAT/LC08/C02/T1_L2"
# T1_L2 = surface reflectance, T1 = raw landsat
# For grabbing panchromatic band, comment out thermal_bands and lines below image.addBands(optical_bands) .
# Change image.select to 'B8'

def apply_scale_factors_8(image):
    # Magic numbers from GEE
    optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)

    image = (image.addBands(optical_bands, None, True)
             .addBands(thermal_bands, None, True))
    image = (image.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10", "QA_PIXEL"])
             .rename(["B1", "B2", "B3", "B4", "B5", "B7", "ST", "QA_PIXEL"]))
    return image

def apply_scale_factors_8_pan(image):
    # Magic numbers from GEE
    optical_bands = image.select('B8').multiply(0.0000275).add(-0.2)

    image = image.addBands(optical_bands, None, True)
             
    return image

def mask_clouds(image):
    qa = image.select("QA_PIXEL")

    mask = (qa.bitwiseAnd(1 << 3).And(qa.bitwiseAnd(1 << 9))
            .Or(qa.bitwiseAnd(1 << 4).And(qa.bitwiseAnd(1 << 11)))
            .Or(qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 13)))
            )

    image = image.updateMask(mask.Not())

    return image


def create_bounding_box(point: ee.Geometry.Point, diameter: float):
    intermediate_circle = point.buffer(diameter / 2.0, 0.0)
    return intermediate_circle.bounds()


def digits_after_decimal(number: float):
    return str(number)[::-1].find('.')


def export_to_drive(city_coords, years=None, months=None,
                    base_folder_name=None, auth=False, verbose=True,
                    export_radius=20000):
    # Trigger the authentication flow.
    if auth:
        ee.Authenticate()

    # Initialize GEE Libary.
    ee.Initialize()

    city = ee.Geometry.Point(city_coords)  # Coord format: E, N
    if months is None:
        months = list(range(1, 12))
    if years is None:
        years = list(range(2013, 2022))
    if base_folder_name is None:
        base_folder_name = f"lat_{int(city_coords[0] * 10 ** digits_after_decimal(city_coords[0]))}" + \
                           f"lon_{int(city_coords[1] * 10 ** digits_after_decimal(city_coords[1]))}"
    base_path = f"data/{base_folder_name}"
    if not os.path.isdir(base_path):
        os.makedirs(base_path)
    if verbose:
        print("Saving in drive folder: ")
        print(base_folder_name)
        print("Creating Folder on local machine: ")
        print(base_path)
    task_list = []
    for year in years:
        if verbose:
            print(f"At Year: {year}")
        bounding_box = create_bounding_box(city, export_radius)
        ls_read = None
        for month in months:
            if ls_read is None:
                ls_read = (ee.ImageCollection(LANDSAT_8)
                           .map(apply_scale_factors_8)
                           .filterBounds(city)
                           .filter(ee.Filter.calendarRange(year, year + 1, "year"))
                           .filter(ee.Filter.calendarRange(month, month + 1, "month"))
                           .map(mask_clouds)
                           )
            else:
                ls_read_ = (ee.ImageCollection(LANDSAT_8)
                            .map(apply_scale_factors_8)
                            .filterBounds(city)
                            .filter(ee.Filter.calendarRange(year, year + 1, "year"))
                            .filter(ee.Filter.calendarRange(month, month + 1, "month"))
                            .map(mask_clouds)
                            )
                ls_read = ls_read.merge(ls_read_)
        if verbose:
            print("Number of exported Months:")
            print(ls_read.size().getInfo())
            time_stamps = ls_read.aggregate_array("system:time_start").getInfo()
            dates = list(
                map(lambda x: datetime.datetime.fromtimestamp(x / 1e3).strftime("%Y/%m/%d %H:%M"), time_stamps))
            print("Months Exported:")
            print(dates)
        ls_median = ls_read.median()
        projection = ls_read.first().select("B1").projection().getInfo()
        if verbose:
            print("Projection Used: ")
            print(projection)
        task = Export.image.toDrive(ls_median,
                                    description=f"image_{year}",
                                    folder=base_folder_name,
                                    crs=projection['crs'],
                                    crsTransform=projection['transform'],
                                    region=bounding_box,
                                    fileFormat="GeoTIFF",
                                    maxPixels=10000000000000)
                                    
        task.start()
        task_list.append(task)
    download_drive_folder(task_list)

def download_drive_folder(task_list):
    while any(task.status().get('state') != task.State.COMPLETED for task in task_list):
        print(task_list[-1].status().get('state'))
        print('~~~~~~~~~~~~~~~~~~~~~~')
        
    status = ee.batch.Task.status(task_list[-1])
    folder_link = status.get('destination_uris')
    folder_id = folder_link[0].split('/')[-1]
    folder_id = 'https://drive.google.com/drive/folders/' + folder_id
    print('folder id: ', folder_id)

    gdown.download_folder(url=folder_id, quiet=True, use_cookies=True, output=f'data/')

def export_to_numpy(years, base_folder_name, band_list):
    images = []
    base_path = f"data/{base_folder_name}"
    for year in years:
        base_path_year = f"{base_path}/image_{year}.tif"
        ds = gdal.Open(base_path_year, gdal.GA_ReadOnly)
        if not ds and not isinstance(ds, Dataset):
            raise Exception(f"could not read file: {base_path_year}")
        img_array = ds.ReadAsArray(band_list=band_list)
        min_side = min(img_array.shape[1], img_array.shape[2])
        img_array = img_array[:, :min_side, :min_side]
        images.append(img_array)

    data_set = np.asarray(images)
    print(data_set[:-1].shape)
    print(data_set[-1:].shape)
    np.save(f"{base_path}/data_raw", data_set)
    np.save(f"{base_path}/train_raw", data_set[:-1])
    np.save(f"{base_path}/test_raw", data_set[-1:])


# Tokyo: 139.6503, 35.6762
# Pohang-si: 129.3145, 36.0030 (Works)

# nairobi center: 36.74905523581975, -1.2815372605877613
# nairobi east: 36.86905523581975, -1.2815372605877613 
# Accra Ghana: -0.1870, 5.6037 (try a bit further north)
# Athi river Kenya: 36.9785, -1.4577
# Cape Town South Africa: 18.655297, -33.991888
# Dar es salaam Tanzania: 39.266257, -6.836356
# Davao PH: 125.567598, 7.052342
# Freetown Sierra Leone: -13.248984, 8.483229
# Kampala Uganada: 32.584486, 0.323141
# Kisumu Kenya: 34.769850, -0.095443
# Lagos Nigeria: 3.351209, 6.421560
# Malabon PH: 120.960334, 14.665835
# My house: 121.005953, 14.479313
# Port Harcourt Nigeria: 7.031628, 4.761043
# Tamagawa River 139.635918, 35.601604

# Caracas -66.8032216, 10.4692009

if __name__ == '__main__':
    base_folder_name = "caracas_images"
    years = list(range(2013, 2022))
    point = [-66.8032216, 10.4692009]
    export_to_drive(point, base_folder_name=base_folder_name, years=years)

    # Note it is adivable to inspect the data with QGis beforehand and they need to be downloaded from Gdrive
    band_list = [1, 2, 3, 4, 5, 6, 7, 8]
    export_to_numpy(years, base_folder_name, band_list)
