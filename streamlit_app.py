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
    return full_df

full_df = load_data()

# =========================================================
# 2) DASHBOARD TITLE
# =========================================================

st.title("📊 Incentive Dashboard - Slab-wise + Course Targets")

# =========================================================
# 3) FIND CORRECT COLUMNS
# =========================================================

# Clean column names
full_df.columns = [str(col).strip() for col in full_df.columns]

# Find required columns
deal_owner_col = None
amount_col = None
close_date_col = None
course_col = None

for col in full_df.columns:
    col_lower = str(col).lower()
    if 'deal' in col_lower and 'owner' in col_lower:
        deal_owner_col = col
    elif 'amount' in col_lower or 'value' in col_lower:
        amount_col = col
    elif 'close' in col_lower and 'date' in col_lower:
        close_date_col = col
    elif 'course' in col_lower or 'product' in col_lower:
        course_col = col

# Use defaults if not found
if not deal_owner_col and len(full_df.columns) > 0:
    deal_owner_col = full_df.columns[0]
if not amount_col and len(full_df.columns) > 1:
    amount_col = full_df.columns[1]
if not close_date_col and len(full_df.columns) > 2:
    close_date_col = full_df.columns[2]
if not course_col and len(full_df.columns) > 3:
    course_col = full_df.columns[3]

# Create TWO dataframes:
# 1. For revenue calculation (ALL deals)
# 2. For course count (only CLOSED deals)

# ALL deals for revenue
revenue_df = full_df[[deal_owner_col, amount_col]].copy()
revenue_df.columns = ["Deal owner", "Amount"]
revenue_df["Amount"] = pd.to_numeric(revenue_df["Amount"], errors="coerce")

# CLOSED deals only for course count
if close_date_col and course_col:
    closed_df = full_df[[deal_owner_col, close_date_col, course_col]].copy()
    closed_df.columns = ["Deal owner", "Close Date", "Course"]
    # Filter for closed deals only
    closed_df = closed_df[closed_df["Close Date"].notna() & (closed_df["Close Date"].astype(str).str.strip() != "")]
else:
    # If no close date column, use all deals for course count
    closed_df = full_df[[deal_owner_col, course_col]].copy()
    closed_df.columns = ["Deal owner", "Course"]

# =========================================================
# 4) TABLE DATA WITH DIFFERENT SLABS FOR EACH PERSON
# =========================================================

