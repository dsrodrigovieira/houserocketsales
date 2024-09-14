# libraries
import base64
import config
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import folium
from pipeline.extrator import Extrator
from pipeline.transformador import Transformador
from pipeline.carga import Carga
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

    extract = Extrator()
    transform = Transformador()
    load = Carga()

    # extract
    df_raw = extract.obter_dados(caminho_arquivo=config.raw_data, colunas_data=config.raw_date_cols)
    # transform
    df = transform.corrigir_tipos(dataframe=df_raw)
    df = transform.remover_colunas(dataframe=df,colunas_remocao=config.cols_remove)
    df = transform.tratar_outliers(dataframe=df)
    df = transform.criar_novos_atributos(dataframe=df)
    df_aux1 = transform.calcular_mediana_por_regiao(dataframe=df)
    df_aux2 = transform.calcular_mediana_por_estacao_regiao(dataframe=df)
    df_prd = transform.criar_dataframe_final(dataframe=df, df_regional_median=df_aux1, df_season_region_median=df_aux2)
    # load
    cards = load.criar_cards(df_prd)
    tabs = load.criar_tabelas(df_prd)
    report, columns = load.criar_dataframe_relatorio(df_prd)
    plot_pareto = load.criar_grafico_pareto(tabs[2])
    region, condition, suggestion = load.criar_filtros(df_prd)  

    with st.sidebar:
        st.logo(config.logo_img)
        st.subheader("Desenvolvido por Rodrigo Vieira")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(
            """
            <a href="https://www.linkedin.com/in/dsrodrigovieira/">
            <img src="data:image/png;base64,{}" width="20">
            </a>
            """.format(base64.b64encode(open("img/icons/linkedin-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )
        c2.markdown(
            """
            <a href="https://github.com/dsrodrigovieira">
            <img src="data:image/png;base64,{}" width="20">
            </a>
            """.format(base64.b64encode(open("img/icons/github-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )   
        c3.markdown(
            """
            <a href="https://medium.com/@dsrodrigovieira">
            <img src="data:image/png;base64,{}" width="20">
            </a>
            """.format(base64.b64encode(open("img/icons/medium-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )     
        c4.markdown(
            """
            <a href="mailto:dsrodrigoviera@gmail.com?subject=Contato via Projeto Houser Rocket">
            <img src="data:image/png;base64,{}" width="20">
            </a>
            """.format(base64.b64encode(open("img/icons/envelope-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )        
        st.divider()
        st.write("Como você avalia este dashboard?")
        selected = st.feedback("stars")
        if selected is not None:
            st.caption("Obrigado pelo seu feedback :relieved:")
      
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
    tab1, tab2, tab3 = st.tabs(["Gráficos :bar_chart:", "Pareto :chart_with_upwards_trend:", "Mapas :world_map:"])
    with tab1:
        tab1_col1, tab1_col2 = st.columns(2) 
        with tab1_col1:
            st.write("### Imóveis por estado de conservação")
            fig = plt.figure() 
            ax = sns.barplot(tabs[4], x='id', y='condition_type')
            ax.spines[['top','right','bottom']].set_visible(False)
            ax.grid(False)
            plt.ylabel('Estado de Conservação',fontsize=10)
            plt.xlabel('')
            plt.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=False,      # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=False) # labels along the bottom edge are off            
            plt.yticks(fontsize=12)
            for i, val in enumerate(tabs[4]['id']):
                if i == 0:
                    ax.annotate(f"{val:,d}",(val,i),ha="right",fontsize=12,xytext=(val-(val*.02), i),color="white",fontweight="bold")
                else:
                    ax.annotate(f"{val:,d}",(val,i),ha="left",fontsize=12,xytext=(val+(val*.02), i),fontweight="bold")   
            st.pyplot(fig)
        with tab1_col2:
            st.write("### Rentabilidade por estação do ano") 
            fig = plt.figure() 
            ax = sns.barplot(tabs[0], x='profit', y='season')
            ax.spines[['top','right','bottom']].set_visible(False)
            ax.grid(False)
            plt.ylabel('Estação',fontsize=10)
            plt.xlabel('')
            plt.tick_params(
                axis='x',          # changes apply to the x-axis
                which='both',      # both major and minor ticks are affected
                bottom=False,      # ticks along the bottom edge are off
                top=False,         # ticks along the top edge are off
                labelbottom=False) # labels along the bottom edge are off            
            plt.yticks(fontsize=12)
            for i, val in enumerate(tabs[0]['profit']):
                ax.annotate(f"${val*1e-6:1.1f}M",(val,i),ha="right",fontsize=12,xytext=(val-(val*.02), i),color="white", fontweight="bold")
            st.pyplot(fig)
    with tab2:
        st.write("### Análise de Pareto")        
        st.pyplot(plot_pareto) 
    with tab3:
        st.write("### Localização dos imóveis")
        with st.expander("Configurações do mapa"):
            st.write("Filtros")
            mfiltro1, mfiltro2, mfiltro3, mfiltro4 = st.columns(4,vertical_alignment='center')
            with mfiltro1:
                mdesabilitar_filtros = st.checkbox('Desabilitar filtros', key='mapa_des', value=True)
            with mfiltro2:
                mfiltro_regiao = st.multiselect('Região', region, key='mapa_regiao', disabled=mdesabilitar_filtros)
            with mfiltro3:
                mfiltro_condicao_imovel = st.multiselect('Condição do imóvel', condition, key='mapa_condicao', disabled=mdesabilitar_filtros)
            with mfiltro4:
                mfiltro_sugestao_compra = st.multiselect('Sugestão de compra', suggestion, key='mapa_sugestao', disabled=mdesabilitar_filtros)        
        #st.write(load.make_map(mapdata=tabs[3],filter_region=region,filter_clear=disable))

        # map_data = data
        # marker_map = folium.Map(location=[map_data['lat'].mean(),map_data['long'].mean()],
        #                             default_zoom_start=20, width='100%')
        # marker_cluster = MarkerCluster().add_to(marker_map)
        # for name, row in map_data.iterrows():
        #     folium.Marker([row['lat'],row['long']],
        #                     popup='ID: {:} | Cost: US${:.2f} | Sell for US${:.2f} at {:} to earn US${:.2f} for profit'
        #                     .format(row['id'],row['price'],row['sell_price'],row['season'],row['profit'])
        #     ).add_to(marker_cluster)
        # st.subheader('View on map')
        # folium_static(marker_map)

    st.divider()
    st.write("#### Relatório")
    with st.expander("Configurações do relatório"):
        options = st.multiselect("Colunas do relatório", options=columns, default=columns, placeholder="Selecione uma ou mais opções")
        st.write("Filtros")
        filtro1, filtro2, filtro3, filtro4 = st.columns(4,vertical_alignment='center')
        with filtro1:
            desabilitar_filtros = st.checkbox('Desabilitar filtros', key='report_des', value=True)
        with filtro2:
            filtro_regiao = st.multiselect('Região', region, key='report_regiao', disabled=desabilitar_filtros)
        with filtro3:
            filtro_condicao_imovel = st.multiselect('Condição do imóvel', condition, key='report_condicao', disabled=desabilitar_filtros)
        with filtro4:
            filtro_sugestao_compra = st.multiselect('Sugestão de compra', suggestion, key='report_sugestao', disabled=desabilitar_filtros)
    if desabilitar_filtros | (len(filtro_regiao) == 0 | len(filtro_condicao_imovel) == 0 | len(filtro_sugestao_compra) == 0):
        data_report = report.copy()
    else:
        data_report = report.loc[report['Região'].astype(int).isin(filtro_regiao) & report['Conservação'].isin(filtro_condicao_imovel) & report['Sugerida compra'].isin(filtro_sugestao_compra)].copy()
    st.dataframe(data_report[options].reset_index(drop=True))