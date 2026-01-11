# Process Data Script
library(sf)
library(dplyr)
library(readr)
library(stringr)

source("src/config.R")

process_geography <- function() {
  message("Processing Geography...")
  
  shp_path <- file.path(DATA_RAW, "shapefiles", "tl_2020_53_bg.shp")
  if (!file.exists(shp_path)) {
    stop("Shapefile not found. Run download_data.R first.")
  }
  
  # Load and filter for King County (FIPS 53033)
  gdf <- st_read(shp_path, quiet = TRUE) %>%
    filter(str_starts(GEOID, "53033")) %>%
    st_transform(crs = CRS_PROJECTED) # Project to WA North
  
  # Calculate Centroids
  # st_centroid returns a geometry column
  gdf$centroid <- st_centroid(gdf$geometry)
  
  # Define Stations
  stations_df <- data.frame(
    name = names(STATIONS),
    lat = sapply(STATIONS, function(x) x["lat"]),
    lon = sapply(STATIONS, function(x) x["lon"])
  )
  
  stations_sf <- st_as_sf(stations_df, coords = c("lon", "lat"), crs = 4326) %>%
    st_transform(crs = CRS_PROJECTED)
  
  # Calculate Distances
  # st_distance returns a matrix. We want min dist to ANY station for each BG.
  dist_matrix <- st_distance(gdf$centroid, stations_sf)
  gdf$dist_to_station <- apply(dist_matrix, 1, min)
  
  # Classify
  gdf <- gdf %>%
    mutate(group = case_when(
      dist_to_station <= TREATMENT_RADIUS_METERS ~ "Treatment",
      dist_to_station >= CONTROL_MIN_DIST_METERS ~ "Control",
      TRUE ~ "Buffer"
    ))
  
  # Filter out Buffer and select columns
  gdf_analysis <- gdf %>%
    filter(group != "Buffer") %>%
    select(GEOID, group, dist_to_station) # geometry is sticky in sf
  
  # Count groups
  counts <- table(gdf_analysis$group)
  message(sprintf("Geography ready. Treatment: %d, Control: %d", 
                  counts["Treatment"], counts["Control"]))
  
  return(gdf_analysis)
}

process_employment <- function(geo_df) {
  message("Processing Employment Data...")
  
  all_years_data <- list()
  
  for (year in YEARS) {
    message(sprintf("Loading %d...", year))
    file_path <- file.path(DATA_RAW, sprintf("%s_wac_S000_JT00_%d.csv.gz", STATE, year))
    
    if (!file.exists(file_path)) {
      warning(sprintf("%s not found. Skipping.", file_path))
      next
    }
    
    # Read CSV
    # col_types: w_geocode is character, C000 (Total Jobs) is double
    df <- read_csv(file_path, 
                   col_types = cols_only(w_geocode = col_character(), C000 = col_double()),
                   progress = FALSE)
    
    # Create Block Group ID (First 12 chars) and Filter for King County (53033)
    df_agg <- df %>%
      mutate(bg_id = str_sub(w_geocode, 1, 12)) %>%
      filter(str_starts(bg_id, "53033")) %>%
      group_by(bg_id) %>%
      summarise(employment = sum(C000, na.rm = TRUE)) %>%
      rename(GEOID = bg_id)
    
    # Join with Geography
    # Inner join to keep only matching records
    merged <- geo_df %>%
      inner_join(df_agg, by = "GEOID") %>%
      mutate(
        year = year,
        post = as.integer(year >= INTERVENTION_YEAR),
        treated = as.integer(group == "Treatment")
      )
    
    all_years_data[[as.character(year)]] <- merged
  }
  
  if (length(all_years_data) == 0) {
    stop("No data processed.")
  }
  
  final_df <- do.call(rbind, all_years_data)
  return(final_df)
}

process_data_main <- function() {
  geo_df <- process_geography()
  panel_df <- process_employment(geo_df)
  
  # Save to CSV (drop geometry for CSV)
  out_path <- file.path(DATA_PROCESSED, "panel_dataset.csv")
  st_set_geometry(panel_df, NULL) %>% # Drop geometry
    write_csv(out_path)
    
  message(sprintf("Saved processed dataset to %s", out_path))
}

if (sys.nframe() == 0) {
  process_data_main()
}
