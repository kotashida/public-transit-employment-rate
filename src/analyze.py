import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import config
from typing import Tuple

def run_did_model(df: pd.DataFrame, intervention_year: int) -> Tuple[object, str]:
    """
    Runs the Difference-in-Differences regression model.
    
    Args:
        df: The panel dataset.
        intervention_year: The year to define the 'post' period.
        
    Returns:
        model_result: The fitted statsmodels result.
        summary_text: Text summary of the model.
    """
    # Create temporary post variable for this specific run
    df_run = df.copy()
    df_run['post'] = (df_run['year'] >= intervention_year).astype(int)
    
    # Model: employment ~ treated + post + treated:post
    # Clustered SE by GEOID
    model = smf.ols("employment ~ treated * post", data=df_run).fit(
        cov_type='cluster', 
        cov_kwds={'groups': df_run['GEOID']}
    )
    return model, model.summary().as_text()

def analyze() -> None:
    """
    Main analysis function.
    1. Loads data.
    2. Generates descriptive plots.
    3. Runs Primary DiD Model.
    4. Runs Placebo Test (Robustness Check).
    5. Generates a comprehensive Markdown report.
    """
    data_path = config.DATA_PROCESSED / "panel_dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError("Processed dataset not found. Run process_data.py first.")
    
    df = pd.read_csv(data_path)
    
    print("--- Starting Analysis ---")
    
    # --- 1. Parallel Trends Plot ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='year', y='employment', hue='group', estimator='mean', marker='o')
    plt.axvline(x=config.INTERVENTION_YEAR - 0.5, color='r', linestyle='--', label='Intervention (2016)')
    plt.title("Parallel Trends Check: Average Employment")
    plt.ylabel("Avg Jobs per Block Group")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plot_path = config.OUTPUTS / "parallel_trends.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    # --- 2. Primary DiD Regression ---
    print("\nRunning Primary DiD Model (2016)...")
    primary_model, primary_summary = run_did_model(df, config.INTERVENTION_YEAR)
    
    # --- 3. Placebo Test (Robustness) ---
    # We test for an effect in 2015 (Pre-treatment). 
    # Use 2014 as Pre, 2015 as Post. Drop years >= 2016 to avoid contamination.
    print("\nRunning Placebo Test (2015)...")
    df_placebo = df[df['year'] < config.INTERVENTION_YEAR].copy()
    placebo_year = 2015
    placebo_model, placebo_summary = run_did_model(df_placebo, placebo_year)
    
    # --- 4. Generate Report ---
    report_path = config.OUTPUTS / "analysis_report.md"
    with open(report_path, "w") as f:
        f.write("# Quantitative Analysis Report\n\n")
        
        f.write("## 1. Descriptive Statistics\n")
        stats = df.groupby(['group', 'year'])['employment'].mean().unstack()
        f.write(stats.to_markdown())
        f.write("\n\n")
        
        f.write("## 2. Primary Model Results (2016 Intervention)\n")
        f.write("The following table estimates the causal impact of the station opening.\n")
        f.write("```\n")
        f.write(primary_summary)
        f.write("\n```\n\n")
        
        f.write("## 3. Robustness Check: Placebo Test (2015)\n")
        f.write(f"Testing for 'effects' in {placebo_year} (before stations opened). ")
        f.write("Ideally, the interaction term should be insignificant.\n")
        f.write("```\n")
        f.write(placebo_summary)
        f.write("\n```\n")
        
    print(f"Full analysis report generated at {report_path}")

if __name__ == "__main__":
    analyze()
