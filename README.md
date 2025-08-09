# Weather Activity Planner

This project recommends optimal times for outdoor activities based on weather forecasts for 5 Canadian cities. 

- Fetches 5-day weather data from OpenWeatherMap API using AWS Lambda.
- Processes and scores weather conditions per activity.
- Stores CSV data in AWS S3.
- Visualizes recommendations via Streamlit app.

## Setup

1. Get an OpenWeatherMap API key.
2. Configure AWS Lambda and S3.
3. Run Streamlit app locally or deploy.

## Requirements

- Python 3.x
- pandas
- requests
- boto3
- streamlit

## Usage

- Run the Lambda function to fetch and process data.
- Launch Streamlit app to explore recommendations.
