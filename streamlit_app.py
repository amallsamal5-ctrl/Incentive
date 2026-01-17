import streamlit as st
import pandas as pd
import requests
import numpy as np
import math

# =========================================================
# 1) GOOGLE SHEET URL
# =========================================================

SHEET_URL = "https://script.google.com/macros/s/AKfycbzp20rll0uyWA6TbKvEsZIBM9m6uzfiu8O4sSsozxeZAQiNst7zW1fDy3Maq4cgh6x95w/exec"

@st.cache_data
def load_data():
    response = requests.get(SHEET_URL)
    data = response.json()
    full_df = pd.DataFrame(data[1:], columns=data[0])
    required_cols = ["Deal owner", "Amount"]
    df = full_df.loc[:, full_df.columns.intersection(required_cols)]
    return df

df = load_data()
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

# =========================================================
# 2) DASHBOARD TITLE
# =========================================================

st.title("📊 Incentive Dashboard - Person-specific Slabs")

# =========================================================
# 3) COMPLETE TABLE DATA WITH DIFFERENT SLABS FOR EACH PERSON
# =========================================================

# Directly from your table - ALL VALUES ARE NET REVENUE (after GST removal)
table_data = {
    # Format: {name: [GST_Revenue, first_slab, first_incentive, second_slab, second_incentive, third_slab, third_incentive, fourth_slab]}
    
    # TEAM 1
    "Nisha Samuel": [298690, 90000, 2100, 300000, 7050, 750000, 10290, 1020000],
    "Bindu -": [353694, 130000, 4900, 620000, 9520, 1040000, 15760, 1560000],
    "Remya Raghunath": [257716, 110000, 3500, 460000, 8340, 900000, 12660, 1260000],
    "Jibymol Varghese": [215973, 100000, 3200, 420000, 7710, 830000, 11430, 1140000],
    "akhila shaji": [218119, 100000, 3400, 440000, 8240, 880000, 12080, 1200000],
    "Geethu Babu": [190431, 110000, 3500, 460000, 8340, 900000, 12660, 1260000],
    "parvathy R": [126050, 80000, 2500, 330000, 6130, 660000, 9010, 900000],
    "Arya S": [187849, 80000, 2500, 330000, 6130, 660000, 9010, 900000],
    
    # TEAM 2
    "Remya Ravindran": [205280, 100000, 3400, 440000, 8240, 880000, 12080, 1200000],
    "Sumithra -": [202138, 120000, 4100, 530000, 9930, 1060000, 14490, 1440000],
    "Jayasree -": [274577, 90000, 3100, 400000, 7500, 800000, 10860, 1080000],
    "SANIJA K P": [118004, 90000, 3100, 400000, 7500, 800000, 10860, 1080000],
    "Shubha Lakshmi": [233883, 90000, 3100, 400000, 7500, 800000, 10860, 1080000],
    "Arya Bose": [114519, 100000, 3400, 440000, 8240, 880000, 12080, 1200000],
    "Aneena Elsa Shibu": [220605, 90000, 3100, 400000, 7500, 800000, 10860, 1080000],
    "Merin j": [234160, 100000, 3200, 420000, 7710, 830000, 11430, 1140000]
}

# Progressive rates (SAME for everyone)
slab_rates = {1: 100, 2: 110, 3: 120, 4: 130}

# =========================================================
# 4) SUMMARIZE REVENUE FROM GOOGLE SHEET
# =========================================================

summary = df.groupby("Deal owner")["Amount"].sum().reset_index()
summary.columns = ["Name", "Actual GST Revenue"]  # From Google Sheet

# Calculate NET Revenue (remove 18% GST)
summary["Actual Net Revenue"] = np.floor(summary["Actual GST Revenue"] / 1.18)
summary["GST Amount"] = summary["Actual GST Revenue"] - summary["Actual Net Revenue"]

# =========================================================
# 5) ADD TABLE DATA FOR COMPARISON
# =========================================================

