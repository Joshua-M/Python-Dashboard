import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import base64

warnings.filterwarnings('ignore')

# Function to set background image
def set_background(png_file):
    if png_file is not None:
        encoded_image = base64.b64encode(png_file.getvalue()).decode("utf-8")
        page_bg_img = f'''
            <style>
                body {{
                    background-image: url("data:image/png;base64,{encoded_image}");
                    background-size: cover;
                }}
            </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the page config
st.set_page_config(page_title="Dashboard", page_icon='bar_chart', layout='wide')

# Upload Background Image
bg_image = st.file_uploader("Upload Background Image (PNG)", type=["png"])
if bg_image is not None:
    set_background(bg_image)

st.title(" :bar_chart: MIH - Exploratory Data Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# File Uploader for Data
df = None
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    df = pd.read_excel(fl, engine='openpyxl') if "xlsx" in fl.name else pd.read_excel(fl, engine='xlrd') if "xls" in fl.name else pd.read_csv(fl)
    st.write(f"Loaded file: {fl.name}")
else:
    sample_file = "Sample - Superstore.xls"
    if os.path.exists(sample_file):
        df = pd.read_excel(sample_file, engine='xlrd')  # Specify engine for .xls files
        st.write("Loaded default dataset.")
    else:
        st.error("No file uploaded and default dataset is missing. Please upload a file.")

if df is not None:
    col1, col2 = st.columns((2))
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    
    # Getting the min and max date
    startDate, endDate = df["Order Date"].min(), df["Order Date"].max()
    
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

    # Sidebar Filters
    st.sidebar.header("Choose your filter:")
    region = st.sidebar.multiselect("Select your Region", df["Region"].dropna().unique())
    state = st.sidebar.multiselect("Select your State", df["State"].dropna().unique())
    city = st.sidebar.multiselect("Select your City", df["City"].dropna().unique())
    
    # Apply Filters
    filtered_df = df.copy()
    if region:
        filtered_df = filtered_df[filtered_df["Region"].isin(region)]
    if state:
        filtered_df = filtered_df[filtered_df["State"].isin(state)]
    if city:
        filtered_df = filtered_df[filtered_df["City"].isin(city)]
    
    # Category Sales Bar Chart
    category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
    with col1:
        st.subheader("Category Sales")
        fig = px.bar(category_df, x="Category", y="Sales", text=category_df["Sales"].map("${:,.2f}".format), template="seaborn")
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional Sales Pie Chart
    with col2:
        st.subheader("Regional Sales")
        fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
        fig.update_traces(text=filtered_df["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    
    # Time Series Analysis
    st.subheader("Time Series Analysis")
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    linechart = filtered_df.groupby(filtered_df["month_year"].astype(str))["Sales"].sum().reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Download Processed Data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Processed Data", data=csv, file_name="Processed_Data.csv", mime="text/csv")
