import pandas as pd
import numpy  as np
import logging
import os
from geopy.geocoders import Nominatim

#current_file = os.path.basename(__file__) 
#logging.basicConfig(filename='houserocket.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Extract (object):

    def __init__(self) -> None:
        pass

    def get_data(file_path=str, date_cols=list) -> pd.DataFrame:
        """Retrieve raw data from CSV file."""
        if file_path == None or date_cols == None or date_cols == []:
            logging.error(f"get_data@{os.path.basename(__file__)} - Couldn't find raw data file path or date column name. Value is empty.")
        else:
            try:
                df = pd.read_csv(filepath_or_buffer=file_path, parse_dates=date_cols)
                df = df.drop_duplicates(subset='id',keep='last')
            except FileNotFoundError as error:
                logging.error(f"get_data@{os.path.basename(__file__)} - Couldn't retrieve raw data. {error}")        
        return df
    
    def get_geolocation(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Retrieve geolocation data from Nominatim API."""  
        # dataframe['street'] = 'NA'
        # dataframe['house_num'] = 'NA'
        # dataframe['city'] = 'NA'
        # dataframe['neighbourhood'] = 'NA'
        # dataframe['state'] = 'NA'
        # for i in range( len( dataframe ) ):
        #     query = str( dataframe.loc[i, 'lat'] ) + ',' + str( dataframe.loc[i, 'long'] )
        #     response = Nominatim( user_agent=f'geoapiExercises{i}' ).reverse( query )
        #     response = pd.json_normalize( response.raw['address'] )
        #     dataframe.iloc[i, 3] = response.apply( lambda x: x['road']          if 'road'          in response.columns else 'NA', axis = 1 )    
        #     dataframe.iloc[i, 4] = response.apply( lambda x: x['house_number']  if 'house_number'  in response.columns else 'NA', axis = 1 )
        #     dataframe.iloc[i, 5] = response.apply( lambda x: x['city']          if 'city'          in response.columns else 'NA', axis = 1 )
        #     dataframe.iloc[i, 6] = response.apply( lambda x: x['neighbourhood'] if 'neighbourhood' in response.columns else
        #                                                      x['county']        if 'county'        in response.columns else 'NA', axis = 1 )
        #     dataframe.iloc[i, 7] = response.apply( lambda x: x['state']         if 'state'         in response.columns else 'NA', axis = 1 )
        # dataframe['address'] = dataframe['street'] + ', ' + dataframe['house_num']
        return None