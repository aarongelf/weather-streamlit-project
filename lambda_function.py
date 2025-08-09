import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

def lambda_handler(event, context):
    
    #site for api information https://openweathermap.org/forecast5
    #API Key
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    def get_weather_forecast(city):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error:", response.status_code, response.text)
            return None
        
    def process_forecast_data(weather_data):
        latitude = weather_data["city"]["coord"]["lat"]
        longitude = weather_data["city"]["coord"]["lon"]
        timezone_offset = weather_data["city"]["timezone"]

        forecast_list = weather_data["list"]
        
        weather_records = []
        for forecast in forecast_list:
            #for time conversion
            unix_time = forecast["dt"]
            local_time = datetime.fromtimestamp(unix_time, tz=timezone.utc) + timedelta(seconds=timezone_offset)

            temp = forecast["main"]["temp"]
            temp_feels_like = forecast["main"]["feels_like"]
            wind_speed = forecast["wind"]["speed"]
            precipitation = forecast.get("rain", {}).get("3h", 0) 
            snow = forecast.get("snow", {}).get("3h", 0)

            weather_records.append([local_time, temp, temp_feels_like, wind_speed, precipitation, snow, latitude, longitude])

        #convert to df
        df = pd.DataFrame(weather_records, columns=[
            "Local Timestamp", 
            "Temperature (°C)", 
            "Feels Like (°C)",
            "Wind Speed (m/s)", 
            "Precipitation (mm)", 
            "Snow (mm)",
            "Latitude",
            "Longitude"])
        df["Wind Speed (km/h)"] = df["Wind Speed (m/s)"] * 3.6
        df.drop(columns=["Wind Speed (m/s)"], inplace=True)
        return df

    #define list of cities
    citieslist = ['Calgary','Toronto','Vancouver','Montreal','Saskatoon']
    weatherdatadict = {}
        #loop
    for city in citieslist:

        #Calgary ex
        # city = "Calgary"
        weather_data = get_weather_forecast(city)

    # Process
        #df_name = f"weather_df_{city}"
        weatherdatadict[city] = process_forecast_data(weather_data)
        #globals()[df_name] = process_forecast_data(weather_data)

        #ranges 
    def getranges():
        ranges = pd.DataFrame({'temp_best':(), 'temp_ok':(), 'wind_best':(), 'wind_ok':(), 'precip_best':(), 'precip_ok':(), 'snow_best':(), 'snow_ok':()})
        ranges.loc['running']       = [(7.5,15),(0,20),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['walking']       = [(15,24),(9,30),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['swimming']      = [(15,24),(9,30),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['climbing']      = [(15,24),(9,30),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['hiking']        = [(15,19),(9,26),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['cycling']       = [(15,24),(9,30),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['golfing']       = [(10,24),(0,26),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['skiing']        = [(-15,-1),(-20,-1),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['snowboarding']  = [(-15,-1),(-20,-1),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]
        ranges.loc['paintballing']     = [(7.5,15),(0,20),(0,10),(0,20),(0,2.5),(0,7.6),(0,2.5),(0,7.6)]

        # possible col values (SHOULD BE SAME ORDER AS THOSE ABOVE)
        weathervars = ['temp','wind','precip','snow']
        weathertype = ['best','ok']
        # possible index values (SAME ORDER)
        sports = ['running','walking','swimming','climbing','hiking','cycling','golfing','skiing','snowboarding','paintballing']

        # generate multicolumn index from all combinations of `weathervars` and `weathertype`, and row index from `sports` list
        multicol = pd.MultiIndex.from_product([weathervars, weathertype], names=["Weather","Range"])
        sportind = pd.Index(sports, name = "Sport")

        # replace index and columns with generated ones from above
        ranges.columns = multicol
        ranges.set_index(sportind, inplace=True)
        return ranges

    rangesdf = getranges()

    def score(
            checkvalue      : float, 
            sport           : str, 
            weathertype     : str, 
            rangesdf        : pd.DataFrame = rangesdf,
            )               -> int:
        """returns the +2/+1/-1 score for a single checkvalue,
        checkvalue is what we want to check (single number)
        sport is 'running', 'cycling', etc,
        weathertype is 'temp','wind','precip','snow',
        rangesdf is the dataframe containing the ranges,
        """
        # convert string "(1,2)" into tuple (1.0,2.0)
        best = tuple(
            float(num) for num in rangesdf.loc[sport][weathertype]['best']#[1:-1].split(", ")
        )
        ok = tuple(
            float(num) for num in rangesdf.loc[sport][weathertype]['ok']#[1:-1].split(", ")
        )

        # check what range checkvalue falls into, return that score
        if (checkvalue >= best[0]) & (checkvalue < best[1]): # best range
            return 2
        elif (checkvalue >= ok[0]) & (checkvalue < ok[1]): # middling range
            return 1
        else: # outside of both ranges
            return -1
        
    def aggregate_score(
            weather_row     : pd.Series, 
            sport           : str,
            )               -> int:
        """
        get sum score from score function for a specific row of weather data, for a given sport
        row names are hard-coded, so don't change them
        """
        tempscore   = score(weather_row["Temperature (°C)"],   sport, 'temp')
        windscore   = score(weather_row["Wind Speed (km/h)"],  sport, 'wind')
        precipscore = score(weather_row["Precipitation (mm)"], sport, 'precip')
        snowscore   = score(weather_row["Snow (mm)"],          sport, 'snow')

        # return aggregate score
        return tempscore + windscore + precipscore + snowscore

    def dataframe_aggscores(
            weatherdf       : pd.DataFrame, 
            rangesdf        : pd.DataFrame,
            )               -> pd.DataFrame:
        """ return dataframe of original weatherdf, with additional columns for
        total aggregate score for each sport in rangesdf.index.values, based on the values
        within weatherdf for that row, and ranges specified in rangesdf
        """
        # copy df for output    
        outdf = weatherdf.copy(deep=True)

        # loop over rows
        for i in range(len(outdf.values)):
            row = outdf.iloc[i] # get current row of weather data
            # loop over sports
            for sport in rangesdf.index.values:
                # append aggregate score to column
                outdf.loc[i, sport+"_aggscore"] = aggregate_score(row, sport)
        
        return outdf   

    def final_city_ranking(city):
        weatherdf = weatherdatadict[city]
        filename = f'weather_df_{city}'

    # call main function to get dataframe and save to csv
        outdf = pd.DataFrame(dataframe_aggscores(weatherdf=weatherdf, rangesdf=rangesdf))
        outdf.to_csv(f'/tmp/{filename}.csv')
        BUCKET_NAME = "data608weatherproject"
        FILE_PATH = f'/tmp/{filename}.csv'
        
        s3 = boto3.client('s3')
        try:
            # Upload the file to S3
            s3.upload_file(FILE_PATH, BUCKET_NAME, filename+".csv")
            print(f"File '{FILE_PATH}' successfully uploaded to 's3://{BUCKET_NAME}/{filename}.csv'")
        except Exception as e:
            print(f"Error uploading file: {e}")


    for city in citieslist:
        final_city_ranking(city)