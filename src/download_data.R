# Download Data Script
source("src/config.R")

download_data <- function() {
  # 1. Download LODES WAC Data (Employment)
  message("--- Downloading LODES Data ---")
  for (year in YEARS) {
    filename <- sprintf("%s_wac_S000_JT00_%d.csv.gz", STATE, year)
    url <- sprintf("%s/%s/wac/%s", LODES_BASE_URL, STATE, filename)
    dest_path <- file.path(DATA_RAW, filename)
    
    if (file.exists(dest_path)) {
      message(sprintf("File already exists: %s", filename))
    } else {
      message(sprintf("Downloading %s...", url))
      tryCatch({
        download.file(url, dest_path, mode = "wb")
        message(sprintf("Downloaded to %s", dest_path))
      }, error = function(e) {
        message(sprintf("Failed to download %s: %s", url, e$message))
      })
    }
  }
  
  # 2. Download Geography (Block Groups Shapefile)
  # Using TIGER 2020 Block Groups for WA
  message("\n--- Downloading Geography Data ---")
  geo_filename <- sprintf("tl_2020_%s_bg.zip", STATE)
  # FIPS code for WA is 53
  geo_url <- "https://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_53_bg.zip"
  geo_dest <- file.path(DATA_RAW, geo_filename)
  
  if (file.exists(geo_dest)) {
    message(sprintf("File already exists: %s", geo_filename))
  } else {
    message(sprintf("Downloading %s...", geo_url))
    tryCatch({
      download.file(geo_url, geo_dest, mode = "wb")
      message(sprintf("Downloaded to %s", geo_dest))
    }, error = function(e) {
      message(sprintf("Failed to download %s: %s", geo_url, e$message))
    })
  }
  
  # Extract Shapefile
  extract_dir <- file.path(DATA_RAW, "shapefiles")
  if (!dir.exists(extract_dir)) {
    message("Extracting shapefile...")
    tryCatch({
      unzip(geo_dest, exdir = extract_dir)
      message("Extraction complete.")
    }, error = function(e) {
      message(sprintf("Error extracting shapefile: %s", e$message))
    })
  } else {
    message("Shapefiles directory already exists.")
  }
}

if (sys.nframe() == 0) {
  download_data()
}
