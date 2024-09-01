import pandas            as pd
import streamlit         as st
import plotly.express    as px
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import logging
import os

#current_file = os.path.basename(__file__) 
#logging.basicConfig(filename='houserocket.log',level=logging.INFO, format='dashboard.py: %(asctime)s - %(levelname)s - %(message)s')

class Dashboard(object):

    def __init__(self) -> None:
        pass

    def make_filters(dataframe=pd.DataFrame) -> tuple:
        """Create filter to use in the dashboard"""   
        if type(dataframe.shape) != tuple:
            logging.error(f"make_filters@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:           
            cols = ['zipcode','condition_type','condition','buy']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"make_filters@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else:   
                f_select_region    = st.sidebar.selectbox('Região', dataframe['zipcode'].sort_values().unique())
                f_select_condition = st.sidebar.selectbox('Condição do imóvel', dataframe['condition_type'].unique())
                f_select_buy       = st.sidebar.selectbox('Sugestão de compra', dataframe['buy'].sort_values().unique())
                f_disable_filters  = st.sidebar.checkbox('Desabilitar filtros')
        return [f_select_region, f_select_condition, f_select_buy, f_disable_filters]
    
    def make_cards(dataframe=pd.DataFrame) -> tuple:
        """Create metrics that will be shown within the cards"""     
        if type(dataframe.shape) != tuple:
            logging.error(f"make_cards@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:              
            cols = ['id','price','buy','sell_price','profit']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"make_cards@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else: 
                # tamanho da base
                metric_1 = dataframe.shape[0]
                # custo total da base
                val_metric_1 = dataframe['price'].sum()
                metric_2 = f"${val_metric_1*1e-9:1.1f}B"
                # total imóveis sugeridos
                metric_3 = dataframe.loc[dataframe['buy']=="Yes",'id'].count()
                # investimento total previsto
                val_metric_4 = dataframe.loc[dataframe['buy']=="Yes",'price'].sum()
                metric_4 = f"${val_metric_4*1e-6:1.1f}M"
                # faturamento total previsto
                val_metric_5 = dataframe.loc[dataframe['buy']=="Yes",'sell_price'].sum()
                metric_5 = f"${val_metric_5*1e-6:1.1f}M"
                # lucro total previsto
                val_metric_6 = dataframe.loc[dataframe['buy']=="Yes",'profit'].sum()
                metric_6 = f"${val_metric_6*1e-6:1.1f}M"
                # lucro total previsto %
                aux = dataframe.loc[dataframe['buy']=="Yes",['price','profit']].sum().reset_index()
                aux.columns=['feature','value']
                val = (aux['value'].pct_change()+1).dropna().values[0]
                metric_7 = f"{val*100:.1f}%"  
        return [metric_1,metric_2,metric_3,metric_4,metric_5,metric_6,metric_7]
    
    def make_tables(dataframe=pd.DataFrame) -> tuple:
        """Create tables"""
        if type(dataframe.shape) != tuple:
            logging.error(f"make_tables@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:           
            cols = ['id','lat','long','zipcode','sqft_lot','condition_type','buy','season','price','sell_price','profit']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"make_tables@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else:         
                # rentabilidade por estação do ano
                tbl_1 = dataframe.loc[dataframe['buy']=="Yes",['season','profit']].groupby('season').sum().reset_index()
                tbl_1 = tbl_1.sort_values('profit',ascending=False)
                # preco do m2 por regiao
                aux = dataframe[['zipcode','sqft_lot','price']].copy()
                aux['price_m2'] = aux['price']/aux['sqft_lot']
                tbl_2 = aux[['zipcode','price_m2']].groupby('zipcode').mean().reset_index()
                # pareto lucro por regiao
                tbl_3 = dataframe[['zipcode','profit']].groupby('zipcode').sum().reset_index().sort_values('profit',ascending=False).reset_index(drop=True)
                tbl_3['acumulado'] = tbl_3['profit'].cumsum()
                tbl_3['total'] = dataframe['profit'].sum()
                tbl_3['perc_acumulado'] = tbl_3['acumulado']/tbl_3['total']
                tbl_3['zipcode'] = tbl_3['zipcode'].astype(str)
                # map data
                tbl_4 = dataframe[['id','lat','long','zipcode','buy','season','price','sell_price','profit']].copy()
                tbl_4.columns=[i.capitalize().replace('_',' ') for i in tbl_4.columns]
                tbl_4['Season'] = tbl_4['Season'].apply(lambda x: x.capitalize())
                tbl_4['Price'] = tbl_4['Price'].apply(lambda x: f"${x*1e-3:1.1f}K")
                tbl_4['Sell price'] = tbl_4['Sell price'].apply(lambda x: f"${x*1e-3:1.1f}K" if x != 0 else f"${x}")
                tbl_4['size'] = tbl_4['Profit'].apply(lambda x: int(dataframe.loc[dataframe['profit']!=0,'profit'].min()*.7) if x == 0 else int(x))
                tbl_4['Profit'] = tbl_4['Profit'].apply(lambda x: f"${x*1e-3:1.1f}K" if x != 0 else f"${x}")   
                # imóveis por estado de conservação
                tbl_5 = dataframe[['condition_type','id']].groupby('condition_type').count().reset_index()
        return [tbl_1,tbl_2,tbl_3,tbl_4,tbl_5]
    
    def make_pareto(dataframe=pd.DataFrame) -> None:
        """Create pareto chart"""
        def millions(x, pos):
            'The two args are the value and tick position'
            return '$ %1.1fM' % (x * 1e-6)   
        if type(dataframe.shape) != tuple:
            logging.error(f"make_pareto@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:     
            cols = ['zipcode','profit','perc_acumulado']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"make_pareto@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else: 
                # estilo bmh
                plt.style.use("bmh")
                fig, ax = plt.subplots()
                # cria um segundo grafico que compartilha o eixo X mas tem o eixo Y independente
                ax2 = ax.twinx()
                # estrutura dos gráficos
                ax.bar(dataframe['zipcode'],dataframe['profit'],color="C0")
                ax2.plot(dataframe['zipcode'],dataframe['perc_acumulado'],color='C4',marker="o")
                # arrumando eixo y coluna
                ax.set_ylabel("Lucro por região", color="C0")
                ax.tick_params(axis="y", labelcolor="C0")
                # arrumando eixo y linha
                ax2.set_ylabel("Percentual", color="C4")
                ax2.tick_params(axis="y", labelcolor="C4")
                # formatar percentual
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(millions))
                ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1))
                # rotacao eixo x
                ax.tick_params(axis="x", rotation=90)
                for i, percentual in enumerate(dataframe['perc_acumulado']):
                    if i < 25:
                        ax2.annotate(f"{percentual:.0%}", (i, percentual), textcoords="offset points", xytext=(0, 20), ha="center", color="C4", fontweight="bold")
                    else:
                        if i%2 == 1:
                            ax2.annotate(f"{percentual:.0%}", (i, percentual), textcoords="offset points", xytext=(10, -20), ha="center", color="C4", fontweight="bold")
                        else:
                            ax2.annotate(f"{percentual:.0%}", (i, percentual), textcoords="offset points", xytext=(0, 10), ha="center", color="C4", fontweight="bold")
                for i, profit in enumerate(dataframe['profit']):
                    if i < 38:
                        ax.annotate(f"${profit*1e-6:1.1f}M", (i, profit), textcoords="offset points", xytext=(0, -40), ha="center", rotation=90, color="white", fontweight="bold")
                    else:
                        ax.annotate(f"${profit*1e-6:1.1f}M", (i, profit), textcoords="offset points", xytext=(0, 10), ha="center", rotation=90, color="C0", fontweight="bold")        
                ax.grid(False)
                ax2.grid(True)
                plt.show()    
        return None
    
    def make_map( mapdata = pd.DataFrame, filter_region = list, filter_clear = bool ) -> None: 
        """Crate scatter map"""  
        if mapdata == None:
            logging.error(f"make_map@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:
            cols = ['Id', 'Lat', 'Long', 'Zipcode', 'Buy', 'Season', 'Price', 'Sell price', 'Profit', 'size']
            if False in [cols[i] in list(mapdata.columns) for i in range(len(cols))]:
                logging.error(f"make_map@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else:
                if filter_clear:
                    mapdata
                else:
                    mapdata = mapdata.loc[mapdata['Zipcode']==filter_region]
                
                _map = px.scatter_mapbox( mapdata,
                                        lat='Lat',
                                        lon='Long',                            
                                        color='Buy',
                                        color_discrete_sequence=['#999999','#0F3D6E'],
                                        zoom=10,
                                        size='size',
                                        hover_data={'Id': True,
                                                    'Lat': False,
                                                    'Long': False,
                                                    'Zipcode': True,
                                                    'Buy': False,
                                                    'Season': True,
                                                    'Price': True,
                                                    'Sell price': True,
                                                    'Profit': True}
                                        )
                _map.update_layout(mapbox_style='carto-positron')
                _map.update_layout(height=600, margin = {'r':0,'t':0,'l':0,'b':0})
                _map.show()        
        return None
    
    def make_report(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Create dataframe for report"""
        if type(dataframe.shape) != tuple:
            logging.error(f"make_report@{os.path.basename(__file__)} - Couldn't find dataframe. Value is empty.")
        else:           
            cols = ['id','zipcode','price','sqft_lot','condition_type','buy','sell_price','season','bathrooms','bedrooms','floors','waterfront','yr_built','yr_renovated']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"make_report@{os.path.basename(__file__)} - Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")    
            else:   
                df = dataframe[cols].copy()
                df['price']    = df['price'].apply(lambda x: f"${x:,.2f}")
                df['sell_price'] = df['sell_price'].apply(lambda x: f"${x:,.2f}")
                df['waterfront'] = df['waterfront'].apply(lambda x: 'Yes' if x == 1 else 'No')
                df['yr_renovated'] = df['yr_renovated'].apply(lambda x: 'N/A' if x == 0 else x)
                df[['id','yr_built','yr_renovated','zipcode']] = df[['id','yr_built','yr_renovated','zipcode']].astype(str)
                df.columns = ['ID','Região','Custo','m² Lote','Conservação','Sugerida compra','Preço sugerido','Estação sugerida','Nº banheiros','Nº quartos','Nº pavimentos','Vista para água','Ano construção','Ano reforma']                
        return df