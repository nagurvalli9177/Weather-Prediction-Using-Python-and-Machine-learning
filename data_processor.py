import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DataProcessor:
    """Utility class for processing weather data"""
    
    def __init__(self):
        pass
    
    def process_current_weather(self, weather_data):
        """
        Process current weather data from API response
        
        Args:
            weather_data (dict): Raw weather data from API
            
        Returns:
            dict: Processed weather data
        """
        if not weather_data:
            return None
        
        try:
            processed = {
                'location': weather_data.get('name', 'Unknown'),
                'country': weather_data.get('sys', {}).get('country', 'Unknown'),
                'coordinates': {
                    'lat': weather_data.get('coord', {}).get('lat', 0),
                    'lon': weather_data.get('coord', {}).get('lon', 0)
                },
                'datetime': datetime.fromtimestamp(weather_data.get('dt', 0)),
                'temperature': weather_data.get('main', {}).get('temp', 0),
                'feels_like': weather_data.get('main', {}).get('feels_like', 0),
                'temp_min': weather_data.get('main', {}).get('temp_min', 0),
                'temp_max': weather_data.get('main', {}).get('temp_max', 0),
                'humidity': weather_data.get('main', {}).get('humidity', 0),
                'pressure': weather_data.get('main', {}).get('pressure', 0),
                'sea_level': weather_data.get('main', {}).get('sea_level', 0),
                'ground_level': weather_data.get('main', {}).get('grnd_level', 0),
                'visibility': weather_data.get('visibility', 0) / 1000,  # Convert to km
                'wind_speed': weather_data.get('wind', {}).get('speed', 0),
                'wind_direction': weather_data.get('wind', {}).get('deg', 0),
                'wind_gust': weather_data.get('wind', {}).get('gust', 0),
                'cloudiness': weather_data.get('clouds', {}).get('all', 0),
                'weather_main': weather_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': weather_data.get('weather', [{}])[0].get('description', 'Unknown'),
                'weather_icon': weather_data.get('weather', [{}])[0].get('icon', '01d'),
                'sunrise': datetime.fromtimestamp(weather_data.get('sys', {}).get('sunrise', 0)),
                'sunset': datetime.fromtimestamp(weather_data.get('sys', {}).get('sunset', 0))
            }
            
            # Add rain and snow data if available
            if 'rain' in weather_data:
                processed['rain_1h'] = weather_data['rain'].get('1h', 0)
                processed['rain_3h'] = weather_data['rain'].get('3h', 0)
            else:
                processed['rain_1h'] = 0
                processed['rain_3h'] = 0
            
            if 'snow' in weather_data:
                processed['snow_1h'] = weather_data['snow'].get('1h', 0)
                processed['snow_3h'] = weather_data['snow'].get('3h', 0)
            else:
                processed['snow_1h'] = 0
                processed['snow_3h'] = 0
            
            return processed
            
        except Exception as e:
            print(f"Error processing current weather data: {str(e)}")
            return None
    
    def process_forecast_data(self, forecast_data):
        """
        Process forecast data from API response
        
        Args:
            forecast_data (dict): Raw forecast data from API
            
        Returns:
            pd.DataFrame: Processed forecast data
        """
        if not forecast_data or 'list' not in forecast_data:
            return pd.DataFrame()
        
        try:
            forecast_list = []
            
            for item in forecast_data['list']:
                forecast_point = {
                    'datetime': datetime.fromtimestamp(item.get('dt', 0)),
                    'temperature': item.get('main', {}).get('temp', 0),
                    'feels_like': item.get('main', {}).get('feels_like', 0),
                    'temp_min': item.get('main', {}).get('temp_min', 0),
                    'temp_max': item.get('main', {}).get('temp_max', 0),
                    'humidity': item.get('main', {}).get('humidity', 0),
                    'pressure': item.get('main', {}).get('pressure', 0),
                    'sea_level': item.get('main', {}).get('sea_level', 0),
                    'ground_level': item.get('main', {}).get('grnd_level', 0),
                    'visibility': item.get('visibility', 10000) / 1000,  # Convert to km
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'wind_direction': item.get('wind', {}).get('deg', 0),
                    'wind_gust': item.get('wind', {}).get('gust', 0),
                    'cloudiness': item.get('clouds', {}).get('all', 0),
                    'weather_main': item.get('weather', [{}])[0].get('main', 'Unknown'),
                    'weather_description': item.get('weather', [{}])[0].get('description', 'Unknown'),
                    'weather_icon': item.get('weather', [{}])[0].get('icon', '01d'),
                    'precipitation_probability': item.get('pop', 0) * 100  # Convert to percentage
                }
                
                # Add rain and snow data if available
                if 'rain' in item:
                    forecast_point['rain_3h'] = item['rain'].get('3h', 0)
                else:
                    forecast_point['rain_3h'] = 0
                
                if 'snow' in item:
                    forecast_point['snow_3h'] = item['snow'].get('3h', 0)
                else:
                    forecast_point['snow_3h'] = 0
                
                forecast_list.append(forecast_point)
            
            df = pd.DataFrame(forecast_list)
            df = df.sort_values('datetime').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error processing forecast data: {str(e)}")
            return pd.DataFrame()
    
    def calculate_weather_indices(self, weather_data):
        """
        Calculate additional weather indices and comfort metrics
        
        Args:
            weather_data (dict): Processed weather data
            
        Returns:
            dict: Additional weather indices
        """
        if not weather_data:
            return {}
        
        try:
            indices = {}
            
            temp = weather_data.get('temperature', 0)
            humidity = weather_data.get('humidity', 0)
            wind_speed = weather_data.get('wind_speed', 0)
            
            # Heat Index (simplified formula)
            if temp >= 27:  # Only calculate for temperatures above 27°C
                hi = temp + 0.5 * (humidity - 50) * 0.1
                indices['heat_index'] = round(hi, 1)
            else:
                indices['heat_index'] = temp
            
            # Wind Chill (for temperatures below 10°C and wind > 4.8 km/h)
            if temp <= 10 and wind_speed > 1.3:  # wind_speed in m/s
                wc = 13.12 + 0.6215 * temp - 11.37 * (wind_speed * 3.6) ** 0.16 + 0.3965 * temp * (wind_speed * 3.6) ** 0.16
                indices['wind_chill'] = round(wc, 1)
            else:
                indices['wind_chill'] = temp
            
            # Comfort Index
            if 18 <= temp <= 24 and 40 <= humidity <= 60:
                indices['comfort_level'] = 'Comfortable'
            elif temp < 18 or temp > 30:
                indices['comfort_level'] = 'Uncomfortable'
            elif humidity > 70:
                indices['comfort_level'] = 'Humid'
            elif humidity < 30:
                indices['comfort_level'] = 'Dry'
            else:
                indices['comfort_level'] = 'Moderate'
            
            # Air Quality Index (placeholder - would need actual AQI data)
            indices['aqi_status'] = 'Data not available'
            
            # UV Index (placeholder - would need actual UV data)
            indices['uv_index'] = 'Data not available'
            
            return indices
            
        except Exception as e:
            print(f"Error calculating weather indices: {str(e)}")
            return {}
    
    def aggregate_daily_data(self, forecast_df):
        """
        Aggregate hourly forecast data into daily summaries
        
        Args:
            forecast_df (pd.DataFrame): Hourly forecast data
            
        Returns:
            pd.DataFrame: Daily aggregated data
        """
        if forecast_df.empty:
            return pd.DataFrame()
        
        try:
            # Add date column
            forecast_df['date'] = forecast_df['datetime'].dt.date
            
            # Group by date and aggregate
            daily_data = forecast_df.groupby('date').agg({
                'temperature': ['min', 'max', 'mean'],
                'humidity': 'mean',
                'pressure': 'mean',
                'wind_speed': 'max',
                'cloudiness': 'mean',
                'precipitation_probability': 'max',
                'rain_3h': 'sum',
                'snow_3h': 'sum'
            }).round(1)
            
            # Flatten column names
            daily_data.columns = ['_'.join(col).strip() for col in daily_data.columns]
            daily_data = daily_data.reset_index()
            
            return daily_data
            
        except Exception as e:
            print(f"Error aggregating daily data: {str(e)}")
            return pd.DataFrame()
    
    def detect_weather_patterns(self, forecast_df):
        """
        Detect weather patterns and trends in forecast data
        
        Args:
            forecast_df (pd.DataFrame): Forecast data
            
        Returns:
            dict: Detected patterns and trends
        """
        if forecast_df.empty:
            return {}
        
        try:
            patterns = {}
            
            # Temperature trend
            temp_trend = np.polyfit(range(len(forecast_df)), forecast_df['temperature'], 1)[0]
            if temp_trend > 0.5:
                patterns['temperature_trend'] = 'Rising'
            elif temp_trend < -0.5:
                patterns['temperature_trend'] = 'Falling'
            else:
                patterns['temperature_trend'] = 'Stable'
            
            # Pressure trend
            if 'pressure' in forecast_df.columns:
                pressure_trend = np.polyfit(range(len(forecast_df)), forecast_df['pressure'], 1)[0]
                if pressure_trend > 0.5:
                    patterns['pressure_trend'] = 'Rising'
                elif pressure_trend < -0.5:
                    patterns['pressure_trend'] = 'Falling'
                else:
                    patterns['pressure_trend'] = 'Stable'
            
            # Weather stability
            weather_changes = forecast_df['weather_main'].nunique()
            if weather_changes <= 2:
                patterns['weather_stability'] = 'Stable'
            elif weather_changes <= 4:
                patterns['weather_stability'] = 'Variable'
            else:
                patterns['weather_stability'] = 'Highly Variable'
            
            # Precipitation pattern
            precip_hours = (forecast_df['precipitation_probability'] > 50).sum()
            total_hours = len(forecast_df)
            precip_ratio = precip_hours / total_hours
            
            if precip_ratio > 0.7:
                patterns['precipitation_pattern'] = 'Frequent Rain'
            elif precip_ratio > 0.3:
                patterns['precipitation_pattern'] = 'Occasional Rain'
            else:
                patterns['precipitation_pattern'] = 'Mostly Dry'
            
            return patterns
            
        except Exception as e:
            print(f"Error detecting weather patterns: {str(e)}")
            return {}