table_data = {
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

# Progressive rates
slab_rates = {1: 100, 2: 110, 3: 120, 4: 130}

# =========================================================
# 5) STEP 1: CALCULATE FIRST INCENTIVE (BASED ON TOTAL REVENUE)
# =========================================================

st.header("💰 STEP 1: Calculate First Incentive (Based on TOTAL Revenue)")

# Summarize ALL revenue (not just closed deals)
summary = revenue_df.groupby("Deal owner")["Amount"].sum().reset_index()
summary.columns = ["Name", "Total GST Revenue"]

# Calculate NET Revenue (remove 18% GST) - from ALL deals
summary["Total Net Revenue"] = np.floor(summary["Total GST Revenue"] / 1.18)
summary["GST Amount"] = summary["Total GST Revenue"] - summary["Total Net Revenue"]

# Add table data for comparison
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

# Calculate slab-wise incentive based on TOTAL net revenue
def calculate_incentive_different_slabs(row):
    name = row["Name"]
    total_net = row["Total Net Revenue"]  # From ALL deals
    
    data = table_data.get(name, [0]*8)
    first_slab = data[1]
    second_slab = data[3]
    third_slab = data[5]
    fourth_slab = data[7]
    
    incentive = 0
    current_slab = "Not Reached"
    
    # Check if eligible
    if total_net < first_slab:
        return incentive, current_slab
    
    # SLAB 1: First to Second slab
    if total_net < second_slab:
        current_slab = "First Slab"
        amount_in_slab1 = total_net - first_slab
        blocks_slab1 = math.floor(amount_in_slab1 / 10000)
        incentive = blocks_slab1 * slab_rates[1]
    
    # SLAB 2: Second to Third slab
    elif total_net < third_slab:
        current_slab = "Second Slab"
        
        # Slab 1 (full)
        slab1_amount = second_slab - first_slab
        slab1_blocks = math.floor(slab1_amount / 10000)
        slab1_inc = slab1_blocks * slab_rates[1]
        
        # Slab 2 (partial)
        slab2_amount = total_net - second_slab
        slab2_blocks = math.floor(slab2_amount / 10000)
        slab2_inc = slab2_blocks * slab_rates[2]
        
        incentive = slab1_inc + slab2_inc
    
    # SLAB 3: Third to Fourth slab
    elif total_net < fourth_slab:
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
        slab3_amount = total_net - third_slab
        slab3_blocks = math.floor(slab3_amount / 10000)
        slab3_inc = slab3_blocks * slab_rates[3]
        
        incentive = slab1_inc + slab2_inc + slab3_inc
    
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
        slab4_amount = total_net - fourth_slab
        slab4_blocks = math.floor(slab4_amount / 10000)
        slab4_inc = slab4_blocks * slab_rates[4]
        
        incentive = slab1_inc + slab2_inc + slab3_inc + slab4_inc
    
    return incentive, current_slab

# Apply calculation
results = summary.apply(calculate_incentive_different_slabs, axis=1, result_type='expand')
results.columns = ["First Incentive", "Current Slab"]
summary = pd.concat([summary, results], axis=1)

# Display first incentive
st.subheader("First Incentive Based on TOTAL Revenue")
st.dataframe(summary[["Name", "Total Net Revenue", "Current Slab", "First Incentive"]], 
             use_container_width=True, hide_index=True)

# =========================================================
# 6) STEP 2: COUNT COURSE-WISE ADMISSIONS (CLOSED DEALS ONLY)
# =========================================================

st.header("🎯 STEP 2: Count Course-wise Admissions (CLOSED Deals Only)")

# Define courses with their search patterns
course_patterns = {
    "OET": ["oet"],
    "PTE": ["pte"],
    "IELTS": ["ielts"],
    "German": ["german", "deutsch"],
    "Prometric": ["prometric"],
    "Nclex-RN": ["nclex", "nclex-rn"],
    "DM": ["digital marketing", "dm", "digital marketing full package"],
    "Fluency": ["fluency"],
    "Media": [
        "media",
        "diploma in cinematography and photography",
        "diploma in editing & colour grading", 
        "diploma in editing and colour grading",
        "diploma in scriptwriting and direction",
        "cinematography",
        "photography",
        "editing",
        "colour grading",
        "scriptwriting",
        "direction"
    ]
}

target_per_course = 3

# Create a dictionary to store course counts and top performers
course_top_performers = {}
course_summary_data = []

# Count CLOSED admissions per course per person
for course_name, patterns in course_patterns.items():
    # Create a mask for this course using all patterns
    course_mask = pd.Series(False, index=closed_df.index)
    for pattern in patterns:
        course_mask = course_mask | closed_df["Course"].astype(str).str.contains(pattern, case=False, na=False)
    
    course_counts = closed_df[course_mask].groupby("Deal owner").size().reset_index()
    course_counts.columns = ["Name", f"{course_name}_Closed_Count"]
    
    # Merge with summary
    summary = pd.merge(summary, course_counts, on="Name", how="left")
    summary[f"{course_name}_Closed_Count"] = summary[f"{course_name}_Closed_Count"].fillna(0).astype(int)
    
    # Find top performer(s) for this course
    if not course_counts.empty:
        top_count = course_counts[f"{course_name}_Closed_Count"].max()
        top_performers = course_counts[course_counts[f"{course_name}_Closed_Count"] == top_count]["Name"].tolist()
        course_top_performers[course_name] = {"count": top_count, "names": top_performers}
    
    # Calculate course summary
    total_admissions = course_counts[f"{course_name}_Closed_Count"].sum() if not course_counts.empty else 0
    people_with_course = len(course_counts) if not course_counts.empty else 0
    met_target = len(course_counts[course_counts[f"{course_name}_Closed_Count"] >= target_per_course]) if not course_counts.empty else 0
    
    course_summary_data.append({
        "Course": course_name,
        "Total Admissions": total_admissions,
        "People with Course": people_with_course,
        "Met Target (≥3)": met_target,
        "Below Target": people_with_course - met_target,
        "Top Performer Count": top_count if not course_counts.empty else 0,
        "Top Performers": ", ".join(top_performers) if not course_counts.empty else "None"
    })

# Display course counts with emoji indicators
st.subheader("📊 Closed Deals Count (Course-wise)")

# Create display dataframe with emojis
course_display_data = []
for idx, row in summary.iterrows():
    person_data = {"Name": row["Name"]}
    
    for course_name in course_patterns.keys():
        count = row[f"{course_name}_Closed_Count"]
        if count > 0:
            # Check if target met
            target_met = count >= target_per_course
            
            # Check if top performer
            is_top = False
            if course_name in course_top_performers:
                if row["Name"] in course_top_performers[course_name]["names"]:
                    is_top = True
            
            # Create display string with emojis
            display_text = f"{count}"
            if is_top:
                display_text += " 🏆"  # Trophy for top performer
            if target_met:
                display_text += " ✅"   # Green tick for target met
            else:
                display_text += " ❌"   # Red X for target not met
            
            person_data[course_name] = display_text
        else:
            person_data[course_name] = "0"
    
    course_display_data.append(person_data)

course_display_df = pd.DataFrame(course_display_data)
st.dataframe(course_display_df, use_container_width=True, hide_index=True)

# Display course summary
st.subheader("📈 Course-wise Summary")

course_summary_df = pd.DataFrame(course_summary_data)
st.dataframe(course_summary_df, use_container_width=True, hide_index=True)

# =========================================================
# 7) STEP 3: APPLY 11% PENALTY/REWARD PER COURSE (WITH TIE HANDLING)
# =========================================================

st.header("💰 STEP 3: Apply Course Penalty/Reward (11% of First Incentive)")

# Initialize columns
summary["Total_Penalty"] = 0.0
summary["Total_Reward"] = 0.0
summary["Final_Incentive"] = summary["First Incentive"].copy()

# Store detailed penalty/reward info
penalty_reward_details = {}

# Apply penalty per course
for course_name in course_patterns.keys():
    # Add columns for this course
    summary[f"{course_name}_Penalty"] = 0.0
    summary[f"{course_name}_Reward"] = 0.0
    
    # Get people with this course (who have at least 1 closed deal)
    course_people = summary[summary[f"{course_name}_Closed_Count"] > 0].copy()
    
    if len(course_people) > 0:
        # Find below target people (< 3 closed deals)
        below_target = course_people[course_people[f"{course_name}_Closed_Count"] < target_per_course]
        
        if len(below_target) > 0:
            # Find ALL top performers (max closed deals count)
            max_count = course_people[f"{course_name}_Closed_Count"].max()
            top_performers = course_people[course_people[f"{course_name}_Closed_Count"] == max_count]["Name"].tolist()
            
            # Apply 11% penalty to below-target people
            total_penalty = 0.0
            penalty_details = []
            
            for _, person in below_target.iterrows():
                name = person["Name"]
                penalty_amount = person["First Incentive"] * 0.11
                
                # Apply penalty
                mask = summary["Name"] == name
                summary.loc[mask, f"{course_name}_Penalty"] = penalty_amount
                summary.loc[mask, "Total_Penalty"] += penalty_amount
                summary.loc[mask, "Final_Incentive"] -= penalty_amount
                
                total_penalty += penalty_amount
                penalty_details.append({
                    "person": name,
                    "count": person[f"{course_name}_Closed_Count"],
                    "penalty": penalty_amount,
                    "first_incentive": person["First Incentive"]
                })
            
            # Split penalty equally among ALL top performers
            if total_penalty > 0 and len(top_performers) > 0:
                reward_per_person = total_penalty / len(top_performers)
                
                for top_name in top_performers:
                    if top_name in summary["Name"].values:
                        top_mask = summary["Name"] == top_name
                        summary.loc[top_mask, f"{course_name}_Reward"] = reward_per_person
                        summary.loc[top_mask, "Total_Reward"] += reward_per_person
                        summary.loc[top_mask, "Final_Incentive"] += reward_per_person
                
                # Store details for display
                penalty_reward_details[course_name] = {
                    "total_penalty": total_penalty,
                    "top_performers": top_performers,
                    "reward_per_person": reward_per_person,
                    "penalty_details": penalty_details,
                    "max_count": max_count
                }

# Calculate net adjustment
summary["Net_Adjustment"] = summary["Total_Reward"] - summary["Total_Penalty"]

# Display tie-case handling examples
st.subheader("🎯 Tie-Case Handling Examples")

if penalty_reward_details:
    for course_name, details in penalty_reward_details.items():
        if len(details["top_performers"]) > 1:  # Only show if there's a tie
            st.write(f"**{course_name} Course - Tie Case Example:**")
            
            # Show top performers
            st.write(f"🏆 **Top Performers ({len(details['top_performers'])} people tied):**")
            for i, top_name in enumerate(details["top_performers"], 1):
                st.write(f"  {i}. {top_name} - {details['max_count']} closed deals")
            
            # Show penalty details
            st.write(f"💰 **Penalties Collected:** ₹{details['total_penalty']:,.2f}")
            for penalty_detail in details["penalty_details"]:
                st.write(f"  - {penalty_detail['person']}: {penalty_detail['count']} deals → 11% of ₹{penalty_detail['first_incentive']:,.0f} = ₹{penalty_detail['penalty']:,.2f}")
            
            # Show reward distribution
            st.write(f"🎁 **Reward Distribution (split equally):**")
            st.write(f"  Each top performer gets: ₹{details['total_penalty']:,.2f} ÷ {len(details['top_performers'])} = ₹{details['reward_per_person']:,.2f}")
            
            st.write("---")

# =========================================================
# 8) DISPLAY FINAL RESULTS
# =========================================================

st.header("🏆 FINAL RESULTS")

# Final summary table
final_cols = [
    "Name", 
    "Total Net Revenue",
    "First Incentive",
    "Total_Penalty",
    "Total_Reward",
    "Net_Adjustment",
    "Final_Incentive"
]

final_display = summary[final_cols].copy()
final_display.columns = [
    "Name",
    "Total Net Revenue",
    "First Incentive",
    "Total Penalties",
    "Total Rewards",
    "Net Adjustment",
    "Final Incentive"
]

st.dataframe(
    final_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Total Net Revenue": st.column_config.NumberColumn(format="₹%d"),
        "First Incentive": st.column_config.NumberColumn(format="₹%d"),
        "Total Penalties": st.column_config.NumberColumn(format="₹%d"),
        "Total Rewards": st.column_config.NumberColumn(format="₹%d"),
        "Net Adjustment": st.column_config.NumberColumn(format="₹%d"),
        "Final Incentive": st.column_config.NumberColumn(format="₹%d"),
    }
)

