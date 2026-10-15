import requests
import pandas as pd
import matplotlib.pyplot as plt


def analyze_weather(location, latitude=None, longitude=None):

    # -----------------------------------
    # FIND LOCATION
    # -----------------------------------

    if latitude is None or longitude is None:

        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": location,
            "count": 10,
            "language": "en",
            "format": "json"
        }

        response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        response.raise_for_status()

        geo_data = response.json()

        results = geo_data.get("results", [])

        if not results:
            raise ValueError("Location could not be found.")

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]


    # -----------------------------------
    # GET WEATHER DATA
    # -----------------------------------

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {

        "latitude": latitude,
        "longitude": longitude,

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),

        "hourly": "relative_humidity_2m",

        "forecast_days": 7,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm",

        "timezone": "auto"
    }


    response = requests.get(
        weather_url,
        params=weather_params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    daily = data.get("daily", {})
    hourly = data.get("hourly", {})


    # -----------------------------------
    # CREATE DATAFRAME
    # -----------------------------------

    df = pd.DataFrame({

        "Date": daily.get("time", []),

        "Max Temperature":
            daily.get(
                "temperature_2m_max",
                []
            ),

        "Min Temperature":
            daily.get(
                "temperature_2m_min",
                []
            ),

        "Rainfall":
            daily.get(
                "precipitation_sum",
                []
            ),

        "Wind Speed":
            daily.get(
                "wind_speed_10m_max",
                []
            )
    })


    # -----------------------------------
    # TEMPERATURE GRAPH
    # -----------------------------------

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["Date"],
        df["Max Temperature"],
        marker="o",
        label="Maximum Temperature"
    )

    plt.plot(
        df["Date"],
        df["Min Temperature"],
        marker="o",
        label="Minimum Temperature"
    )

    plt.xlabel("Date")

    plt.ylabel("Temperature (°C)")

    plt.title("7-Day Temperature Analysis")

    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()

    plt.savefig("static/temperature.png")

    plt.close()


    # -----------------------------------
    # RAINFALL GRAPH
    # -----------------------------------

    plt.figure(figsize=(10, 5))

    plt.bar(
        df["Date"],
        df["Rainfall"]
    )

    plt.xlabel("Date")

    plt.ylabel("Rainfall (mm)")

    plt.title("7-Day Rainfall Analysis")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("static/rainfall.png")

    plt.close()


    # -----------------------------------
    # WIND SPEED GRAPH
    # -----------------------------------

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["Date"],
        df["Wind Speed"],
        marker="o"
    )

    plt.xlabel("Date")

    plt.ylabel("Wind Speed (km/h)")

    plt.title("7-Day Wind Speed Analysis")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("static/wind.png")

    plt.close()


    # -----------------------------------
    # HUMIDITY GRAPH
    # -----------------------------------

    humidity_values = hourly.get(
        "relative_humidity_2m",
        []
    )

    humidity_dates = hourly.get(
        "time",
        []
    )


    if humidity_values and humidity_dates:

        humidity_df = pd.DataFrame({

            "Time": humidity_dates,

            "Humidity": humidity_values

        })

        humidity_df["Time"] = pd.to_datetime(
            humidity_df["Time"]
        )

        humidity_df["Date"] = (
            humidity_df["Time"]
            .dt.date
        )


        daily_humidity = (
            humidity_df
            .groupby("Date")["Humidity"]
            .mean()
            .reset_index()
        )


        plt.figure(figsize=(10, 5))

        plt.plot(
            daily_humidity["Date"],
            daily_humidity["Humidity"],
            marker="o"
        )

        plt.xlabel("Date")

        plt.ylabel("Humidity (%)")

        plt.title("7-Day Humidity Analysis")

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig("static/humidity.png")

        plt.close()


    # -----------------------------------
    # RETURN DATAFRAME
    # -----------------------------------

    return df