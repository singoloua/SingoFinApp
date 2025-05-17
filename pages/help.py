import streamlit as st

# ---------- Page Config ----------
st.set_page_config(layout="wide")
st.sidebar.markdown("# ❓ HELP")

# ---------- Custom Styles ----------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Intro ----------
st.markdown("## 🧭 Overview")
st.write("""
This dashboard helps you **analyze**, **monitor**, and **forecast** **Net Foreign Assets (NFA)** 
across countries using **IMF** data. Navigate using the sidebar menu:
- 🏠 **Dashboard**: Global overview of NFA levels.
- 📊 **Analysis**: Risk indicators for selected countries.
- 📄 **Prediction**: Forecast future NFA using various models with explainability.
- ❓ **Help**: You're here!
""")

# ---------- Section Guide ----------
st.markdown("## 📌 Page-by-Page Guide")

with st.expander("🏠 Dashboard"):
    st.markdown("""
- Choose a **year** and **currency unit** (Domestic or USD).
- View:
  - 🌍 **World map** of NFA values by country.
  - 🔝 **Top countries** by NFA.
  - 🔻 **Biggest gain/loss** changes.
  - 📈 **NFA trend line** for selected country.
""")

with st.expander("📊 Analysis"):
    st.markdown("""
- Select a **country** and currency.
- View key financial risk metrics:
  - 🧭 **Volatility-based risk level gauge**
  - 📉 **Year-over-year change chart**
  - 📊 **Value at Risk (VaR), Exposure, and Loss Probability**
""")

with st.expander("📄 Prediction"):
    st.markdown("""
- Choose a **country**, **currency**, and **forecasting model**:
    - 🌳 **Decision Tree**
    - 🌲 **Random Forest**
    - 🚀 **XGBoost**
    - 🧮 **Moving Average**
    - 📈 **Linear Regression**

- Configure:
    - 🔢 **Moving average window size**
    - ⏩ **Years to forecast**
- Results:
    - 📊 **NFA prediction line chart**
    - ⚠️ **Volatility & risk forecast**
    - 🤖 **SHAP Summary Plot** (for model interpretability on tree-based models)
""")

with st.expander("⚙️ Data & Sources"):
    st.markdown("""
- NFA Source: [IMF IFS](https://legacydata.imf.org/regular.aspx?key=63243611)
- FX Rates: [IMF WEO](https://data.imf.org/en/Data-Explorer?datasetUrn=IMF.RES:WEO(6.0.0))
- Time Coverage: **2015–2024**
- USD conversion uses official FX rates
- Missing data is automatically filled using average-based imputation (front and back)
""")

# ---------- Feedback Section ----------
st.markdown("## 💬 Feedback")
st.write("""
We value your feedback to improve this dashboard. Please let us know your thoughts, suggestions, or any issues you encountered.
""")

# Feedback Form
with st.form("feedback_form"):
    name = st.text_input("Your Name (optional)")
    email = st.text_input("Your Email (optional)")
    feedback = st.text_area("Your Feedback", placeholder="Write your feedback here...")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if feedback.strip():
            with open("feedback.txt", "a") as f:
                f.write(f"Name: {name}\nEmail: {email}\nFeedback:\n{feedback}\n{'-'*40}\n")
            st.success("Thank you for your feedback!")
        else:
            st.error("Feedback cannot be empty. Please provide your thoughts.")

# ---------- Footer ----------
st.markdown('<div class="h1"></div>', unsafe_allow_html=True)
st.markdown('[© 2025 Singo Loua](https://www.linkedin.com/in/singo-l-3a2931130/)', unsafe_allow_html=True)
