from typing import Any, Union
import requests
from dify_plugin import Tool
from pydantic import BaseModel, Field


class WeatherForecastInput(BaseModel):
    location: str = Field(..., description="Location name (city, country) or coordinates (lat,lon)")
    days: int = Field(default=5, description="Number of days for forecast (1-5)")
    units: str = Field(default="metric", description="Units for temperature (metric, imperial, kelvin)")


class WeatherForecastTool(Tool):
    name: str = "weather_forecast"
    description: str = "Get weather forecast for a specific location"
    parameters: type[BaseModel] = WeatherForecastInput

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[str, list, dict]:
        """
        Invoke the weather forecast tool
        """
        location = tool_parameters.get('location')
        days = min(tool_parameters.get('days', 5), 5)  # API limit is 5 days
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
                        'units': units,
                        'cnt': days * 8  # 8 forecasts per day (every 3 hours)
                    }
                except ValueError:
                    # Not valid coordinates, treat as city name
                    params = {
                        'q': location,
                        'appid': api_key,
                        'units': units,
                        'cnt': days * 8
                    }
            else:
                params = {
                    'q': location,
                    'appid': api_key,
                    'units': units,
                    'cnt': days * 8
                }

            response = requests.get(
                'http://api.openweathermap.org/data/2.5/forecast',
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
            
            result = {
                'location': f"{data['city']['name']}, {data['city']['country']}",
                'forecast': []
            }
            
            # Group forecasts by day
            daily_forecasts = {}
            for item in data['list'][:days * 8]:
                date = item['dt_txt'].split(' ')[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            # Process each day
            for date, forecasts in list(daily_forecasts.items())[:days]:
                # Get min/max temperatures for the day
                temps = [f['main']['temp'] for f in forecasts]
                descriptions = [f['weather'][0]['description'] for f in forecasts]
                
                # Most common weather description
                most_common_desc = max(set(descriptions), key=descriptions.count)
                
                day_forecast = {
                    'date': date,
                    'min_temp': f"{min(temps)}{unit_symbol}",
                    'max_temp': f"{max(temps)}{unit_symbol}",
                    'description': most_common_desc.title(),
                    'humidity': f"{forecasts[0]['main']['humidity']}%",
                    'hourly_details': []
                }
                
                # Add hourly details
                for forecast in forecasts:
                    hourly = {
                        'time': forecast['dt_txt'].split(' ')[1],
                        'temperature': f"{forecast['main']['temp']}{unit_symbol}",
                        'description': forecast['weather'][0]['description'].title(),
                        'humidity': f"{forecast['main']['humidity']}%"
                    }
                    day_forecast['hourly_details'].append(hourly)
                
                result['forecast'].append(day_forecast)
            
            return result

        except requests.RequestException as e:
            return {'error': f'Failed to fetch weather forecast: {str(e)}'}
        except Exception as e:
            return {'error': f'An error occurred: {str(e)}'}