def add_table_data(row):
    name = row["Name"]
    data = table_data.get(name, [0]*8)
    
    return pd.Series({
        "Table GST Revenue": data[0],
        "Table Net Revenue": data[0] / 1.18,
        "First Slab": data[1],
        "First Incentive at Target": data[2],
        "Second Slab": data[3],
        "Second Incentive at Target": data[4],
        "Third Slab": data[5],
        "Third Incentive at Target": data[6],
        "Fourth Slab": data[7]
    })

table_info = summary.apply(add_table_data, axis=1)
summary = pd.concat([summary, table_info], axis=1)

# =========================================================
# 6) CORRECT INCENTIVE CALCULATION WITH DIFFERENT SLABS
# =========================================================

def calculate_incentive_different_slabs(row):
    name = row["Name"]
    actual_net = row["Actual Net Revenue"]  # From Google Sheet
    
    # Get person's specific slab thresholds
    data = table_data.get(name, [0]*8)
    first_slab = data[1]    # Person's first slab
    first_inc_target = data[2]  # Incentive at second slab
    second_slab = data[3]   # Person's second slab
    second_inc_target = data[4] # Incentive at third slab
    third_slab = data[5]    # Person's third slab
    third_inc_target = data[6] # Incentive at fourth slab
    fourth_slab = data[7]   # Person's fourth slab
    
    # Initialize results
    incentive = 0
    current_slab = "Not Reached"
    
    # Slab metrics
    slab_details = {
        "slab1_amount": 0, "slab1_blocks": 0, "slab1_inc": 0,
        "slab2_amount": 0, "slab2_blocks": 0, "slab2_inc": 0,
        "slab3_amount": 0, "slab3_blocks": 0, "slab3_inc": 0,
        "slab4_amount": 0, "slab4_blocks": 0, "slab4_inc": 0
    }
    
    # Check if eligible
    if actual_net < first_slab:
        return incentive, current_slab, slab_details
    
    # SLAB 1: First to Second slab
    if actual_net < second_slab:
        current_slab = "First Slab"
        amount_in_slab1 = actual_net - first_slab
        blocks_slab1 = math.floor(amount_in_slab1 / 10000)
        inc_slab1 = blocks_slab1 * slab_rates[1]
        incentive = inc_slab1
        
        slab_details.update({
            "slab1_amount": amount_in_slab1,
            "slab1_blocks": blocks_slab1,
            "slab1_inc": inc_slab1
        })
    
    # SLAB 2: Second to Third slab
    elif actual_net < third_slab:
        current_slab = "Second Slab"
        
        # Slab 1 (full)
        slab1_amount = second_slab - first_slab
        slab1_blocks = math.floor(slab1_amount / 10000)
        slab1_inc = slab1_blocks * slab_rates[1]
        
        # Slab 2 (partial)
        slab2_amount = actual_net - second_slab
        slab2_blocks = math.floor(slab2_amount / 10000)
        slab2_inc = slab2_blocks * slab_rates[2]
        
        incentive = slab1_inc + slab2_inc
        
        slab_details.update({
            "slab1_amount": slab1_amount,
            "slab1_blocks": slab1_blocks,
            "slab1_inc": slab1_inc,
            "slab2_amount": slab2_amount,
            "slab2_blocks": slab2_blocks,
            "slab2_inc": slab2_inc
        })
    
    # SLAB 3: Third to Fourth slab
    elif actual_net < fourth_slab:
        current_slab = "Third Slab"
        
        # Slab 1 (full)
        slab1_amount = second_slab - first_slab
        slab1_blocks = math.floor(slab1_amount / 10000)
        slab1_inc = slab1_blocks * slab_rates[1]
        
        # Slab 2 (full)
        slab2_amount = third_slab - second_slab
        slab2_blocks = math.floor(slab2_amount / 10000)
        slab2_inc = slab2_blocks * slab_rates[2]
        
        # Slab 3 (partial)
        slab3_amount = actual_net - third_slab
        slab3_blocks = math.floor(slab3_amount / 10000)
        slab3_inc = slab3_blocks * slab_rates[3]
        
        incentive = slab1_inc + slab2_inc + slab3_inc
        
        slab_details.update({
            "slab1_amount": slab1_amount,
            "slab1_blocks": slab1_blocks,
            "slab1_inc": slab1_inc,
            "slab2_amount": slab2_amount,
            "slab2_blocks": slab2_blocks,
            "slab2_inc": slab2_inc,
            "slab3_amount": slab3_amount,
            "slab3_blocks": slab3_blocks,
            "slab3_inc": slab3_inc
        })
    
    # SLAB 4: Above Fourth slab
    else:
        current_slab = "Fourth Slab"
        
        # Slab 1 (full)
        slab1_amount = second_slab - first_slab
        slab1_blocks = math.floor(slab1_amount / 10000)
        slab1_inc = slab1_blocks * slab_rates[1]
        
        # Slab 2 (full)
        slab2_amount = third_slab - second_slab
        slab2_blocks = math.floor(slab2_amount / 10000)
        slab2_inc = slab2_blocks * slab_rates[2]
        
        # Slab 3 (full)
        slab3_amount = fourth_slab - third_slab
        slab3_blocks = math.floor(slab3_amount / 10000)
        slab3_inc = slab3_blocks * slab_rates[3]
        
        # Slab 4 (partial)
        slab4_amount = actual_net - fourth_slab
        slab4_blocks = math.floor(slab4_amount / 10000)
        slab4_inc = slab4_blocks * slab_rates[4]
        
        incentive = slab1_inc + slab2_inc + slab3_inc + slab4_inc
        
        slab_details.update({
            "slab1_amount": slab1_amount,
            "slab1_blocks": slab1_blocks,
            "slab1_inc": slab1_inc,
            "slab2_amount": slab2_amount,
            "slab2_blocks": slab2_blocks,
            "slab2_inc": slab2_inc,
            "slab3_amount": slab3_amount,
            "slab3_blocks": slab3_blocks,
            "slab3_inc": slab3_inc,
            "slab4_amount": slab4_amount,
            "slab4_blocks": slab4_blocks,
            "slab4_inc": slab4_inc
        })
    
    return incentive, current_slab, slab_details

