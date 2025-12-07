import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Battery Material Value Calculator", layout="wide")

st.title("🔋 Lithium-Ion Battery & Black Mass Value Calculator")
st.markdown("Calculate the value of battery materials based on composition and commodity prices")

# Sidebar for commodity prices
st.sidebar.header("💰 Commodity Prices (USD/kg)")
st.sidebar.markdown("*Update with current market prices*")

prices = {
    "Lithium (Li)": st.sidebar.number_input("Lithium (Li)", value=20.0, min_value=0.0, step=0.5),
    "Cobalt (Co)": st.sidebar.number_input("Cobalt (Co)", value=30.0, min_value=0.0, step=0.5),
    "Nickel (Ni)": st.sidebar.number_input("Nickel (Ni)", value=18.0, min_value=0.0, step=0.5),
    "Manganese (Mn)": st.sidebar.number_input("Manganese (Mn)", value=2.5, min_value=0.0, step=0.1),
    "Copper (Cu)": st.sidebar.number_input("Copper (Cu)", value=9.0, min_value=0.0, step=0.5),
    "Aluminum (Al)": st.sidebar.number_input("Aluminum (Al)", value=2.5, min_value=0.0, step=0.1),
}

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Payable Percentage")
payable_pct = st.sidebar.slider("Payable %", min_value=0, max_value=100, value=85, step=5)
st.sidebar.markdown(f"*Recycler pays {payable_pct}% of material value*")

# Main content - Material composition input
st.header("📊 Material Composition")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Method")
    input_method = st.radio("Choose input method:", ["Manual Entry", "Preset Battery Types"])

with col2:
    st.subheader("Total Material Weight")
    total_weight = st.number_input("Total weight (kg)", value=100.0, min_value=0.1, step=1.0)

# Composition inputs
composition = {}

if input_method == "Manual Entry":
    st.markdown("### Enter composition percentages:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        composition["Lithium (Li)"] = st.number_input("Lithium (%)", value=2.0, min_value=0.0, max_value=100.0, step=0.1)
        composition["Cobalt (Co)"] = st.number_input("Cobalt (%)", value=15.0, min_value=0.0, max_value=100.0, step=0.1)
    
    with col2:
        composition["Nickel (Ni)"] = st.number_input("Nickel (%)", value=20.0, min_value=0.0, max_value=100.0, step=0.1)
        composition["Manganese (Mn)"] = st.number_input("Manganese (%)", value=10.0, min_value=0.0, max_value=100.0, step=0.1)
    
    with col3:
        composition["Copper (Cu)"] = st.number_input("Copper (%)", value=8.0, min_value=0.0, max_value=100.0, step=0.1)
        composition["Aluminum (Al)"] = st.number_input("Aluminum (%)", value=5.0, min_value=0.0, max_value=100.0, step=0.1)

else:
    battery_type = st.selectbox("Select battery type:", 
                                ["NMC 111", "NMC 622", "NMC 811", "LFP", "NCA"])
    
    # Preset compositions (simplified examples - adjust with real data)
    presets = {
        "NMC 111": {"Lithium (Li)": 2.0, "Cobalt (Co)": 20.0, "Nickel (Ni)": 20.0, "Manganese (Mn)": 20.0, "Copper (Cu)": 8.0, "Aluminum (Al)": 5.0},
        "NMC 622": {"Lithium (Li)": 2.5, "Cobalt (Co)": 12.0, "Nickel (Ni)": 36.0, "Manganese (Mn)": 12.0, "Copper (Cu)": 8.0, "Aluminum (Al)": 5.0},
        "NMC 811": {"Lithium (Li)": 3.0, "Cobalt (Co)": 5.0, "Nickel (Ni)": 48.0, "Manganese (Mn)": 6.0, "Copper (Cu)": 8.0, "Aluminum (Al)": 5.0},
        "LFP": {"Lithium (Li)": 4.0, "Cobalt (Co)": 0.0, "Nickel (Ni)": 0.0, "Manganese (Mn)": 0.0, "Copper (Cu)": 10.0, "Aluminum (Al)": 6.0},
        "NCA": {"Lithium (Li)": 2.8, "Cobalt (Co)": 9.0, "Nickel (Ni)": 48.0, "Manganese (Mn)": 0.0, "Copper (Cu)": 8.0, "Aluminum (Al)": 5.0},
    }
    composition = presets[battery_type]
    
    st.info(f"**{battery_type}** composition loaded")

# Calculations
st.markdown("---")
st.header("💵 Value Calculation")

total_composition = sum(composition.values())
if total_composition > 100:
    st.error(f"⚠️ Total composition is {total_composition:.1f}% - exceeds 100%!")

# Calculate values
results = []
total_gross_value = 0
total_payable_value = 0

for material, percentage in composition.items():
    weight = (percentage / 100) * total_weight
    gross_value = weight * prices[material]
    payable_value = gross_value * (payable_pct / 100)
    
    total_gross_value += gross_value
    total_payable_value += payable_value
    
    results.append({
        "Material": material,
        "Composition (%)": percentage,
        "Weight (kg)": round(weight, 2),
        "Price (USD/kg)": prices[material],
        "Gross Value (USD)": round(gross_value, 2),
        "Payable Value (USD)": round(payable_value, 2)
    })

df = pd.DataFrame(results)

# Display results
col1, col2, col3 = st.columns(3)
col1.metric("Total Gross Value", f"${total_gross_value:,.2f}")
col2.metric("Total Payable Value", f"${total_payable_value:,.2f}")
col3.metric("Value per kg", f"${total_payable_value/total_weight:,.2f}")

st.dataframe(df, use_container_width=True)

# Visualization
st.markdown("---")
st.header("📈 Value Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Payable Value by Material")
    chart_data = df[["Material", "Payable Value (USD)"]].set_index("Material")
    st.bar_chart(chart_data)

with col2:
    st.subheader("Composition by Weight")
    chart_data = df[["Material", "Weight (kg)"]].set_index("Material")
    st.bar_chart(chart_data)

# Export option
st.markdown("---")
if st.button("📥 Export Results as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="battery_value_calculation.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("💡 Tip: Adjust commodity prices in the sidebar to see real-time value changes")
