import pandas as pd
import logging
#import os

#current_file = os.path.basename(__file__) 
#logging.basicConfig(filename='houserocket.log',level=logging.INFO, format=f'{current_file}: %(asctime)s - %(levelname)s - %(message)s')

class Load(object):

    def __init__(self) -> None:
        pass

    def load_data(dataframe=pd.DataFrame,path=str) -> None:
        if dataframe==None or path==None or path=='':
           logging.error("Couldn't find dataframe or path. Value is empty.")
        else:
            try: 
                dataframe.to_csv(path,index=False)
            except ValueError as error:
                logging.error(f"Couldn't load data to CSV file. {error}")    
            finally:               
                logging.info(f"Load file completed.")    
        return None