# =========================================================
# 9) DETAILED COURSE-WISE ADJUSTMENTS
# =========================================================

st.subheader("📊 Detailed Course-wise Adjustments")

for idx, row in summary.iterrows():
    # Check if person has any course data or penalties/rewards
    has_course_data = any([row[f"{course}_Closed_Count"] > 0 for course in course_patterns.keys()])
    has_adjustments = row["Total_Penalty"] > 0 or row["Total_Reward"] > 0
    
    if has_course_data or has_adjustments:
        with st.expander(f"{row['Name']} - First: ₹{row['First Incentive']:,.0f} | Final: ₹{row['Final_Incentive']:,.0f}"):
            
            # Basic info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Revenue & Incentive:**")
                st.write(f"Total Net Revenue: ₹{row['Total Net Revenue']:,.0f}")
                st.write(f"First Incentive: ₹{row['First Incentive']:,.0f}")
                st.write(f"Total Penalties: ₹{row['Total_Penalty']:,.0f}")
                st.write(f"Total Rewards: ₹{row['Total_Reward']:,.0f}")
                st.write(f"**Final Incentive: ₹{row['Final_Incentive']:,.0f}**")
            
            with col2:
                st.write("**Closed Deals Count:**")
                course_data = []
                for course_name in course_patterns.keys():
                    count = row[f"{course_name}_Closed_Count"]
                    if count > 0:
                        # Check if target met
                        target_met = count >= target_per_course
                        
                        # Check if top performer
                        is_top = False
                        if course_name in course_top_performers:
                            if row["Name"] in course_top_performers[course_name]["names"]:
                                is_top = True
                        
                        status = ""
                        if is_top:
                            status += "🏆 "  # Trophy for top performer
                        if target_met:
                            status += "✅"   # Green tick for target met
                        else:
                            status += "❌"   # Red X for target not met
                        
                        course_data.append(f"{course_name}: {count} {status}")
                
                if course_data:
                    for data in course_data:
                        st.write(data)
                else:
                    st.write("No closed deals recorded")
            
            # Show penalties and rewards by course
            adjustments = []
            for course_name in course_patterns.keys():
                penalty = row[f"{course_name}_Penalty"]
                reward = row[f"{course_name}_Reward"]
                
                if penalty > 0:
                    adjustments.append({
                        "Course": course_name,
                        "Type": "Penalty (11%)",
                        "Amount": f"-₹{penalty:,.0f}",
                        "Reason": f"Below target ({row[f'{course_name}_Closed_Count']} < {target_per_course})"
                    })
                elif reward > 0:
                    adjustments.append({
                        "Course": course_name,
                        "Type": "Reward",
                        "Amount": f"+₹{reward:,.0f}",
                        "Reason": "Top performer in course"
                    })
            
            if adjustments:
                st.write("**Course-wise Adjustments:**")
                adjustments_df = pd.DataFrame(adjustments)
                st.dataframe(adjustments_df, use_container_width=True, hide_index=True)

