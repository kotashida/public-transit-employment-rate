import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import config
from pathlib import Path
from typing import Optional

def process_geography() -> gpd.GeoDataFrame:
    """
    Loads TIGER/Line shapefiles, filters for King County, calculates centroids,
    and assigns Treatment/Control status based on distance to transit stations.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing [GEOID, group, dist_to_station, geometry].
                          Rows in the 'Buffer' zone are excluded.
    """
    print("Processing Geography...")
    # Load Shapefile
    shp_path = config.DATA_RAW / "shapefiles" / f"tl_2020_53_bg.shp"
    if not shp_path.exists():
        raise FileNotFoundError(f"Shapefile not found at {shp_path}. Run download_data.py first.")
    
    gdf = gpd.read_file(shp_path)
    
    # Filter for King County (033)
    # GEOID format: State(2) + County(3) + Tract(6) + BlkGrp(1)
    # GEOID starts with '53033'
    gdf = gdf[gdf['GEOID'].str.startswith('53033')].copy()
    
    # Reproject to EPSG:3857 (Web Mercator - Meters) for distance calc
    gdf = gdf.to_crs(epsg=3857)
    
    # Calculate Centroids
    gdf['centroid'] = gdf.geometry.centroid
    
    # Define Stations
    stations_df = pd.DataFrame.from_dict(config.STATIONS, orient='index', columns=['lat', 'lon'])
    stations_gdf = gpd.GeoDataFrame(
        stations_df, 
        geometry=gpd.points_from_xy(stations_df.lon, stations_df.lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    # Calculate Distances
    # Find distance to NEAREST station for each BG
    def get_min_dist(point):
        return stations_gdf.distance(point).min()
        
    gdf['dist_to_station'] = gdf['centroid'].apply(get_min_dist)
    
    # Classify
    def classify(dist: float) -> str:
        if dist <= config.TREATMENT_RADIUS_METERS:
            return 'Treatment'
        elif dist >= config.CONTROL_MIN_DIST_METERS:
            return 'Control'
        else:
            return 'Buffer'
            
    gdf['group'] = gdf['dist_to_station'].apply(classify)
    
    # Filter out Buffer
    gdf_analysis = gdf[gdf['group'] != 'Buffer'][['GEOID', 'group', 'dist_to_station', 'geometry']].copy()
    
    print(f"Geography ready. Treatment: {sum(gdf_analysis['group']=='Treatment')}, Control: {sum(gdf_analysis['group']=='Control')}")
    return gdf_analysis

def process_employment(geo_df: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Loads LODES WAC data for multiple years, aggregates to Block Group level,
    and merges with the geography dataframe.

    Args:
        geo_df (gpd.GeoDataFrame): The geography dataframe from process_geography().

    Returns:
        pd.DataFrame: A panel dataset ready for regression analysis.
    """
    print("Processing Employment Data...")
    dfs = []
    
    for year in config.YEARS:
        print(f"Loading {year}...")
        file_path = config.DATA_RAW / f"{config.STATE}_wac_S000_JT00_{year}.csv.gz"
        if not file_path.exists():
            print(f"Warning: {file_path} not found. Skipping.")
            continue
            
        # Read only necessary columns: w_geocode (Block ID), C000 (Total Jobs)
        # dtype={'w_geocode': str} is crucial to preserve leading zeros
        df = pd.read_csv(file_path, compression='gzip', usecols=['w_geocode', 'C000'], dtype={'w_geocode': str})
        
        # Create Block Group ID (First 12 chars)
        df['bg_id'] = df['w_geocode'].str.slice(0, 12)
        
        # Filter for King County (Optimization)
        df = df[df['bg_id'].str.startswith('53033')]
        
        # Aggregate to Block Group
        df_agg = df.groupby('bg_id')['C000'].sum().reset_index()
        df_agg.rename(columns={'C000': 'employment', 'bg_id': 'GEOID'}, inplace=True)
        
        # Merge with Geography
        merged = geo_df.merge(df_agg, on='GEOID', how='inner') # Inner join: keep only those with geo and data
        
        merged['year'] = year
        merged['post'] = int(year >= config.INTERVENTION_YEAR)
        merged['treated'] = (merged['group'] == 'Treatment').astype(int)
        
        dfs.append(merged)
        
    if not dfs:
        raise ValueError("No data processed.")
        
    final_df = pd.concat(dfs, ignore_index=True)
    return final_df

def main():
    geo_df = process_geography()
    panel_df = process_employment(geo_df)
    
    out_path = config.DATA_PROCESSED / "panel_dataset.csv"
    # Drop geometry for CSV saving
    panel_df.drop(columns='geometry').to_csv(out_path, index=False)
    print(f"Saved processed dataset to {out_path}")

if __name__ == "__main__":
    main()