# Apply calculation
results = summary.apply(calculate_incentive_different_slabs, axis=1, result_type='expand')
results.columns = ["Incentive", "Current Slab", "Slab Details"]

summary = pd.concat([summary, results], axis=1)

# Extract slab details
details_df = pd.json_normalize(summary["Slab Details"])
summary = pd.concat([summary, details_df], axis=1)

# Calculate totals
summary["Total Eligible Amount"] = (
    summary["slab1_amount"] + summary["slab2_amount"] + 
    summary["slab3_amount"] + summary["slab4_amount"]
)
summary["Total Blocks"] = (
    summary["slab1_blocks"] + summary["slab2_blocks"] + 
    summary["slab3_blocks"] + summary["slab4_blocks"]
)

# Status
summary["Status"] = summary["Incentive"].apply(lambda x: "✅ Eligible" if x > 0 else "❌ Not Eligible")

# =========================================================
# 7) COMPREHENSIVE METRICS - SLAB WISE FOR EACH PERSON
# =========================================================

st.subheader("📊 Overall Performance Metrics")

# Row 1: Main KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total GST Revenue", f"₹{summary['Actual GST Revenue'].sum():,.0f}")

with col2:
    st.metric("Total Net Revenue", f"₹{summary['Actual Net Revenue'].sum():,.0f}")

with col3:
    st.metric("Total Incentive", f"₹{summary['Incentive'].sum():,.0f}")

with col4:
    eligible = (summary["Incentive"] > 0).sum()
    st.metric("Eligible People", f"{eligible}/{len(summary)}")

# Row 2: Slab Distribution
st.subheader("📈 People in Each Slab")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    not_reached = (summary["Current Slab"] == "Not Reached").sum()
    st.metric("Not Reached", not_reached)

with col2:
    in_first = (summary["Current Slab"] == "First Slab").sum()
    st.metric("First Slab", in_first)

with col3:
    in_second = (summary["Current Slab"] == "Second Slab").sum()
    st.metric("Second Slab", in_second)

