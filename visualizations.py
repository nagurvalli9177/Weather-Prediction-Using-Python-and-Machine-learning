import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class WeatherVisualizations:
    """Class for creating weather-related visualizations using Plotly"""
    
    def __init__(self):
        # Color scheme based on requirements
        self.colors = {
            'primary': '#1E3A8A',      # Deep blue
            'secondary': '#0EA5E9',    # Sky blue
            'accent': '#F59E0B',       # Sunny orange
            'background': '#F8FAFC',   # Light grey
            'text': '#1F2937',         # Dark grey
            'alert': '#EF4444',        # Storm red
            'success': '#10B981',      # Green
            'warning': '#F59E0B'       # Orange
        }
    
    def create_temperature_chart(self, forecast_df):
        """
        Create temperature trend chart
        
        Args:
            forecast_df (pd.DataFrame): Forecast data
            
        Returns:
            plotly.graph_objects.Figure: Temperature chart
        """
        if forecast_df.empty:
            # Return empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No temperature data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['text'])
            )
            fig.update_layout(
                title="Temperature Trends",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        try:
            fig = go.Figure()
            
            # Add temperature line
            fig.add_trace(go.Scatter(
                x=forecast_df['datetime'],
                y=forecast_df['temperature'],
                mode='lines+markers',
                name='Temperature',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=6, color=self.colors['primary']),
                hovertemplate='<b>%{x}</b><br>Temperature: %{y}°C<extra></extra>'
            ))
            
            # Add feels like temperature if available
            if 'feels_like' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['feels_like'],
                    mode='lines',
                    name='Feels Like',
                    line=dict(color=self.colors['secondary'], width=2, dash='dash'),
                    hovertemplate='<b>%{x}</b><br>Feels Like: %{y}°C<extra></extra>'
                ))
            
            # Add temperature range if min/max available
            if 'temp_min' in forecast_df.columns and 'temp_max' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['temp_max'],
                    mode='lines',
                    name='Max Temp',
                    line=dict(color=self.colors['accent'], width=1),
                    showlegend=False,
                    hovertemplate='<b>%{x}</b><br>Max: %{y}°C<extra></extra>'
                ))
                
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['temp_min'],
                    mode='lines',
                    name='Min Temp',
                    line=dict(color=self.colors['accent'], width=1),
                    fill='tonexty',
                    fillcolor=f'rgba(245, 158, 11, 0.1)',
                    showlegend=False,
                    hovertemplate='<b>%{x}</b><br>Min: %{y}°C<extra></extra>'
                ))
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="Temperature Trends",
                    font=dict(size=20, color=self.colors['text']),
                    x=0.5
                ),
                xaxis=dict(
                    title="Time",
                    color=self.colors['text'],
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                yaxis=dict(
                    title="Temperature (°C)",
                    color=self.colors['text'],
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            # Return error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating temperature chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['alert'])
            )
            fig.update_layout(
                title="Temperature Trends",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
    
    def create_precipitation_chart(self, forecast_df):
        """
        Create precipitation probability chart
        
        Args:
            forecast_df (pd.DataFrame): Forecast data
            
        Returns:
            plotly.graph_objects.Figure: Precipitation chart
        """
        if forecast_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No precipitation data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['text'])
            )
            fig.update_layout(
                title="Precipitation Forecast",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        try:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Precipitation Probability', 'Rainfall Amount'),
                vertical_spacing=0.15,
                row_heights=[0.6, 0.4]
            )
            
            # Precipitation probability
            if 'precipitation_probability' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['precipitation_probability'],
                    mode='lines+markers',
                    name='Precipitation %',
                    line=dict(color=self.colors['secondary'], width=3),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor=f'rgba(14, 165, 233, 0.2)',
                    hovertemplate='<b>%{x}</b><br>Precipitation: %{y}%<extra></extra>'
                ), row=1, col=1)
            
            # Rainfall amount
            if 'rain_3h' in forecast_df.columns:
                fig.add_trace(go.Bar(
                    x=forecast_df['datetime'],
                    y=forecast_df['rain_3h'],
                    name='Rain (mm)',
                    marker=dict(color=self.colors['primary']),
                    hovertemplate='<b>%{x}</b><br>Rain: %{y}mm<extra></extra>'
                ), row=2, col=1)
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text="Precipitation Forecast",
                    font=dict(size=20, color=self.colors['text']),
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update axes
            fig.update_xaxes(title_text="Time", color=self.colors['text'])
            fig.update_yaxes(title_text="Probability (%)", row=1, col=1, color=self.colors['text'])
            fig.update_yaxes(title_text="Rainfall (mm)", row=2, col=1, color=self.colors['text'])
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating precipitation chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['alert'])
            )
            fig.update_layout(
                title="Precipitation Forecast",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
    
    def create_weather_overview_chart(self, forecast_df):
        """
        Create comprehensive weather overview chart
        
        Args:
            forecast_df (pd.DataFrame): Forecast data
            
        Returns:
            plotly.graph_objects.Figure: Overview chart
        """
        if forecast_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No weather data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['text'])
            )
            return fig
        
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Temperature & Humidity', 'Pressure', 'Wind Speed', 'Cloud Cover'),
                specs=[[{"secondary_y": True}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]],
                vertical_spacing=0.1,
                horizontal_spacing=0.1
            )
            
            # Temperature and Humidity
            fig.add_trace(go.Scatter(
                x=forecast_df['datetime'],
                y=forecast_df['temperature'],
                name='Temperature (°C)',
                line=dict(color=self.colors['primary']),
                yaxis='y'
            ), row=1, col=1)
            
            if 'humidity' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['humidity'],
                    name='Humidity (%)',
                    line=dict(color=self.colors['secondary']),
                    yaxis='y2'
                ), row=1, col=1, secondary_y=True)
            
            # Pressure
            if 'pressure' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['pressure'],
                    name='Pressure (hPa)',
                    line=dict(color=self.colors['accent']),
                    showlegend=False
                ), row=1, col=2)
            
            # Wind Speed
            if 'wind_speed' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['wind_speed'],
                    name='Wind Speed (m/s)',
                    line=dict(color=self.colors['success']),
                    fill='tozeroy',
                    fillcolor=f'rgba(16, 185, 129, 0.2)',
                    showlegend=False
                ), row=2, col=1)
            
            # Cloud Cover
            if 'cloudiness' in forecast_df.columns:
                fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['cloudiness'],
                    name='Cloud Cover (%)',
                    line=dict(color=self.colors['text']),
                    fill='tozeroy',
                    fillcolor=f'rgba(31, 41, 55, 0.2)',
                    showlegend=False
                ), row=2, col=2)
            
            fig.update_layout(
                title=dict(
                    text="Weather Overview",
                    font=dict(size=20, color=self.colors['text']),
                    x=0.5
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=True,
                height=600
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating overview chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['alert'])
            )
            return fig
    
    def create_prediction_confidence_chart(self, predictions):
        """
        Create chart showing prediction confidence levels
        
        Args:
            predictions (dict): ML model predictions
            
        Returns:
            plotly.graph_objects.Figure: Confidence chart
        """
        if not predictions or 'error' in predictions:
            fig = go.Figure()
            error_msg = predictions.get('error', 'No prediction data available')
            fig.add_annotation(
                text=error_msg,
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['text'])
            )
            fig.update_layout(
                title="Prediction Confidence",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        try:
            # Extract confidence values
            categories = []
            values = []
            colors = []
            
            if 'storm_probability' in predictions:
                categories.append('Storm Risk')
                values.append(predictions['storm_probability'] * 100)
                colors.append(self.colors['alert'] if predictions['storm_probability'] > 0.7 else self.colors['warning'] if predictions['storm_probability'] > 0.4 else self.colors['success'])
            
            if 'precipitation_probability' in predictions:
                categories.append('Precipitation')
                values.append(predictions['precipitation_probability'] * 100)
                colors.append(self.colors['secondary'])
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker=dict(color=colors),
                    text=[f"{v:.1f}%" for v in values],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Probability: %{y:.1f}%<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Prediction Confidence",
                    font=dict(size=20, color=self.colors['text']),
                    x=0.5
                ),
                xaxis=dict(title="Weather Events", color=self.colors['text']),
                yaxis=dict(title="Probability (%)", color=self.colors['text'], range=[0, 100]),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating confidence chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=self.colors['alert'])
            )
            fig.update_layout(
                title="Prediction Confidence",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
