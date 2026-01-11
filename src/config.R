# Configuration

# Paths
# Assumes the script is run from the project root or src_r. 
# Best practice is running from project root.
BASE_DIR <- getwd()
DATA_RAW <- file.path(BASE_DIR, "data", "raw")
DATA_PROCESSED <- file.path(BASE_DIR, "data", "processed")
OUTPUTS <- file.path(BASE_DIR, "outputs")

# Ensure directories exist
if (!dir.exists(DATA_RAW)) dir.create(DATA_RAW, recursive = TRUE)
if (!dir.exists(DATA_PROCESSED)) dir.create(DATA_PROCESSED, recursive = TRUE)
if (!dir.exists(OUTPUTS)) dir.create(OUTPUTS, recursive = TRUE)

# Case Study: Seattle University Link Extension
# Opening Date: March 2016
INTERVENTION_YEAR <- 2016

# Coordinates (Lat, Lon)
STATIONS <- list(
  "University of Washington" = c(lat = 47.6503, lon = -122.3016),
  "Capitol Hill" = c(lat = 47.6198, lon = -122.3200)
)

# Analysis Settings
YEARS <- 2014:2018
STATE <- "wa"
LODES_BASE_URL <- "https://lehd.ces.census.gov/data/lodes/LODES8"

# Distances
# Using EPSG:32148 (NAD83 / Washington North) for accurate meter calculation
# 800m ~ 0.5 miles, 1600m ~ 1 mile
TREATMENT_RADIUS_METERS <- 800
CONTROL_MIN_DIST_METERS <- 1600

# Projection
CRS_PROJECTED <- 32148 # NAD83 / Washington North (meters)