with col4:
    in_third = (summary["Current Slab"] == "Third Slab").sum()
    st.metric("Third Slab", in_third)

with col5:
    in_fourth = (summary["Current Slab"] == "Fourth Slab").sum()
    st.metric("Fourth Slab", in_fourth)

# Row 3: Total Blocks by Slab
st.subheader("🧱 Total 10k Blocks Earned by Slab")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_slab1 = summary["slab1_blocks"].sum()
    st.metric("First Slab Blocks", f"{total_slab1:,.0f}")

with col2:
    total_slab2 = summary["slab2_blocks"].sum()
    st.metric("Second Slab Blocks", f"{total_slab2:,.0f}")

with col3:
    total_slab3 = summary["slab3_blocks"].sum()
    st.metric("Third Slab Blocks", f"{total_slab3:,.0f}")

with col4:
    total_slab4 = summary["slab4_blocks"].sum()
    st.metric("Fourth Slab Blocks", f"{total_slab4:,.0f}")

# Row 4: Total Incentive by Slab
st.subheader("💰 Total Incentive Earned by Slab")

col1, col2, col3, col4 = st.columns(4)

with col1:
    inc_slab1 = summary["slab1_inc"].sum()
    st.metric("First Slab Incentive", f"₹{inc_slab1:,.0f}")

with col2:
    inc_slab2 = summary["slab2_inc"].sum()
    st.metric("Second Slab Incentive", f"₹{inc_slab2:,.0f}")

with col3:
    inc_slab3 = summary["slab3_inc"].sum()
    st.metric("Third Slab Incentive", f"₹{inc_slab3:,.0f}")

with col4:
    inc_slab4 = summary["slab4_inc"].sum()
    st.metric("Fourth Slab Incentive", f"₹{inc_slab4:,.0f}")

# =========================================================
# 8) INDIVIDUAL SLAB COMPARISON TABLE
# =========================================================

st.subheader("🔍 Individual Slab Comparison")

# Create comparison table
comparison_data = []
for name, data in table_data.items():
    comparison_data.append({
        "Name": name,
        "First Slab": f"₹{data[1]:,.0f}",
        "Second Slab": f"₹{data[3]:,.0f}",
        "Third Slab": f"₹{data[5]:,.0f}",
        "Fourth Slab": f"₹{data[7]:,.0f}",
        "Max First Inc": f"₹{data[2]:,.0f}",
        "Max Second Inc": f"₹{data[4]:,.0f}",
        "Max Third Inc": f"₹{data[6]:,.0f}"
    })

comparison_df = pd.DataFrame(comparison_data)

# Split into Team 1 and Team 2
team1_names = ["Nisha Samuel", "Bindu -", "Remya Raghunath", "Jibymol Varghese", 
               "akhila shaji", "Geethu Babu", "parvathy R", "Arya S"]

comparison_df["Team"] = comparison_df["Name"].apply(lambda x: "Team 1" if x in team1_names else "Team 2")

col1, col2 = st.columns(2)
with col1:
    st.write("**Team 1 Slabs**")
    team1_df = comparison_df[comparison_df["Team"] == "Team 1"].drop(columns=["Team"])
    st.dataframe(team1_df, use_container_width=True, hide_index=True)

with col2:
    st.write("**Team 2 Slabs**")
    team2_df = comparison_df[comparison_df["Team"] == "Team 2"].drop(columns=["Team"])
    st.dataframe(team2_df, use_container_width=True, hide_index=True)

# =========================================================
# 9) INDIVIDUAL DETAILED CALCULATIONS
# =========================================================

st.subheader("👤 Individual Detailed Calculations with Different Slabs")

