from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
OUTPUTS = BASE_DIR / "outputs"

# Case Study: Seattle University Link Extension
# Opening Date: March 2016
INTERVENTION_YEAR = 2016

# Coordinates (Lat, Lon)
STATIONS = {
    "University of Washington": (47.6503, -122.3016),
    "Capitol Hill": (47.6198, -122.3200)
}

# Analysis Settings
YEARS = [2014, 2015, 2016, 2017, 2018]
STATE = "wa"
LODES_BASE_URL = "https://lehd.ces.census.gov/data/lodes/LODES8"

# Distances in degrees (approximate for simplicity in raw calculations, 
# but better to use projection in GeoPandas).
# 1 degree lat ~ 69 miles. 0.01 deg ~ 0.7 miles.
# We will use GeoPandas projected CRS for accuracy later.
TREATMENT_RADIUS_METERS = 800  # ~0.5 miles
CONTROL_MIN_DIST_METERS = 1600 # ~1 mile
