from flask import (
    Flask,
    render_template,
    request,
    Response,
    redirect,
    url_for
)

import requests
import csv
import io

from database import (
    create_table,
    save_search,
    get_search_history,
    delete_search,
    clear_search_history
)

from weather_analysis import analyze_weather
from weather_prediction import predict_temperature


app = Flask(__name__)

create_table()


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- WEATHER DASHBOARD ----------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    weather = None
    error = None
    insights = []
    summary = ""
    weather_condition = None

    if request.method == "POST":

        location = request.form.get("location", "").strip()

        if not location:
            error = "Please enter a city, district, or location."

        else:
            try:
                # STEP 1: Find the location's coordinates

                geocoding_url = (
                    "https://geocoding-api.open-meteo.com/v1/search"
                )

                geocoding_params = {
                    "name": location,
                    "count": 10,
                    "language": "en",
                    "format": "json",
                }

                geocoding_response = requests.get(
                    geocoding_url,
                    params=geocoding_params,
                    timeout=10
                )

                geocoding_response.raise_for_status()

                geocoding_data = geocoding_response.json()
                results = geocoding_data.get("results", [])

                if not results:
                    error = (
                        "Location not found. Try entering a valid "
                        "city, district, or PIN code."
                    )

                else:
                    place = results[0]

                    latitude = place["latitude"]
                    longitude = place["longitude"]

                    place_name = place.get("name", location)
                    state = place.get("admin1", "")
                    country = place.get("country", "India")

                    # STEP 2: Get current weather and 7-day forecast

                    weather_url = (
                        "https://api.open-meteo.com/v1/forecast"
                    )

                    weather_params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": (
                            "temperature_2m,"
                            "relative_humidity_2m,"
                            "precipitation,"
                            "wind_speed_10m"
                        ),
                        "daily": (
                            "temperature_2m_max,"
                            "temperature_2m_min,"
                            "precipitation_sum,"
                            "wind_speed_10m_max"
                        ),
                        "forecast_days": 7,
                        "temperature_unit": "celsius",
                        "wind_speed_unit": "kmh",
                        "precipitation_unit": "mm",
                        "timezone": "auto"
                    }

                    weather_response = requests.get(
                        weather_url,
                        params=weather_params,
                        timeout=15
                    )

                    weather_response.raise_for_status()

                    weather_data = weather_response.json()

                    current = weather_data.get("current", {})
                    daily = weather_data.get("daily", {})

                    if not current or not daily:
                        error = (
                            "Weather data is currently unavailable "
                            "for this location."
                        )

                    else:
                        # STEP 3: Save successful search in database

                        save_search(place_name)

                        # STEP 4: Generate weather graphs

                        try:
                            analyze_weather(
                                location,
                                latitude,
                                longitude
                            )
                        except Exception as graph_error:
                            print("Graph generation error:", graph_error)

                        # STEP 5: Prepare weather information

                        temperature = current.get("temperature_2m")
                        humidity = current.get("relative_humidity_2m")
                        rainfall = current.get("precipitation")
                        wind = current.get("wind_speed_10m")

                        dates = daily.get("time", [])
                        max_temperatures = daily.get(
                            "temperature_2m_max", []
                        )
                        min_temperatures = daily.get(
                            "temperature_2m_min", []
                        )
                        daily_rainfall = daily.get(
                            "precipitation_sum", []
                        )
                        daily_wind = daily.get(
                            "wind_speed_10m_max", []
                        )

                        weather = {
                            "location": place_name,
                            "state": state,
                            "country": country,
                            "latitude": latitude,
                            "longitude": longitude,
                            "temperature": temperature,
                            "humidity": humidity,
                            "rainfall": rainfall,
                            "wind": wind,
                            "time": current.get("time", ""),
                            "dates": dates,
                            "max_temperature": max_temperatures,
                            "min_temperature": min_temperatures,
                            "daily_rainfall": daily_rainfall,
                            "daily_wind": daily_wind
                        }

                        # STEP 6: Predict temperature trend

                        try:
                            numeric_temperatures = [
                                value
                                for value in max_temperatures
                                if value is not None
                            ]

                            if len(numeric_temperatures) >= 2:
                                predicted_temperature = predict_temperature(
                                    numeric_temperatures
                                )
                            else:
                                predicted_temperature = None

                        except Exception as prediction_error:
                            print(
                                "Prediction error:",
                                prediction_error
                            )
                            predicted_temperature = None

                        weather["predicted_temperature"] = (
                            predicted_temperature
                        )

                        # STEP 7: Generate automatic insights

                        if temperature is not None:
                            if temperature >= 35:
                                insights.append(
                                    "High temperature detected. "
                                    "Stay hydrated and avoid excessive "
                                    "heat exposure."
                                )
                            elif temperature >= 25:
                                insights.append(
                                    "The weather is relatively warm."
                                )
                            else:
                                insights.append(
                                    "The current temperature is "
                                    "relatively cool."
                                )

                        if humidity is not None:
                            if humidity >= 70:
                                insights.append(
                                    "Humidity is high, so the weather "
                                    "may feel more uncomfortable."
                                )
                            elif humidity >= 40:
                                insights.append(
                                    "Humidity is at a moderate level."
                                )
                            else:
                                insights.append(
                                    "Humidity is relatively low."
                                )

                        if rainfall is not None:
                            if rainfall > 0:
                                insights.append(
                                    "Precipitation has been recorded "
                                    "in the current weather data."
                                )
                            else:
                                insights.append(
                                    "No precipitation is recorded "
                                    "in the current weather data."
                                )

                        if wind is not None:
                            if wind >= 30:
                                insights.append(
                                    "Wind speed is high. Check local "
                                    "weather advisories if necessary."
                                )
                            elif wind >= 10:
                                insights.append(
                                    "Moderate wind speed is recorded."
                                )
                            else:
                                insights.append(
                                    "Wind speed is relatively low."
                                )

                        # STEP 8: Generate a weather summary

                        summary_parts = []

                        if temperature is not None:
                            summary_parts.append(
                                f"Current temperature is "
                                f"{temperature}°C"
                            )

                        if humidity is not None:
                            summary_parts.append(
                                f"humidity is {humidity}%"
                            )

                        if rainfall is not None:
                            summary_parts.append(
                                f"recorded precipitation is "
                                f"{rainfall} mm"
                            )

                        if wind is not None:
                            summary_parts.append(
                                f"wind speed is {wind} km/h"
                            )

                        summary = ". ".join(summary_parts) + "."

                        # STEP 9: Classify the weather

                        if temperature is not None:
                            if temperature >= 35:
                                weather_condition = "Hot"
                            elif temperature >= 25:
                                weather_condition = "Warm"
                            elif temperature >= 15:
                                weather_condition = "Moderate"
                            else:
                                weather_condition = "Cool"

            except requests.exceptions.RequestException as network_error:
                print("Network error:", network_error)

                error = (
                    "Unable to fetch weather data. Please check your "
                    "internet connection and try again."
                )

            except Exception as general_error:
                print("Unexpected error:", general_error)

                error = (
                    "Something went wrong while analyzing the weather. "
                    "Please try again."
                )

    # Get the latest saved searches

    search_history = get_search_history()

    return render_template(
        "dashboard.html",
        weather=weather,
        error=error,
        insights=insights,
        summary=summary,
        weather_condition=weather_condition,
        search_history=search_history
    )