for idx, row in summary.iterrows():
    with st.expander(f"{row['Name']} - Slab: {row['Current Slab']} | Incentive: ₹{row['Incentive']:,.0f}"):
        
        # Revenue comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Actual Revenue (Google Sheet):**")
            st.write(f"GST Revenue: ₹{row['Actual GST Revenue']:,.0f}")
            st.write(f"Net Revenue: ₹{row['Actual Net Revenue']:,.0f}")
            
        with col2:
            st.write("**Table Reference (from your data):**")
            st.write(f"GST Revenue in Table: ₹{row['Table GST Revenue']:,.0f}")
            st.write(f"Net Revenue in Table: ₹{row['Table Net Revenue']:,.0f}")
        
        # Person's specific slabs
        st.write("**This Person's Slab Structure:**")
        cols = st.columns(4)
        with cols[0]:
            st.metric("First Slab", f"₹{row['First Slab']:,.0f}")
        with cols[1]:
            st.metric("Second Slab", f"₹{row['Second Slab']:,.0f}")
        with cols[2]:
            st.metric("Third Slab", f"₹{row['Third Slab']:,.0f}")
        with cols[3]:
            st.metric("Fourth Slab", f"₹{row['Fourth Slab']:,.0f}")
        
        # Calculation breakdown
        st.write("**Incentive Calculation Breakdown:**")
        
        breakdown_data = []
        if row["slab1_inc"] > 0:
            breakdown_data.append({
                "Slab": "First",
                "Threshold": f"₹{row['First Slab']:,.0f} - ₹{row['Second Slab']:,.0f}",
                "Eligible Amount": f"₹{row['slab1_amount']:,.0f}",
                "10k Blocks": row["slab1_blocks"],
                "Rate": "₹100",
                "Incentive": f"₹{row['slab1_inc']:,.0f}"
            })
        
        if row["slab2_inc"] > 0:
            breakdown_data.append({
                "Slab": "Second",
                "Threshold": f"₹{row['Second Slab']:,.0f} - ₹{row['Third Slab']:,.0f}",
                "Eligible Amount": f"₹{row['slab2_amount']:,.0f}",
                "10k Blocks": row["slab2_blocks"],
                "Rate": "₹110",
                "Incentive": f"₹{row['slab2_inc']:,.0f}"
            })
        
        if row["slab3_inc"] > 0:
            breakdown_data.append({
                "Slab": "Third",
                "Threshold": f"₹{row['Third Slab']:,.0f} - ₹{row['Fourth Slab']:,.0f}",
                "Eligible Amount": f"₹{row['slab3_amount']:,.0f}",
                "10k Blocks": row["slab3_blocks"],
                "Rate": "₹120",
                "Incentive": f"₹{row['slab3_inc']:,.0f}"
            })
        
        if row["slab4_inc"] > 0:
            breakdown_data.append({
                "Slab": "Fourth",
                "Threshold": f"Above ₹{row['Fourth Slab']:,.0f}",
                "Eligible Amount": f"₹{row['slab4_amount']:,.0f}",
                "10k Blocks": row["slab4_blocks"],
                "Rate": "₹130",
                "Incentive": f"₹{row['slab4_inc']:,.0f}"
            })
        
        if breakdown_data:
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            
            st.success(f"**Total Incentive = ₹{row['Incentive']:,.0f}**")
        else:
            st.write(f"Net Revenue (₹{row['Actual Net Revenue']:,.0f}) below first slab (₹{row['First Slab']:,.0f})")
            st.write("**No incentive earned**")

# =========================================================
# 10) MAIN SUMMARY TABLE
# =========================================================

st.subheader("📋 Complete Summary Table")

display_cols = [
    "Name", 
    "Actual Net Revenue", 
    "Current Slab",
    "First Slab", "Second Slab", "Third Slab", "Fourth Slab",
    "slab1_blocks", "slab1_inc",
    "slab2_blocks", "slab2_inc",
    "slab3_blocks", "slab3_inc",
    "slab4_blocks", "slab4_inc",
    "Incentive", 
    "Status"
]

summary_display = summary[display_cols].copy()
summary_display.columns = [
    "Name", "Net Revenue", "Current Slab",
    "1st Slab", "2nd Slab", "3rd Slab", "4th Slab",
    "1st Blocks", "1st Inc",
    "2nd Blocks", "2nd Inc",
    "3rd Blocks", "3rd Inc",
    "4th Blocks", "4th Inc",
    "Total Incentive", "Status"
]

