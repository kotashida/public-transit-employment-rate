# Causal Impact Analysis: Public Transit & Employment Rates

## Overview
This project investigates the causal relationship between public transit infrastructure and local economic development. specifically employing a **Quasi-Experimental Design** to estimate the impact of the 2016 Seattle Link Light Rail extension (University Link) on employment density in surrounding neighborhoods.

By leveraging **Difference-in-Differences (DiD)** estimation on high-granularity US Census data, this analysis seeks to determine if gaining access to a new transit station leads to a statistically significant increase in jobs compared to a control group.

## Key Quantitative Skills Demonstrated
*   **Econometric Modeling:** Implementation of Difference-in-Differences (DiD) estimators to isolate causal effects from confounding variables.
*   **Statistical Inference:** Hypothesis testing using Cluster-Robust Standard Errors to account for serial correlation and heteroskedasticity in panel data.
*   **Robustness Testing:** Implementation of Placebo Tests (counterfactual validation) to confirm the internal validity of the DiD design.
*   **Spatial Data Science:** Geographic manipulation using Coordinate Reference Systems (CRS) transformations, spatial joins, and geodesic buffering (800m vs 1600m radii) to define treatment/control groups.
*   **Data Engineering:** Automated ETL pipeline construction to fetch, process, and aggregate multi-gigabyte census datasets (LODES) and TIGER/Line shapefiles.

## Methodology

### 1. Research Design: Difference-in-Differences (DiD)
To infer causality rather than simple correlation, I utilized a DiD framework. This approach compares the *change* in outcomes over time between a "Treatment Group" and a "Control Group," effectively differencing out:
1.  **Time-Invariant Heterogeneity:** Characteristics of neighborhoods that don't change over time (e.g., proximity to downtown).
2.  **Common Time Shocks:** Regional economic trends affecting all neighborhoods equally (e.g., a city-wide boom).

### 2. Spatial Sampling & Variable Definition
*   **Data Source:** US Census Bureau LODES (Workplace Area Characteristics) & TIGER/Line Shapefiles (2020 Vintage).
*   **Treatment Group:** Census Block Groups with centroids within **800m (0.5 miles)** of the new Capitol Hill or University of Washington stations.
*   **Control Group:** Census Block Groups situated **> 1600m (1 mile)** from the stations to avoid spillover effects, serving as the counterfactual.
*   **Period:** 2014-2015 (Pre-Intervention) vs. 2016-2018 (Post-Intervention).

### 3. Statistical Model
I estimated the following linear regression model:

$$ Employment_{it} = \beta_0 + \beta_1(Treat_i) + \beta_2(Post_t) + \beta_3(Treat_i \times Post_t) + \epsilon_{it} $$

*   **$Employment_{it}$**: Total jobs in Block Group $i$ at year $t$.
*   **$Treat_i$**: Binary dummy (1 if Treatment group, 0 if Control).
*   **$Post_t$**: Binary dummy (1 if Year $\ge$ 2016).
*   **$eta_3$ (Interaction Term)**: The coefficient of interest, representing the **Average Treatment Effect on the Treated (ATT)**.

*Standard errors were clustered by Block Group ID to ensure robust inference.*

### 4. Robustness Check: Placebo Test
To validate that the DiD model is not picking up a pre-existing trend, I conducted a **Placebo Test** by shifting the intervention date to 2015 (a period when no stations opened). A successful model should show an insignificant interaction term for the placebo year, confirming that the treatment and control groups were following parallel trends prior to the actual intervention.

## Quantitative Results

The analysis was performed on **7,591 observations** across King County, WA.

| Variable | Coefficient | Std. Error | P-Value |
| :--- | :--- | :--- | :--- |
| **Intercept** | 797.48 | 78.87 | 0.000 |
| **Treatment (Baseline Diff)** | -536.68 | 94.21 | 0.000 |
| **Post (Time Trend)** | 62.92 | 15.75 | 0.000 |
| **Treatment $\times$ Post ($\beta_3$)** | **-24.96** | **17.62** | **0.157** |

### Interpretation
1.  **Regional Growth:** The `Post` coefficient (62.92) is positive and significant ($p < 0.001$), indicating that the control region saw an average increase of ~63 jobs per block group after 2016.
2.  **Baseline Disparity:** The `Treatment` coefficient (-536.68) confirms that the station areas historically had lower employment density than the control group average.
3.  **Causal Impact:** The interaction term ($eta_3$) is **-24.96** with a p-value of **0.157**.
    *   **Conclusion:** We **fail to reject the null hypothesis**. There is no statistically significant evidence that the opening of the transit stations *caused* an increase in employment rates in the immediate 2-year post-opening period, controlling for regional trends. In fact, the point estimate suggests a slight (non-significant) lag compared to the regional average.

## Technical Setup

### Prerequisites
*   Python 3.x
*   `pip` packages: `pandas`, `geopandas`, `statsmodels`, `linearmodels`, `matplotlib`

### Reproduction Steps
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Pipeline (Download -> Process -> Analyze):**
    ```powershell
    .\run_pipeline.bat
    ```
    *This will automatically download ~200MB of raw Census data, process the geospatial joins, and output the regression table.*

## Project Structure
*   `src/download_data.py`: Automated data fetching script.
*   `src/process_data.py`: Geospatial logic for Treatment/Control assignment (with full type hints).
*   `src/analyze.py`: OLS regression, Placebo testing, and report generation.
*   `outputs/`:
    *   `analysis_report.md`: Comprehensive generated report with statistical tables.
    *   `parallel_trends.png`: Visual verification of the parallel trends assumption.