# =========================================================
# 10) COURSE DEFINITIONS AND TARGET EXPLANATION
# =========================================================

st.subheader("📚 Course Definitions & Media Courses Included")

course_definitions = pd.DataFrame([
    {
        "Course": "OET",
        "Definition": "Occupational English Test",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "PTE", 
        "Definition": "Pearson Test of English",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "IELTS",
        "Definition": "International English Language Testing System",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "German",
        "Definition": "German Language Courses",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "Prometric",
        "Definition": "Prometric Exam Preparation",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "Nclex-RN",
        "Definition": "NCLEX-RN Exam Preparation",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "DM",
        "Definition": "Digital Marketing Full Package",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "Fluency",
        "Definition": "Fluency Development Programs",
        "Target": "≥3 closed deals"
    },
    {
        "Course": "Media",
        "Definition": "Includes: Diploma in Cinematography & Photography, Diploma in Editing & Colour Grading, Diploma in Scriptwriting & Direction",
        "Target": "≥3 closed deals (combined)"
    }
])

st.dataframe(course_definitions, use_container_width=True, hide_index=True)

st.info("""
**📊 Display Legend:**
- **🏆 Trophy** = Top performer in that course (most closed deals) - can be multiple people
- **✅ Green Tick** = Met target (≥3 closed deals)
- **❌ Red X** = Below target (<3 closed deals)
- **0** = No closed deals in that course

**TIE CASE HANDLING:**
- When multiple people have same highest count, ALL get 🏆 trophy
- Penalty money is split EQUALLY among all top performers
- Example: 2 people tied with 9 count, 1 person with 2 count → Penalty split 50/50
""")

