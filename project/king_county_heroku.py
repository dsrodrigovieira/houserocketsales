# libraries
import base64
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim

# parameters
st.set_page_config(layout='wide', page_title='KC House Sales')

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
    data['season'] = data['month'].apply(lambda x: 'winter' if x in(12,1,2) else
                                                'spring' if x in(3,4,5) else
                                                'summer' if x in(6,7,8) else 'fall' )
    data['sn_compra'] = data['sn_compra'].astype('string')
    data['condition_type'] = data['condition_type'].astype('string')
    data['season'] = data['season'].astype('string')
    
    return data 

def set_filters( data ):  
    st.sidebar.title('Options :gear:')  
    f_zipcode = st.sidebar.selectbox('Select region', data['zipcode'].sort_values().unique())
    f_filters = st.sidebar.checkbox("Disable filters (View all houses on grid and map. Doesn't affect chart)")

    return f_zipcode, f_filters

def get_geolocation ( path ):
    geolocation = pd.read_csv( path )
    
    return geolocation

def get_regional_median ( data ):
    regional_median = data[['zipcode','price']].groupby('zipcode').median().reset_index().copy()
    regional_median.columns = ['zipcode','regional_median']

    return regional_median

def get_season_median ( data ):
    season_median = data[['price','zipcode','season']].groupby(['zipcode','season']).median('price')
    season_median = season_median.rename(columns={'price': 'season_median'})

    return season_median

def purchase_list ( data, median ):
    purchase = data.merge( median, how='inner', on='zipcode' ).copy()
    purchase['condition_type'] = purchase['condition_type'].astype( 'string' )
    purchase['sn_compra'] = purchase['sn_compra'].astype( 'string' )
    purchase['condition_type'] = purchase['condition'].apply( lambda x: 'good' if x==5 else
                                                                        'regular' if x in(3,4) else 'bad')
    purchase['sn_compra'] = purchase.apply( lambda x: 'y' if ( x['price'] < x['regional_median'] ) &
                                                             ( x['condition_type'] == 'good') else 'n',
                                                                axis=1 )
    purchase = purchase.drop( columns=['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'waterfront',
                                      'view', 'condition', 'grade', 'sqft_above', 'sqft_basement', 'yr_built',
                                      'yr_renovated', 'month'] )
    
    return purchase

def data_viz( data, geodata, season_median, region, filter ):  

    # header
    st.title('House sales in King County, USA :house_with_garden:')  
    st.header('Indentifying houses for purchase and resale')
    st.header('')
        
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

    #Report
    sell = data.copy()
    sell = sell.merge( season_median, how='inner', on=['zipcode','season'])
    sell['sell_price'] = sell.apply(lambda x: x['price']*1.3 if x['price'] < x['season_median'] else
                                              x['price']*1.1, axis = 1 )
    sell['profit'] = sell['sell_price'] - sell['price']
    sell = sell.loc[sell['sn_compra'] == 'y']
    sell = sell.drop( columns = ['date','sn_compra','condition_type','regional_median'] )    
    sell = sell.merge( geodata[['id', 'address', 'neighbourhood', 'city']], how = 'inner', on = 'id' )
    sell.reset_index( drop = True )

    if filter:
        None
    else:
        sell = sell.loc[sell['zipcode'] == region]

    st.subheader('Recommended houses for purchase')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Details and price suggestion - {:} houses'.format(sell.shape[0]))
    st.dataframe(sell[['id', 'zipcode', 'address', 'price', 'sell_price', 'season', 'profit']].rename(columns={'id': 'ID', 'zipcode': 'Region', 'address': 'Address', 'price': 'Cost',
        'sell_price': 'Price suggestion', 'season': 'Season', 'profit': 'Profit'}).sort_values(['Season','Profit']).reset_index(drop=True))    

    map_data = sell

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

# application
if __name__ == '__main__':

    set_background('bg.jpg')    

    # ETL
    # data extraction
    path_houses = 'kc_house_data.csv'    
    path_geoloc = 'geoloc.csv' 

    data = get_data( path_houses )
    
    # data transformation
    df = set_features( data_transformation( data ) )    
    filters = set_filters ( df )  
    regional_median = get_regional_median( df )
    season_median = get_season_median( df ) 
    pl = purchase_list( df, regional_median )
    geodata = get_geolocation ( path_geoloc )

    # data load
    data_viz( pl, geodata, season_median, filters[0], filters[1])

# EOF
    
