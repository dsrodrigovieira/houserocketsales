# libraries
import base64
import config
import streamlit            as st
import unicode_emoji        as emoji
from pipeline.extrator      import Extrator
from pipeline.transformador import Transformador
from pipeline.carga         import Carga

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = config.style_background_img % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

if __name__ == '__main__':
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
    df_map = load.criar_dataframe_mapa(tabs[3])
    region, condition, suggestion = load.criar_filtros(df_prd)  

    # sidebar
    with st.sidebar:
        st.logo(config.logo_img)
        st.write(config.page_title)
        st.divider()
        st.subheader(f"Desenvolvido por Rodrigo Vieira {emoji.men_tech_dark}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(
            config.social_linkedin.format(base64.b64encode(open("src/img/icons/linkedin-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )
        c2.markdown(
            config.social_github.format(base64.b64encode(open("src/img/icons/github-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )   
        c3.markdown(
            config.social_medium.format(base64.b64encode(open("src/img/icons/medium-brands-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )     
        c4.markdown(
            config.social_email.format(base64.b64encode(open("src/img/icons/envelope-solid.png", "rb").read()).decode())
            ,unsafe_allow_html=True
        )        
        st.divider()
        st.write("Como você avalia este dashboard?")
        selected = st.feedback("stars")
        if selected is not None:
            st.caption("Obrigado pelo seu feedback :relieved:")
      
    # cabecalho
    st.logo(config.logo_img)
    st.write(config.page_title)
    st.divider()

    # metricas
    st.write("### Métricas")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with st.container(border=True):
        col1.metric(label="Custo total da base", value=cards[1])
        col2.metric(label="Imóveis na base", value=cards[0])
        col3.metric(label="Imóveis sugeridos revenda", value=cards[2])
        col4.metric(label="Investimento total previsto", value=cards[3])
        col5.metric(label="Faturamento total previsto", value=cards[4])
        col6.metric(label="Lucro previsto", value=cards[5], delta=cards[6])
    
    # abas
    tab1, tab2, tab3, tab4 = st.tabs(["Gráficos :bar_chart:", "Pareto :chart_with_upwards_trend:", "Mapas :world_map:", "Relatório :page_with_curl:"])
    # graficos
    with tab1:
        tab1_col1, tab1_col2 = st.columns(2) 
        with tab1_col1:
            st.write("### Imóveis por estado de conservação")
            st.pyplot(load.criar_grafico_imoveis_conservacao(tabs[4]))
        with tab1_col2:
            st.write("### Rentabilidade por estação do ano") 
            st.pyplot(load.criar_grafico_rentabilidade(tabs[0]))
    # pareto
    with tab2:
        st.write("### Análise de Pareto")        
        st.pyplot(plot_pareto) 
    # mapas
    with tab3:
        st.write("### Localização dos imóveis")
        with st.expander("Configurações do mapa"):
            st.write("Filtros")
            mfiltro1, mfiltro2, mfiltro3, mfiltro4 = st.columns(4,vertical_alignment='center')
            with mfiltro1:
                mdesabilitar_filtros = st.checkbox('Desabilitar filtros', key='mapa_des', value=False)
            with mfiltro2:
                mfiltro_regiao = st.multiselect('Região', region, key='mapa_regiao', default=region, disabled=mdesabilitar_filtros)
            with mfiltro3:
                mfiltro_condicao_imovel = st.multiselect('Condição do imóvel', condition, key='mapa_condicao', default=condition, disabled=mdesabilitar_filtros)
            with mfiltro4:
                mfiltro_sugestao_compra = st.multiselect('Sugestão de compra', suggestion, key='mapa_sugestao', default='Sim', disabled=mdesabilitar_filtros)        
        if mdesabilitar_filtros | (len(mfiltro_regiao) == 0 | len(mfiltro_condicao_imovel) == 0 | len(mfiltro_sugestao_compra) == 0):
            map_data = report.copy()
        else:
            map_data = report.loc[report['Região'].astype(int).isin(mfiltro_regiao) & report['Conservação'].isin(mfiltro_condicao_imovel) & report['Sugerida compra'].isin(mfiltro_sugestao_compra)].copy()
        load.criar_mapa(map_data)
    # relatorio
    with tab4:
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