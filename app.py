import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load dataset (replace this with your dataset loading code)
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSr2GZqDREbSXZ-U3GGH8ib-kC_ZKkUAuhtdSbRnuxJTcLsCl5gNvfli6SUyqHYnyF_3wa4qGLf6aeO/pub?output=csv'
df_airline = pd.read_csv(url)

# Helper function for geolocation parsing
def parse_lat_lon(geo_str):
    try:
        lat, lon = geo_str.strip("()").split(",")
        return float(lat), float(lon)
    except (ValueError, AttributeError):
        return None, None

# Data preparation for visualizations
yearly_data = df_airline.groupby(['Year']).agg({'fare': 'mean', 'passengers': 'sum', 'large_ms': 'mean'}).reset_index()
airline_yearly_data = df_airline.groupby(['Year', 'carrier_full']).agg({'fare': 'mean'}).reset_index()
market_data = df_airline.groupby(['Year', 'carrier_full']).agg({'large_ms': 'mean'}).reset_index()
route_data = df_airline.groupby(['city1', 'city2', 'Geocoded_City1', 'Geocoded_City2'])['passengers'].sum().reset_index()

route_data[['lat1', 'lon1']] = route_data['Geocoded_City1'].apply(lambda x: pd.Series(parse_lat_lon(x)))
route_data[['lat2', 'lon2']] = route_data['Geocoded_City2'].apply(lambda x: pd.Series(parse_lat_lon(x)))
route_data = route_data.dropna(subset=['lat1', 'lon1', 'lat2', 'lon2'])
top_5_routes = route_data.sort_values(by='passengers', ascending=False).head(5)

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.title = "Airline Market Analysis"

# App layout
app.layout = html.Div([
    html.H1("Airline Market Visualization Dashboard", style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs", value='tab1', children=[
        dcc.Tab(label='Yearly Fare Trend', value='tab1'),
        dcc.Tab(label='Average Fare by Airline', value='tab2'),
        dcc.Tab(label='Quarterly Fare Trends', value='tab3'),
        dcc.Tab(label='Yearly Market Share', value='tab4'),
        dcc.Tab(label='Quarterly Market Share by Airline', value='tab5'),
        dcc.Tab(label='Geographic Route Map', value='tab6'),
    ]),
    html.Div(id='tabs-content')
])

# Callback for rendering content
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'tab1':  # Yearly Fare Trend
        fig = px.line(
            yearly_data, x='Year', y='fare',
            title='Average Fare Over Time (Yearly)',
            labels={'fare': 'Average Fare ($)', 'Year': 'Year'}
        )
        fig.update_layout(hovermode="x unified")
        return dcc.Graph(figure=fig)

    elif tab == 'tab2':  # Average Fare by Airline
        fig = px.line(
            airline_yearly_data, x='Year', y='fare', color='carrier_full',
            title='Average Fare Over Time by Airline',
            labels={'fare': 'Average Fare ($)', 'Year': 'Year', 'carrier_full': 'Airline'}
        )

        # Add dropdown for filtering airlines
        dropdown_buttons = [{'label': 'All Airlines', 'method': 'update', 'args': [{'visible': [True] * len(fig.data)}]}]
        for i, airline in enumerate(airline_yearly_data['carrier_full'].unique()):
            visible = [False] * len(fig.data)
            visible[i] = True
            dropdown_buttons.append({'label': airline, 'method': 'update', 'args': [{'visible': visible}]})

        fig.update_layout(updatemenus=[{
            'buttons': dropdown_buttons,
            'direction': 'down',
            'showactive': True,
            'x': 1.0,
            'y': 1.15,
            'xanchor': 'left',
            'yanchor': 'top'
        }])
        return dcc.Graph(figure=fig)

    elif tab == 'tab3':  # Quarterly Fare Trends
        fig = px.line(
            df_airline, x='quarter', y='fare', color='Year',
            title='Quarterly Fare Trends (with Interpolation)',
            labels={'fare': 'Average Fare ($)', 'quarter': 'Quarter'}
        )
        fig.update_layout(hovermode="x unified")
        return dcc.Graph(figure=fig)


    elif tab == 'tab4':  # Yearly Market Share
        fig = px.bar(
            market_data, x='Year', y='large_ms', color='carrier_full',
            title='Market Share by Airline (Yearly)',
            labels={'large_ms': 'Market Share (%)', 'Year': 'Year', 'carrier_full': 'Airline'}
        )
        fig.update_layout(barmode='stack')
        return dcc.Graph(figure=fig)


    elif tab == 'tab5':  # Quarterly Market Share by Airline with Slider
        fig = go.Figure()

        # Group data by Year, quarter, and airline for quarterly market share
        quarterly_market_data = df_airline.groupby(['Year', 'quarter', 'carrier_full']).agg({'large_ms': 'mean'}).reset_index()

        # Create a list of unique airlines and assign each a color
        unique_airlines = quarterly_market_data['carrier_full'].unique()
        colors = px.colors.qualitative.Plotly  # Get a color palette from Plotly

        # Create a color map for each airline
        color_map = {airline: colors[i % len(colors)] for i, airline in enumerate(unique_airlines)}

        # Create traces for each airline in each year
        years = sorted(quarterly_market_data['Year'].unique())
        for year in years:
            data_for_year = quarterly_market_data[quarterly_market_data['Year'] == year]
            for airline in unique_airlines:
                airline_data = data_for_year[data_for_year['carrier_full'] == airline]
                fig.add_trace(go.Bar(
                    x=airline_data['quarter'],
                    y=airline_data['large_ms'],
                    name=f"{airline} ({year})",
                    marker=dict(color=color_map[airline]),
                    visible=False,  # All traces hidden initially
                    hovertemplate="Airline: %{text}<br>Market Share: %{y:.2f}%<extra></extra>",
                    text=[airline] * len(airline_data)  # To display airline name on hover
                ))

        # Set traces for the first year to be visible by default
        for i in range(len(unique_airlines)):
            fig.data[i].visible = True

        # Create slider steps for each year
        steps = []
        for i, year in enumerate(years):
            step = dict(
                method='update',
                label=str(year),
                args=[
                    {'visible': [((j // len(unique_airlines)) == i) for j in range(len(fig.data))]},  # Show traces for the selected year
                    {'title': f'Quarterly Market Share by Airline for {year}'}
                ]
            )
            steps.append(step)

        # Add the slider to the layout
        fig.update_layout(
            sliders=[{
                'active': 0,
                'currentvalue': {'prefix': 'Year: '},
                'pad': {'t': 50},
                'steps': steps
            }],
            title='Quarterly Market Share by Airline',
            xaxis_title='Quarter',
            yaxis_title='Market Share (%)',
            barmode='stack'
        )

        return dcc.Graph(figure=fig)



    elif tab == 'tab6':  # Geographic Route Map
        fig = go.Figure()
        for _, row in top_5_routes.iterrows():
            fig.add_trace(go.Scattergeo(
                locationmode='USA-states',
                lon=[row['lon1'], row['lon2']],
                lat=[row['lat1'], row['lat2']],
                mode='lines',
                name=f"{row['city1']} to {row['city2']}",
                line=dict(width=1, color="blue"),
                opacity=0.7
            ))
        fig.update_layout(
            title="Top 5 Routes by Passenger Volume",
            geo=dict(scope="usa", showland=True, landcolor="lightgrey")
        )
        return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
