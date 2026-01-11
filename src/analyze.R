# Analysis Script
library(readr)
library(dplyr)
library(ggplot2)
library(fixest) # Efficient Fixed Effects / DiD
library(knitr)

source("src/config.R")

run_did_model <- function(df, intervention_year) {
  # Create post variable locally
  df_run <- df %>%
    mutate(post = as.integer(year >= intervention_year))
  
  # Model: employment ~ treated * post
  # Cluster SEs by GEOID
  model <- feols(employment ~ treated * post, 
                 data = df_run, 
                 cluster = ~GEOID)
  
  return(model)
}

analyze <- function() {
  data_path <- file.path(DATA_PROCESSED, "panel_dataset.csv")
  if (!file.exists(data_path)) {
    stop("Processed dataset not found. Run process_data.R first.")
  }
  
  df <- read_csv(data_path, show_col_types = FALSE)
  
  message("--- Starting Analysis ---")
  
  # --- 1. Parallel Trends Plot ---
  # Calculate means for plotting
  plot_data <- df %>%
    group_by(year, group) %>%
    summarise(mean_emp = mean(employment), .groups = 'drop')
  
  p <- ggplot(plot_data, aes(x = year, y = mean_emp, color = group)) +
    geom_line(size = 1) +
    geom_point(size = 2) +
    geom_vline(xintercept = INTERVENTION_YEAR - 0.5, linetype = "dashed", color = "red") +
    annotate("text", x = INTERVENTION_YEAR - 0.5, y = max(plot_data$mean_emp), 
             label = paste("Intervention (", INTERVENTION_YEAR, ")", sep=""), 
             vjust = -1, color = "red", angle = 90) +
    labs(title = "Parallel Trends Check: Average Employment",
         y = "Avg Jobs per Block Group",
         x = "Year") +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  plot_path <- file.path(OUTPUTS, "parallel_trends.png")
  ggsave(plot_path, plot = p, width = 10, height = 6)
  message(sprintf("Plot saved to %s", plot_path))
  
  # --- 2. Primary DiD Regression ---
  message("\nRunning Primary DiD Model (2016)...")
  primary_model <- run_did_model(df, INTERVENTION_YEAR)
  primary_summary <- capture.output(print(primary_model))
  
  # --- 3. Placebo Test (Robustness) ---
  message("\nRunning Placebo Test (2015)...")
  df_placebo <- df %>% filter(year < INTERVENTION_YEAR)
  placebo_year <- 2015
  placebo_model <- run_did_model(df_placebo, placebo_year)
  placebo_summary <- capture.output(print(placebo_model))
  
  # --- 4. Generate Report ---
  report_path <- file.path(OUTPUTS, "analysis_report.md")
  
  # Descriptive Stats Table
  stats_table <- df %>%
    group_by(group, year) %>%
    summarise(mean_employment = mean(employment), .groups = 'drop') %>%
    kable(format = "markdown")
  
  report_content <- c(
    "# Quantitative Analysis Report (R Implementation)",
    "",
    "## 1. Descriptive Statistics",
    paste(stats_table, collapse = "\n"),
    "",
    "## 2. Primary Model Results (2016 Intervention)",
    "The following table estimates the causal impact of the station opening.",
    "```",
    primary_summary,
    "```",
    "",
    "## 3. Robustness Check: Placebo Test (2015)",
    paste("Testing for 'effects' in", placebo_year, "(before stations opened)."),
    "Ideally, the interaction term should be insignificant.",
    "```",
    placebo_summary,
    "```"
  )
  
  writeLines(report_content, report_path)
  message(sprintf("Full analysis report generated at %s", report_path))
}

if (sys.nframe() == 0) {
  analyze()
}

