from typing import Any
from dify_plugin import ToolProvider
from tools.current_weather import CurrentWeatherTool
from tools.weather_forecast import WeatherForecastTool
from tools.weather_alerts import WeatherAlertsTool


class WeatherProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the weather provider
        """
        api_key = credentials.get('openweathermap_api_key')
        if not api_key:
            raise ValueError('OpenWeatherMap API key is required')
        
        # Test the API key by making a simple request
        import requests
        try:
            response = requests.get(
                f'http://api.openweathermap.org/data/2.5/weather',
                params={
                    'q': 'London',
                    'appid': api_key,
                    'units': 'metric'
                },
                timeout=10
            )
            if response.status_code == 401:
                raise ValueError('Invalid OpenWeatherMap API key')
            elif response.status_code != 200:
                raise ValueError('Failed to validate OpenWeatherMap API key')
        except requests.RequestException as e:
            raise ValueError(f'Failed to connect to OpenWeatherMap API: {str(e)}')

    def _get_tools(self) -> list:
        """
        Return available tools
        """
        return [
            CurrentWeatherTool,
            WeatherForecastTool,
            WeatherAlertsTool
        ]