# ---------------- DELETE ONE SEARCH ----------------

@app.route(
    "/delete_search/<int:search_id>",
    methods=["POST"]
)
def delete_search_route(search_id):

    delete_search(search_id)

    return redirect(url_for("dashboard"))


# ---------------- CLEAR ALL SEARCH HISTORY ----------------

@app.route("/clear_history", methods=["POST"])
def clear_history_route():

    clear_search_history()

    return redirect(url_for("dashboard"))


# ---------------- DOWNLOAD 7-DAY FORECAST AS CSV ----------------

@app.route("/download/<path:location>")
def download_weather(location):

    try:
        # Find location coordinates

        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geocoding_params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format":"json"
        }

        geocoding_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        geocoding_response.raise_for_status()

        geocoding_data = geocoding_response.json()
        results = geocoding_data.get("results", [])

        if not results:
            return Response(
                "Location not found.",
                status=404,
                mimetype="text/plain"
            )

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        # Fetch 7-day forecast

        forecast_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        forecast_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum,"
                "wind_speed_10m_max"
            ),
            "forecast_days": 7,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "timezone": "auto"
        }

        forecast_response = requests.get(
            forecast_url,
            params=forecast_params,
            timeout=15
        )

        forecast_response.raise_for_status()

        forecast_data = forecast_response.json()
        daily = forecast_data.get("daily", {})

        # Create CSV file in memory

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Date",
            "Maximum Temperature (C)",
            "Minimum Temperature (C)",
            "Rainfall (mm)",
            "Maximum Wind Speed (km/h)"
        ])

        dates = daily.get("time", [])
        maximums = daily.get("temperature_2m_max", [])
        minimums = daily.get("temperature_2m_min", [])
        rainfall = daily.get("precipitation_sum", [])
        wind = daily.get("wind_speed_10m_max", [])

        for index, date in enumerate(dates):
            writer.writerow([
                date,
                maximums[index] if index < len(maximums) else "",
                minimums[index] if index < len(minimums) else "",
                rainfall[index] if index < len(rainfall) else "",
                wind[index] if index < len(wind) else ""
            ])

        csv_content = "\ufeff" + output.getvalue()

        filename = "".join(
            character if character.isalnum() or character in "-_"
            else "_"
            for character in location
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                    f'attachment; filename="{filename}_forecast.csv"'
            }
        )

    except requests.exceptions.RequestException as download_error:
        print("CSV download error:", download_error)

        return Response(
            "Unable to download the forecast. Please try again.",
            status=502,
            mimetype="text/plain"
        )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)