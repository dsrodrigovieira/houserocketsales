# libraries
import base64
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim

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

@st.cache(allow_output_mutation=True)
def get_data( path ):
    raw_data = pd.read_csv( path )

    return raw_data

def data_transformation( raw_data ):    
    data = raw_data.copy()
    data['date'] = pd.to_datetime(data['date'],format='%Y-%m-%d')
    data['bathrooms'] = data['bathrooms'].astype('int64')
    data['floors'] = data['floors'].astype('int64')
    data = data.drop(columns=['sqft_living15','sqft_lot15'])
    data.loc[data['bedrooms']==33,'bedrooms'] = 3
    data = data.drop_duplicates(subset='id', keep='last')    

    return data

def set_features( data ):
    data['sn_compra'] = 'NA'
    data['condition_type'] = 'NA'
    data['sell_price'] = 0.0
    data['profit'] = 0.0
    data['month'] = data['date'].dt.strftime('%m').astype('int64')
    data['season'] = data['month'].apply(lambda x: 'Winter' if x in(12,1,2) else
                                                'Spring' if x in(3,4,5) else
                                                'Summer' if x in(6,7,8) else 'Fall' )
    data['sn_compra'] = data['sn_compra'].astype('string')
    data['condition_type'] = data['condition_type'].astype('string')
    data['season'] = data['season'].astype('string')
    
    return data 

def set_filters( data ):  
    st.sidebar.title('Options :gear:')  
    f_zipcode = st.sidebar.selectbox('Select region', data['zipcode'].sort_values().unique())
    f_filters = st.sidebar.checkbox('Disable filters')

    return f_zipcode, f_filters

def get_geolocation ( data ):
    #geolocation = data.loc[data['sn_compra'] == 'y'][['id', 'lat', 'long']].copy().reset_index( drop=True )
    #geolocator = Nominatim( user_agent='geoapiExercises' )
    #geolocation['street'] = 'NA'
    #geolocation['house_num'] = 'NA'
    #geolocation['city'] = 'NA'
    #geolocation['neighbourhood'] = 'NA'
    #geolocation['state'] = 'NA'
    #for i in range( len( geolocation ) ):
    #    query = str( geolocation.loc[i, 'lat'] ) + ',' + str( geolocation.loc[i, 'long'] )
    #    response = geolocator.reverse( query, timeout=10000 )
    #    response = pd.json_normalize( response.raw['address'] )
    #    geolocation.iloc[i, 3] = response.apply( lambda x: x['road'] if 'road' in response.columns else 'NA', axis = 1 )    
    #    geolocation.iloc[i, 4] = response.apply( lambda x: x['house_number'] if 'house_number' in response.columns else 'NA', axis = 1 )
    #    geolocation.iloc[i, 5] = response.apply( lambda x: x['city'] if 'city' in response.columns else 'NA', axis = 1 )
    #    geolocation.iloc[i, 6] = response.apply( lambda x: x['neighbourhood'] if 'neighbourhood' in response.columns else
    #                                                       x['county'] if 'county' in response.columns else 'NA', axis = 1 )
    #    geolocation.iloc[i, 7] = response.apply( lambda x: x['state'] if 'state' in response.columns else 'NA', axis = 1 )
    #geolocation['address'] = geolocation['street'] + ', ' + geolocation['house_num']
    
    geolocation = pd.read_csv('data/geoloc.csv')

    return geolocation

def get_regional_median ( data ):
    regional_median = data[['zipcode','price']].groupby('zipcode').median().reset_index().copy()
    regional_median.columns = ['zipcode','regional_median']

    return regional_median

def get_season_median ( data ):
    season_median = data[['price','zipcode','season']].groupby(['zipcode','season']).median('price')
    season_median = season_median.rename(columns={'price': 'season_median'}).reset_index(drop=False)

    return season_median

