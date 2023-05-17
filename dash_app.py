import dash
from dash.dependencies import Input, Output
import pandas as pd
import requests
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash import dash_table as dt

# Set the API key and base URL.
API_KEY = "77d6491088262b92cec4ece652be428b"
API_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Create a Dash app.
app = dash.Dash(__name__)

# Add a custom CSS file.
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="/assets/custom.css">  <!-- Add this line -->
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Create the layout for the app.
app.layout = html.Div([
    # Add a title.
    html.H1("Weather App", className="title"),

    # Add a dropdown menu to select a city.
    dcc.Dropdown(
        id="city",
        options=[
            {
                "label": "London",
                "value": "London"
            },
            {
                "label": "New York",
                "value": "New York"
            },
            {
                "label": "Sydney",
                "value": "Sydney"
            }
        ],
        value="London",
        className="card"
    ),

    # Add a map to show the current weather in the selected city.
    dcc.Graph(id="weather-map", className="card"),

    # Add a table to show the weather forecast for the selected city.
    html.Div(dt.DataTable(id="weather-table"), className="card")
])

# Define a function to convert Kelvin to Celsius.
def kelvin_to_celsius(temp_k):
    return temp_k - 273.15

# Define a function to get the current weather data for a city.
def get_weather_data(city):
    url = f"{API_BASE_URL}/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['main'], data['coord']

# Define a function to get the weather forecast for a city.
def get_weather_forecast(city):
    url = f"{API_BASE_URL}/forecast?q={city}&appid={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['list']

# Create a callback to update the map when the city is changed.
@app.callback(
    Output("weather-map", "figure"),  
    Input("city", "value")
)
def update_weather_map(city):
    (data, coords) = get_weather_data(city)
    fig = go.Figure(
        data=go.Scattergeo(
            lon=[coords['lon']],
            lat=[coords['lat']],
            mode='markers',
            marker=dict(
                size=12,
                reversescale=True,
                autocolorscale=False,
                symbol='circle',
                line=dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale='Blues',
                cmin=0,
                color=data['temp'],
                cmax=data['temp'],
                colorbar_title="Temperature<br>°C"
            ),
            text=[f"{city}: {data['temp']}°C"],
        )
    )
    
    # Update the layout of the map when the city is changed.
    fig.update_layout(
        title_text=f'Current Temperature in {city}',
        geo=dict(
            showland=True,
            landcolor="rgb(217, 217, 217)",
            subunitcolor="rgb(217, 217, 217)",
            countrycolor="rgb(217, 217, 217)",
            showcountries=True,
            showlakes=True,
            lakecolor='rgba(127,205,255,0.8)',
            showsubunits=True,
            showocean=True,
            oceancolor='rgba(127,205,255,0.8)'
        )
    )

    return fig

# Create a callback to update the table when the city is changed.
@app.callback(
    Output("weather-table", "data"),
    Output("weather-table", "columns"),
    Output("weather-table", "style_data_conditional"),
    Input("city", "value")
)
def update_weather_table(city):
    data = get_weather_forecast(city)
    table = pd.DataFrame([
        {"Date": d["dt_txt"], "Temperature": kelvin_to_celsius(d["main"]["temp"]), "Weather": d["weather"][0]["description"]}
        for d in data
    ])
    columns = [{"name": i, "id": i} for i in table.columns]
    data = table.to_dict('records')

    style_data_conditional = [
        {
            'if': {
                'column_id': 'Temperature',
                'filter_query': '{Temperature} <= 0'
            },
            'backgroundColor': 'skyblue',
            'color': 'white'
        },
        {
            'if': {
                'column_id': 'Temperature',
                'filter_query': '{Temperature} > 0'
            },
            'backgroundColor': 'tomato',
            'color': 'white'
        }
    ]

    return data, columns, style_data_conditional

# Run the app.
if __name__ == '__main__':
    app.run_server(debug=True)