# =========================================================
# 11) OVERALL METRICS
# =========================================================

st.subheader("📈 Overall Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total First Incentive", f"₹{summary['First Incentive'].sum():,.0f}")

with col2:
    total_penalty = summary['Total_Penalty'].sum()
    st.metric("Total Penalties", f"₹{total_penalty:,.0f}")

with col3:
    total_reward = summary['Total_Reward'].sum()
    st.metric("Total Rewards", f"₹{total_reward:,.0f}")

with col4:
    st.metric("Final Total Incentive", f"₹{summary['Final_Incentive'].sum():,.0f}")

# Course target metrics
st.subheader("🎯 Course Target Achievement")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_closed = sum([summary[f"{course}_Closed_Count"].sum() for course in course_patterns.keys()])
    st.metric("Total Closed Deals", f"{total_closed}")

with col2:
    total_met = sum([(summary[f"{course}_Closed_Count"] >= target_per_course).sum() for course in course_patterns.keys()])
    st.metric("Total Met Targets", f"{total_met}")

with col3:
    total_below = sum([((summary[f"{course}_Closed_Count"] > 0) & (summary[f"{course}_Closed_Count"] < target_per_course)).sum() for course in course_patterns.keys()])
    st.metric("Total Below Targets", f"{total_below}")

with col4:
    total_top = len(set([name for course in course_top_performers.values() for name in course["names"]]))
    st.metric("Top Performers", f"{total_top}")

