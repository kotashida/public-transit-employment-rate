# Master Pipeline Script
# This script executes the full analysis pipeline:
# 1. Download Data
# 2. Process Data
# 3. Analyze Data

# Ensure working directory is project root
# (If running from command line Rscript src/run_pipeline.R, getwd() is usually where you ran it from)

message("--- Starting R Pipeline ---")

# 1. Download
message("\n[Step 1/3] Downloading Data...")
source("src/download_data.R")
download_data()

# 2. Process
message("\n[Step 2/3] Processing Data...")
source("src/process_data.R")
process_data_main()

# 3. Analyze
message("\n[Step 3/3] Analyzing Data...")
source("src/analyze.R")
analyze()

message("\n--- Pipeline Complete ---")
