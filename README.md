
# 🌐.: SINGO FINANCIAL RISK APP :.

A Streamlit-based interactive dashboard to **analyze**, **monitor**, and **forecast** Net Foreign Assets (NFA) across countries using IMF data.

> 📊 Built for financial analysts, economists, and researchers monitoring macroeconomic stability and cross-border financial risks.

---

## 📁 Project Structure

```
├── app.py                             # Main Streamlit launcher
├── requirements.txt                   # Python dependencies
├── README.md                          # Project overview
├── app.py                             # Main entry for Streamlit multipage app
├── pages/
│   ├── main_page.py                   # Dashboard page (map, top countries, trends)
│   ├── analysis.py                    # Financial risk analysis (volatility, VaR, etc.)
│   ├── prediction.py                  # Forecasting models + SHAP explainability
│   └── help.py                        # Help and usage guide
│
├── style/
│   └── style.css                      # Dark theme custom styling
│
├── data/   
│   ├── Monetary_Sector_Depository_Corporat.xlsx    # IMF NFA data
│   └── dataset_2025-04-13T00_34_41.138915637Z_DEFAULT_INTEGRATION_IMF.RES_WEO_6.0.0.csv  # IMF FX rates (WEO)
│
├── .venv/                             # Virtual environment for project dependencies.
│   └── ...

```


## 🚀 Features

### 🏠 **Dashboard**
- Interactive **world map** of NFA by country.
- **Top 20 countries** and biggest **gains/losses**.
- Trendlines for individual country performance.
- Toggle between **domestic ** and **USD** currency.

### 📊 **Analysis**
- **Volatility-based risk level** visualization.
- Exposure & **Value at Risk (VaR)**.
- **Loss probability** indicators and trend breakdown.

### 📄 **Prediction**
- Forecast NFA with:
  - Moving Average
  - Linear Regression
  - Decision Tree
  - Random Forest
  - XGBoost
- Model **explainability** with SHAP values (tree models only).
- Adjustable forecast window and configuration.

### ❓ **Help**
- Page-by-page usage instructions.
- Data source documentation.
- Currency conversion explanations.

---

## 📈 Data Sources

- **Net Foreign Assets**: [IMF International Financial Statistics (IFS)](https://legacydata.imf.org/regular.aspx?key=63243611)
- **FX Conversion Rates**: [IMF World Economic Outlook (WEO)](https://data.imf.org/)
- Time Range: **2015–2024**
- Missing values filled via average-based **forward and backward imputation**.

---

## 🛠️ Setup Instructions

### ✅ Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt` (see below)

### 📦 Installation

```bash

# Create a virtual environment (optional)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### ▶️ Run the App

```bash
streamlit run app.py
```

---

## 🧠 Models & Explainability

- Forecasting supports basic statistical and tree-based machine learning models.
- **SHAP plots** are used for transparency and risk interpretability.
- Currency risk is modeled both in **domestic** and **USD** terms.

---


## 👨‍💻 Author

Built by **Singo Loua**  
[LinkedIn](https://www.linkedin.com/in/singo-l-3a2931130)

The WebApp can be found at: https://singofinapp.streamlit.app/ 

---

## ✨ Acknowledgements

- IMF IFS and WEO datasets
- Streamlit, Plotly, Altair, Scikit-learn, XGBoost, SHAP

---