def purchase_list ( data, median ):
    purchase = pd.merge( data, median, how='left', on='zipcode' )
    purchase['condition_type'] = purchase['condition'].apply( lambda x: 'good' if x==5 else
                                                                        'regular' if x in(3,4) else 'bad')
    purchase['sn_compra'] = purchase.apply( lambda x: 'y' if ( x['price'] < x['regional_median'] ) &
                                                             ( x['condition_type'] == 'good') else 'n',
                                                                axis=1 )
    purchase = purchase.drop( columns=['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'waterfront',
                                      'view', 'condition', 'grade', 'sqft_above', 'sqft_basement', 'yr_built',
                                      'yr_renovated', 'month'] )    
    return purchase

def plot_purchase( data, region, filter ):

    if filter:
        with st.empty():
            st.info('Uncheck "Disable filters" option to see this content')
    
    else:
        #Plot
        plot_data = data.loc[data['zipcode'] == region,['id','price','zipcode','regional_median','condition_type','sn_compra']].copy().reset_index(drop=True)
        plot_data = plot_data.reset_index(drop=False)
        plot_data_y = plot_data.loc[plot_data['sn_compra']=='y',:].copy()
        plot_data_n = plot_data.loc[plot_data['sn_compra']=='n',:].copy()
        
        # Add traces
        plot_y = go.Scatter(x=plot_data_y['index'], y=plot_data_y['price'],
                                marker_color = 'darkblue',
                                mode = 'markers',
                                text = 'ID: ' + plot_data_y['id'].astype('string') +
                                        ' | Region: ' + plot_data_y['zipcode'].astype('string') +
                                        ' | Condition: ' + plot_data_y['condition_type'] +
                                        ' | Price: US$' + plot_data_y['price'].astype('string'),
                                name = 'Buy'
                                )

        plot_n = go.Scatter(x=plot_data_n['index'], y=plot_data_n['price'],
                                marker_color = 'grey',
                                opacity=0.2,
                                mode = 'markers',
                                text = 'ID: ' + plot_data_n['id'].astype('string') +
                                        ' | Region: ' + plot_data_n['zipcode'].astype('string') +
                                        ' | Condition: ' + plot_data_n['condition_type'] +
                                        ' | Price: US$' + plot_data_n['price'].astype('string'),
                                name = 'Skip'
                                )

        plot_median = go.Scatter(y = plot_data['regional_median'],
                                mode = 'lines',
                                text = 'Region: ' + plot_data['zipcode'].astype('string') +
                                        ' | Median: US$' + plot_data['regional_median'].astype('string'),
                                name = 'Regional Median'
                                )
        plot = [plot_y, plot_n, plot_median]
        layout = go.Layout(
                legend=dict(orientation="h"),
                template='seaborn'
                )
                        
        fig = go.Figure(data=plot,layout=layout)

        fig.update_layout(
            title="Region {:}".format(region),
            title_x=0.5,
            xaxis_title="Houses",
            yaxis_title="Aquisition cost",
            font=dict( color="#000000" )
        )   

        st.subheader('Recommended houses for purchase')
        st.plotly_chart(fig, use_container_width=True)

    return None

def report_sales( data, geodata, season_median, region, filter ):

    #Report
    sell = pd.merge(data,season_median,how='inner',on=['zipcode'])
    sell = sell.loc[sell['sn_compra'] == 'y']
    sell['sell_price'] = sell.apply(lambda x: x['price'] * 1.3 if x['price'] < x['season_median'] else x['price'] * 1.1, axis=1)
    sell['diff_price'] = sell.apply(lambda x: np.sqrt((x['sell_price']-x['season_median'])**2),axis=1)

    aux = sell[['id','diff_price']].groupby('id').min().reset_index(drop=False)
    aux['sn_vende'] = 'y'

    sell = pd.merge(sell,aux,how='left',on=['id','diff_price']).drop_duplicates(subset=['id','diff_price'])
    sell = sell.loc[sell['sn_vende']=='y']

    sell['profit'] = sell['sell_price'] - sell['price']

    sell = sell.drop(columns=['date','sn_compra','condition_type','regional_median','season_median','season_x','diff_price','sn_vende'])
    sell = pd.merge(sell,geodata[['id','address','neighbourhood','city']],how='left',on='id').rename(columns={'season_y':'season'})

    insights = sell.copy()

    st.subheader('Details and price suggestion')
    if filter:
        st.dataframe(sell[['id', 'zipcode', 'address', 'price', 'sell_price', 'season', 'profit']].rename(columns={'id': 'ID', 'zipcode': 'Region', 'address': 'Address', 'price': 'Cost',
        'sell_price': 'Price suggestion', 'season': 'Best season to sell', 'profit': 'Profit'}).sort_values(['Region','ID']).reset_index(drop=True), height=420) 
        
    else:
        sell = sell.loc[sell['zipcode'] == region]
        st.dataframe(sell[['id', 'zipcode', 'address', 'price', 'sell_price', 'season', 'profit']].rename(columns={'id': 'ID', 'zipcode': 'Region', 'address': 'Address', 'price': 'Cost',
        'sell_price': 'Price suggestion', 'season': 'Best season to sell', 'profit': 'Profit'}).sort_values(['Region','ID']).reset_index(drop=True), height=420) 

    return sell, insights

