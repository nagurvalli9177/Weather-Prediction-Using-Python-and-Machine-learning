import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class WeatherPredictor:
    """Machine learning models for weather event prediction"""
    
    def __init__(self):
        self.storm_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.temp_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.precip_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
    def prepare_features(self, weather_data):
        """
        Prepare features from weather data for ML models
        
        Args:
            weather_data (pd.DataFrame): Weather data
            
        Returns:
            np.array: Feature matrix
        """
        if weather_data.empty:
            return np.array([]).reshape(0, 0)
        
        features = []
        
        # Basic weather features
        if 'temperature' in weather_data.columns:
            features.append(weather_data['temperature'].values)
        if 'humidity' in weather_data.columns:
            features.append(weather_data['humidity'].values)
        if 'pressure' in weather_data.columns:
            features.append(weather_data['pressure'].values)
        if 'wind_speed' in weather_data.columns:
            features.append(weather_data['wind_speed'].values)
        if 'wind_direction' in weather_data.columns:
            features.append(weather_data['wind_direction'].values)
        if 'visibility' in weather_data.columns:
            features.append(weather_data['visibility'].values)
        
        # Time-based features
        if 'datetime' in weather_data.columns:
            weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])
            features.append(weather_data['datetime'].dt.hour.values)
            features.append(weather_data['datetime'].dt.dayofyear.values)
            features.append(weather_data['datetime'].dt.month.values)
        
        # Derived features
        if 'temperature' in weather_data.columns and 'humidity' in weather_data.columns:
            # Heat index approximation
            heat_index = weather_data['temperature'] + 0.5 * weather_data['humidity']
            features.append(heat_index.values)
        
        if 'pressure' in weather_data.columns:
            # Pressure trend (if multiple data points)
            if len(weather_data) > 1:
                pressure_diff = np.diff(weather_data['pressure'].values, prepend=weather_data['pressure'].iloc[0])
                features.append(pressure_diff)
            else:
                features.append(np.array([0]))
        
        if len(features) == 0:
            return np.array([]).reshape(0, 0)
        
        # Ensure all features have the same length
        min_length = min(len(f) for f in features)
        features = [f[:min_length] for f in features]
        
        return np.column_stack(features)
    
    def create_synthetic_training_data(self):
        """
        Create synthetic training data for demonstration purposes
        This would typically be replaced with historical weather data
        
        Returns:
            tuple: (features, storm_labels, temp_targets, precip_labels)
        """
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic weather features
        temperature = np.random.normal(15, 10, n_samples)  # Celsius
        humidity = np.random.uniform(30, 100, n_samples)   # Percentage
        pressure = np.random.normal(1013, 20, n_samples)   # hPa
        wind_speed = np.random.exponential(5, n_samples)   # m/s
        wind_direction = np.random.uniform(0, 360, n_samples)  # degrees
        visibility = np.random.uniform(1, 20, n_samples)   # km
        hour = np.random.randint(0, 24, n_samples)
        day_of_year = np.random.randint(1, 366, n_samples)
        month = np.random.randint(1, 13, n_samples)
        
        # Create feature matrix
        features = np.column_stack([
            temperature, humidity, pressure, wind_speed, wind_direction,
            visibility, hour, day_of_year, month
        ])
        
        # Create synthetic labels based on weather conditions
        # Storm prediction (based on low pressure, high wind, high humidity)
        storm_prob = ((1013 - pressure) / 50 + wind_speed / 10 + humidity / 100) / 3
        storm_labels = (storm_prob > 0.6).astype(int)
        
        # Temperature prediction (next hour temperature)
        temp_targets = temperature + np.random.normal(0, 2, n_samples)
        
        # Precipitation prediction (based on humidity and pressure)
        precip_prob = (humidity / 100 + (1013 - pressure) / 50) / 2
        precip_labels = (precip_prob > 0.7).astype(int)
        
        return features, storm_labels, temp_targets, precip_labels
    
    def train_models(self):
        """Train all ML models with synthetic data"""
        try:
            # Create synthetic training data
            features, storm_labels, temp_targets, precip_labels = self.create_synthetic_training_data()
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train storm classifier
            X_train, X_test, y_train, y_test = train_test_split(
                features_scaled, storm_labels, test_size=0.2, random_state=42
            )
            self.storm_classifier.fit(X_train, y_train)
            storm_accuracy = accuracy_score(y_test, self.storm_classifier.predict(X_test))
            
            # Train temperature regressor
            X_train, X_test, y_train, y_test = train_test_split(
                features_scaled, temp_targets, test_size=0.2, random_state=42
            )
            self.temp_regressor.fit(X_train, y_train)
            temp_mse = mean_squared_error(y_test, self.temp_regressor.predict(X_test))
            
            # Train precipitation classifier
            X_train, X_test, y_train, y_test = train_test_split(
                features_scaled, precip_labels, test_size=0.2, random_state=42
            )
            self.precip_classifier.fit(X_train, y_train)
            precip_accuracy = accuracy_score(y_test, self.precip_classifier.predict(X_test))
            
            self.is_trained = True
            
            return {
                'storm_accuracy': storm_accuracy,
                'temperature_mse': temp_mse,
                'precipitation_accuracy': precip_accuracy
            }
            
        except Exception as e:
            print(f"Error training models: {str(e)}")
            return None
    
    def predict_weather_events(self, weather_data):
        """
        Predict weather events based on current conditions using real-time analysis
        
        Args:
            weather_data (pd.DataFrame): Current weather data
            
        Returns:
            dict: Predictions for various weather events
        """
        try:
            if weather_data.empty:
                return {"error": "No weather data provided"}
            
            predictions = {}
            
            # Get current weather conditions
            current_temp = weather_data['temperature'].iloc[-1] if 'temperature' in weather_data.columns else 20
            current_humidity = weather_data['humidity'].iloc[-1] if 'humidity' in weather_data.columns else 50
            current_pressure = weather_data['pressure'].iloc[-1] if 'pressure' in weather_data.columns else 1013
            current_wind = weather_data['wind_speed'].iloc[-1] if 'wind_speed' in weather_data.columns else 5
            current_visibility = weather_data['visibility'].iloc[-1] if 'visibility' in weather_data.columns else 10
            
            # Storm prediction based on atmospheric conditions
            storm_factors = []
            
            # Low pressure indicates storm potential
            if current_pressure < 1000:
                storm_factors.append(0.4)
            elif current_pressure < 1010:
                storm_factors.append(0.2)
            else:
                storm_factors.append(0.0)
            
            # High wind speed increases storm probability
            if current_wind > 15:
                storm_factors.append(0.3)
            elif current_wind > 10:
                storm_factors.append(0.15)
            else:
                storm_factors.append(0.0)
            
            # High humidity with other factors
            if current_humidity > 85:
                storm_factors.append(0.2)
            elif current_humidity > 70:
                storm_factors.append(0.1)
            else:
                storm_factors.append(0.0)
            
            # Low visibility indicates storm conditions
            if current_visibility < 5:
                storm_factors.append(0.2)
            elif current_visibility < 8:
                storm_factors.append(0.1)
            else:
                storm_factors.append(0.0)
            
            storm_probability = min(sum(storm_factors), 1.0)
            predictions['storm_probability'] = storm_probability
            predictions['storm_risk'] = 'High' if storm_probability > 0.7 else 'Medium' if storm_probability > 0.4 else 'Low'
            
            # Temperature prediction based on trends and pressure
            temp_change_factors = []
            
            # Pressure trend affects temperature
            if len(weather_data) > 1:
                pressure_trend = weather_data['pressure'].iloc[-1] - weather_data['pressure'].iloc[0]
                if pressure_trend > 5:  # Rising pressure - clearing weather
                    temp_change_factors.append(2)
                elif pressure_trend < -5:  # Falling pressure - incoming weather
                    temp_change_factors.append(-1)
                else:
                    temp_change_factors.append(0)
            else:
                temp_change_factors.append(0)
            
            # Time of day effect (simplified)
            current_hour = weather_data['datetime'].iloc[-1].hour if 'datetime' in weather_data.columns else 12
            if 6 <= current_hour <= 18:  # Daytime
                temp_change_factors.append(1)
            else:  # Nighttime
                temp_change_factors.append(-1)
            
            temp_change = sum(temp_change_factors)
            predictions['temperature_forecast'] = current_temp + temp_change
            predictions['temperature_change'] = 'Rising' if temp_change > 0 else 'Falling' if temp_change < 0 else 'Stable'
            
            # Precipitation prediction
            precip_factors = []
            
            # High humidity indicates precipitation potential
            if current_humidity > 80:
                precip_factors.append(0.4)
            elif current_humidity > 65:
                precip_factors.append(0.2)
            else:
                precip_factors.append(0.0)
            
            # Low pressure increases precipitation chance
            if current_pressure < 1005:
                precip_factors.append(0.3)
            elif current_pressure < 1013:
                precip_factors.append(0.15)
            else:
                precip_factors.append(0.0)
            
            # Wind speed can indicate incoming weather systems
            if current_wind > 12:
                precip_factors.append(0.2)
            elif current_wind > 8:
                precip_factors.append(0.1)
            else:
                precip_factors.append(0.0)
            
            # Temperature and humidity combination (dewpoint approximation)
            if current_temp < 10 and current_humidity > 75:
                precip_factors.append(0.2)  # Cold and humid - potential for precipitation
            
            precip_probability = min(sum(precip_factors), 1.0)
            predictions['precipitation_probability'] = precip_probability
            predictions['precipitation_likelihood'] = 'High' if precip_probability > 0.7 else 'Medium' if precip_probability > 0.4 else 'Low'
            
            # Generate weather alerts based on current conditions
            alerts = []
            
            if storm_probability > 0.7:
                alerts.append("High storm risk detected - Low pressure and strong winds")
            
            if precip_probability > 0.8:
                alerts.append("Heavy precipitation expected - High humidity and low pressure")
            
            if current_wind > 20:
                alerts.append("Strong wind conditions - Exercise caution outdoors")
            
            if current_visibility < 3:
                alerts.append("Poor visibility conditions - Fog or precipitation present")
            
            if current_temp < 0:
                alerts.append("Freezing temperatures - Risk of ice formation")
            elif current_temp > 35:
                alerts.append("Extreme heat conditions - Stay hydrated")
            
            if current_pressure < 995:
                alerts.append("Very low atmospheric pressure - Severe weather possible")
            
            predictions['alerts'] = alerts
            
            # Add confidence metrics
            predictions['prediction_confidence'] = {
                'storm': 'High' if len(weather_data) > 5 else 'Medium',
                'temperature': 'High' if 'pressure' in weather_data.columns else 'Medium',
                'precipitation': 'High' if current_humidity > 0 else 'Medium'
            }
            
            return predictions
            
        except Exception as e:
            return {"error": f"Real-time prediction failed: {str(e)}"}
    
    def get_feature_importance(self):
        """
        Get feature importance from trained models
        
        Returns:
            dict: Feature importance for each model
        """
        if not self.is_trained:
            return {"error": "Models not trained yet"}
        
        feature_names = [
            'temperature', 'humidity', 'pressure', 'wind_speed', 
            'wind_direction', 'visibility', 'hour', 'day_of_year', 'month'
        ]
        
        return {
            'storm_model': dict(zip(feature_names, self.storm_classifier.feature_importances_)),
            'temperature_model': dict(zip(feature_names, self.temp_regressor.feature_importances_)),
            'precipitation_model': dict(zip(feature_names, self.precip_classifier.feature_importances_))
        }
