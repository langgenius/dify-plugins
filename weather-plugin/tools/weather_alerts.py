from typing import Any, Union
import requests
from dify_plugin import Tool
from pydantic import BaseModel, Field


class WeatherAlertsInput(BaseModel):
    location: str = Field(..., description="Location coordinates (lat,lon) for weather alerts")


class WeatherAlertsTool(Tool):
    name: str = "weather_alerts"
    description: str = "Get weather alerts and warnings for a specific location"
    parameters: type[BaseModel] = WeatherAlertsInput

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[str, list, dict]:
        """
        Invoke the weather alerts tool
        """
        location = tool_parameters.get('location')
        
        if not location:
            return {'error': 'Location coordinates (lat,lon) are required'}

        # Get API key from runtime credentials
        api_key = self.runtime.credentials.get('openweathermap_api_key')
        if not api_key:
            return {'error': 'OpenWeatherMap API key not configured'}

        try:
            # Parse coordinates
            if ',' not in location:
                return {'error': 'Location must be in lat,lon format'}
            
            try:
                lat, lon = location.split(',')
                lat = float(lat.strip())
                lon = float(lon.strip())
            except ValueError:
                return {'error': 'Invalid coordinates format. Use: lat,lon'}

            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key
            }

            response = requests.get(
                'http://api.openweathermap.org/data/3.0/onecall',
                params=params,
                timeout=10
            )
            
            if response.status_code == 401:
                return {'error': 'Invalid API key or insufficient permissions for alerts'}
            elif response.status_code != 200:
                return {'error': f'Weather API error: {response.status_code}'}

            data = response.json()
            
            # Check for alerts
            alerts = data.get('alerts', [])
            
            if not alerts:
                return {
                    'location': f"Lat: {lat}, Lon: {lon}",
                    'alerts': [],
                    'message': 'No weather alerts for this location'
                }
            
            # Format alerts
            formatted_alerts = []
            for alert in alerts:
                formatted_alert = {
                    'event': alert.get('event', 'Unknown'),
                    'sender': alert.get('sender_name', 'Unknown'),
                    'start': alert.get('start'),
                    'end': alert.get('end'),
                    'description': alert.get('description', ''),
                    'tags': alert.get('tags', [])
                }
                formatted_alerts.append(formatted_alert)
            
            result = {
                'location': f"Lat: {lat}, Lon: {lon}",
                'alerts_count': len(formatted_alerts),
                'alerts': formatted_alerts
            }
            
            return result

        except requests.RequestException as e:
            return {'error': f'Failed to fetch weather alerts: {str(e)}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