st.dataframe(
    summary_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Net Revenue": st.column_config.NumberColumn(format="₹%d"),
        "1st Slab": st.column_config.NumberColumn(format="₹%d"),
        "2nd Slab": st.column_config.NumberColumn(format="₹%d"),
        "3rd Slab": st.column_config.NumberColumn(format="₹%d"),
        "4th Slab": st.column_config.NumberColumn(format="₹%d"),
        "1st Inc": st.column_config.NumberColumn(format="₹%d"),
        "2nd Inc": st.column_config.NumberColumn(format="₹%d"),
        "3rd Inc": st.column_config.NumberColumn(format="₹%d"),
        "4th Inc": st.column_config.NumberColumn(format="₹%d"),
        "Total Incentive": st.column_config.NumberColumn(format="₹%d"),
    }
)

# =========================================================
# 11) EXAMPLES OF DIFFERENT SLABS
# =========================================================

st.subheader("📝 Examples Showing Different Slabs")

examples = pd.DataFrame([
    {
        "Person": "Nisha Samuel",
        "Slabs": "90,000 → 300,000 → 750,000 → 1,020,000",
        "At 300,000 NET": "21 blocks × ₹100 = ₹2,100",
        "At 750,000 NET": "₹2,100 + (45×₹110=₹4,950) = ₹7,050"
    },
    {
        "Person": "Aneena",
        "Slabs": "90,000 → 400,000 → 800,000 → 1,080,000",
        "At 400,000 NET": "31 blocks × ₹100 = ₹3,100",
        "At 619,246 NET": "₹3,100 + (21×₹110=₹2,310) = ₹5,410"
    },
    {
        "Person": "Bindu",
        "Slabs": "130,000 → 620,000 → 1,040,000 → 1,560,000",
        "At 620,000 NET": "49 blocks × ₹100 = ₹4,900",
        "At 1,040,000 NET": "₹4,900 + (42×₹110=₹4,620) = ₹9,520"
    },
    {
        "Person": "Remya Raghunath",
        "Slabs": "110,000 → 460,000 → 900,000 → 1,260,000",
        "At 460,000 NET": "35 blocks × ₹100 = ₹3,500",
        "At 900,000 NET": "₹3,500 + (44×₹110=₹4,840) = ₹8,340"
    }
])

st.dataframe(examples, use_container_width=True, hide_index=True)

# =========================================================
# 12) DOWNLOAD
# =========================================================

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(summary)

st.download_button(
    label="📥 Download Full Report",
    data=csv,
    file_name="incentive_different_slabs.csv",
    mime="text/csv"
)

# =========================================================
# 13) FINAL VALIDATION
# =========================================================

st.subheader("✅ Final Validation - Different Slabs Confirmed")

st.info("""
**CORRECT UNDERSTANDING FINALIZED:**

✅ **Each person has DIFFERENT slab thresholds:**
- Nisha: 90K → 300K → 750K → 1,020K
- Aneena: 90K → 400K → 800K → 1,080K  
- Bindu: 130K → 620K → 1,040K → 1,560K
- Remya R.: 110K → 460K → 900K → 1,260K

✅ **Same progressive rates for everyone:**
- First Slab: ₹100 per ₹10,000 NET above person's first slab
- Second Slab: ₹110 per ₹10,000 NET above person's second slab
- Third Slab: ₹120 per ₹10,000 NET above person's third slab
- Fourth Slab: ₹130 per ₹10,000 NET above person's fourth slab

✅ **Table values are verification points at exact slab thresholds**
✅ **Uses NET Revenue (after GST removal)**
✅ **Only full ₹10,000 blocks count**

**Example Calculations Verified:**
- Nisha at ₹300,000: 21 × ₹100 = ₹2,100 ✓
- Aneena at ₹619,246: ₹3,100 + ₹2,310 = ₹5,410 ✓
- Bindu at ₹1,040,000: ₹4,900 + ₹4,620 = ₹9,520 ✓
""")

# =========================================================
# 14) RAW DATA
# =========================================================

with st.expander("📁 View Raw Google Sheet Data"):
    st.dataframe(df, use_container_width=True)
