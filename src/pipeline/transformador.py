import pandas as pd
import numpy  as np

class Transformador(object):
    """Classe responsável pela transformação dos dados."""

    def __init__(self):
        """Inicializa a classe."""
        pass

    def corrigir_tipos(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Corrige os tipos de dados do DataFrame.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            O DataFrame original com tipos de dados corrigidos (banheiros e andares como inteiros).

        Raises:
            ValueError: Se o DataFrame for vazio ou não possuir as colunas esperadas ('banheiros', 'andares').
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ['bathrooms','floors']
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        try:
            dataframe['bathrooms'] = dataframe['bathrooms'].astype('int64')
            dataframe['floors']    = dataframe['floors'].astype('int64')
            return dataframe
        except ValueError as error:
            raise error
    
    def remover_colunas(self, dataframe: pd.DataFrame, colunas_remocao: list[str]) -> pd.DataFrame:
        """Remove colunas desnecessárias do DataFrame.

        Args:
            dataframe: DataFrame contendo os dados.
            colunas_remocao: Lista de colunas a serem removidas.

        Returns:
            O DataFrame original sem as colunas especificadas.

        Raises:
            ValueError: Se o DataFrame for vazio, a lista de colunas para remoção estiver vazia ou conter colunas inexistentes.
        """

        if not isinstance(dataframe, pd.DataFrame) or not colunas_remocao or not all(coluna in dataframe.columns for coluna in colunas_remocao):
            raise ValueError("Erro ao remover colunas: verifique o dataframe e a lista de colunas.")

        try:
            return dataframe.drop(columns=colunas_remocao)
        except ValueError as error:
            raise error

    def tratar_outliers(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Trata outliers (valores discrepantes) no DataFrame.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            O DataFrame original com outliers corrigidos (quartos com valor 33 trocados para 3).

        Raises:
            ValueError: Se o DataFrame for vazio ou não possuir a coluna esperada ('bedrooms').
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        coluna_esperada = "bedrooms"
        if coluna_esperada not in dataframe.columns:
            raise ValueError(f"A coluna '{coluna_esperada}' não foi encontrada no DataFrame.")

        try:
            dataframe.loc[dataframe[coluna_esperada] == 33, coluna_esperada] = 3
            return dataframe
        except ValueError as error:
            raise error 

    def criar_novos_atributos(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Cria novas colunas derivadas a partir de colunas existentes.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            O DataFrame original com novas colunas ('month', 'month_name', 'season', 'condition_type').

        Raises:
            ValueError: Se o DataFrame for vazio ou não possuir as colunas esperadas ('date','condition').
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ['date','condition']
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        try:
            dataframe['month'] = dataframe['date'].dt.month
            dataframe['month_name'] = dataframe['date'].dt.month_name()
            dataframe['season'] = dataframe['month'].apply(lambda x: 'Inverno' if x in(12,1,2) else
                                                                     'Primavera' if x in(3,4,5)  else
                                                                     'Verão' if x in(6,7,8)  else 'Outono' )
            dataframe['condition_type'] = dataframe['condition'].apply(lambda x: 'Bom' if x==5 else 'Regular' if x in(3,4) else 'Ruim')
            return dataframe
        except ValueError as error:
            raise error

    def calcular_mediana_por_regiao(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calcula a mediana do preço por região.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            Um novo DataFrame contendo a mediana do preço por região (colunas 'zipcode' e 'regional_median').

        Raises:
            ValueError: Se o DataFrame for vazio ou não possuir as colunas esperadas ('zipcode', 'price').
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["zipcode", "price"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        try:
            regional_median = dataframe[colunas_esperadas].groupby('zipcode').median().reset_index().copy()
            regional_median.columns = ['zipcode', 'regional_median']
            return regional_median
        except ValueError as error:
            raise error

    def calcular_mediana_por_estacao_regiao(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calcula a mediana do preço por estação por região.

        Args:
            dataframe: DataFrame contendo os dados.

        Returns:
            Um novo DataFrame contendo a mediana do preço por estação por região (colunas 'zipcode', 'season', 'season_region_median').

        Raises:
            ValueError: Se o DataFrame for vazio ou não possuir as colunas esperadas ('price', 'zipcode', 'season').
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("O dataframe não é válido.")

        colunas_esperadas = ["price", "zipcode", "season"]
        if not all(coluna in dataframe.columns for coluna in colunas_esperadas):
            raise ValueError(f"As colunas '{', '.join(colunas_esperadas)}' não foram encontradas no DataFrame.")

        try:
            season_region_median = dataframe[colunas_esperadas].groupby(['zipcode', 'season']).median('price')
            season_region_median = season_region_median.rename(columns={'price': 'season_region_median'}).reset_index(drop=False)
            return season_region_median
        except ValueError as error:
            raise error
       
    def criar_dataframe_final(self, dataframe: pd.DataFrame, df_regional_median: pd.DataFrame, df_season_region_median: pd.DataFrame) -> pd.DataFrame:
        """Cria o DataFrame final para análise de compra e venda.

        Args:
            dataframe: DataFrame principal contendo os dados dos imóveis.
            df_regional_median: DataFrame contendo a mediana do preço por região.
            df_season_region_median: DataFrame contendo a mediana do preço por estação por região.

        Returns:
            Um novo DataFrame contendo informações para compra e venda (colunas 'buy', 'sell_price', 'diff_price', 'profit').

        Raises:
            ValueError: Se algum DataFrame for vazio ou possuir colunas inesperadas.
        """

        if not isinstance(dataframe, pd.DataFrame) or not isinstance(df_regional_median, pd.DataFrame) or not isinstance(df_season_region_median, pd.DataFrame):
            raise ValueError("Um ou mais DataFrames inválidos.")

        colunas_esperadas_regional = ["zipcode", "regional_median"]
        colunas_esperadas_seasonal = ["zipcode", "season", "season_region_median"]
        if dataframe.shape[1] != 23 or not all(coluna in df_regional_median.columns for coluna in colunas_esperadas_regional) or not all(coluna in df_season_region_median.columns for coluna in colunas_esperadas_seasonal):
            raise ValueError("DataFrames com colunas inesperadas.")

        try:
            # Merge dataframes e criar colunas de recomendação
            dataframe = pd.merge(dataframe.copy(), df_regional_median, how='left', on='zipcode')
            dataframe['buy'] = dataframe.apply(lambda x: 'Sim' if (x['price'] < x['regional_median']) & (x['condition_type'] == 'Bom') else 'Não', axis=1)
            dataframe = pd.merge(dataframe.copy(), df_season_region_median, how='left', on=['zipcode', 'season'])
            dataframe['sell_price'] = dataframe.apply(lambda x: x['price'] * 1.3 if (x['price'] < x['season_region_median']) & (x['buy'] == 'Sim') else (x['price'] * 1.1 if (x['price'] >= x['season_region_median']) & (x['buy'] == 'Sim') else 0), axis=1)
            dataframe['diff_price'] = dataframe.apply(lambda x: np.sqrt((x['sell_price'] - x['season_region_median']) ** 2) if x['sell_price'] != 0 else 0, axis=1)
            dataframe['profit'] = dataframe.apply(lambda x: x['sell_price'] - x['price'] if x['buy'] == 'Sim' else 0, axis=1)
            return dataframe
        except ValueError as error:
            raise error