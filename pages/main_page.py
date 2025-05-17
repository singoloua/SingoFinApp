import streamlit as st

# ---------- Must be first Streamlit command ----------
st.set_page_config(layout="wide")

import plotly.express as px
import pandas as pd
import pycountry
import altair as alt

# To have the three-letter code representing the country
def get_iso_alpha(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

# using suffixes like "T" (trillion), "B" (billion), "M" (million), and "K" (thousand)
def format_number(n):
    if n >= 1e12:
        return f"{n/1e12:.2f}T"
    elif n >= 1e9:
        return f"{n/1e9:.2f}B"
    elif n >= 1e6:
        return f"{n/1e6:.2f}M"
    elif n >= 1e3:
        return f"{n/1e3:.2f}K"
    else:
        return f"{n:.0f}"


# ---------- Custom Styles ----------
# Load and inject CSS from file
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="header">.: SINGO FINANCIAL RISK APP :.</div>', unsafe_allow_html=True)

# ---------- Load Data from Session State ----------
df_nfa = st.session_state.df_nfa # Domestic currency data
df_fx = st.session_state.df_fx  # Exchange rate data
df_usd = st.session_state.df_usd # Converted to USD
year_cols = st.session_state.year_cols # List of years

# ---------- Sidebar Selections ----------
st.sidebar.markdown("# DASHBOARD 🏠")
year_list = year_cols
selected_year = st.sidebar.selectbox("Select year", year_list, index=len(year_list)-1)
unit_option = st.sidebar.radio("Unit", ["Domestic Currency", "USD"])
unit_suffix = "_local" if unit_option == "Domestic Currency" else "_usd"
selected_col = str(selected_year) + unit_suffix

# ---------- Merge and Prepare Main Data ----------
merged_df = pd.merge(df_nfa, df_fx, on="Country", suffixes=("_local", "_fx"))
for year in year_cols:
    usd_col = f"{year}_usd"
    if usd_col not in merged_df.columns:
        merged_df[usd_col] = merged_df[f"{year}_local"] / merged_df[f"{year}_fx"]

merged_df["iso_alpha"] = merged_df["Country"].apply(get_iso_alpha)




# ---------- Layout Columns ----------
col = st.columns((2, 4.5, 2), gap='small')

# ---------- World Map + Trends ----------
with col[1]:
    map_df = merged_df[["Country", "iso_alpha", selected_col]].dropna()
    map_df.rename(columns={selected_col: "Amount"}, inplace=True)

    st.write(f"#### 🌍 World Map - Net Foreign Assets (NFA) by Country ({selected_year}) [{unit_option}]")

    # Plotly choropleth map (World map)
    fig = px.choropleth(
        map_df,
        locations="iso_alpha",
        color="Amount",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ---------- Top Countries ----------
with col[2]:
    st.markdown('#### Top Countries')
    df_top_countries = merged_df[["Country", selected_col]].dropna().sort_values(by=selected_col, ascending=False).reset_index(drop=True)
    df_top_countries.rename(columns={"Country": "country", selected_col: "nfa"}, inplace=True)
    df_top_countries = df_top_countries.head(20)

    st.dataframe(
        df_top_countries,
        column_order=("country", "nfa"),
        hide_index=True,
        column_config={
            "country": st.column_config.TextColumn("Country"),
            "nfa": st.column_config.ProgressColumn(
                f"NFA ({unit_option})",
                format="%f",
                min_value=0,
                max_value=max(df_top_countries["nfa"]),
            )
        }
    )

# ---------- Gains/Losses ----------
with col[0]:
    st.markdown('#### Gains/Losses')
    prev_year = str(int(selected_year) - 1)

    # Check if the previous year exists in the DataFrame
    if prev_year in year_list:
        prev_col = prev_year + unit_suffix
        merged_df["NFA_change"] = merged_df[selected_col] - merged_df[prev_col]
        df_change_sorted = merged_df[["Country", selected_col, "NFA_change"]].dropna().sort_values("NFA_change", ascending=False)
        
        top_country = df_change_sorted.iloc[0]
        st.metric(label=top_country["Country"], value=format_number(top_country[selected_col]), delta=format_number(top_country['NFA_change']))

        bottom_country = df_change_sorted.iloc[-1]
        st.metric(label=bottom_country["Country"], value=format_number(bottom_country[selected_col]), delta=format_number(bottom_country['NFA_change']))
    else:
        st.metric(label="No Data", value="-", delta="-")
        st.metric(label="No Data", value="-", delta="-")

    ## ---------- About Section ----------
    with st.expander("About", expanded=True):
        st.write(f'''
        - :orange[**Data Source**]: [IMF IFS](https://legacydata.imf.org/regular.aspx?key=63243611) & [WEO](https://data.imf.org/en/Data-Explorer?datasetUrn=IMF.RES:WEO(6.0.0)&INDICATOR=PPPEX)
        - :orange[**Top Countries**]: Highest NFA in {selected_year}
        - :orange[**Units**]: {unit_option}
        ''')

# ---------- lign ----------
st.markdown('<div class="h"></div>', unsafe_allow_html=True)

# ---------- Country Trend Part----------
coll = st.columns((1.5, 4.5), gap='medium')

with coll[0]:
    selected_country = st.selectbox("Select a country", sorted(merged_df["Country"].unique()))
    selected_row = merged_df[merged_df["Country"] == selected_country]
    selected_value = selected_row[selected_col].values[0] if not selected_row.empty else "N/A"
    st.write(f"**{selected_country} - {selected_year} Amount ({unit_option}):** {selected_value:,}")

with coll[1]:
    if not selected_row.empty:
        trend_cols = [y + unit_suffix for y in year_cols]
        trend_data = selected_row[trend_cols].T
        trend_data.columns = [selected_country]
        trend_data.index = year_cols
        trend_data.index.name = "Year"
        trend_data = trend_data.reset_index()

        st.write(f"### 📈 NFA Trend for {selected_country} ({unit_option})")
        trend_fig = px.line(trend_data, x="Year", y=selected_country, markers=True,
                            title=f"{selected_country} - NFA Trend ({unit_option})",
                            labels={selected_country: "Net Foreign Assets", "Year": "Year"})
        trend_fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(trend_fig, use_container_width=True)

# ---------- Footer ----------
st.markdown('<div class="h1"></div>', unsafe_allow_html=True)
st.markdown('[© 2025 Singo Loua](https://www.linkedin.com/in/singo-l-3a2931130/)', unsafe_allow_html=True)