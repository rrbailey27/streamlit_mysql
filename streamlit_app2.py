import pandas as pd
import streamlit as st
import plotly.express as px  # interactive charts
import time

#from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="AWS MySQL Testing",
    page_icon="XX",
    layout="wide",
)

st.title('Here is my weather app!')
st.header('Live Data')
display = st.empty() #this is the top row on the dashboard 
temp_graph = st.empty() #this is the line chart of the temp on the dashboardw
humid_graph = st.empty() #this is the line chart of the humidity on the dashboardw


# Initialize connection.
conn = st.connection('mysql', type='sql')

#st_autorefresh(interval=5000, key="fetch_data")

@st.cache_data(ttl=55)
def fetch_data():
    df = conn.query('SELECT tempF, humidity, YEAR(date_add(time_stamp,INTERVAL-5 HOUR)) as year, MONTH(date_add(time_stamp,INTERVAL-5 HOUR)) as month, DAY(date_add(time_stamp,INTERVAL-5 HOUR)) as day, HOUR(date_add(time_stamp,INTERVAL-5 HOUR)) as hour, MINUTE(date_add(time_stamp,INTERVAL-5 HOUR)) as minute, SECOND(date_add(time_stamp,INTERVAL-5 HOUR)) as second, date_add(time_stamp,INTERVAL-5 HOUR) as ts FROM esp32_dht ORDER BY time_stamp DESC LIMIT 5760;', ttl=1) 
    return df

def twodigits(string):
    if len(string)==1:
        newstring = "0" + string
    else:
        newstring = string
    return newstring

while True:
    data = fetch_data()

    current_temp, current_humidity = data.at[data.index[0], "tempF"], data.at[data.index[0], "humidity"]
    old_temp, old_humidity = data.at[data.index[1], "tempF"], data.at[data.index[1], "humidity"]
    temp_delta, humid_delta = int(current_temp)-int(old_temp), int(current_humidity)-int(old_humidity)
    
    month = str(data.at[data.index[0],"month"])
    day = str(data.at[data.index[0],"day"])
    year = str(data.at[data.index[0],"year"])
    hour = twodigits(str(data.at[data.index[0],"hour"]))
    minute = twodigits(str(data.at[data.index[0],"minute"]))
    second = twodigits(str(data.at[data.index[0],"second"]))
    lasttime_str = "Time of Last Data: "+ month + "/" + day + "/" + year + " at "+ hour + ":" + minute + ":" + second   

    with display.container():
        st.text(lasttime_str)    
        
        # Create Summary Temperature Information
        kpi1, kpi2 = st.columns(2)
   
        kpi1.metric(
            label = "Temperature F",
            value = "{} F".format(current_temp),
            delta = "{} F".format(temp_delta)
        )

        kpi2.metric(
            label="Humdity",
            value="{} %".format(current_humidity),
            delta="{} %".format(humid_delta)
        )
             
    with temp_graph:
        tempdata = data[['ts','tempF']].copy()
        fig_t = px.line(
            tempdata,
            x="ts", 
            y="tempF",
            title="Temperature (F)")
        st.plotly_chart(fig_t)


    with humid_graph:
        humiddata = data[['ts','humidity']].copy()
        fig_h = px.area(
            humiddata,
            x="ts", 
            y="humidity",
            title="Humidity (%)")
        st.plotly_chart(fig_h)
        
    
    wait_time = 2 # Change to required intervals
    time.sleep(wait_time)
