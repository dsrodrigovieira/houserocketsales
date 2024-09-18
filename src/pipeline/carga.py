import folium
import pandas            as pd
import seaborn           as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from streamlit_folium    import folium_static
from folium.plugins      import MarkerCluster

class Carga(object):
    """Classe responsável pela carga dos dados para o dashboard."""

    def __init__(self) -> None:
        """Inicializa a classe."""
        pass

    def criar_filtros(self, dataframe: pd.DataFrame) -> tuple:
        """Cria filtros para serem utilizados no dashboard.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            Uma tupla contendo os dados para os filtros (região, condição do imóvel, sugestão de compra).
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["zipcode", "condition_type", "condition", "buy"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        # Criar dados para os elementos de filtro na barra lateral do Streamlit
        filtro_regiao = dataframe['zipcode'].sort_values().unique()
        filtro_condicao_imovel = dataframe['condition_type'].unique()
        filtro_sugestao_compra = dataframe['buy'].sort_values().unique()

        return filtro_regiao, filtro_condicao_imovel, filtro_sugestao_compra

    def criar_cards(self, dataframe: pd.DataFrame) -> tuple:
        """Cria métricas para serem exibidas nos cards do dashboard.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            Uma tupla contendo as métricas calculadas (tamanho da base, custo total, imóveis sugeridos para compra, investimento previsto, faturamento previsto, lucro previsto e lucro percentual previsto).
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["id", "price", "buy", "sell_price", "profit"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        # Calcular métricas
        metric_1 = dataframe.shape[0]  # Tamanho da base

        val_metric_2 = dataframe['price'].sum()  # Custo total da base
        metric_2 = f"${val_metric_2 * 1e-9:1.1f}B"  # Custo total formatado

        metric_3 = dataframe[dataframe['buy'] == "Sim"]['id'].count()  # Total imóveis sugeridos para compra

        val_metric_4 = dataframe[dataframe['buy'] == "Sim"]['price'].sum()  # Investimento total previsto
        metric_4 = f"${val_metric_4 * 1e-6:1.1f}M"  # Investimento total formatado

        val_metric_5 = dataframe[dataframe['buy'] == "Sim"]['sell_price'].sum()  # Faturamento total previsto
        metric_5 = f"${val_metric_5 * 1e-6:1.1f}M"  # Faturamento total formatado

        val_metric_6 = dataframe[dataframe['buy'] == "Sim"]['profit'].sum()  # Lucro total previsto
        metric_6 = f"${val_metric_6 * 1e-6:1.1f}M"  # Lucro total formatado

        # Lucro total previsto %
        aux = dataframe[dataframe['buy'] == "Sim"][['price', 'profit']].sum().reset_index()
        aux.columns = ['feature', 'value']
        val = (aux['value'].pct_change() + 1).dropna().values[0]
        metric_7 = f"{val * 100:.1f}%"

        return metric_1, metric_2, metric_3, metric_4, metric_5, metric_6, metric_7
   
    def criar_tabelas(self, dataframe: pd.DataFrame) -> tuple:
        """Cria tabelas para serem exibidas no dashboard.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            Uma tupla contendo as tabelas criadas (rentabilidade por estação, preço por m² por região, Pareto de lucro por região, dados do mapa, imóveis por estado de conservação).
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["id", "lat", "long", "zipcode", "sqft_lot", "condition_type", "buy", "season", "price", "sell_price", "profit"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        # Rentabilidade por estação do ano
        tbl_1 = (
            dataframe[dataframe['buy'] == "Sim"]
            .groupby('season')['profit']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        # Preço do m² por região
        aux = dataframe[['zipcode', 'sqft_lot', 'price']].copy()
        aux['price_m2'] = aux['price'] / aux['sqft_lot']
        tbl_2 = aux.groupby('zipcode')['price_m2'].mean().reset_index()

        # Pareto de lucro por região
        tbl_3 = (
            dataframe[dataframe['buy'] == "Sim"]
            .groupby('zipcode')['profit']
            .sum()
            .reset_index()
            .sort_values('profit', ascending=False)
            .reset_index(drop=True)
        )
        tbl_3['acumulado'] = tbl_3['profit'].cumsum()
        tbl_3['total'] = tbl_3['profit'].sum()
        tbl_3['perc_acumulado'] = tbl_3['acumulado'] / tbl_3['total']
        tbl_3['zipcode'] = tbl_3['zipcode'].astype(str)

        # Dados para o mapa
        tbl_4 = dataframe[['id', 'lat', 'long', 'zipcode', 'buy', 'season', 'price', 'sell_price', 'profit']].copy()
        tbl_4.columns = [col.capitalize().replace('_', ' ') for col in tbl_4.columns]
        tbl_4['Season'] = tbl_4['Season'].apply(lambda x: x.capitalize())
        tbl_4['Price'] = tbl_4['Price'].apply(lambda x: f"${x * 1e-3:1.1f}K")
        tbl_4['Sell price'] = tbl_4['Sell price'].apply(lambda x: f"${x * 1e-3:1.1f}K" if x != 0 else "N/A")
        min_profit_size = dataframe.loc[dataframe['profit'] != 0, 'profit'].min() * .7 # Tamanho mínimo para as bolhas no mapa
        tbl_4['size'] = tbl_4['Profit'].apply(lambda x: int(min_profit_size) if x == 0 else int(x))
        tbl_4['Profit'] = tbl_4['Profit'].apply(lambda x: f"${x * 1e-3:1.1f}K" if x >= 0 else "N/A")
        tbl_4[['Id','Zipcode']] = tbl_4[['Id','Zipcode']].astype(str)

        # Imóveis por estado de conservação
        tbl_5 = dataframe[['condition_type', 'id']].groupby('condition_type').count().sort_values('id', ascending=False).reset_index()

        return tbl_1, tbl_2, tbl_3, tbl_4, tbl_5
    
    def criar_grafico_pareto(self, dataframe: pd.DataFrame, estilo='bmh', cores=['C0', 'C4']) -> plt.Figure:
        """Cria um gráfico de Pareto para mostrar a distribuição do lucro por região.

        Args:
            dataframe: DataFrame contendo os dados.
            estilo: Estilo do gráfico (e.g., 'bmh', 'ggplot', 'seaborn').
            cores: Lista com as cores para as barras e linha.

        Returns:
            Um objeto do tipo plt.Figure contendo o gráfico de Pareto.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["zipcode", "profit", "perc_acumulado"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        def formatar_valor(valor, formato):
            """Formata um valor de acordo com o formato especificado."""
            if formato == 'milhoes':
                return f"${valor * 1e-6:,.1f}M"
            elif formato == 'porcentagem':
                return f"{valor:.0%}"
            else:
                return str(valor)

        def adicionar_anotacoes(ax, dados, formato, rotation=0):
            """Adiciona anotações a um gráfico."""
            for i, valor in enumerate(dados):
                if formato == 'porcentagem':
                    ax.annotate(
                        formatar_valor(valor, formato),
                        (i, valor),
                        textcoords="offset points",
                        xytext= (0, 20) if i < 25 else ((10, -20) if i % 2 == 1 else (0, 10)),
                        ha="center",
                        rotation=rotation,
                        color=cores[1] if formato == 'porcentagem' else cores[0],
                        fontweight="bold",
                    )
                else:
                    ax.annotate(
                        formatar_valor(valor, formato),
                        (i, valor),
                        textcoords="offset points",
                        xytext= (0, -40) if i < 38 else (0, 10),
                        ha="center",
                        rotation=rotation,
                        color=cores[1] if formato == 'porcentagem' else cores[0],
                        fontweight="bold",
                    )


        # Criar o gráfico
        plt.style.use(estilo)
        fig, ax = plt.subplots(figsize=(20, 8))
        ax2 = ax.twinx()

        # Barras para lucro por região
        ax.bar(dataframe['zipcode'], dataframe['profit'], color=cores[0])

        # Linha para percentual acumulado
        ax2.plot(dataframe['zipcode'], dataframe['perc_acumulado'], color=cores[1], marker="o")

        # Formatação dos eixos Y
        ax.set_ylabel("Lucro por região", color=cores[0])
        ax.tick_params(axis="y", labelcolor=cores[0])
        ax2.set_ylabel("Percentual", color=cores[1])
        ax2.tick_params(axis="y", labelcolor=cores[1])

        # Formatação de porcentagem e valores
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: formatar_valor(x, 'milhoes')))
        ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: formatar_valor(x, 'porcentagem')))

        # Rotação do eixo X
        ax.tick_params(axis="x", rotation=90)

        # Adicionar anotações
        adicionar_anotacoes(ax2, dataframe['perc_acumulado'], 'porcentagem')
        adicionar_anotacoes(ax, dataframe['profit'], 'milhoes', rotation=90)

        # Ocultar linhas de grade no eixo principal e exibi-las no secundário
        ax.grid(False)
        ax2.grid(True)  

        return fig
    
    def criar_dataframe_mapa(self, dataframe = pd.DataFrame ) -> pd.DataFrame: 
        """Cria um DataFrame formatado para o mapa.

        Args:
            dataframe: DataFrame original.

        Returns:
            Um DataFrame formatado para o mapa.
        """        
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ['Id', 'Lat', 'Long', 'Zipcode', 'Buy', 'Season', 'Price', 'Sell price', 'Profit', 'size']
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")
        
        colunas_renomeadas = ['Id', 'Lat', 'Long', 'Região', 'Sugerida compra', 'Estação', 'Preço de custo', 'Preço de venda', 'Lucro esperado', 'size']
        dataframe.columns = colunas_renomeadas

        return dataframe
    
    def criar_dataframe_relatorio(self, dataframe: pd.DataFrame) -> tuple:
        """Cria um DataFrame formatado para relatórios.

        Args:
            dataframe: DataFrame original.

        Returns:
            Um DataFrame formatado para relatórios.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ['id', 'zipcode', 'price', 'sqft_lot', 'condition_type', 'buy', 'sell_price', 'profit', 'season',
                             'bathrooms', 'bedrooms', 'floors', 'waterfront', 'yr_built', 'yr_renovated', 'lat', 'long']
        # Verificar se as colunas esperadas estão presentes
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas necessárias não foram encontradas: {', '.join(colunas_esperadas)}")

        def formatar_valor_monetario(valor):
            """Formata um valor monetário para exibição."""
            return f"${valor:,.2f}"

        def renomear_colunas(df):
            """Renomeia as colunas do DataFrame para português."""
            mapeamento_colunas = {
                'id': 'ID',
                'zipcode': 'Região',
                'price': 'Custo',
                'sqft_lot': 'm² Lote',
                'condition_type': 'Conservação',
                'buy': 'Sugerida compra',
                'sell_price': 'Preço de venda',
                'profit': 'Lucro esperado',
                'season': 'Estação sugerida',
                'bathrooms': 'Nº banheiros',
                'bedrooms': 'Nº quartos',
                'floors': 'Nº pavimentos',
                'waterfront': 'Vista para água',
                'yr_built': 'Ano construção',
                'yr_renovated': 'Ano reforma'
            }
            df.rename(columns=mapeamento_colunas, inplace=True)

        df = dataframe[colunas_esperadas].copy()

        # Formatar valores e converter tipos
        df['price'] = df['price'].apply(formatar_valor_monetario)
        df['sell_price'] = df['sell_price'].apply(formatar_valor_monetario)
        df['waterfront'] = df['waterfront'].apply(lambda x: 'Sim' if x == 1 else 'Não')
        df['yr_renovated'] = df['yr_renovated'].apply(lambda x: 'N/A' if x == 0 else str(x))
        min_profit_size = df.loc[df['profit'] != 0, 'profit'].min() * .7 # Tamanho mínimo para as bolhas no mapa
        df['size'] = df['profit'].apply(lambda x: int(min_profit_size) if x == 0 else int(x))
        df['profit'] = df['profit'].apply(formatar_valor_monetario)
        df[['id', 'yr_built', 'yr_renovated', 'zipcode']] = df[['id', 'yr_built', 'yr_renovated', 'zipcode']].astype(str)

        # Renomear colunas
        renomear_colunas(df)

        # Remover colunas lat, long e size
        aux_colunas = df.columns.to_list()
        [ aux_colunas.remove(j) if aux_colunas[i] in ['lat','long','size'] else aux_colunas[i] for i,j in enumerate(aux_colunas) ]

        return df, aux_colunas
    
    def criar_grafico_imoveis_conservacao(self, data:pd.DataFrame) -> plt.Figure:
        """Cria um gráfico de barras horizontais para visualizar a distribuição de imóveis por estado de conservação.

        Args:
            data: DataFrame com os dados.   

        Returns:
            Um objeto matplotlib.figure.Figure.
        """  
        # Verificar se as colunas necessárias estão presentes
        colunas_necessarias = ['id', 'condition_type']
        if not all(coluna in data.columns for coluna in colunas_necessarias):
            raise ValueError(f"As colunas necessárias não foram encontradas: {', '.join(colunas_necessarias)}")  
              
        fig = plt.figure() 
        ax = sns.barplot(data, x='id', y='condition_type')
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
        for i, val in enumerate(data['id']):
            if i == 0:
                ax.annotate(f"{val:,d}",(val,i),ha="right",fontsize=12,xytext=(val-(val*.02), i),color="white",fontweight="bold")
            else:
                ax.annotate(f"{val:,d}",(val,i),ha="left",fontsize=12,xytext=(val+(val*.02), i),fontweight="bold") 
        return fig

    def criar_grafico_rentabilidade(self, data: pd.DataFrame) -> plt.Figure:
        """Cria um gráfico de barras horizontais para visualizar a distribuição da rentabilidade dos imóveis por estação do ano.

        Args:
            data: DataFrame com os dados.   

        Returns:
            Um objeto matplotlib.figure.Figure.
        """  
        # Verificar se as colunas necessárias estão presentes
        colunas_necessarias = ['profit', 'season']
        if not all(coluna in data.columns for coluna in colunas_necessarias):
            raise ValueError(f"As colunas necessárias não foram encontradas: {', '.join(colunas_necessarias)}")  
                
        fig = plt.figure() 
        ax = sns.barplot(data, x='profit', y='season')
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
        for i, val in enumerate(data['profit']):
            ax.annotate(f"${val*1e-6:1.1f}M",(val,i),ha="right",fontsize=12,xytext=(val-(val*.02), i),color="white", fontweight="bold")
        return fig    
    
    def criar_mapa(self, map_data: pd.DataFrame) -> None:
        """Cria um mapa de pontos interativo.

        Args:
            map_data: DataFrame com os dados do mapa.
        """

        def criar_popup(row, colunas_popup):
            """Cria o conteúdo do popup para um marcador.

            Args:
                row: Uma linha do DataFrame.
                colunas_popup: Lista com as colunas a serem incluídas no popup.

            Returns:
                Um objeto folium.Popup.
            """

            html = """
                <ul style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; list-style-type: none; font-size: small;">
                """
            for coluna in colunas_popup:
                html += f"<li><b>{coluna}:</b> {row[coluna]}</li>"
            html += "</ul>"
            iframe = folium.IFrame(html=html, width=300, height=180)
            return folium.Popup(iframe)

        colunas_popup = ['ID', 'Região', 'm² Lote', 'Conservação','Custo',
                         'Sugerida compra', 'Preço de venda', 'Estação sugerida','Lucro esperado']
        # Verificar se as colunas necessárias estão presentes
        colunas_necessarias = ['lat', 'long'] + colunas_popup
        if not all(coluna in map_data.columns for coluna in colunas_necessarias):
            raise ValueError(f"As colunas necessárias não foram encontradas: {', '.join(colunas_necessarias)}")
        # Calcular o centro do mapa        
        zoom_lat_long = [map_data['lat'].mean(),map_data['long'].mean()]
        # Criar o mapa
        marker_map = folium.Map( location=zoom_lat_long,
                                 default_zoom_start=50,
                                 width='100%' )
        marker_cluster = MarkerCluster().add_to(marker_map)
        # Adicionar marcadores
        for index, row in map_data.iterrows():
            popup = criar_popup(row, colunas_popup) 
            folium.Marker( [row['lat'],row['long']], popup=popup, 
                           tooltip=f"ID: {row['ID']} | Sugerida compra: {row['Sugerida compra']}" ).add_to(marker_cluster)
        folium_static(marker_map) 
        return None