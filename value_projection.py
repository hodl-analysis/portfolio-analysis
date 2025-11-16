import pandas as pd
import matplotlib.pyplot as plt

def run_projection(initial_price_usd, smash_buy_capital_usd, cagr, monthly_dca_usd, months):
    monthly_growth = (1 + cagr) ** (1/12) - 1

    prices = []
    dca_units = []
    dca_value = []
    smash_value = []
    combined_value = []
    combined_units_list = []

    price = initial_price_usd
    smash_units = smash_buy_capital_usd / initial_price_usd
    total_dca_units = 0.0

    for month in range(months + 1):
        prices.append(price)

        # Smash buy portfolio value
        smash_val = smash_units * price
        smash_value.append(smash_val)

        # DCA accumulation
        if month > 0:
            units_bought = monthly_dca_usd / price
            total_dca_units += units_bought

        dca_units.append(total_dca_units)

        dca_val = total_dca_units * price
        dca_value.append(dca_val)

        # Combined portfolio
        combined_units = smash_units + total_dca_units
        combined_units_list.append(combined_units)
        combined_value.append(combined_units * price)

        # Monthly price growth
        price = price * (1 + monthly_growth)

    return {
        "prices": prices,
        "dca_units": dca_units,
        "dca_value": dca_value,
        "smash_units": smash_units,
        "smash_value": smash_value,
        "combined_units": combined_units_list,
        "combined_value": combined_value
    }

def format_usd(value: float) -> str:
    return "USD {:,.2f}".format(value)


def format_btc(value: float) -> str:
    return "BTC {:,.8f}".format(value)

if __name__ == "__main__":
    import json, os
    OUTPUT_DIR = "./output_value"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    params = json.load(open('parameters.json'))
    initial_price_usd = params['initial_price_usd']
    smash_buy_capital_usd = params['smash_buy_capital_usd']
    cagr = params['cagr']
    monthly_dca_usd = params['monthly_dca_usd']
    total_years = params['total_years']
    total_months = total_years * 12
    result = run_projection(initial_price_usd, smash_buy_capital_usd, cagr, monthly_dca_usd, total_months)

    # ---------------------------
    # Create CSV output
    # ---------------------------

    df = pd.DataFrame({
        "Month": list(range(total_months+1)),
        "Price": result["prices"],
        "DCA_Units_Total": result["dca_units"],
        "DCA_Value_USD": result["dca_value"],
        "Smash_Units": [result["smash_units"]] * (total_months+1),
        "Smash_Value_USD": result["smash_value"],
        "Combined_Units": result["combined_units"],
        "Combined_Value_USD": result["combined_value"]
    })

    df.to_csv(f"{OUTPUT_DIR}/value_projection_output_{cagr}_{total_years}yr.csv", index=False)
    print(f"CSV saved as projection_output_{cagr}_{total_years}yr.csv")

    # ---------------------------
    # Plot 1: Price Over Time (with legend)
    # ---------------------------

    plt.figure(figsize=(10, 6))
    plt.plot(df["Month"], df["Price"], label="Asset Price")
    plt.xlabel("Month")
    plt.ylabel("Asset Price (USD)")
    plt.title(f"Asset Price Projection Over {total_years} Years, CAGR = {cagr}")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(f"{OUTPUT_DIR}/price_{cagr}_{total_years}.png")
    plt.close()

    print(f"price_{cagr}_{total_years}yr.png")

    # ---------------------------
    # Plot 2: DCA vs Smash vs Combined Portfolio Values
    # ---------------------------

    plt.figure(figsize=(10, 6))
    labels = [f'DCA Value (Final value: {format_usd(df["DCA_Value_USD"].iloc[-1])})',
            f'Smash Buy Value (Final value: {format_usd(df["Smash_Value_USD"].iloc[-1])})',
            f'Combined Value (Final value: {format_usd(df["Combined_Value_USD"].iloc[-1])})']
    plt.plot(df["Month"], df["DCA_Value_USD"], label=labels[0])
    plt.plot(df["Month"], df["Smash_Value_USD"], label=labels[1])
    plt.plot(df["Month"], df["Combined_Value_USD"], label=labels[2])
    plt.xlabel("Month")
    plt.ylabel("Portfolio Value (USD)")
    plt.title(f"DCA {format_usd(monthly_dca_usd)} vs Smash Buy {format_usd(smash_buy_capital_usd)} vs Combined Portfolio Value Over {total_years} Years, CAGR = {cagr}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/portfolios_usd_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}.png")
    plt.close()

    print(f"Plot saved as {OUTPUT_DIR}/portfolios_usd_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}.png")

    # ---------------------------
    # Plot 2: DCA vs Smash vs Combined Portfolio Values (in BTC)
    # ---------------------------

    plt.figure(figsize=(10, 6))
    labels = [f'DCA Value (Final value: {format_btc(df["DCA_Units_Total"].iloc[-1])})',
            f'Smash Buy Value (Final value: {format_btc(df["Smash_Units"].iloc[-1])})',
            f'Combined Value (Final value: {format_btc(df["Combined_Units"].iloc[-1])})']
    plt.plot(df["Month"], df["DCA_Units_Total"], label=labels[0])
    plt.plot(df["Month"], df["Smash_Units"], label=labels[1])
    plt.plot(df["Month"], df["Combined_Units"], label=labels[2])
    plt.xlabel("Month")
    plt.ylabel("Portfolio Value (BTC)")
    plt.title(f"DCA {format_usd(monthly_dca_usd)} vs Smash Buy {format_usd(smash_buy_capital_usd)} vs Combined Portfolio Value Over {total_years} Years, CAGR = {cagr}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/portfolios_btc_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}.png")
    plt.close()

    print(f"Plot saved as {OUTPUT_DIR}/portfolios_btc_{cagr}_{total_years}yr_{smash_buy_capital_usd}_{monthly_dca_usd}.png")
