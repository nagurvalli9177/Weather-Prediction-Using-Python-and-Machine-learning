import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os

# Import custom modules
from services.weather_api import WeatherAPI
from services.ml_models import WeatherPredictor
from utils.data_processor import DataProcessor
from components.visualizations import WeatherVisualizations
from components.dashboard import Dashboard

# Page configuration
st.set_page_config(
    page_title="Weather Prediction System",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()



# Initialize session state
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = pd.DataFrame()

# Initialize components
@st.cache_resource
def initialize_components():
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    
    weather_api = WeatherAPI(api_key) if api_key else None
    predictor = WeatherPredictor()
    processor = DataProcessor()
    visualizations = WeatherVisualizations()
    dashboard = Dashboard()
    
    return weather_api, predictor, processor, visualizations, dashboard

weather_api, predictor, processor, visualizations, dashboard = initialize_components()

# Check if API key is available for API mode
api_available = weather_api is not None

# Sidebar
st.sidebar.title("🌤️ Weather Control Panel")

# Data source selection
data_source = st.sidebar.radio(
    "Data Source",
    ["Real-time API", "Manual Input"],
    help="Choose between live weather data or manual input for testing"
)

# Initialize default values
location = "London"
refresh_button = False
auto_refresh = False

if data_source == "Real-time API":
    if not api_available:
        st.sidebar.error("API key required for real-time data")
        st.sidebar.info("Switch to Manual Input or add your OpenWeatherMap API key")
        # Don't force manual input, let user choose
    else:
        # Location input
        location = st.sidebar.text_input(
            "Enter Location",
            value="London",
            help="Enter city name or coordinates (lat,lon)"
        )
        
        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
        
        # Refresh button
        refresh_button = st.sidebar.button("🔄 Refresh Data", type="primary")

elif data_source == "Manual Input":
    # Manual input fields
    st.sidebar.subheader("Manual Weather Input")
    
    manual_temp = st.sidebar.number_input(
        "Temperature (°C)",
        min_value=-50.0,
        max_value=60.0,
        value=20.0,
        step=0.1,
        key="manual_temp"
    )
    
    manual_humidity = st.sidebar.number_input(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=65.0,
        step=1.0,
        key="manual_humidity"
    )
    
    manual_pressure = st.sidebar.number_input(
        "Pressure (hPa)",
        min_value=900.0,
        max_value=1100.0,
        value=1013.0,
        step=0.1,
        key="manual_pressure"
    )
    
    manual_wind = st.sidebar.number_input(
        "Wind Speed (m/s)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.1,
        key="manual_wind"
    )
    
    # Predict button
    predict_button = st.sidebar.button("🔮 Predict Weather", type="primary", key="predict_btn")
    
    refresh_button = False
    auto_refresh = False
else:
    # Default values for other modes
    manual_temp = 20.0
    manual_humidity = 65.0
    manual_pressure = 1013.0
    manual_wind = 5.0
    predict_button = False

# Main header
st.markdown("""
<div class="weather-header">
    <h1>🌤️ Weather Prediction System</h1>
    <p>Real-time weather analysis with machine learning predictions</p>
</div>
""", unsafe_allow_html=True)

# Data fetching logic
def fetch_and_process_data(location):
    try:
        with st.spinner("🌍 Fetching weather data..."):
            # Get current weather from API
            current_weather = weather_api.get_current_weather(location)
            if not current_weather:
                st.error("❌ Failed to fetch current weather data. Please check the location or API key.")
                return None, None
            
            # Get forecast data
            forecast_data = weather_api.get_forecast(location)
            
            # Process data
            processed_current = processor.process_current_weather(current_weather)
            processed_forecast = processor.process_forecast_data(forecast_data) if forecast_data else pd.DataFrame()
            
            # Generate predictions using current weather data
            if processed_current:
                # Convert current weather to DataFrame for prediction
                current_df = pd.DataFrame([processed_current])
                predictions = predictor.predict_weather_events(current_df)
            else:
                predictions = {}
            
            return processed_current, predictions
    
    except Exception as e:
        st.error(f"❌ Error fetching weather data: {str(e)}")
        return None, None

# Function to create manual weather data
def create_manual_weather_data(temp, humidity, pressure, wind_speed):
    """Create weather data structure from manual inputs"""
    from datetime import datetime
    return {
        'location': 'Manual Input',
        'country': 'Test',
        'coordinates': {'lat': 0, 'lon': 0},
        'datetime': datetime.now(),
        'temperature': temp,
        'feels_like': temp,
        'temp_min': temp - 2,
        'temp_max': temp + 2,
        'humidity': humidity,
        'pressure': pressure,
        'sea_level': pressure,
        'ground_level': pressure,
        'visibility': 10,
        'wind_speed': wind_speed,
        'wind_direction': 180,
        'wind_gust': wind_speed + 2,
        'cloudiness': 30,
        'weather_main': 'Clear',
        'weather_description': 'clear sky',
        'weather_icon': '01d',
        'sunrise': datetime.now().replace(hour=6, minute=30),
        'sunset': datetime.now().replace(hour=19, minute=45),
        'rain_1h': 0,
        'rain_3h': 0,
        'snow_1h': 0,
        'snow_3h': 0
    }

# Simple prediction function for manual inputs
def get_instant_predictions(temp, humidity, pressure, wind_speed):
    """Generate instant predictions using simple if-else logic"""
    predictions = {}
    
    # Temperature classification
    if temp < 0:
        temp_class = "Freezing"
        temp_color = "blue"
    elif temp < 10:
        temp_class = "Cold"
        temp_color = "lightblue"
    elif temp < 20:
        temp_class = "Cool"
        temp_color = "green"
    elif temp < 30:
        temp_class = "Moderate"
        temp_color = "orange"
    elif temp < 40:
        temp_class = "Hot"
        temp_color = "red"
    else:
        temp_class = "Extreme Heat"
        temp_color = "darkred"
    
    predictions['temperature_class'] = temp_class
    predictions['temperature_color'] = temp_color
    
    # Weather comfort prediction
    if 18 <= temp <= 24 and 40 <= humidity <= 60 and 1010 <= pressure <= 1020 and wind_speed <= 10:
        comfort = "Perfect"
        comfort_color = "green"
    elif 15 <= temp <= 28 and 30 <= humidity <= 70:
        comfort = "Comfortable"
        comfort_color = "lightgreen"
    elif temp > 35 or humidity > 80:
        comfort = "Uncomfortable"
        comfort_color = "orange"
    else:
        comfort = "Fair"
        comfort_color = "yellow"
    
    predictions['comfort'] = comfort
    predictions['comfort_color'] = comfort_color
    
    # Storm risk prediction
    storm_risk = 0
    if pressure < 1000:
        storm_risk += 40
    elif pressure < 1010:
        storm_risk += 20
    
    if wind_speed > 15:
        storm_risk += 30
    elif wind_speed > 10:
        storm_risk += 15
    
    if humidity > 85:
        storm_risk += 20
    elif humidity > 70:
        storm_risk += 10
    
    storm_risk = min(storm_risk, 100)
    
    if storm_risk > 70:
        storm_level = "High Risk"
        storm_color = "red"
    elif storm_risk > 40:
        storm_level = "Medium Risk"
        storm_color = "orange"
    elif storm_risk > 15:
        storm_level = "Low Risk"
        storm_color = "yellow"
    else:
        storm_level = "No Risk"
        storm_color = "green"
    
    predictions['storm_risk'] = storm_risk
    predictions['storm_level'] = storm_level
    predictions['storm_color'] = storm_color
    
    # Rain prediction
    rain_chance = 0
    if humidity > 80:
        rain_chance += 40
    elif humidity > 65:
        rain_chance += 20
    
    if pressure < 1005:
        rain_chance += 30
    elif pressure < 1013:
        rain_chance += 15
    
    if wind_speed > 12:
        rain_chance += 20
    elif wind_speed > 8:
        rain_chance += 10
    
    rain_chance = min(rain_chance, 100)
    
    if rain_chance > 70:
        rain_level = "Very Likely"
        rain_color = "blue"
    elif rain_chance > 50:
        rain_level = "Likely"
        rain_color = "lightblue"
    elif rain_chance > 30:
        rain_level = "Possible"
        rain_color = "lightgray"
    else:
        rain_level = "Unlikely"
        rain_color = "green"
    
    predictions['rain_chance'] = rain_chance
    predictions['rain_level'] = rain_level
    predictions['rain_color'] = rain_color
    
    return predictions

# Function to display instant predictions
def display_instant_predictions(predictions):
    """Display instant predictions for manual input"""
    st.markdown("### 🔮 Weather Prediction Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp_class = predictions.get('temperature_class', 'Unknown')
        temp_color = predictions.get('temperature_color', 'gray')
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-icon">🌡️</div>
            <div class="prediction-title">Temperature</div>
            <div class="prediction-value" style="color: {temp_color}">{temp_class}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        comfort = predictions.get('comfort', 'Unknown')
        comfort_color = predictions.get('comfort_color', 'gray')
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-icon">😌</div>
            <div class="prediction-title">Comfort Level</div>
            <div class="prediction-value" style="color: {comfort_color}">{comfort}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        storm_level = predictions.get('storm_level', 'Unknown')
        storm_color = predictions.get('storm_color', 'gray')
        storm_risk = predictions.get('storm_risk', 0)
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-icon">⛈️</div>
            <div class="prediction-title">Storm Risk</div>
            <div class="prediction-value" style="color: {storm_color}">{storm_level}</div>
            <div class="prediction-label">{storm_risk}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rain_level = predictions.get('rain_level', 'Unknown')
        rain_color = predictions.get('rain_color', 'gray')
        rain_chance = predictions.get('rain_chance', 0)
        st.markdown(f"""
        <div class="prediction-card">
            <div class="prediction-icon">🌧️</div>
            <div class="prediction-title">Rain Chance</div>
            <div class="prediction-value" style="color: {rain_color}">{rain_level}</div>
            <div class="prediction-label">{rain_chance}%</div>
        </div>
        """, unsafe_allow_html=True)

# Handle data based on source
if data_source == "Manual Input":
    # Create weather data from manual inputs
    current_data = create_manual_weather_data(manual_temp, manual_humidity, manual_pressure, manual_wind)
    st.session_state.weather_data = current_data
    
    # Handle predict button click
    if predict_button:
        instant_predictions = get_instant_predictions(manual_temp, manual_humidity, manual_pressure, manual_wind)
        st.session_state.predictions = instant_predictions
        st.session_state.prediction_made = True
        # Show success message
        st.sidebar.success("Prediction generated!")
    
    # Initialize predictions state if not exists
    if 'prediction_made' not in st.session_state:
        st.session_state.prediction_made = False
        st.session_state.predictions = None
    
elif data_source == "Real-time API" and api_available:
    # Auto-refresh logic for API data
    if auto_refresh:
        placeholder = st.empty()
        while auto_refresh:
            current_data, predictions = fetch_and_process_data(location)
            if current_data:
                st.session_state.weather_data = current_data
                st.session_state.predictions = predictions
            time.sleep(30)
            st.rerun()

    # Manual refresh or initial load for API data
    if refresh_button or st.session_state.weather_data is None:
        current_data, predictions = fetch_and_process_data(location)
        if current_data:
            st.session_state.weather_data = current_data
            st.session_state.predictions = predictions

# Display dashboard if data is available
if st.session_state.weather_data is not None:
    # Current weather display
    dashboard.display_current_weather(st.session_state.weather_data)
    
    st.markdown("---")
    
    # Predictions section
    if st.session_state.predictions:
        if data_source == "Manual Input":
            # Display instant predictions for manual input
            display_instant_predictions(st.session_state.predictions)
        else:
            # Display regular predictions for API data
            dashboard.display_predictions(st.session_state.predictions)
        st.markdown("---")
    elif data_source == "Manual Input":
        # Show instruction when no predictions yet
        if not st.session_state.get('prediction_made', False):
            st.info("Enter your weather values in the sidebar and click 'Predict Weather' to see predictions.")
        else:
            st.info("Click 'Predict Weather' again to update predictions with new values.")
    
    # Charts and visualizations
    if data_source == "Real-time API" and api_available:
        # Fetch forecast data once and cache it
        if (refresh_button or auto_refresh or 
            'forecast_data' not in st.session_state or 
            st.session_state.get('current_location') != location):
            
            with st.spinner("Loading forecast data..."):
                forecast_data = weather_api.get_forecast(location)
                if forecast_data:
                    processed_forecast = processor.process_forecast_data(forecast_data)
                    st.session_state.forecast_data = processed_forecast
                    st.session_state.current_location = location
                else:
                    st.session_state.forecast_data = pd.DataFrame()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Temperature Trends")
        try:
            if data_source == "Real-time API" and api_available:
                if 'forecast_data' in st.session_state and not st.session_state.forecast_data.empty:
                    temp_chart = visualizations.create_temperature_chart(st.session_state.forecast_data)
                    st.plotly_chart(temp_chart, use_container_width=True)
                elif 'forecast_data' in st.session_state:
                    st.warning("Temperature forecast data unavailable")
                else:
                    st.info("Click 'Refresh Data' to load temperature trends")
            elif data_source == "Real-time API":
                st.info("API key required for temperature trends")
            else:
                st.info("Switch to Real-time API mode to view temperature trends")
        except Exception as e:
            st.error(f"Error creating temperature chart: {str(e)}")
    
    with col2:
        st.subheader("🌧️ Precipitation Forecast")
        try:
            if data_source == "Real-time API" and api_available:
                if 'forecast_data' in st.session_state and not st.session_state.forecast_data.empty:
                    precip_chart = visualizations.create_precipitation_chart(st.session_state.forecast_data)
                    st.plotly_chart(precip_chart, use_container_width=True)
                elif 'forecast_data' in st.session_state:
                    st.warning("Precipitation forecast data unavailable")
                else:
                    st.info("Click 'Refresh Data' to load precipitation forecast")
            elif data_source == "Real-time API":
                st.info("API key required for precipitation forecast")
            else:
                st.info("Switch to Real-time API mode to view precipitation forecast")
        except Exception as e:
            st.error(f"Error creating precipitation chart: {str(e)}")
    
    # Weather details section
    st.markdown("---")
    st.subheader("🔍 Detailed Weather Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dashboard.display_weather_details(st.session_state.weather_data, "atmospheric")
    
    with col2:
        dashboard.display_weather_details(st.session_state.weather_data, "wind")
    
    with col3:
        dashboard.display_weather_details(st.session_state.weather_data, "visibility")

else:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <h3>🌍 Welcome to Weather Prediction System</h3>
        <p>Enter a location and click "Refresh Data" to get started with real-time weather analysis.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🌤️ Weather Prediction System | Powered by OpenWeatherMap API & Machine Learning</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
