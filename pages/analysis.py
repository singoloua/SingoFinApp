import streamlit as st

# ---------- Must be first Streamlit command ----------
st.set_page_config(layout="wide")

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pycountry
import numpy as np


# ---------- Custom Styles ----------
# Load and inject CSS from file
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



# ---------- Session State Check ----------
if not all(k in st.session_state for k in ("df_nfa", "df_fx", "df_usd", "year_cols")):
    st.error("⚠️ Data not loaded. Please return to the Home page to initialize.")
    st.stop()

# ---------- Load Data from Session State ----------
df_nfa = st.session_state.df_nfa # Domestic currency data
df_fx = st.session_state.df_fx  # Exchange rate data
df_usd = st.session_state.df_usd # Converted to USD
year_cols = st.session_state.year_cols # List of years

# ---------- Sidebar ----------
st.sidebar.markdown("# ANALYSIS 📊")
country_list = sorted(df_usd['Country'].unique())
selected_country = st.sidebar.selectbox("Select Country", country_list)
unit_option = st.sidebar.radio("Display in", ["Domestic Currency", "USD"])
unit_suffix = "_local" if unit_option == "Domestic Currency" else "_usd"
year_list = [str(y) for y in year_cols]

# ---------- Choose correct dataset ----------
if unit_option == "USD":
    base_df = df_usd
    data_cols = year_list
else: # for Domestic Currency
    base_df = df_nfa
    data_cols = year_list

# ---------- Extract Values ----------
country_data = base_df[base_df['Country'] == selected_country]
year_values = country_data[data_cols].values.flatten()

# ---------- Risk Metrics ----------
if len(year_values) > 1:
    clean_vals = year_values[~np.isnan(year_values)]
    var_95 = np.percentile(clean_vals, 5)  # the value 5 is used to calculate the 5th percentile of the #clean_vals# array
    exposure = clean_vals[-1] if len(clean_vals) > 0 else 0 
    volatility = np.std(clean_vals) / np.mean(clean_vals) if np.mean(clean_vals) != 0 else 0 # To avoid  the division by zero
else:
    var_95 = exposure = volatility = np.nan

# ---------- Loss Probability ----------
if len(year_values) > 2:
    pct_change = pd.Series(year_values).pct_change().dropna() * 100
    loss_count = (pct_change < 0).sum()
    total_count = pct_change.count()
    loss_probability = (loss_count / total_count) * 100
else:
    loss_probability = np.nan

# ---------- Layout ----------
st.markdown('<div style="background-color:#0A0A23; color:white; text-align:center; font-size:30px; font-weight:bold; padding:15px; border-radius:10px; margin-bottom:20px;">.: FINANCIAL RISK ANALYSIS :.</div>', unsafe_allow_html=True)
col = st.columns((1.5, 3), gap='medium')

with col[0]:
    st.markdown("### 🧭 Risk Level Indicator")

    def get_risk_level(val):
        if val < 0.02: return "Low", "green"
        elif val < 0.05: return "Moderate", "orange"
        else: return "High", "red"

    if not np.isnan(volatility):
        level, color = get_risk_level(volatility)
        gauge_max = max(0.1, round(volatility * 1.5, 2)) * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=volatility * 100,
            number={'suffix': "%", 'valueformat': '.2f'},
            delta={'reference': 5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            title={'text': f"<b>{level.upper()} RISK</b><br><span style='font-size:14px'>{selected_country}</span>"},
            gauge={
                'axis': {'range': [0, gauge_max]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 2], 'color': "lightgreen"},
                    {'range': [2, 5], 'color': "orange"},
                    {'range': [5, gauge_max], 'color': "red"}
                ],
                'threshold': {'line': {'color': "black", 'width': 4}, 'value': volatility * 100}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to calculate risk.")

with col[1]:
    st.markdown("#### Risk Distribution")
    if len(year_values) > 2:
        pct_years = year_list[1:]
        fig = px.line(
            x=pct_years,
            y=pct_change,
            markers=True,
            labels={"x": "Year", "y": "YoY % Change"},
            title=f"Risk Distribution: YoY % Change in NFA - {selected_country}"
        )
        fig.update_traces(line=dict(color='orange', width=3))
        fig.update_layout(yaxis_title="Return (%)", xaxis_title="Year")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to calculate year-over-year change.")


# ---------- lign ----------
st.markdown('<div class="h"></div>', unsafe_allow_html=True)


row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Value at Risk (VaR)", f"{var_95:,.2f}")
    with col2:
        st.metric("Exposure", f"{exposure:,.2f}")
    with col3:
        st.metric("Volatility", f"{volatility * 100:.2f}%")

with row2_col2:
    st.markdown("### Loss Probability")
    if not np.isnan(loss_probability):
        st.metric("", f"{loss_probability:.1f}%")
    else:
        st.info("Not enough data to calculate loss probability.")


# ---------- FX Rate Over Time ----------
if unit_option == "USD":
    # ---------- lign ----------
    st.markdown('<div class="h"></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 40px"></div>', unsafe_allow_html=True)
    st.markdown("### 💱 FX Rate Over Time (USD)")

    # Use df_fx from session state (exchange rate table)
    df_fx = st.session_state.df_fx

    # Get FX data for the selected country
    fx_row = df_fx[df_fx["Country"] == selected_country]

    if not fx_row.empty:
        fx_data = fx_row[year_list].T
        fx_data.columns = ["FX Rate"]
        fx_data.index.name = "Year"
        fx_data = fx_data.reset_index()

        fx_fig = px.line(
            fx_data,
            x="Year",
            y="FX Rate",
            markers=True,
            title=f"{selected_country} Exchange Rate to USD Over Time",
            labels={"FX Rate": "Rate (Domestic per USD)", "Year": "Year"}
        )
        fx_fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )
        st.plotly_chart(fx_fig, use_container_width=True)
    else:
        st.info("FX data not available for this country.")



# ---------- lign ----------
st.markdown('<div class="h"></div>', unsafe_allow_html=True)

# ---------- Show DataFrames and Download Buttons ----------
st.markdown('<div style="margin-top: 50px"></div>', unsafe_allow_html=True)
st.markdown("## 📂 View & Download Data")



# The users can download the datasets used in the project for their own analysis.

# Buttons to expand and download each dataset used in the project
with st.expander("📘 View Net Foreign Assets data per country"):
    st.dataframe(df_nfa, use_container_width=True)
    csv = df_nfa.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download as CSV", csv, "df_nfa.csv", "text/csv")

with st.expander("💱 View FX Rates per country over years "):
    st.dataframe(df_fx, use_container_width=True)
    csv = df_fx.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download as CSV", csv, "df_fx.csv", "text/csv")

with st.expander("💰 View USD-Converted NFA of countries "):
    st.dataframe(df_usd, use_container_width=True)
    csv = df_usd.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download as CSV", csv, "df_usd.csv", "text/csv")

# ---------- Footer ----------
st.markdown('<div class="h1"></div>', unsafe_allow_html=True)
st.markdown('[© 2025 Singo Loua](https://www.linkedin.com/in/singo-l-3a2931130/)', unsafe_allow_html=True)
