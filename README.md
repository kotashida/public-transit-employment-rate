# Causal Impact Analysis: Public Transit & Local Economic Development

## Overview
This project employs a **Quasi-Experimental Design** to estimate the causal impact of the 2016 Seattle Link Light Rail extension (University Link) on local employment density. By leveraging high-granularity US Census data and a **Difference-in-Differences (DiD)** framework, this analysis seeks to isolate the specific economic effects of transit infrastructure investment from broader regional growth trends.

**Key Finding:** The analysis of 7,591 observations reveals that while the region experienced significant growth, the opening of new transit stations did not cause a statistically significant immediate increase in employment density within an 800m radius ($p = 0.157$) during the initial 2-year post-intervention period.

## Key Quantitative Skills
This project demonstrates proficiency in the following analytical and technical areas:

*   **Econometric Modeling:** Implementation of Difference-in-Differences (DiD) estimators to identify causal effects, controlling for time-invariant heterogeneity and common time shocks.
*   **Statistical Inference:** Utilization of **Cluster-Robust Standard Errors** to account for serial correlation and heteroskedasticity inherent in panel data.
*   **Spatial Data Science:** Precision geospatial analysis using **R (`sf`)**, including coordinate transformation to **EPSG:32148 (NAD83 / Washington North)** for accurate geodesic buffering (800m treatment vs. 1600m control radii).
*   **Robustness Testing:** Execution of **Placebo Tests** (counterfactual validation) to verify the parallel trends assumption and ensure internal validity.
*   **Data Engineering:** Construction of an automated ETL pipeline in **R** to fetch, process, and aggregate multi-gigabyte Census LODES and Shapefile datasets.

## Methodology

### 1. Research Design: Difference-in-Differences (DiD)
To infer causality, I utilized a DiD framework which compares the *change* in outcomes over time between a "Treatment Group" (neighborhoods receiving a station) and a "Control Group" (similar neighborhoods further away). This approach effectively differences out:
1.  **Time-Invariant Characteristics:** Fundamental differences between neighborhoods that stay constant (e.g., distance to downtown).
2.  **Common Time Shocks:** Economic trends affecting the entire city equally (e.g., a regional tech boom).

### 2. Spatial Sampling & Variable Definition
*   **Data Source:** US Census Bureau LODES (Workplace Area Characteristics) & TIGER/Line Shapefiles.
*   **Spatial Projection:** All geometries were projected to **EPSG:32148**, a State Plane coordinate system specifically optimized for Washington, ensuring meter-level accuracy for distance calculations.
*   **Treatment Group:** Census Block Groups with centroids within **800m (approx. 0.5 miles)** of the new Capitol Hill or University of Washington stations.
*   **Control Group:** Census Block Groups situated **> 1600m (approx. 1 mile)** from the stations to avoid spillover effects, serving as the counterfactual.
*   **Study Period:** 2014-2015 (Pre-Intervention) vs. 2016-2018 (Post-Intervention).

### 3. Statistical Model
I estimated the following linear regression model:

$$ Employment_{it} = \beta_0 + \beta_1(Treat_i) + \beta_2(Post_t) + \beta_3(Treat_i \times Post_t) + \epsilon_{it} $$

*   **$Employment_{it}$**: Total jobs in Block Group $i$ at year $t$.
*   **$Treat_i$**: Binary dummy (1 if Treatment group, 0 if Control).
*   **$Post_t$**: Binary dummy (1 if Year $\ge$ 2016).
*   **$eta_3$ (Interaction Term)**: The coefficient of interest, representing the **Average Treatment Effect on the Treated (ATT)**.

*Standard errors were clustered by Block Group ID to ensure robust inference.*

## Quantitative Results

The analysis was performed on **7,591 observations** across King County, WA.

| Variable | Coefficient | Std. Error | P-Value | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Intercept** | 797.48 | 78.87 | < 0.001 | Average baseline employment in the Control group. |
| **Treatment (Baseline)** | -536.68 | 94.21 | < 0.001 | Station areas historically had significantly lower job density than the control average. |
| **Post (Time Trend)** | 62.92 | 15.75 | < 0.001 | The entire region saw a significant growth of ~63 jobs per block group after 2016. |
| **Treatment $\times$ Post ($\beta_3$)** | **-24.96** | **17.62** | **0.157** | **The Causal Impact.** |

### Interpretation of Findings
1.  **No Significant Causal Effect:** The interaction term ($eta_3$) is **-24.96** with a p-value of **0.157**. We **fail to reject the null hypothesis** at the 5% significance level.
2.  **Context:** While the region grew (Post coefficient > 0), the areas near the new stations did not experience an *additional* boost in employment relative to the control group in the immediate aftermath. In fact, the point estimate suggests a slight (statistically insignificant) lag.
3.  **Robustness Check:** A **Placebo Test** simulating an intervention in 2015 yielded no significant interaction effect, confirming that the treatment and control groups followed parallel trends prior to the actual opening.

## Technical Implementation (R)

The project is implemented as a reproducible R pipeline.

### Prerequisites
*   R (>= 4.0.0)
*   Key Packages: `tidyverse`, `sf`, `fixest`, `knitr`

### Project Structure
*   `src/run_pipeline.R`: **Master script** that executes the entire workflow.
*   `src/process_data.R`: Handles complex geospatial joins and coordinate transformations.
*   `src/analyze.R`: Performs the DiD regression using `fixest` (Fast Fixed-Effects Estimation) and generates outputs.

### How to Run
1.  **Install Dependencies:**
    ```R
    install.packages(c("tidyverse", "sf", "fixest", "knitr"))
    ```
2.  **Execute Pipeline:**
    ```bash
    Rscript src/run_pipeline.R
    ```
    *This command will automatically download raw Census data, process the geometry, run the statistical models, and generate the report in `outputs/`.*
