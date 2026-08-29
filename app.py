import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt


# ---------------------------------------------------
# Page configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Bike Ride Demand Forecasting",
    page_icon="🏍️",
    layout="wide"
)


# ---------------------------------------------------
# Load model and scaler
# ---------------------------------------------------

@st.cache_resource
def load_artifacts():

    with open("ola_model.pkl", "rb") as file:
        model = pickle.load(file)

    with open("scaler.pkl", "rb") as file:
        scaler = pickle.load(file)

    return model, scaler


model, scaler = load_artifacts()


# ---------------------------------------------------
# Load dataset
# ---------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_csv("ola.csv")

    return data


data = load_data()


# ---------------------------------------------------
# Title
# ---------------------------------------------------

st.title("🏍️ Ola Bike Ride Demand Forecasting")

st.write(
    "Predict the expected number of Ola bike ride requests "
    "based on date, weather, and working-day conditions."
)

st.divider()


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

st.sidebar.header("📅 Ride & Weather Details")


selected_date = st.sidebar.date_input(
    "Select Date"
)


hour = st.sidebar.slider(
    "Hour of Day",
    min_value=0,
    max_value=23,
    value=12
)


temp = st.sidebar.slider(
    "Temperature (°C)",
    min_value=0.0,
    max_value=50.0,
    value=25.0,
    step=0.5
)


humidity = st.sidebar.slider(
    "Humidity (%)",
    min_value=0,
    max_value=100,
    value=60
)


windspeed = st.sidebar.slider(
    "Wind Speed (km/h)",
    min_value=0.0,
    max_value=60.0,
    value=10.0,
    step=0.5
)


holiday = st.selectbox(
    "Holiday",
    [0, 1],
    format_func=lambda x: "Yes" if x == 1 else "No"
)


workingday = st.selectbox(
    "Working Day",
    [0, 1],
    format_func=lambda x: "Yes" if x == 1 else "No"
)


# ---------------------------------------------------
# Extract date features
# ---------------------------------------------------

day = selected_date.day
month = selected_date.month
year = selected_date.year


# ---------------------------------------------------
# Rain feature
# ---------------------------------------------------

rain = 1 if (humidity > 75 and windspeed > 20) else 0


# ---------------------------------------------------
# Prediction
# ---------------------------------------------------

st.subheader("🔮 Demand Prediction")


if st.button(
    "Predict Ride Demand",
    type="primary",
    use_container_width=True
):

    input_data = pd.DataFrame(
        [[
            hour,
            day,
            month,
            year,
            temp,
            humidity,
            windspeed,
            holiday,
            workingday,
            rain
        ]],
        columns=[
            "hour",
            "day",
            "month",
            "year",
            "temp",
            "humidity",
            "windspeed",
            "holiday",
            "workingday",
            "rain"
        ]
    )

    try:

        # Scale input
        scaled_input = scaler.transform(input_data)

        # Prediction
        prediction = model.predict(scaled_input)

        predicted_requests = max(
            0,
            round(float(prediction[0]))
        )

        st.success(
            f"🏍️ Expected Ride Requests: **{predicted_requests:,}**"
        )

        # Show input summary
        st.subheader("Prediction Details")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Date",
            selected_date.strftime("%d %b %Y")
        )

        col2.metric(
            "Hour",
            f"{hour}:00"
        )

        col3.metric(
            "Temperature",
            f"{temp:.1f} °C"
        )

        col4.metric(
            "Humidity",
            f"{humidity}%"
        )

    except Exception as e:

        st.error(
            f"Prediction failed: {e}"
        )


# ---------------------------------------------------
# Historical demand visualization
# ---------------------------------------------------

st.divider()

st.subheader("📊 Historical Ride Demand Pattern")


# Find datetime column
datetime_col = None

for col in data.columns:

    if "date" in col.lower() or "time" in col.lower():

        datetime_col = col
        break


if datetime_col is None:

    st.warning(
        "No datetime column was found in the dataset."
    )

elif "count" not in data.columns:

    st.warning(
        "The dataset does not contain a 'count' column."
    )

else:

    data["datetime"] = pd.to_datetime(
        data[datetime_col],
        errors="coerce"
    )

    data["hour"] = data["datetime"].dt.hour

    hourly_avg = (
        data.groupby("hour")["count"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots()

    ax.plot(
        hourly_avg["hour"],
        hourly_avg["count"]
    )

    ax.set_xlabel("Hour of Day")

    ax.set_ylabel(
        "Average Ride Requests"
    )

    ax.set_title(
        "Average Ride Requests by Hour"
    )

    ax.grid(True, alpha=0.3)

    st.pyplot(fig)


# ---------------------------------------------------
# Information
# ---------------------------------------------------

st.info(
    "This forecasting system can help with driver allocation, "
    "fleet planning, and anticipating periods of high ride demand."
)
