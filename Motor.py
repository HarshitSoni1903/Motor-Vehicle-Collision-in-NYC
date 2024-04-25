import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL=("Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor Vehicle Collision in NYC")
st.markdown("This dashboard analyzes and visualizes Vehicle collision in NYC!")

@st.cache_data
@st.cache_resource
def load_data(nrows):
    data=pd.read_csv(DATA_URL, nrows=nrows)
    data['crash_date_crash_time'.upper()]=pd.to_datetime(data['CRASH_DATE']+' '+data['CRASH_TIME'])
    data.drop(columns=['CRASH_DATE','CRASH_TIME'],inplace=True)
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(str.lower, axis="columns", inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
    return data

data=load_data(100000)
orignaldata=load_data(100000)

midpoint=(np.average(data['longitude']),np.average(data['latitude']))

st.header("Where are most people injured in NYC?")
injured_people=st.slider("# of poeple injured in collisions",0,19)
st.map(data.query("injured_persons >= @injured_people")[['latitude','longitude']].dropna(how='any'),latitude=midpoint[1], longitude=midpoint[0], zoom=9,size=1)

st.header("Collisions occured during a given time of day")
hour = st.slider("hour:", 0,23,1)
data=data[data['date/time'].dt.hour==hour]

st.markdown("Vehicle Collisions between %i:00 and %i:00"%(hour,(hour+1) %24))
# print(midpoint)
st.write(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                  initial_view_state={
                      "latitude":midpoint[1],
                      "longitude":midpoint[0],
                      "zoom":10,
                      "pitch":50
                  },
                  layers=[
                      pdk.Layer("HexagonLayer",
                                data=data[['date/time','latitude','longitude']],
                                get_position=['longitude',"latitude"],
                                radius=100,
                                extruded=True,
                                pickable=True,
                                elevation_scale=4,
                                elevation_range=[0,1000],
                                ),
                    
                  ]
                )
        )

st.subheader("breakdown by minute between %i:00 and %i:00" %(hour,(hour+1) %24))

filtered = data[(data['date/time'].dt.hour>=hour)&(data['date/time'].dt.hour<(hour+1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chartdata = pd.DataFrame({'minute':range(60), 'crashes':hist})

fig = px.bar(chartdata, x='minute', y='crashes', hover_data=['minute','crashes'], height=400)
st.write(fig)

st.header("top 5 dangerous streets by affected type")
select = st.selectbox("afftected type",['pedestrians', 'cyclists', 'motorists'])

if select=='pedestrians':
    st.write(orignaldata.query("injured_pedestrians>=1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select=='cyclists':
    st.write(orignaldata.query("injured_cyclists>=1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

elif select=='motorists':
    st.write(orignaldata.query("injured_motorists>=1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])



if st.checkbox("Show Raw Data",False):
    st.subheader("Raw")
    st.write(data)