# =========================================================
# 12) DOWNLOAD FINAL REPORT
# =========================================================

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(summary)

st.download_button(
    label="📥 Download Full Report",
    data=csv,
    file_name="final_incentive_report.csv",
    mime="text/csv"
)

# =========================================================
# 13) LOGIC SUMMARY
# =========================================================

st.subheader("✅ FINAL LOGIC IMPLEMENTED")

st.success("""
**TWO-STEP CALCULATION COMPLETE:**

**STEP 1: Calculate First Incentive (Slab-wise)**
- Based on TOTAL revenue (ALL deals, not just closed)
- Different slabs for each person
- Progressive rates: ₹100 → ₹110 → ₹120 → ₹130 per ₹10,000 block
- Uses NET Revenue (GST removed)

**STEP 2: Apply Course Penalty/Reward (11% of First Incentive)**
- **Target:** 3 CLOSED deals per course
- **Below target (<3 closed):** Lose 11% of First Incentive
- **Top performer(s):** Gets ALL penalties from below-target
- **TIE CASE:** When multiple people have same max count → ALL get penalty split EQUALLY
- **Met target (≥3 closed, not top):** No penalty, no reward
- Applied separately for EACH course

**TIE CASE EXAMPLE:**
- Person A: 9 count, First Incentive ₹10,000
- Person B: 9 count, First Incentive ₹8,000 (TIE with A)
- Person C: 2 count, First Incentive ₹6,000

**Calculation:**
1. Person C penalty = ₹6,000 × 11% = ₹660
2. Total penalty = ₹660
3. 2 top performers → Each gets ₹660 ÷ 2 = ₹330
4. **Results:** 
   - Person A: ₹10,000 + ₹330 = ₹10,330 🏆
   - Person B: ₹8,000 + ₹330 = ₹8,330 🏆
   - Person C: ₹6,000 - ₹660 = ₹5,340 ❌
""")

# =========================================================
# 14) RAW DATA VIEW
# =========================================================

with st.expander("📁 View Raw Data"):
    tab1, tab2 = st.tabs(["All Deals (Revenue)", "Closed Deals (Count)"])
    
    with tab1:
        st.write("**All Deals for Revenue Calculation:**")
        st.dataframe(revenue_df, use_container_width=True)
    
    with tab2:
        st.write("**Closed Deals for Course Count:**")
        st.dataframe(closed_df, use_container_width=True)
        
        # Show course matching examples
        st.write("**Course Pattern Matching Examples:**")
        for course_name, patterns in course_patterns.items():
            sample_matches = closed_df[closed_df["Course"].astype(str).str.contains(patterns[0], case=False, na=False)]["Course"].unique()[:3]
            if len(sample_matches) > 0:
                st.write(f"{course_name}: {', '.join(sample_matches[:3])}")
