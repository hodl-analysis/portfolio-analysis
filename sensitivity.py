import pandas as pd
import matplotlib.pyplot as plt

def run_projection(initial_price_usd, smash_buy_capital_usd, cagr, monthly_dca_usd, months):
    monthly_growth = (1 + cagr) ** (1/12) - 1

    prices = []
    dca_units = []
    dca_value = []
    smash_value = []
    combined_value = []

    price = initial_price_usd
    smash_units = smash_buy_capital_usd / initial_price_usd
    total_dca_units = 0.0

    for month in range(months + 1):
        prices.append(price)
        smash_value.append(smash_units * price)

        if month > 0:
            units_bought = monthly_dca_usd / price
            total_dca_units += units_bought

        dca_units.append(total_dca_units)

        dca_val = total_dca_units * price
        dca_value.append(dca_val)

        combined_value.append((smash_units + total_dca_units) * price)

        price = price * (1 + monthly_growth)

    return {
        "final_price": prices[-1],
        "final_dca_value": dca_value[-1],
        "final_smash_value": smash_value[-1],
        "final_combined_value": combined_value[-1],
    }


# ---------------------------------------------------
# Sensitivity Analysis Function
# ---------------------------------------------------

def sensitivity_analysis(
    initial_price_usd=94447,
    smash_buy_capital_usd=100000,
    cagr=0.25,
    monthly_dca_usd=600,
    months=12,
    sensitivity_range=10,
    dir="."
):
    results = []

    param_sets = {
        "smash_buy_capital_usd": smash_buy_capital_usd,
        "cagr": cagr,
        "monthly_dca_usd": monthly_dca_usd
    }

    for param, base_value in param_sets.items():
        for label, factor in [(f"-{sensitivity_range}%", 1-(sensitivity_range/100)), ("Baseline", 1.0), (f"+{sensitivity_range}%", 1+(sensitivity_range/100))]:
            modified_params = {
                "smash_buy_capital_usd": smash_buy_capital_usd,
                "cagr": cagr,
                "monthly_dca_usd": monthly_dca_usd
            }

            modified_params[param] = base_value * factor

            result = run_projection(
                initial_price_usd=initial_price_usd,
                smash_buy_capital_usd=modified_params["smash_buy_capital_usd"],
                cagr=modified_params["cagr"],
                monthly_dca_usd=modified_params["monthly_dca_usd"],
                months=months
            )

            results.append({
                "Parameter": param,
                "Variation": label,
                "Value Used": modified_params[param],
                "Final Smash Value (USD)": result["final_smash_value"],
                "Final DCA Value (USD)": result["final_dca_value"],
                "Final Combined Value (USD)": result["final_combined_value"]
            })

    df = pd.DataFrame(results)
    df.to_csv(f"{dir}/sensitivity_analysis_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}_{sensitivity_range}.csv", index=False)
    print(f"Saved sensitivity_analysis_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}_{sensitivity_range}.csv")

    return df

def format_usd(value: float) -> str:
    return "USD {:,.2f}".format(value)

# ---------------------------------------------------
# Run the sensitivity analysis
# ---------------------------------------------------
if __name__ == "__main__":
    import json, os
    OUTPUT_DIR = "./output_sensitivity"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    params = json.load(open('parameters.json'))
    initial_price_usd = params['initial_price_usd']
    smash_buy_capital_usd = params['smash_buy_capital_usd']
    cagr = params['cagr']
    monthly_dca_usd = params['monthly_dca_usd']
    total_years = params['total_years']
    total_months = total_years * 12
    sensitivity_range = params['sensitivity_range']
    df = sensitivity_analysis(initial_price_usd,smash_buy_capital_usd, cagr, monthly_dca_usd, total_months, sensitivity_range, OUTPUT_DIR)
    print(df)

    tornado_data = []

    for param in df['Parameter'].unique():
        subset = df[df['Parameter'] == param]
        low = subset[subset['Variation'] == f'-{sensitivity_range}%']['Final Combined Value (USD)'].values[0]
        high = subset[subset['Variation'] == f'+{sensitivity_range}%']['Final Combined Value (USD)'].values[0]
        baseline = subset[subset['Variation'] == 'Baseline']['Final Combined Value (USD)'].values[0]
        
        tornado_data.append({
            "Parameter": param,
            "Low": low,
            "High": high,
            "Baseline": baseline
        })

    tornado_df = pd.DataFrame(tornado_data)

    # ---------------------------
    # Plot Tornado Chart
    # ---------------------------

    plt.figure(figsize=(10, 6))

    # Horizontal bars: plot from low to high relative to baseline
    for i, row in enumerate(tornado_df.itertuples()):
        plt.hlines(y=i, xmin=row.Low, xmax=row.High, color='skyblue', linewidth=8)
        plt.plot(row.Baseline, i, 'ko')  # baseline marker

    # Labels and formatting
    plt.yticks(range(len(tornado_df)), tornado_df['Parameter'])
    plt.xlabel("Final Portfolio Value (USD)")
    plt.title(f"Tornado Chart: Sensitivity of Final Portfolio Value to Inputs\n Baseline: DCA {format_usd(monthly_dca_usd)}, Smash Buy Initial {format_usd(smash_buy_capital_usd)}, CAGR {cagr}, Variation: +/-{sensitivity_range}%")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/tornado_chart_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}.png")
    plt.show()

