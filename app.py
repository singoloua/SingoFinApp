import streamlit as st
import pandas as pd
import numpy as np 
import os

# ------------ To fill the missing values in the data ------------
def fill_with_directional_average(row):
    row_filled = row.copy()
    for i in range(len(row)):
        if pd.isna(row[i]):
            # If it's the first few cells, take average of next available values
            if row[:i].dropna().empty and not row[i+1:].dropna().empty:
                row_filled[i] = row[i+1:].dropna().mean()
            # If it's later or middle, take average of previous available values
            elif not row[:i].dropna().empty:
                row_filled[i] = row[:i].dropna().mean()
            # If no data anywhere, keep as NaN
    return row_filled


# ---------------- To Load and Prepare NFA + FX + USD Data ----------------

def load_nfa_fx_usd_data():
    # --- Load NFA Excel file (Net Foreign Assets by Country)
    nfa_path = "./data/Monetary_Sector_Depository_Corporat.xlsx"
    if not os.path.exists(nfa_path):
        st.error("NFA file not found!")
        return None, None, None

    excel_file = pd.ExcelFile(nfa_path)
    df_raw = excel_file.parse('Annual', skiprows=6)
    df = df_raw.iloc[:, [1] + list(range(4, 14))].copy()
    df.columns = ['Country'] + [str(c)[:4] for c in df.columns[1:]]
    df = df[df['Country'].notna()].reset_index(drop=True)

    for year in df.columns[1:]:
        df[year] = pd.to_numeric(df[year], errors='coerce')

    # Fill NFA missing values
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(fill_with_directional_average, axis=1)

    # --- Load FX CSV (exchange rates)
    fx_path = "./data/dataset_2025-04-13T00_34_41.138915637Z_DEFAULT_INTEGRATION_IMF.RES_WEO_6.0.0.csv"
    if not os.path.exists(fx_path):
        st.error("FX data file not found!")
        return None, None, None

    fx_raw = pd.read_csv(fx_path)
    year_cols = [col for col in fx_raw.columns if str(col).isdigit() and len(str(col)) == 4]
    fx_cleaned = fx_raw[['COUNTRY'] + year_cols].copy()
    fx_cleaned.columns = ['Country'] + year_cols
    fx_cleaned = fx_cleaned.sort_values(by='Country').reset_index(drop=True)

    # Fill FX missing values
    fx_cleaned.iloc[:, 1:] = fx_cleaned.iloc[:, 1:].apply(fill_with_directional_average, axis=1)

    # ---  Manually compute USD values
    df_usd = pd.DataFrame()
    df_usd['Country'] = df['Country']

    for year in df.columns[1:]:
        usd_values = []
        for i, country in enumerate(df['Country']):
            nfa_value = df.at[i, year]
            fx_row = fx_cleaned[fx_cleaned['Country'] == country]

            if not fx_row.empty and year in fx_row.columns:
                fx_value = fx_row[year].values[0]
                usd = nfa_value / fx_value if pd.notna(nfa_value) and pd.notna(fx_value) and fx_value != 0 else None
            else:
                usd = None

            usd_values.append(usd)

        df_usd[year] = usd_values

    # Fill USD missing values
    df_usd.iloc[:, 1:] = df_usd.iloc[:, 1:].apply(fill_with_directional_average, axis=1)

    # Drop rows where all values are still missing
    df_usd_cleaned = df_usd.dropna(subset=df_usd.columns[1:], how='all').reset_index(drop=True)

    return df, fx_cleaned, df_usd_cleaned


# ---------------- To Initialize Session State ----------------
# To ensure data is loaded only once and available across pages
def initialize_data():
    if 'df_nfa' not in st.session_state:
        df_nfa, df_fx, df_usd_cleaned = load_nfa_fx_usd_data()
        if df_nfa is None:
            return
        st.session_state.df_nfa = df_nfa
        st.session_state.df_fx = df_fx
        st.session_state.df_usd = df_usd_cleaned
        st.session_state.year_cols = df_nfa.columns[1:]

initialize_data()

# ---------------- Navigation ----------------
main_page = st.Page("pages/main_page.py", title="DASHBOARD", icon="🏠") #To Do, Doing, Done
analysis = st.Page("pages/analysis.py", title="ANALYSIS", icon="📊") #To Do, Doing, Done
prediction = st.Page("pages/prediction.py", title="PREDICTION", icon="📄") #To Do, Doing, Done
setting = st.Page("pages/help.py", title="HELP", icon="❓") #To Do, Doing, Done

# Set page layout to wide
pg = st.navigation([main_page, analysis, prediction, setting])
pg.run()