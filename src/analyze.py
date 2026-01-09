import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
import config

def analyze():
    data_path = config.DATA_PROCESSED / "panel_dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError("Processed dataset not found. Run process_data.py first.")
    
    df = pd.read_csv(data_path)
    
    print("Dataset Summary:")
    print(df.groupby(['group', 'year'])['employment'].mean().unstack())
    
    # --- 1. Parallel Trends Plot ---
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='year', y='employment', hue='group', estimator='mean', marker='o')
    plt.axvline(x=config.INTERVENTION_YEAR - 0.5, color='r', linestyle='--', label='Intervention')
    plt.title("Average Employment: Treatment vs Control")
    plt.ylabel("Avg Jobs per Block Group")
    plt.legend()
    plot_path = config.OUTPUTS / "parallel_trends.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    # --- 2. DiD Regression ---
    # Model: employment ~ treated + post + treated:post
    # We use clustered standard errors by GEOID to account for serial correlation
    
    print("\nRunning Difference-in-Differences Regression...")
    model = smf.ols("employment ~ treated * post", data=df).fit(cov_type='cluster', cov_kwds={'groups': df['GEOID']})
    
    print(model.summary())
    
    with open(config.OUTPUTS / "regression_results.txt", "w") as f:
        f.write(model.summary().as_text())

if __name__ == "__main__":
    analyze()