def show_map( data ):
    
    map_data = data

    marker_map = folium.Map(location=[map_data['lat'].mean(),map_data['long'].mean()],
                                default_zoom_start=20, width='100%')
    marker_cluster = MarkerCluster().add_to(marker_map)
    for name, row in map_data.iterrows():
        folium.Marker([row['lat'],row['long']],
                        popup='ID: {:} | Cost: US${:.2f} | Sell for US${:.2f} at {:} to earn US${:.2f} for profit'
                        .format(row['id'],row['price'],row['sell_price'],row['season'],row['profit'])
        ).add_to(marker_cluster)

    st.subheader('View on map')
    folium_static(marker_map)
    
    return None

def show_insights( data ):
    # top3 regions with more available houses to sell
    i1 = data[['id','zipcode']].groupby('zipcode').count().sort_values('id',ascending=False).head(1).reset_index()

    # top3 most valuable regions
    i2 = data[['profit','zipcode']].groupby('zipcode').sum().sort_values('profit',ascending=False).head(1).reset_index()
    i2['profit'] = (i2.at[0,'profit'] / 1000000)

    # most valuable regions per season
    a = data[['profit','zipcode','season']].groupby(['season','zipcode']).sum().sort_values(['season','profit'],ascending=False).reset_index()
    b = data[['profit','zipcode','season']].groupby(['season','zipcode']).sum().groupby('season').max().reset_index()
    i3 = pd.merge(a,b,how='right', on=['season','profit']).rename(columns={'season':'Season','zipcode':'Zipcode','profit':'Profit'})

    st.subheader('Quick insights')
    st.subheader(':cityscape: {} houses available at {}'.format(i1.at[0,'id'],i1.at[0,'zipcode']))
    st.caption('Region with more available houses to sell')
    st.subheader(':moneybag: US$ {:.1f}mi profit foreseen at {}'.format(i2.at[0,'profit'],i2.at[0,'zipcode']))
    st.caption('Most valuable region')    
    st.subheader('Most valuable regions per season')
    st.table(i3)    

    return None

# application
if __name__ == '__main__':
    # parameters
    st.set_page_config(layout='wide', page_title='House Rocket Sales')
    set_background('reports/figures/bg.jpg')    

    # header
    st.title('House Rocket Sales :house_with_garden:')  
    st.header('Indentifying houses por purchase and resale at King County, USA')
    st.header('')

    # ETL
    # data extraction
    path = 'data/kc_house_data.csv'    
    data = get_data( path )
    
    # data transformation
    df = set_features( data_transformation( data ) )    
    filters = set_filters ( df )  
    regional_median = get_regional_median( df )
    season_median = get_season_median( df )     
    pl = purchase_list( df, regional_median )
    plot_purchase(pl, filters[0], filters[1])
    geodata = get_geolocation ( pl )

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            map_data, insights_data = report_sales(pl, geodata, season_median, filters[0], filters[1])        
        with col2:
            show_insights(insights_data)
            
    show_map( map_data )

    st.caption('Developed by Rodrigo Vieira')