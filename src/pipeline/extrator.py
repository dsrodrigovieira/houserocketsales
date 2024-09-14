import pandas as pd
import logging
from geopy.geocoders import Nominatim

class Extrator(object):
    """Classe responsável pela extração de dados."""

    def __init__(self):
        """Inicializa a classe."""
        self.geolocator = Nominatim(user_agent="geoapiExercises")  # Define o user-agent padrão

    def obter_dados(self, caminho_arquivo: str, colunas_data: list[str]) -> pd.DataFrame:
        """Recupera dados brutos de um arquivo CSV.

        Args:
            caminho_arquivo: Caminho para o arquivo CSV.
            colunas_data: Lista de colunas que representam datas.

        Returns:
            Um DataFrame contendo os dados brutos.

        Raises:
            ValueError: Se o caminho do arquivo ou a lista de colunas de data estiver vazia.
            FileNotFoundError: Se o arquivo CSV não for encontrado.
        """
        if not caminho_arquivo or not colunas_data:
            raise ValueError(
                "Caminho do arquivo ou lista de colunas de data vazia."
            )
        try:
            df = pd.read_csv(caminho_arquivo, parse_dates=colunas_data)
            df = df.drop_duplicates(subset="id", keep="last")  # Remove duplicatas mantendo a última
            return df
        except FileNotFoundError as error:
            logging.error(f"Erro ao recuperar dados brutos: {error}")            
        raise
        
    def obter_geolocalizacao(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Recupera dados de geolocalização usando a API Nominatim.

        Args:
            dataframe: DataFrame contendo os dados com colunas de latitude e longitude.

        Returns:
            O DataFrame original com novas colunas para dados de geolocalização (rua, número, cidade, bairro, estado).

        Raises:
            KeyError: Se alguma coluna esperada de latitude ou longitude não existir no DataFrame.
        """
        try:
            # Valida a existência das colunas de latitude e longitude
            if "lat" not in dataframe.columns or "long" not in dataframe.columns:
                raise KeyError("Colunas 'lat' ou 'long' não encontradas no DataFrame.")
            
            dataframe['road'] = None
            dataframe['house_number'] = None
            dataframe['city'] = None
            dataframe['neighbourhood'] = None
            dataframe['state'] = None
            dataframe['address'] = None

            for i in range(len(dataframe)):
                # Constrói a consulta usando formatação de string f
                consulta = f"{dataframe.loc[i, 'lat']},{dataframe.loc[i, 'long']}"
                resposta = self.geolocator.reverse(consulta)

                if resposta:  # Verifica se a resposta não é vazia
                    resposta = pd.json_normalize(resposta.raw["address"])
                    dataframe.iloc[i, 3] = resposta.get("road"         , ["NA"])[0]  # Atribuição com valor padrão
                    dataframe.iloc[i, 4] = resposta.get("house_number" , ["NA"])[0]
                    dataframe.iloc[i, 5] = resposta.get("city"         , ["NA"])[0]
                    dataframe.iloc[i, 6] = resposta.get("neighbourhood", resposta.get("county", ["NA"]))[0]
                    dataframe.iloc[i, 7] = resposta.get("state"        , ["NA"])[0]

                    if dataframe.iloc[i, 3] != "NA":
                        dataframe.iloc[i, 8] = dataframe.iloc[i, 3] + ", " + dataframe.iloc[i, 4]
                    dataframe.fillna("NA")
            return dataframe
        except KeyError as error:
            logging.error(f"Erro ao obter geolocalização: {error}")
            raise