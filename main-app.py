import streamlit as st
import pandas as pd
import numpy as np
import urllib
import urllib.request as request
import json
import pydeck as pdk


DATA_URL = ('https://eonet.sci.gsfc.nasa.gov/api/v2.1/events')

st.title("Disaster Delineation")

@st.cache
def load_data():
    with request.urlopen(DATA_URL) as res:
        source = res.read()
        data = json.loads(source)
    df_1 = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
    df_norm = pd.json_normalize(json.loads(df_1.to_json(orient='records')))
    f = df_norm.explode('events.categories')
    f = f.explode('events.sources')
    df = f.explode('events.geometries')
    dataf = pd.json_normalize(json.loads(df.to_json(orient='records')))
    events_data = dataf.copy()
    events_data.drop(columns=['events.description'],axis=1, inplace=True)
    events_data['events.geometries.date'] = pd.to_datetime(events_data['events.geometries.date'])
    return events_data

data = load_data()

#
@st.cache
def map_cordn(data,events_selected):
    lat = []
    lon = []
    idx = data['events.categories.id'].loc[data['events.categories.title']==events_selected]
    for i in range(len(idx)):
        lat.append(data['events.geometries.coordinates'][i][0])
        lon.append(data['events.geometries.coordinates'][i][1])
    dd = pd.DataFrame(data=[pd.Series(lon),pd.Series(lat)],index=['lat','lon'])
    cordn=pd.DataFrame(dd.T,columns=['lon','lat']) 
    return cordn


st.sidebar.markdown('Real Time Disaster Events')

#Plotting bar graph for no of occuring events
events = data.groupby('events.categories.title').mean()
event = events.reset_index()
df =pd.DataFrame( pd.Series(events['events.categories.id'],name='Events'))
dn = df.reset_index()

dn.index=['Sea and Lake Ice','Severe Storms','Volcanoes','WildFires']
dn.drop(columns=['events.categories.title'],inplace=True)
st.write('The bar chart shows the no of occuring disaster events around the world.')
st.bar_chart(dn)

COLOR_BREWER_BLUE_SCALE = [                                                     
      [240, 249, 232],                                                            
      [204, 235, 197],                                                            
      [168, 221, 181],                                                            
      [123, 204, 196],                                                            
      [67, 162, 202],                                                             
      [8, 104, 172],                                                              
]     


disaster_event_selected = [e for e in event['events.categories.title'] 
        if st.sidebar.checkbox(e,True)]

#Plotting the Quick maps
if disaster_event_selected:
    for i in range(len(disaster_event_selected)):
        st.header(disaster_event_selected[i])
        event = data['events.title'].groupby(data['events.categories.title']==disaster_event_selected[i])
        for e in event.head():
            e += e+", "
        e +='.'
        '''Places :''',e
        st.map(map_cordn(data,disaster_event_selected[i])) 

#Plotting the Heatmap Layer
    if st.sidebar.checkbox("Heatmap Layer",True):
        for j in range(len(disaster_event_selected)):            
            st.write(disaster_event_selected[j])
            d = map_cordn(data,disaster_event_selected[j])
            view = pdk.data_utils.compute_view(d[["lon", "lat"]])  
            view.zoom = 0
            
            events = pdk.Layer(
                'HeatmapLayer',
                data=d,
                opacity=30,
                get_position=["lon", "lat"],
                get_weight=50,
                #get_radius=2,
                #auto_highlights=True,
                #aggregation='"MEAN"',
                #get_fill_color=[255, 255, 255],
                #color_range=
                threshold=3,
                pickable=True,
                 )
            r = pdk.Deck(                                                                  
              layers=events,                                                          
              initial_view_state=view,                                                
              map_style=pdk.map_styles.DARK,                                          
              map_provider='mapbox',                                                                      
                 )   
            r

else:
    st.error("Please choose at least one layer above..")
#with row1:
#    r
