import pytest
import responses
import json
from dash_app import get_weather_data, get_weather_forecast

@responses.activate
def test_get_weather_data():
    mock_response = {
        "main": {
            "temp": 280
        },
        "coord": {
            "lon": -0.13,
            "lat": 51.51
        }
    }
    responses.add(responses.GET, 'https://api.openweathermap.org/data/2.5/weather?q=London&appid=77d6491088262b92cec4ece652be428b',
                  json=mock_response, status=200)
    data, coords = get_weather_data("London")
    assert data == mock_response['main']
    assert coords == mock_response['coord']

@responses.activate
def test_get_weather_forecast():
    mock_response = {
        "list": [
            {
                "dt_txt": "2023-05-17 12:00:00",
                "main": {
                    "temp": 280
                },
                "weather": [
                    {
                        "description": "clear sky"
                    }
                ]
            }
        ]
    }
    responses.add(responses.GET, 'https://api.openweathermap.org/data/2.5/forecast?q=London&appid=77d6491088262b92cec4ece652be428b',
                  json=mock_response, status=200)
    data = get_weather_forecast("London")
    assert data == mock_response['list']
