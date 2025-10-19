import requests
import json
from datetime import datetime
import streamlit as st

class WeatherAPI:
    """Weather API service for fetching real-time weather data from OpenWeatherMap"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
        
    def get_current_weather(self, location):
        """
        Fetch current weather data for a given location
        
        Args:
            location (str): City name or coordinates (lat,lon)
            
        Returns:
            dict: Current weather data or None if failed
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"JSON Decode Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error fetching current weather: {str(e)}")
            return None
    
    def get_forecast(self, location, days=5):
        """
        Fetch weather forecast data for a given location
        
        Args:
            location (str): City name or coordinates (lat,lon)
            days (int): Number of days for forecast (default: 5)
            
        Returns:
            dict: Forecast data or None if failed
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"JSON Decode Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error fetching forecast: {str(e)}")
            return None
    
    def get_historical_weather(self, location, start_date, end_date):
        """
        Fetch historical weather data (Note: Requires paid OpenWeatherMap plan)
        
        Args:
            location (str): City name or coordinates (lat,lon)
            start_date (int): Unix timestamp for start date
            end_date (int): Unix timestamp for end date
            
        Returns:
            dict: Historical weather data or None if failed
        """
        try:
            # First get coordinates for the location
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            geo_response = self.session.get(geocoding_url, params=geo_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                st.warning("Location not found for historical data")
                return None
            
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            
            # Get historical data
            url = f"{self.base_url}/onecall/timemachine"
            historical_data = []
            
            current_timestamp = start_date
            while current_timestamp <= end_date:
                params = {
                    'lat': lat,
                    'lon': lon,
                    'dt': current_timestamp,
                    'appid': self.api_key,
                    'units': 'metric'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    historical_data.append(response.json())
                
                current_timestamp += 86400  # Add 1 day (86400 seconds)
            
            return historical_data
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Historical data requires a paid API plan: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error fetching historical weather: {str(e)}")
            return None
    
    def get_air_quality(self, location):
        """
        Fetch air quality data for a given location
        
        Args:
            location (str): City name or coordinates (lat,lon)
            
        Returns:
            dict: Air quality data or None if failed
        """
        try:
            # First get coordinates
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            geo_response = self.session.get(geocoding_url, params=geo_params, timeout=10)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                return None
            
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            
            # Get air quality data
            url = f"{self.base_url}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Air quality data not available: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error fetching air quality: {str(e)}")
            return None
