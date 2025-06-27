from typing import Any, Union
import requests
from dify_plugin import Tool
from pydantic import BaseModel, Field


class CurrentWeatherInput(BaseModel):
    location: str = Field(..., description="Location name (city, country) or coordinates (lat,lon)")
    units: str = Field(default="metric", description="Units for temperature (metric, imperial, kelvin)")


class CurrentWeatherTool(Tool):
    name: str = "current_weather"
    description: str = "Get current weather conditions for a specific location"
    parameters: type[BaseModel] = CurrentWeatherInput

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[str, list, dict]:
        """
        Invoke the current weather tool
        """
        location = tool_parameters.get('location')
        units = tool_parameters.get('units', 'metric')
        
        if not location:
            return {'error': 'Location is required'}

        # Get API key from runtime credentials
        api_key = self.runtime.credentials.get('openweathermap_api_key')
        if not api_key:
            return {'error': 'OpenWeatherMap API key not configured'}

        try:
            # Check if location is coordinates (lat,lon format)
            if ',' in location and len(location.split(',')) == 2:
                try:
                    lat, lon = location.split(',')
                    float(lat.strip())
                    float(lon.strip())
                    params = {
                        'lat': lat.strip(),
                        'lon': lon.strip(),
                        'appid': api_key,
                        'units': units
                    }
                except ValueError:
                    # Not valid coordinates, treat as city name
                    params = {
                        'q': location,
                        'appid': api_key,
                        'units': units
                    }
            else:
                params = {
                    'q': location,
                    'appid': api_key,
                    'units': units
                }

            response = requests.get(
                'http://api.openweathermap.org/data/2.5/weather',
                params=params,
                timeout=10
            )
            
            if response.status_code == 404:
                return {'error': f'Location "{location}" not found'}
            elif response.status_code != 200:
                return {'error': f'Weather API error: {response.status_code}'}

            data = response.json()
            
            # Format the response
            unit_symbol = '°C' if units == 'metric' else '°F' if units == 'imperial' else 'K'
            speed_unit = 'm/s' if units == 'metric' else 'mph' if units == 'imperial' else 'm/s'
            
            result = {
                'location': f"{data['name']}, {data['sys']['country']}",
                'temperature': f"{data['main']['temp']}{unit_symbol}",
                'feels_like': f"{data['main']['feels_like']}{unit_symbol}",
                'description': data['weather'][0]['description'].title(),
                'humidity': f"{data['main']['humidity']}%",
                'pressure': f"{data['main']['pressure']} hPa",
                'wind_speed': f"{data['wind']['speed']} {speed_unit}",
                'visibility': f"{data.get('visibility', 'N/A')} m" if 'visibility' in data else "N/A",
                'cloudiness': f"{data['clouds']['all']}%",
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
            
            if 'wind' in data and 'deg' in data['wind']:
                result['wind_direction'] = f"{data['wind']['deg']}°"
            
            return result

        except requests.RequestException as e:
            return {'error': f'Failed to fetch weather data: {str(e)}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
