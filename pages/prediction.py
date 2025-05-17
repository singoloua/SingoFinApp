import streamlit as st
import pandas as pd
import numpy as np
import pycountry
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import warnings

# ---------- Setup ----------
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")
shap.initjs()

# ---------- Custom CSS ----------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="header">.: NFA FORECAST & RISK :.</div>', unsafe_allow_html=True)

# ---------- Load Data ----------
if "df_nfa" not in st.session_state:
    st.warning("Data not loaded. Please return to the Home page to initialize.")
    st.stop()

df_nfa = st.session_state.df_nfa
df_fx = st.session_state.df_fx
df_usd = st.session_state.df_usd
year_cols = st.session_state.year_cols

# ---------- Sidebar ----------
st.sidebar.markdown("# PREDICTIONS 🔮")
country_list = sorted(df_usd['Country'].unique())
selected_country = st.sidebar.selectbox("Select Country", country_list)
unit_option = st.sidebar.radio("Currency", ["Domestic Currency", "USD"])
unit_suffix = "_local" if unit_option == "Domestic Currency" else "_usd"
prediction_method = st.sidebar.selectbox("Prediction Model", [
    "Decision Tree", "Random Forest", "XGBoost", "Linear Regression", "Moving Average"
])
window_size = st.sidebar.slider("Moving Average Window size", 2, 10, 5)
forecast_years = st.sidebar.slider("Years to Forecast", 1, 5, 3)

# ---------- Prepare Data ----------
df_data = df_usd if unit_suffix == "_local" else df_usd
selected_cols = [str(y) for y in year_cols]
country_data = df_data[df_data["Country"] == selected_country]
values = country_data[selected_cols].values.flatten()
years = np.array([int(y) for y in selected_cols])
valid_mask = ~np.isnan(values)
X = years[valid_mask].reshape(-1, 1)
y = values[valid_mask]

# ---------- Forecasting ----------
forecast = []
future_years = []
model = None

if prediction_method == "Moving Average":
    if len(y) >= window_size:
        y_series = list(y)
        for _ in range(forecast_years):
            ma = np.mean(y_series[-window_size:])
            y_series.append(ma)
            forecast.append(ma)
        future_years = np.arange(X.max() + 1, X.max() + 1 + forecast_years)
        all_years = list(X.flatten()) + list(future_years)
        all_values = list(y) + forecast
    else:
        st.warning(f"Not enough data for Moving Average (need at least {window_size} valid years).")
        all_years, all_values = list(X.flatten()), list(y)
else:
    if len(y) > 1:
        if prediction_method == "Linear Regression":
            model = LinearRegression()
        elif prediction_method == "Decision Tree":
            model = DecisionTreeRegressor()
        elif prediction_method == "Random Forest":
            model = RandomForestRegressor()
        elif prediction_method == "XGBoost":
            model = xgb.XGBRegressor()

        model.fit(X, y)
        future_years = np.arange(X.max() + 1, X.max() + 1 + forecast_years)
        forecast = model.predict(future_years.reshape(-1, 1))
        all_years = list(X.flatten()) + list(future_years)
        all_values = list(y) + list(forecast)
    else:
        st.warning("Not enough data to train the model.")
        all_years, all_values = list(X.flatten()), list(y)

# ---------- SHAP Summary Plot ----------
if prediction_method in ["Decision Tree", "Random Forest", "XGBoost"] and model is not None:
    st.markdown("### 🤖 SHAP Explanation (XAI)")

    try:
        # Create SHAP explainer and compute SHAP values
        explainer = shap.Explainer(model, X)
        shap_values = explainer(X)

        # Assign a meaningful name to the feature
        feature_names = ["Year"]   
        shap_values.feature_names = feature_names

        # SHAP Summary Plot
        st.write("#### SHAP Summary Plot (Feature Importance)")
        fig, ax = plt.subplots()
        shap.plots.beeswarm(shap_values, show=False)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error generating SHAP explanation: {e}")

# ---------- Volatility & Risk ----------
volatility = np.std(y) / np.mean(y) if len(y) > 1 and np.mean(y) != 0 else np.nan
future_vol = np.std(all_values) / np.mean(all_values) if len(all_values) > 1 and np.mean(all_values) != 0 else np.nan
threshold = 0.03
prob_high_risk = np.mean(np.random.normal(future_vol, 0.01, 1000) > threshold) if not np.isnan(future_vol) else np.nan

# ---------- Layout ----------
col1, col2 = st.columns((2, 1), gap='small')

with col1:
    st.markdown(f"### 🔮 Forecasted NFA ({prediction_method})")
    df_pred = pd.DataFrame({"Year": all_years, "NFA": all_values})
    fig = px.line(df_pred, x="Year", y="NFA", markers=True,
                  title=f"Forecasted NFA - {selected_country} ({prediction_method})")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📉 Volatility Forecast")
    st.metric("Current Volatility", f"{volatility*100:.2f}%" if not np.isnan(volatility) else "N/A")
    st.metric("Future Volatility", f"{future_vol*100:.2f}%" if not np.isnan(future_vol) else "N/A")
    st.metric("Probability High Risk", f"{prob_high_risk*100:.1f}%" if not np.isnan(prob_high_risk) else "N/A")


# ---------- About ----------
with st.expander("ℹ️ About this Forecast", expanded=False):
    st.write(f"""
    - **Forecasting Method**: {prediction_method}  
    - **Forecast Horizon**: {forecast_years} years  
    - {"Uses a simple rolling average of past values." if prediction_method == "Moving Average" else "Uses a supervised regression model to predict future values and explain them using SHAP."}
    """)

# ---------- Footer ----------
st.markdown('<div class="h1"></div>', unsafe_allow_html=True)
st.markdown('[© 2025 Singo Loua](https://www.linkedin.com/in/singo-l-3a2931130/)', unsafe_allow_html=True)
