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

def fetch_data():
    rawdata = conn.query('SELECT * from esp32_dht ORDER BY time_stamp DESC LIMIT 300;', ttl=1)
    df = pd.DataFrame(rawdata) #convert to transposed dataframe
    return df


while True:
    data = fetch_data()

    current_temp, current_humidity = data.at[data.index[0], "tempF"], data.at[data.index[0], "humidity"]
    old_temp, old_humidity = data.at[data.index[1], "tempF"], data.at[data.index[1], "humidity"]
    temp_delta, humid_delta = int(current_temp)-int(old_temp), int(current_humidity)-int(old_humidity)

    with display.container():
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
        tempdata = data[['time_stamp','tempF']].copy()
        fig_t = px.line(
            tempdata,
            x="time_stamp", 
            y="tempF",
            title="Temperature (F)")
        st.plotly_chart(fig_t)


    with humid_graph:
        humiddata = data[['time_stamp','humidity']].copy()
        fig_h = px.line(
            humiddata,
            x="time_stamp", 
            y="humidity",
            title="Humidity (%)")
        st.plotly_chart(fig_h)
        
    
    wait_time = 2 # Change to required intervals
    time.sleep(wait_time)
