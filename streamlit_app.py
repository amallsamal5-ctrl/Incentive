import streamlit as st
import pandas as pd
import requests
import numpy as np

# =========================================================
# 1) GOOGLE SHEET URL (Amount + Deal owner only)
# =========================================================

SHEET_URL = "https://script.google.com/macros/s/AKfycbzp20rll0uyWA6TbKvEsZIBM9m6uzfiu8O4sSsozxeZAQiNst7zW1fDy3Maq4cgh6x95w/exec"

@st.cache_data
def load_data():
    response = requests.get(SHEET_URL)
    data = response.json()

    full_df = pd.DataFrame(data[1:], columns=data[0])

    # Fetch only required columns
    required_cols = ["Deal owner", "Amount"]
    df = full_df.loc[:, full_df.columns.intersection(required_cols)]

    return df

df = load_data()

# Convert Amount to numeric
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# =========================================================
# 2) DASHBOARD TITLE
# =========================================================

st.title("📊 Incentive Dashboard (Net Revenue + First Slab Logic)")

# =========================================================
# 3) TARGET + FIRST SLAB (YOUR EXACT TABLE)
# =========================================================

targets = {
# TEAM 1
"Nisha Samuel": 734400,
"Bindu -": 1123200,
"Remya Raghunath": 907200,
"Jibymol Varghese": 820800,
"akhila shaji": 864000,
"Geethu Babu": 907200,
"parvathy R": 650000,
"Arya S": 500000,

# TEAM 2
"Remya Ravindran": 864000,
"Sumithra -": 1036800,
"Jayasree -": 777600,
"SANIJA K P": 777600,
"Shubha Lakshmi": 777600,
"Arya Bose": 864000,
"Aneena Elsa Shibu": 777600,
"Merin j": 400000
}

first_slab = {
# TEAM 1
"Nisha Samuel": 90000,
"Bindu -": 130000,
"Remya Raghunath": 110000,
"Jibymol Varghese": 100000,
"akhila shaji": 100000,
"Geethu Babu": 110000,
"parvathy R": 80000,
"Arya S": 80000,

# TEAM 2
"Remya Ravindran": 100000,
"Sumithra -": 120000,
"Jayasree -": 90000,
"SANIJA K P": 90000,
"Shubha Lakshmi": 90000,
"Arya Bose": 100000,
"Aneena Elsa Shibu": 90000,
"Merin j": 100000
}

# =========================================================
# 4) SUMMARIZE REVENUE PER PERSON
# =========================================================

summary = (
    df.groupby("Deal owner")["Amount"]
    .sum()
    .reset_index()
)

summary.columns = ["Name", "Total Revenue"]

# =========================================================
# 5) AUTO REMOVE GST (YOUR EXCEL LOGIC)
# =========================================================

summary["Net Revenue (GST Removed)"] = np.floor(summary["Total Revenue"] / 1.18)

# Calculate GST only for display
summary["Calculated GST"] = summary["Total Revenue"] - summary["Net Revenue (GST Removed)"]

# Add Target & First Slab per person
summary["Target"] = summary["Name"].apply(lambda x: targets.get(x, 0))
summary["First Slab"] = summary["Name"].apply(lambda x: first_slab.get(x, 0))

# =========================================================
# 6) CALCULATE INCENTIVE (YOUR FINAL CORRECT LOGIC)
# =========================================================

def calculate_incentive(row):
    net = row["Net Revenue (GST Removed)"]
    slab = row["First Slab"]

    # First check eligibility
    if net < slab:
        return 0
    else:
        # Once crossed slab, incentive is based on TOTAL net revenue
        return np.floor(net / 10000) * 100

summary["Incentive ₹"] = summary.apply(calculate_incentive, axis=1)

# Status
summary["Status"] = summary["Incentive ₹"].apply(
    lambda x: "Eligible ✅" if x > 0 else "Not Eligible ❌"
)

# Additional helpful column: How many 10k units achieved
summary["10k Units Achieved"] = np.floor(summary["Net Revenue (GST Removed)"] / 10000)

# =========================================================
# 7) KPI CARDS
# =========================================================

st.subheader("📌 Key Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Net Revenue", f"₹ {summary['Net Revenue (GST Removed)'].sum():,.0f}")

with col2:
    st.metric("Total Incentive", f"₹ {summary['Incentive ₹'].sum():,.0f}")

with col3:
    eligible_count = (summary["Incentive ₹"] > 0).sum()
    st.metric("Eligible People", eligible_count)

# =========================================================
# 8) FINAL CLEAN TABLE
# =========================================================

st.subheader("🎯 Incentive Summary")

st.dataframe(
    summary[[
        "Name",
        "Target",
        "Total Revenue",
        "Net Revenue (GST Removed)",
        "Calculated GST",
        "First Slab",
        "10k Units Achieved",
        "Incentive ₹",
        "Status"
    ]],
    use_container_width=True
)

# =========================================================
# 9) RAW DATA VIEW
# =========================================================

with st.expander("View Raw Google Sheet Data"):
    st.dataframe(df, use_container_width=True)
