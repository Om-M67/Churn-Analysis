"""
Telco Customer Churn Analysis
==============================
Covers:
  1. Data loading & cleaning
  2. Exploratory analysis (churn rate, contract type, charges, tenure)
  3. Visualizations saved as PNG files
  4. Summary of key findings printed to console
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── 0. CONFIG ────────────────────────────────────────────────────────────────
FILE_PATH = "telco_churn.csv"
OUTPUT_DIR = "."

CHURN_COLOR    = "#E05C5C"
STAY_COLOR     = "#4C72B0"
NEUTRAL_COLORS = ["#4C72B0", "#E05C5C", "#55A868", "#F5A623", "#8172B2",
                  "#64B5CD", "#C44E52", "#CCB974", "#1D9E75", "#888780"]

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

# ── 1. LOAD & CLEAN ──────────────────────────────────────────────────────────
print("=" * 60)
print("TELCO CUSTOMER CHURN ANALYSIS")
print("=" * 60)

df = pd.read_csv(FILE_PATH)
print(f"\n[1] Raw dataset shape: {df.shape}")

# Drop duplicates
dupes = df.duplicated().sum()
df.drop_duplicates(inplace=True)
print(f"    Duplicate rows removed : {dupes}")

# TotalCharges has some spaces — fix to numeric
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip(), errors="coerce")
df["TotalCharges"].fillna(0, inplace=True)

# Churn to binary
df["Churn_binary"] = (df["Churn"] == "Yes").astype(int)

# Tenure buckets
df["Tenure Group"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0–12 mo", "13–24 mo", "25–48 mo", "49–72 mo"]
)

# Missing values
missing = df.isnull().sum()
missing = missing[missing > 0]
if missing.empty:
    print("    Missing values         : none")
else:
    print(f"    Missing values:\n{missing.to_string()}")

overall_churn = df["Churn_binary"].mean() * 100
print(f"\n    Total customers  : {len(df):,}")
print(f"    Churned          : {df['Churn_binary'].sum():,} ({overall_churn:.1f}%)")
print(f"    Retained         : {(df['Churn_binary']==0).sum():,} ({100-overall_churn:.1f}%)")

# ── 2. EXPLORATORY ANALYSIS ──────────────────────────────────────────────────
print("\n[2] Exploratory Analysis")

# 2a. Churn by Contract Type
contract_churn = (
    df.groupby("Contract")["Churn_binary"]
    .mean()
    .mul(100)
    .round(1)
    .sort_values(ascending=False)
)
print(f"\n  Churn rate by contract type (%):\n{contract_churn.to_string()}")

# 2b. Churn by Internet Service
internet_churn = (
    df.groupby("InternetService")["Churn_binary"]
    .mean()
    .mul(100)
    .round(1)
    .sort_values(ascending=False)
)
print(f"\n  Churn rate by internet service (%):\n{internet_churn.to_string()}")

# 2c. Monthly charges: churned vs retained
churned_charges  = df[df["Churn"]=="Yes"]["MonthlyCharges"]
retained_charges = df[df["Churn"]=="No"]["MonthlyCharges"]
print(f"\n  Avg monthly charges — Churned : ${churned_charges.mean():.2f}")
print(f"  Avg monthly charges — Retained: ${retained_charges.mean():.2f}")

# 2d. Churn by Tenure Group
tenure_churn = (
    df.groupby("Tenure Group")["Churn_binary"]
    .mean()
    .mul(100)
    .round(1)
)
print(f"\n  Churn rate by tenure group (%):\n{tenure_churn.to_string()}")

# 2e. Churn by Payment Method
payment_churn = (
    df.groupby("PaymentMethod")["Churn_binary"]
    .mean()
    .mul(100)
    .round(1)
    .sort_values(ascending=False)
)
print(f"\n  Churn rate by payment method (%):\n{payment_churn.to_string()}")

# ── 3. VISUALISATIONS ────────────────────────────────────────────────────────
print("\n[3] Creating charts …")

def save(fig, name):
    path = f"{OUTPUT_DIR}/{name}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved → {path}")


# Chart 1 – Overall Churn (donut)
fig, ax = plt.subplots(figsize=(6, 6))
sizes  = [overall_churn, 100 - overall_churn]
labels = [f"Churned\n{overall_churn:.1f}%", f"Retained\n{100-overall_churn:.1f}%"]
ax.pie(sizes, labels=labels, colors=[CHURN_COLOR, STAY_COLOR],
       startangle=90, wedgeprops=dict(width=0.5),
       textprops={"fontsize": 13}, autopct="")
ax.set_title("Overall Churn Rate", fontweight="bold", pad=16, fontsize=14)
save(fig, "chart1_overall_churn.png")


# Chart 2 – Churn Rate by Contract Type
fig, ax = plt.subplots(figsize=(7, 4))
colors = [CHURN_COLOR if v == contract_churn.max() else STAY_COLOR for v in contract_churn.values]
bars = ax.bar(contract_churn.index, contract_churn.values, color=colors, edgecolor="none")
ax.bar_label(bars, labels=[f"{v}%" for v in contract_churn.values], padding=4)
ax.set_ylabel("Churn Rate (%)")
ax.set_title("Churn Rate by Contract Type", fontweight="bold", pad=12)
ax.set_ylim(0, contract_churn.max() * 1.2)
save(fig, "chart2_churn_by_contract.png")


# Chart 3 – Monthly Charges Distribution (churned vs retained)
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(retained_charges, bins=30, alpha=0.6, color=STAY_COLOR, label="Retained", density=True)
ax.hist(churned_charges,  bins=30, alpha=0.6, color=CHURN_COLOR, label="Churned",  density=True)
ax.axvline(retained_charges.mean(), color=STAY_COLOR,  linestyle="--", linewidth=1.5, label=f"Retained avg ${retained_charges.mean():.0f}")
ax.axvline(churned_charges.mean(),  color=CHURN_COLOR, linestyle="--", linewidth=1.5, label=f"Churned avg ${churned_charges.mean():.0f}")
ax.set_xlabel("Monthly Charges ($)")
ax.set_ylabel("Density")
ax.set_title("Monthly Charges: Churned vs Retained", fontweight="bold", pad=12)
ax.legend(fontsize=10)
save(fig, "chart3_monthly_charges.png")


# Chart 4 – Churn Rate by Tenure Group
fig, ax = plt.subplots(figsize=(7, 4))
colors = [CHURN_COLOR if v == tenure_churn.max() else STAY_COLOR for v in tenure_churn.values]
bars = ax.bar(tenure_churn.index.astype(str), tenure_churn.values, color=colors, edgecolor="none")
ax.bar_label(bars, labels=[f"{v}%" for v in tenure_churn.values], padding=4)
ax.set_ylabel("Churn Rate (%)")
ax.set_xlabel("Customer Tenure")
ax.set_title("Churn Rate by Tenure Group", fontweight="bold", pad=12)
ax.set_ylim(0, tenure_churn.max() * 1.2)
save(fig, "chart4_churn_by_tenure.png")


# Chart 5 – Churn Rate by Internet Service
fig, ax = plt.subplots(figsize=(7, 4))
colors = [CHURN_COLOR if v == internet_churn.max() else STAY_COLOR for v in internet_churn.values]
bars = ax.bar(internet_churn.index, internet_churn.values, color=colors, edgecolor="none")
ax.bar_label(bars, labels=[f"{v}%" for v in internet_churn.values], padding=4)
ax.set_ylabel("Churn Rate (%)")
ax.set_title("Churn Rate by Internet Service Type", fontweight="bold", pad=12)
ax.set_ylim(0, internet_churn.max() * 1.2)
save(fig, "chart5_churn_by_internet.png")


# ── 4. KEY FINDINGS ──────────────────────────────────────────────────────────
highest_contract = contract_churn.idxmax()
lowest_contract  = contract_churn.idxmin()
highest_tenure   = tenure_churn.idxmax()
highest_internet = internet_churn.idxmax()
highest_payment  = payment_churn.idxmax()

print("\n" + "=" * 60)
print("KEY FINDINGS")
print("=" * 60)
print(f"  • Overall churn rate       : {overall_churn:.1f}%")
print(f"  • Highest churn contract   : {highest_contract} ({contract_churn.max()}%)")
print(f"  • Lowest churn contract    : {lowest_contract} ({contract_churn.min()}%)")
print(f"  • Highest churn tenure     : {highest_tenure} ({tenure_churn.max()}%)")
print(f"  • Highest churn internet   : {highest_internet} ({internet_churn.max()}%)")
print(f"  • Riskiest payment method  : {highest_payment} ({payment_churn.max()}%)")
print(f"  • Avg charges (churned)    : ${churned_charges.mean():.2f}")
print(f"  • Avg charges (retained)   : ${retained_charges.mean():.2f}")
print("\nAll charts saved as PNG files.")
print("=" * 60)
