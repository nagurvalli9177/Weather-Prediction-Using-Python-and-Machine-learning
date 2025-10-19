import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

class Dashboard:
    """Dashboard components for weather application"""
    
    def __init__(self):
        # Weather icons mapping
        self.weather_icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '🌫️',
            'Haze': '🌫️',
            'Dust': '🌫️',
            'Fog': '🌫️',
            'Sand': '🌫️',
            'Ash': '🌫️',
            'Squall': '💨',
            'Tornado': '🌪️'
        }
        
        # Color scheme
        self.colors = {
            'primary': '#1E3A8A',
            'secondary': '#0EA5E9',
            'accent': '#F59E0B',
            'background': '#F8FAFC',
            'text': '#1F2937',
            'alert': '#EF4444',
            'success': '#10B981'
        }
    
    def display_current_weather(self, weather_data):
        """
        Display current weather information in cards
        
        Args:
            weather_data (dict): Current weather data
        """
        if not weather_data:
            st.error("❌ No weather data available")
            return
        
        try:
            # Main weather card
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                weather_icon = self.weather_icons.get(weather_data.get('weather_main', 'Clear'), '🌤️')
                st.markdown(f"""
                <div class="weather-card main-weather">
                    <div class="weather-icon">{weather_icon}</div>
                    <div class="weather-info">
                        <h2>{weather_data.get('location', 'Unknown')}, {weather_data.get('country', '')}</h2>
                        <h1>{weather_data.get('temperature', 0):.1f}°C</h1>
                        <p>{weather_data.get('weather_description', 'Unknown').title()}</p>
                        <p>Feels like {weather_data.get('feels_like', 0):.1f}°C</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="weather-metric">
                    <div class="metric-icon">💧</div>
                    <div class="metric-value">{weather_data.get('humidity', 0)}%</div>
                    <div class="metric-label">Humidity</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="weather-metric">
                    <div class="metric-icon">🌪️</div>
                    <div class="metric-value">{weather_data.get('wind_speed', 0):.1f} m/s</div>
                    <div class="metric-label">Wind Speed</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="weather-metric">
                    <div class="metric-icon">🌡️</div>
                    <div class="metric-value">{weather_data.get('pressure', 0)} hPa</div>
                    <div class="metric-label">Pressure</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Secondary metrics
            st.markdown("### 📊 Additional Details")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🌅 Visibility",
                    value=f"{weather_data.get('visibility', 0):.1f} km"
                )
            
            with col2:
                st.metric(
                    label="☁️ Cloudiness",
                    value=f"{weather_data.get('cloudiness', 0)}%"
                )
            
            with col3:
                sunrise = weather_data.get('sunrise', datetime.now())
                if isinstance(sunrise, datetime):
                    st.metric(
                        label="🌅 Sunrise",
                        value=sunrise.strftime("%H:%M")
                    )
            
            with col4:
                sunset = weather_data.get('sunset', datetime.now())
                if isinstance(sunset, datetime):
                    st.metric(
                        label="🌇 Sunset",
                        value=sunset.strftime("%H:%M")
                    )
            
        except Exception as e:
            st.error(f"❌ Error displaying weather data: {str(e)}")
    
    def display_predictions(self, predictions):
        """
        Display ML predictions and weather alerts
        
        Args:
            predictions (dict): ML model predictions
        """
        if not predictions or 'error' in predictions:
            st.warning("⚠️ Predictions not available")
            return
        
        try:
            st.markdown("### 🔮 Weather Predictions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Storm prediction
                storm_prob = predictions.get('storm_probability', 0) * 100
                storm_risk = predictions.get('storm_risk', 'Unknown')
                
                color = 'red' if storm_prob > 70 else 'orange' if storm_prob > 40 else 'green'
                st.markdown(f"""
                <div class="prediction-card">
                    <div class="prediction-icon">⛈️</div>
                    <div class="prediction-title">Storm Risk</div>
                    <div class="prediction-value" style="color: {color}">{storm_prob:.1f}%</div>
                    <div class="prediction-label">{storm_risk}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Temperature prediction
                temp_forecast = predictions.get('temperature_forecast', 0)
                temp_change = predictions.get('temperature_change', 'Unknown')
                
                st.markdown(f"""
                <div class="prediction-card">
                    <div class="prediction-icon">🌡️</div>
                    <div class="prediction-title">Temperature</div>
                    <div class="prediction-value">{temp_forecast:.1f}°C</div>
                    <div class="prediction-label">{temp_change}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Precipitation prediction
                precip_prob = predictions.get('precipitation_probability', 0) * 100
                precip_likelihood = predictions.get('precipitation_likelihood', 'Unknown')
                
                st.markdown(f"""
                <div class="prediction-card">
                    <div class="prediction-icon">🌧️</div>
                    <div class="prediction-title">Precipitation</div>
                    <div class="prediction-value">{precip_prob:.1f}%</div>
                    <div class="prediction-label">{precip_likelihood}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Weather alerts
            alerts = predictions.get('alerts', [])
            if alerts:
                st.markdown("### 🚨 Weather Alerts")
                for alert in alerts:
                    st.warning(alert)
            
        except Exception as e:
            st.error(f"❌ Error displaying predictions: {str(e)}")
    
    def display_weather_details(self, weather_data, category):
        """
        Display detailed weather information by category
        
        Args:
            weather_data (dict): Weather data
            category (str): Category to display ('atmospheric', 'wind', 'visibility')
        """
        if not weather_data:
            return
        
        try:
            if category == 'atmospheric':
                st.markdown("#### 🌊 Atmospheric Conditions")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Pressure",
                        value=f"{weather_data.get('pressure', 0)} hPa"
                    )
                    st.metric(
                        label="Sea Level",
                        value=f"{weather_data.get('sea_level', 0)} hPa" if weather_data.get('sea_level') else "N/A"
                    )
                
                with col2:
                    st.metric(
                        label="Humidity",
                        value=f"{weather_data.get('humidity', 0)}%"
                    )
                    st.metric(
                        label="Ground Level",
                        value=f"{weather_data.get('ground_level', 0)} hPa" if weather_data.get('ground_level') else "N/A"
                    )
            
            elif category == 'wind':
                st.markdown("#### 💨 Wind Conditions")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Wind Speed",
                        value=f"{weather_data.get('wind_speed', 0):.1f} m/s"
                    )
                    st.metric(
                        label="Wind Direction",
                        value=f"{weather_data.get('wind_direction', 0)}°"
                    )
                
                with col2:
                    gust_speed = weather_data.get('wind_gust', 0)
                    st.metric(
                        label="Gust Speed",
                        value=f"{gust_speed:.1f} m/s" if gust_speed > 0 else "No gusts"
                    )
                    
                    # Wind direction description
                    wind_dir = weather_data.get('wind_direction', 0)
                    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
                    direction_idx = int((wind_dir + 11.25) / 22.5) % 16
                    st.metric(
                        label="Direction",
                        value=directions[direction_idx]
                    )
            
            elif category == 'visibility':
                st.markdown("#### 👁️ Visibility & Clouds")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Visibility",
                        value=f"{weather_data.get('visibility', 0):.1f} km"
                    )
                    st.metric(
                        label="Cloudiness",
                        value=f"{weather_data.get('cloudiness', 0)}%"
                    )
                
                with col2:
                    rain_1h = weather_data.get('rain_1h', 0)
                    st.metric(
                        label="Rain (1h)",
                        value=f"{rain_1h} mm" if rain_1h > 0 else "No rain"
                    )
                    snow_1h = weather_data.get('snow_1h', 0)
                    st.metric(
                        label="Snow (1h)",
                        value=f"{snow_1h} mm" if snow_1h > 0 else "No snow"
                    )
            
        except Exception as e:
            st.error(f"❌ Error displaying {category} details: {str(e)}")
    
    def display_forecast_summary(self, forecast_df):
        """
        Display forecast summary cards
        
        Args:
            forecast_df (pd.DataFrame): Forecast data
        """
        if forecast_df.empty:
            st.info("📊 No forecast data available")
            return
        
        try:
            st.markdown("### 📅 5-Day Forecast Summary")
            
            # Group by date
            forecast_df['date'] = pd.to_datetime(forecast_df['datetime']).dt.date
            daily_forecast = forecast_df.groupby('date').agg({
                'temperature': ['min', 'max'],
                'weather_main': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown',
                'precipitation_probability': 'max'
            }).round(1)
            
            # Display daily cards
            cols = st.columns(min(5, len(daily_forecast)))
            
            for i, (date, data) in enumerate(daily_forecast.head(5).iterrows()):
                if i < len(cols):
                    with cols[i]:
                        weather_main = data[('weather_main', '<lambda>')]
                        weather_icon = self.weather_icons.get(weather_main, '🌤️')
                        temp_min = data[('temperature', 'min')]
                        temp_max = data[('temperature', 'max')]
                        precip_prob = data[('precipitation_probability', 'max')]
                        
                        st.markdown(f"""
                        <div class="forecast-card">
                            <div class="forecast-date">{date.strftime('%a, %b %d')}</div>
                            <div class="forecast-icon">{weather_icon}</div>
                            <div class="forecast-temp">{temp_max:.0f}° / {temp_min:.0f}°</div>
                            <div class="forecast-precip">💧 {precip_prob:.0f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error displaying forecast summary: {str(e)}")
