import pandas as pd
import numpy as np
import logging

logging.basicConfig(filename='transform.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transform(object):

    def __init__(self) -> None:
        pass

    def fix_tipes(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Fix data types"""
        if dataframe == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols = ['bathrooms','floors']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")   
            else:
                try:            
                    # fix float > int
                    dataframe['bathrooms'] = dataframe['bathrooms'].astype('int64')
                    dataframe['floors']    = dataframe['floors'].astype('int64')
                except ValueError as error:
                    logging.error(f"Couldn't fix data types. {error}")        
        return dataframe
    
    def drop_columns(dataframe=pd.DataFrame,cols_drop=list) -> pd.DataFrame:
        """Drop columns that won't be used"""
        if dataframe == None or cols_drop == None or cols_drop == []:
            logging.error("Couldn't find dataframe or columns to drop. Value is empty.")
        else:
            if False in [cols_drop[i] in list(dataframe.columns) for i in range(len(cols_drop))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(dataframe.columns)}")   
            else:            
                try:  
                    # remove unnecessary columns
                    dataframe = dataframe.drop(columns=cols_drop) 
                except ValueError as error: 
                    logging.error(f"Couldn't drop columns. {error}")        
        return dataframe

    def fix_outlier(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Fix outliers"""
        if dataframe == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols = ['bedrooms']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")   
            else:            
                try:  
                    # fix outlier
                    dataframe.loc[dataframe.bedrooms == 33,'bedrooms'] = 3
                except ValueError as error: 
                    logging.error(f"Couldn't replace outlier value. {error}")          
        return dataframe
    
    def feature_engineering(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Create new attributes"""
        if dataframe == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols = ['date','condition']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")   
            else:             
                try:          
                    #new attributes
                    dataframe['month'] = dataframe['date'].dt.month
                    dataframe['month_name'] = dataframe['date'].dt.month_name()
                    dataframe['season'] = dataframe['month'].apply(lambda x: 'Winter' if x in(12,1,2) else
                                                                            'Spring' if x in(3,4,5)  else
                                                                            'Summer' if x in(6,7,8)  else 'Fall' )
                    dataframe['condition_type'] = dataframe['condition'].apply(lambda x: 'Good' if x==5 else 'Regular' if x in(3,4) else 'Bad')
                except ValueError as error: 
                    logging.error(f"Couldn't create new attributes. {error}")           
        return dataframe
    
    def make_regional_median(dataframe=pd.DataFrame) -> pd.DataFrame:
        """Calculate price's median per region"""
        if dataframe == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols = ['zipcode','price']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")   
            else:             
                try:           
                    # set median per region
                    regional_median = dataframe[['zipcode','price']].groupby('zipcode').median().reset_index().copy()
                    regional_median.columns = ['zipcode','regional_median']
                except ValueError as error: 
                    logging.error(f"Couldn't calculate median per region. {error}")                    
        return regional_median
    
    def make_season_median(dataframe) -> pd.DataFrame:
        """Calculate price's median per season per region"""
        if dataframe == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols = ['price','zipcode','season']
            if False in [cols[i] in list(dataframe.columns) for i in range(len(cols))]:
                logging.error(f"Couldn't find columns within the dataframe. Expected: {', '.join(cols)}")   
            else:             
                try:           
                    # set median per season per region
                    season_region_median = dataframe[['price','zipcode','season']].groupby(['zipcode','season']).median('price')
                    season_region_median = season_region_median.rename(columns={'price': 'season_region_median'}).reset_index(drop=False)
                except ValueError as error: 
                    logging.error(f"Couldn't calculate median per season per region. {error}")                 
        return season_region_median
    
    def make_df_prd(dataframe=pd.DataFrame, df_regional_median=pd.DataFrame, df_season_region_median=pd.DataFrame) -> pd.DataFrame:
        """Find houses to buy and suggest sell price"""
        if dataframe == None or df_regional_median == None or df_season_region_median == None:
            logging.error("Couldn't find dataframe. Value is empty.")
        else:
            cols1 = ['zipcode', 'regional_median']
            cols2 = ['zipcode', 'season', 'season_median']
            if dataframe.shape[1] != 24 or False in [cols1[i] in list(df_regional_median.columns) for i in range(len(cols1))] or False in [cols2[i] in list(df_season_region_median.columns) for i in range(len(cols2))]:
                logging.error(f"Couldn't find columns within the dataframe.")   
            else:             
                try:  
                    # merging median to main dataframe and creting sell price
                    dataframe = pd.merge(dataframe,df_regional_median,how='left',on='zipcode').copy()
                    dataframe['buy'] = dataframe.apply(lambda x: 'Yes' if (x['price'] < x['regional_median']) & (x['condition_type']=='good') else 'No',axis=1 )
                    dataframe = pd.merge(dataframe,df_season_region_median,how='inner',on=['zipcode'])
                    dataframe['sell_price'] = dataframe.apply(lambda x: x['price'] * 1.3 if x['price'] <  x['season_median'] and x['buy']=='Yes' else
                                                                        x['price'] * 1.1 if x['price'] >= x['season_median'] and x['buy']=='Yes'
                                                                        else 0, axis=1)
                    dataframe['diff_price'] = dataframe.apply(lambda x: np.sqrt((x['sell_price']-x['season_median'])**2) if x['sell_price']!=0 else 0,axis=1)
                    dataframe['profit'] = dataframe['sell_price'] - dataframe['price']
                except ValueError as error: 
                    logging.error(f"Couldn't create final dataframe. {error}")  
        return dataframe