import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def predict_temperature(temperatures):

    if not temperatures:
        return None

    df = pd.DataFrame({
        "Day": range(1, len(temperatures) + 1),
        "Temperature": temperatures
    })

    X = df[["Day"]]
    y = df["Temperature"]

    model = LinearRegression()

    model.fit(X, y)

    # Predict the next day
    next_day = [[len(temperatures) + 1]]

    prediction = model.predict(next_day)

    predicted_temperature = round(
        prediction[0],
        2
    )

    # -----------------------------------
    # CREATE PREDICTION GRAPH
    # -----------------------------------

    all_days = list(
        range(
            1,
            len(temperatures) + 2
        )
    )

    predicted_values = list(
        temperatures
    )

    predicted_values.append(
        predicted_temperature
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        range(1, len(temperatures) + 1),
        temperatures,
        marker="o",
        label="7-Day Temperature"
    )

    plt.plot(
        all_days,
        predicted_values,
        marker="o",
        linestyle="--",
        label="Prediction Trend"
    )

    plt.xlabel("Day")

    plt.ylabel("Temperature (°C)")

    plt.title(
        "Temperature Trend and Next-Day Prediction"
    )

    plt.legend()

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        "static/prediction.png"
    )

    plt.close()

    return predicted_temperature


if __name__ == "__main__":

    temperatures = [
        27,
        28,
        29,
        30,
        29,
        31,
        32
    ]

    result = predict_temperature(
        temperatures
    )

    print(
        "Predicted Temperature:",
        result,
        "°C"
    )