# Weather Activity Planner

> **NOTE:** AWS server was linked to a school course, which has now been deactivated.

## Project Overview

Weather significantly influences human activities, health, and lifestyle, often acting as a barrier to outdoor sports and physical activity. Seasonal and regional weather variations can limit opportunities for exercise and recreation, impacting well-being. This project aims to empower users to plan outdoor activities by recommending optimal times based on weather forecasts for five Canadian cities.

The application fetches weather data up to five days in advance, scores weather conditions by activity suitability, and presents personalized recommendations via an interactive web app.

## Motivation & Problem Statement

Physical activity is essential for health, yet weather constraints frequently disrupt outdoor plans. Our solution addresses this challenge by enabling users to adapt activity schedules to predicted weather, reducing missed opportunities and encouraging healthier, more active lifestyles. The app not only facilitates planning but also promotes exploration of new activities suited to upcoming conditions.

## Architecture & Data Pipeline

- **Data Generation:** Uses OpenWeatherMap API for global weather data updated every 3 hours for Calgary, Montreal, Saskatoon, Toronto, and Vancouver.
- **Data Ingestion:** Retrieves nested JSON weather data using Python’s `requests` library, extracting key metrics like temperature, wind speed, precipitation, and snowfall.
- **Data Transformation:** Converts JSON into city-specific Pandas DataFrames; uses CSV format for storage due to data size and simplicity.
- **Data Storage:** Stores processed CSV files in AWS S3 after scoring weather conditions per activity.
- **Data Serving:** Streamlit app fetches data from S3, allowing users to select cities and activities, displaying ranked recommendations and visual weather metrics.

## Scoring Algorithm

Each outdoor activity is scored based on predefined “best,” “okay,” and “bad” weather ranges across multiple factors such as temperature and precipitation. Scores are assigned during data transformation, influencing activity recommendations. Time slots between 9 PM and 6 AM are excluded to ensure user safety.

## Challenges & Limitations

- AWS Academy Learner Lab resource constraints limited the number of supported cities and compute capacity.
- Weather data updates every 3 hours, limiting real-time precision.
- CSV storage works well now but would require migration to a database (RDS/DynamoDB) for scalability.

## Future Improvements

- Expand cities and activities supported.
- Enable on-demand or more frequent data fetching.
- Include additional weather factors (e.g., visibility).
- Add reverse scoring for indoor activity recommendations.
- Introduce user customization for preferred times and activity durations.

## Setup & Usage

1. Get an OpenWeatherMap API key.  
2. Configure AWS Lambda and S3 buckets for data ingestion and storage.
3. Run the Streamlit app locally or deploy for web access.

## Requirements

- Python 3.10.x  
- pandas  
- requests  
- boto3  
- streamlit  
