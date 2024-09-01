# libraries
import base64
import config
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import folium
from pipeline.extract import Extract
from pipeline.transform import Transform
#from pipeline.load import Load
from pipeline.dashboard import Dashboard
from streamlit_extras.stylable_container import stylable_container


from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim

import logging
logging.basicConfig(filename='houserocket.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# functions
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# application
if __name__ == '__main__':
    # parameters
    st.set_page_config(layout='wide', page_title=config.page_name, initial_sidebar_state="expanded")
    set_background(config.background_img)    

    e = Extract
    t = Transform
    d = Dashboard

    # extract
    df = e.get_data(file_path=config.raw_data, date_cols=config.raw_date_cols)
    # transform
    df = t.fix_tipes(dataframe=df)
    df = t.drop_columns(dataframe=df,cols_drop=config.cols_remove)
    df = t.fix_outlier(dataframe=df)
    df = t.feature_engineering(dataframe=df)
    df_aux1 = t.make_regional_median(dataframe=df)
    df_aux2 = t.make_season_region_median(dataframe=df)
    df_prd = t.make_df_prd(dataframe=df, df_regional_median=df_aux1, df_season_region_median=df_aux2)
    # load
    cards = d.make_cards(df_prd)
    tabs = d.make_tables(df_prd)
    report = d.make_report(df_prd)

    with st.sidebar:
        st.logo(config.logo_img)
        st.write("# Filtros")
        filters = d.make_filters(df_prd)
        
    # header
    st.logo(config.logo_img)
    st.write(config.page_title)
    st.divider()
    st.write("### Métricas")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with st.container(border=True):
        col1.metric(label="Custo total da base", value=cards[1])
        col2.metric(label="Imóveis na base", value=cards[0])
        col3.metric(label="Imóveis sugeridos revenda", value=cards[2])
        col4.metric(label="Investimento total previsto", value=cards[3])
        col5.metric(label="Faturamento total previsto", value=cards[4])
        col6.metric(label="Lucro previsto", value=cards[5], delta=cards[6])
    st.divider()
    tab1, tab2, = st.tabs(["Gráficos", "Pareto e Mapas"])
    with tab1:
        tab1_col1, tab1_col2 = st.columns(2) 
        with tab1_col1:
            st.header("Imóveis por estado de conservação")
            st.bar_chart(data=tabs[4],x='condition_type',y='id',x_label='Qtd.',y_label='Condição',horizontal=True)
        with tab1_col2:
            st.header("Rentabilidade por estação do ano")       
            st.bar_chart(data=tabs[0],x='season',y='profit',x_label='Qtd.',y_label='Estação',horizontal=True)
    with tab2:
        tab2_col1, tab2_col2 = st.columns(2) 
        with tab2_col1:
            st.header("Pareto")
            st.write(d.make_pareto(df_prd.loc[df_prd['buy']=="Yes"]))
        with tab2_col2:
            st.header("Mapa")       
    st.divider()
    st.write("#### Relatório")
    st.dataframe(report.sample(20))
