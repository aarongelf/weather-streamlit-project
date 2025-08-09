#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import boto3
from botocore.exceptions import NoCredentialsError
from io import StringIO


# In[ ]:


#let's create client to read/write to S3
s3_client = boto3.client('s3')

#let's use that client to get our bucket
bucket_name = 'data608weatherproject'


# In[ ]:


# object_key = 'Enter-your-object-key-here'
# # access file from bucket
# try:
#     s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
#     # Read the CSV file into a pandas DataFrame
#     csv_content = s3_object['Body'].read().decode('utf-8')  # Decode bytes to string
#     return pd.read_csv(StringIO(csv_content))  # Convert string to DataFrame
# except NoCredentialsError:
#     st.error("AWS credentials not found.")
#     return None
# except Exception as e:
#     st.error(f"Error retrieving data from S3: {e}")
#     return None


# In[ ]:


# add and center title
st.markdown("<h1 style='text-align: center;'>Weather-Based Activity Recommendation App</h1>", unsafe_allow_html=True)


# In[ ]:


# Initialize session state for activity and city if not already set
if 'selected_activity' not in st.session_state:
    st.session_state.selected_activity = None
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None


# In[ ]:


# List of activities and cities
activities = ['Running 🏃‍♂️', 'Walking 🚶‍♀️', 'Swimming 🏊‍♂️', 'Paintballing 🪖', 'Hiking 🥾',
              'Cycling 🚴‍♂️', 'Golfing 🏌️‍♀️', 'Skiing ⛷️', 'Snowboarding 🏂', 'Climbing 🧗‍♀️']
cities = ['Calgary', 'Toronto', 'Vancouver', 'Montreal', 'Saskatoon']

# Display the activity buttons in 5 columns
st.write("### Select an Activity")

activity_columns = st.columns(5)  # Create 5 columns for activities

for i, activity in enumerate(activities):
    col = activity_columns[i % 5]  # Distribute activities across 5 columns
    if col.button(activity):
        st.session_state.selected_activity = activity  # Store the selected activity

# Show the current selected activity
if st.session_state.selected_activity:
    st.write(f"You selected: {st.session_state.selected_activity}")
else:
    st.write("No activity selected")

# Display the city buttons in 5 columns
st.write("### Select a City")

city_columns = st.columns(5)  # Create 5 columns for cities

for i, city in enumerate(cities):
    col = city_columns[i % 5]  # Distribute cities across 5 columns
    if col.button(city):
        st.session_state.selected_city = city  # Store the selected city

# Show the current selected city
if st.session_state.selected_city:
    st.write(f"You selected: {st.session_state.selected_city}")
else:
    st.write("No city selected")


# In[ ]:


# check if both activity and city have been selected before showing the graphs and data
if st.session_state.selected_activity and st.session_state.selected_city:
    
    # remove the emoji from the selected activity before displaying it
    activity = st.session_state.selected_activity.split(' ')[0].lower()
    city = st.session_state.selected_city
    
    st.write(f"### Best times to go {activity} in {city}")

    object_key = f"weather_df_{city}.csv"
    # access file from bucket
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    # Read the CSV file into a pandas DataFrame
    csv_content = s3_object['Body'].read().decode('utf-8')  # Decode bytes to string
    
    csv_file = StringIO(csv_content)  # This creates a file-like object from the string
    df = pd.read_csv(csv_file)
    #st.write(csv_content)
    #st.dataframe(csv_content)
    
    #csv_file_path = f"{city}_weather.csv"
    # read the CSV file into a DataFrame
    #df = pd.read_csv(object_key)
    # construct column name
    aggscore_column = f"{activity}_aggscore"

    #unhash next line to inspect full df
    #st.write(df)

    # Local Timestamp to datetime
    df["Local Timestamp"] = pd.to_datetime(df["Local Timestamp"])

    # format Local Timestamp for easy reading
    df["Date/Time"] = df["Local Timestamp"].dt.strftime('%b %d %I:%M%p')

    # Sort the DataFrame by aggscore_column first (descending) and then by Local Timestamp (ascending) for ties
    sorted_df = df.sort_values(by=[aggscore_column, "Local Timestamp"], ascending=[False, True])
    
    # select only the relevant columns to display
    selected_columns = ["Date/Time", "Temperature (°C)", "Feels Like (°C)", "Precipitation (mm)", "Snow (mm)", "Wind Speed (km/h)"]

    # round variables 
    sorted_df["Temperature (°C)"] = df["Temperature (°C)"].round(0)
    sorted_df["Feels Like (°C)"] = df["Feels Like (°C)"].round(0)
    sorted_df["Precipitation (mm)"] = df["Precipitation (mm)"].round(1)
    sorted_df["Snow (mm)"] = df["Snow (mm)"].round(1)
    sorted_df["Wind Speed (km/h)"] = df["Wind Speed (km/h)"].round(0)

    # Filter only times between 6 AM and 9 PM
    sorted_df = sorted_df[sorted_df["Local Timestamp"].dt.hour >= 6]  # Keep times from 6 AM
    sorted_df = sorted_df[sorted_df["Local Timestamp"].dt.hour <= 21]  # Keep times up to 9 PM

    top_5_df = sorted_df[selected_columns].head()

    # Set the 'Date/Time' as the index before applying the style
    top_5_df.set_index('Date/Time', inplace=True)

    # Display the styled dataframe with color overlay
    st.dataframe(top_5_df, use_container_width=True)

    # create line graphs

    # plot line graph
    fig = px.line(df,
              x="Date/Time", 
              y="Temperature (°C)",
              labels={'Date/Time': 'Date/Time', "Temperature (°C)": "Temperature (°C)"})
    
    #Add vertical lines for points from sorted_df
    for idx, row in sorted_df.head().iterrows():
        # Find the matching row from sorted_date_df based on the Date/Time
        matching_row = df[df["Date/Time"] == row["Date/Time"]]
    
        if not matching_row.empty:
            # Add vertical shaded area (line) at this point using Date/Time from sorted_df
            fig.add_vrect(
                x0=matching_row["Date/Time"].values[0],  # The x-position of the vertical line
                x1=matching_row["Date/Time"].values[0],  # Same value for both x0 and x1 to create a line
                opacity=0.5,  # Set opacity for shading
                line_width=2,  # Line width for vertical line
                line_color= "green" # Color of the vertical line itself (loop over colors)
            )
        
    # increase x-ticks
    fig.update_xaxes(tickmode='linear', dtick=2, tickangle=45)

    st.plotly_chart(fig)

    # plot line graph
    fig = px.line(df,
              x="Date/Time", 
              y="Feels Like (°C)",
              labels={'Date/Time': 'Date/Time', "Feels Like (°C)": "Feels Like (°C)"})
    #Add vertical lines for points from sorted_df
    for idx, row in sorted_df.head().iterrows():
        # Find the matching row from sorted_date_df based on the Date/Time
        matching_row = df[df["Date/Time"] == row["Date/Time"]]
    
        if not matching_row.empty:
            # Add vertical shaded area (line) at this point using Date/Time from sorted_df
            fig.add_vrect(
                x0=matching_row["Date/Time"].values[0],  # The x-position of the vertical line
                x1=matching_row["Date/Time"].values[0],  # Same value for both x0 and x1 to create a line
                opacity=0.5,  # Set opacity for shading
                line_width=2,  # Line width for vertical line
                line_color= "green" # Color of the vertical line itself (loop over colors)
            )
        
    # increase x-ticks
    fig.update_xaxes(tickmode='linear', dtick=2, tickangle=45)

    st.plotly_chart(fig)

    # plot line graph
    fig = px.line(df,
              x="Date/Time", 
              y="Precipitation (mm)",
              labels={'Date/Time': 'Date/Time', "Precipitation (mm)": "Precipitation (mm)"})
    #Add vertical lines for points from sorted_df
    for idx, row in sorted_df.head().iterrows():
        # Find the matching row from sorted_date_df based on the Date/Time
        matching_row = df[df["Date/Time"] == row["Date/Time"]]
    
        if not matching_row.empty:
            # Add vertical shaded area (line) at this point using Date/Time from sorted_df
            fig.add_vrect(
                x0=matching_row["Date/Time"].values[0],  # The x-position of the vertical line
                x1=matching_row["Date/Time"].values[0],  # Same value for both x0 and x1 to create a line
                opacity=0.5,  # Set opacity for shading
                line_width=2,  # Line width for vertical line
                line_color= "green" # Color of the vertical line itself (loop over colors)
            )
        
    # increase x-ticks
    fig.update_xaxes(tickmode='linear', dtick=2, tickangle=45)

    st.plotly_chart(fig)

    # plot line graph
    fig = px.line(df,
              x="Date/Time", 
              y="Snow (mm)",
              labels={'Date/Time': 'Date/Time', "Snow (mm)": "Snow (mm)"})
    #Add vertical lines for points from sorted_df
    for idx, row in sorted_df.head().iterrows():
        # Find the matching row from sorted_date_df based on the Date/Time
        matching_row = df[df["Date/Time"] == row["Date/Time"]]
    
        if not matching_row.empty:
            # Add vertical shaded area (line) at this point using Date/Time from sorted_df
            fig.add_vrect(
                x0=matching_row["Date/Time"].values[0],  # The x-position of the vertical line
                x1=matching_row["Date/Time"].values[0],  # Same value for both x0 and x1 to create a line
                opacity=0.5,  # Set opacity for shading
                line_width=2,  # Line width for vertical line
                line_color= "green" # Color of the vertical line itself (loop over colors)
            )
        
    # increase x-ticks
    fig.update_xaxes(tickmode='linear', dtick=2, tickangle=45)

    st.plotly_chart(fig)
    
    # plot line graph
    fig = px.line(df,
              x="Date/Time", 
              y="Wind Speed (km/h)",
              labels={'Date/Time': 'Date/Time', "Wind Speed (km/h)": "Wind Speed (km/h)"})
    #Add vertical lines for points from sorted_df
    for idx, row in sorted_df.head().iterrows():
        # Find the matching row from sorted_date_df based on the Date/Time
        matching_row = df[df["Date/Time"] == row["Date/Time"]]
    
        if not matching_row.empty:
            # Add vertical shaded area (line) at this point using Date/Time from sorted_df
            fig.add_vrect(
                x0=matching_row["Date/Time"].values[0],  # The x-position of the vertical line
                x1=matching_row["Date/Time"].values[0],  # Same value for both x0 and x1 to create a line
                opacity=0.5,  # Set opacity for shading
                line_width=2,  # Line width for vertical line
                line_color= "green" # Color of the vertical line itself (loop over colors)
            )
        
    # increase x-ticks
    fig.update_xaxes(tickmode='linear', dtick=2, tickangle=45)

    st.plotly_chart(fig)

