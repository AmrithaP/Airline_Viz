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

# Create a list of unique airlines
unique_airlines = df_airline['carrier_full'].unique()

# Define a colorblind-friendly palette
color_palette = px.colors.qualitative.Safe  # Safe for colorblind users

# Map each airline to a color
global_color_map = {airline: color_palette[i % len(color_palette)] for i, airline in enumerate(unique_airlines)}

# App layout
app.layout = html.Div(
     style={
        'backgroundImage': 'url("https://i.pinimg.com/1200x/f5/af/38/f5af38611cd1bda1f68876a13bb6436e.jpg")',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'minHeight': '100vh',
        'padding': '20px',
    },
    children=[
    html.H1("Airline Market Visualization Dashboard",
            style={
                'textAlign': 'center',
                'color': 'white',
                'textShadow': '2px 2px 4px #000000',
            }),

    # Section 1
    html.Div([
        html.H2("Section 1: Default Visualizations",
                style={
                'textAlign': 'center',
                'color': 'white',
                'textShadow': '2px 2px 4px #000000',
            }),
        dcc.Tabs(id="section1-tabs", value='tab1', children=[
            dcc.Tab(label='Yearly Fare Trend', value='tab1'),
            dcc.Tab(label='Average Fare by Airline', value='tab2'),
            dcc.Tab(label='Quarterly Fare Trends', value='tab3'),
            dcc.Tab(label='Yearly Market Share', value='tab4'),
            dcc.Tab(label='Quarterly Market Share by Airline', value='tab5'),
            dcc.Tab(label='Geographic Route Map', value='tab6'),
        ]),
        html.Div(id='section1-tabs-content'),
    ],style={'backgroundColor': 'rgba(255, 255, 255, 0.8)', 'borderRadius': '10px', 'padding': '15px'}),

    # Section 2
    html.Div([
        html.H2("Section 2: Filtered Visualizations",
                style={
                'textAlign': 'center',
                'color': 'white',
                'textShadow': '2px 2px 4px #000000',
            }),
        html.Label("Select Airlines to Filter:"),
        dcc.Dropdown(
            id='airline-dropdown',
            options=[{'label': airline, 'value': airline} for airline in unique_airlines],
            multi=True,
            placeholder="Select one or more airlines",
        ),
        dcc.Tabs(id="section2-tabs", value='tab7', children=[
            dcc.Tab(label='Filtered Yearly Fare Trend', value='tab7'),
            dcc.Tab(label='Average Fare Per Airline (Separate Lines)', value='tab8'),
            dcc.Tab(label='Filtered Yearly Market Share', value='tab9'),

        ], style={'backgroundColor': 'rgba(255, 255, 255, 0.8)', 'borderRadius': '10px', 'padding': '15px'}),
        html.Div(id='section2-tabs-content'),
    ], style={'marginTop': '20px'}),

        # Footer
    html.Div([
        html.P(
            "Powered by Dash | Data Source: Airline Statistics - Kaggle | © Amritha Prakash. All rights reserved.",
            style={'textAlign': 'center', 'color': 'white'}
        ),
    html.A(
        "Kaltura Link: Watch Recording Here",
        href="https://indiana-my.sharepoint.com/:v:/g/personal/amriprak_iu_edu/Ed2CEn5E_5pDmxdqAlb63qkB6VeunUhBi-kuXesr0y0ipw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&e=jTosID",  
        style={
            'textAlign': 'center',
            'color': 'white',
            'textDecoration': 'underline',
            'display': 'block',
            'marginTop': '10px'
        },
        target="_blank"  # Opens the link in a new tab
    )
    ], style={'marginTop': '30px', 'padding': '10px', 'backgroundColor': '#0D47A1'})     
     
])

# Section 1: Callback for rendering default tabs content
@app.callback(
    Output('section1-tabs-content', 'children'),
    Input('section1-tabs', 'value')
)
def render_section1_content(tab):
    if tab == 'tab1':  # Yearly Fare Trend
        fig = px.line(
        yearly_data, x='Year', y='fare',
        title='Average Fare Over Time (Yearly)',
        labels={'fare': 'Average Fare ($)', 'Year': 'Year'}
        )

        # Add annotations for key events
        fig.add_annotation(x=2020, y=yearly_data[yearly_data['Year'] == 2020]['fare'].values[0],
                          text="COVID-19 Impact", showarrow=True, arrowhead=1)
        fig.add_annotation(x=2008, y=yearly_data[yearly_data['Year'] == 2008]['fare'].values[0],
                          text="2008 Financial Crisis", showarrow=True, arrowhead=1)

        # Update layout
        fig.update_layout(hovermode="x unified")

        # Contextual description
        context_info = html.Div([
            html.P("Key Events:"),
            html.Ul([
                html.Li("2008: Financial crisis resulted in fare adjustments and reduced travel demand."),
                html.Li("2020: COVID-19 pandemic led to a sharp decline in travel and significant fare disruptions."),
            ], style={'fontSize': '14px', 'lineHeight': '1.6'}),
        ], style={'marginTop': '20px'})

        fig.add_trace(
              go.Scatter(x=yearly_data['Year'],
                        y=yearly_data['fare'].rolling(window=3).mean(),
                        mode='lines', name='Trendline', line=dict(dash='dot', color='green'))
          )

        return html.Div([
            dcc.Graph(figure=fig),
            context_info
        ])


    elif tab == 'tab2':  # Average Fare by Airline
        fig = px.line(
        airline_yearly_data, x='Year', y='fare', color='carrier_full',
        title='Average Fare Over Time by Airline',
        labels={'fare': 'Average Fare ($)', 'Year': 'Year', 'carrier_full': 'Airline'},
        color_discrete_map=global_color_map  # Apply the global color map
        )
        # Add industry average line
        industry_avg = yearly_data[['Year', 'fare']].rename(columns={'fare': 'Industry Average Fare'})
        fig.add_trace(
            go.Scatter(x=industry_avg['Year'], y=industry_avg['Industry Average Fare'],
                      mode='lines', name='Industry Average', line=dict(dash='dash', color='black'))
        )

        # Dropdown for filtering airlines (unchanged)
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


        # Add contextual information as HTML
        context_info = html.Div([
            html.H5("General Insights on Airline Fare Trends:", style={'marginTop': '20px'}),
            html.Ul([
                html.Li("Industry-wide Trends: The black dashed line shows the average fare across all airlines. Airlines above the industry average may focus on premium services, while those below may emphasize cost-competitiveness."),
                html.Li("Low-Cost Carriers (LCCs): Certain airlines, such as Allegiant Air and Frontier Airlines, demonstrate fares significantly below the industry average, showcasing aggressive pricing strategies aimed at budget-conscious travelers."),
                html.Li("Premium Airlines: Airlines like Delta and American Airlines often stay above the industry average, highlighting their focus on premium services and corporate clients."),
                html.Li("Dynamic Trends: Noticeable shifts in fare trends often correlate with major industry events, such as economic downturns, fuel price volatility, or changes in consumer demand."),
                html.Li("Competitor Analysis: Use the dropdown to explore specific airlines' fare strategies and their deviation from the industry benchmark."),
            ], style={'fontSize': '14px', 'lineHeight': '1.6'}),
        ])

        return html.Div([
            dcc.Graph(figure=fig),
            context_info
        ])

    elif tab == 'tab3':  # Quarterly Fare Trends
        fig = px.line(
        df_airline, x='quarter', y='fare', color='Year',
        title='Quarterly Fare Trends (with Interpolation)',
        labels={'fare': 'Average Fare ($)', 'quarter': 'Quarter'},
        color_discrete_map=global_color_map  # Apply the global color map
        )
        # Add slider for years
        years = sorted(df_airline['Year'].unique())
        fig.update_layout(
            sliders=[{
                'active': 0,
                'currentvalue': {'prefix': 'Year: '},
                'pad': {'t': 50},
                'steps': [{'label': str(year), 'method': 'update', 'args': [{'visible': [year == yr for yr in years]}]} for year in years]
            }]
        )
        fig.update_layout(hovermode="x unified")

                # Add rolling average line for each year
        df_airline['rolling_fare'] = df_airline.groupby('Year')['fare'].transform(lambda x: x.rolling(window=2).mean())

        fig.add_trace(
            go.Scatter(
                x=df_airline['quarter'],
                y=df_airline['rolling_fare'],
                mode='lines',
                name='Trendline (Rolling Average)',
                line=dict(dash='dot', color='green')
            )
        )

        return html.Div([
              dcc.Graph(figure=fig),
              html.Div([
                  html.P("This visualization highlights fare trends across quarters, helping to identify seasonal patterns or anomalies in pricing."),
              ], style={'marginTop': '20px', 'fontSize': '14px', 'lineHeight': '1.6'}),
          ])


    elif tab == 'tab4':  # Yearly Market Share
        # Calculate total market share for each airline to determine the order
        airline_order = (
            market_data.groupby('carrier_full')['large_ms']
            .sum()
            .sort_values(ascending=False)
            .index
        )

        # Create the bar chart with sorted airlines
        fig = px.bar(
            market_data,
            x='Year',
            y='large_ms',
            color='carrier_full',
            category_orders={'carrier_full': list(airline_order)},  # Order airlines by total market share
            title='Market Share by Airline (Yearly)',
            labels={'large_ms': 'Market Share (%)', 'Year': 'Year', 'carrier_full': 'Airline'},
            color_discrete_map=global_color_map  # Apply the global color map
        )

        # Add annotations for specific years
        highlight_years = [1995, 2000, 2010, 2020]
        for year in highlight_years:
            year_data = market_data[market_data['Year'] == year]
            if not year_data.empty:
                # Get the airline with the largest market share for the year
                max_airline = year_data.loc[year_data['large_ms'].idxmax()]
                fig.add_annotation(
                    x=year,
                    y=max_airline['large_ms'] + 0.5,  # Position annotation slightly above the bar
                    text=f"Top Airline: {max_airline['carrier_full']}",
                    showarrow=False,  # No arrow for clean design
                    font=dict(size=12, color="black"),
                    bgcolor="rgba(255,255,255,0.7)",  # Semi-transparent background for readability
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=4
                )

        # Update layout
        fig.update_layout(
            barmode='stack',
            legend_title="Airlines",
            xaxis_title="Year",
            yaxis_title="Market Share (%)",
        )

        # Add contextual information as HTML
        context_info = html.Div([
            html.H5("Context for Highlighted Years:", style={'marginTop': '20px'}),
            html.Ul([
                html.Li("1995: This was a period when many legacy carriers (e.g., American Airlines, Delta) were consolidating their dominance, and deregulation impacts were still shaping the market."),
                html.Li("2000: The late 1990s to 2000 saw major changes in airline strategies, including increased competition and the rise of low-cost carriers."),
                html.Li("2010: The airline industry saw recovery from the 2008 financial crisis, coupled with significant mergers and acquisitions (e.g., United with Continental, Delta with Northwest)."),
                html.Li("2020: The COVID-19 pandemic dramatically disrupted the airline industry, with market shares shifting due to reduced passenger volumes, bankruptcies, and operational changes."),
            ], style={'fontSize': '14px', 'lineHeight': '1.6'}),
        ])

        return html.Div([
            dcc.Graph(figure=fig),
            context_info
        ])


    elif tab == 'tab5':  # Quarterly Market Share by Airline with Slider
        fig = go.Figure()

        # Use global color map
        color_map = global_color_map

        # Group data by Year, quarter, and airline for quarterly market share
        quarterly_market_data = df_airline.groupby(['Year', 'quarter', 'carrier_full']).agg({'large_ms': 'mean'}).reset_index()

        # Filter top 5 airlines based on cumulative market share
        top_5_airlines = quarterly_market_data.groupby('carrier_full')['large_ms'].sum().nlargest(5).index
        filtered_quarterly_data = quarterly_market_data[quarterly_market_data['carrier_full'].isin(top_5_airlines)]

        # Create a list of unique airlines and assign each a color
        unique_airlines = top_5_airlines  # Use only the top 5 airlines

        # Create traces for each airline in each year
        years = sorted(filtered_quarterly_data['Year'].unique())
        for year in years:
            data_for_year = filtered_quarterly_data[filtered_quarterly_data['Year'] == year]
            for airline in unique_airlines:
                airline_data = data_for_year[data_for_year['carrier_full'] == airline]
                fig.add_trace(go.Bar(
                    x=airline_data['quarter'],
                    y=airline_data['large_ms'],
                    name=f"{airline} ({year})",
                    marker=dict(color=color_map[airline]),  # Use global color map
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
            title='Quarterly Market Share by Airline (Top 5 Airlines)',
            xaxis_title='Quarter',
            yaxis_title='Market Share (%)',
            barmode='stack'
        )

        # Add trendline for the top airline
        top_airline = top_5_airlines[0]  # Select the top airline based on market share
        top_airline_data = filtered_quarterly_data[filtered_quarterly_data['carrier_full'] == top_airline]

        fig.add_trace(
            go.Scatter(
                x=top_airline_data['quarter'],
                y=top_airline_data['large_ms'].rolling(window=2).mean(),
                mode='lines',
                name=f'Trendline: {top_airline}',
                line=dict(dash='dot', color='red')
            )
        )

        return html.Div([
            dcc.Graph(figure=fig),
            html.Div([
                html.P("This chart provides insights into the market dynamics of the top 5 airlines over quarters, highlighting trends and competitive shifts."),
            ], style={'marginTop': '20px', 'fontSize': '14px', 'lineHeight': '1.6'}),
        ])



    elif tab == 'tab6':  # Geographic Route Map
        fig = go.Figure()

        # Add traces for top 5 routes with passenger volume determining line width
        for _, row in top_5_routes.iterrows():
            fig.add_trace(go.Scattergeo(
                locationmode='USA-states',
                lon=[row['lon1'], row['lon2']],
                lat=[row['lat1'], row['lat2']],
                mode='lines',
                name=f"{row['city1']} to {row['city2']}",
                line=dict(width=row['passengers'] / 100000,
                          color=f"rgba(0, 0, 255, {row['passengers'] / top_5_routes['passengers'].max()})"),  # Gradient color
                hoverinfo='text',
                text=f"Route: {row['city1']} to {row['city2']}<br>Passengers: {row['passengers']}"
            ))

        fig.update_layout(
            title="Top 5 Routes by Passenger Volume",
            geo=dict(scope="usa", showland=True, landcolor="lightgrey")
        )

        # Add contextual information as HTML
        context_info = html.Div([
            html.H5("Key Insights on Top Routes:", style={'marginTop': '20px'}),
            html.Ul([
                html.Li("Dominance of Key Metropolitan Areas: The visualization highlights the dominance of major metropolitan areas such as Los Angeles, New York City, Miami, and Chicago in passenger volume. These areas serve as major hubs for both domestic and international travel."),
                html.Li("Regional Connectivity: The route between Los Angeles and San Francisco emphasizes the high passenger volume on short-haul regional routes, driven by business travel and intercity commuting."),
                html.Li("Coastal Hubs: Routes connecting East Coast hubs (e.g., New York City and Miami) with West Coast hubs (e.g., Los Angeles and San Francisco) showcase the importance of cross-coastal connectivity."),
                html.Li("Leisure Travel Influence: The inclusion of routes such as New York City to Orlando highlights the impact of leisure destinations on passenger traffic."),
                html.Li("High-Frequency Routes: Routes like Los Angeles to New York City and Chicago to New York City indicate the importance of high-frequency corridors for business travelers and tourists."),
                html.Li("Opportunities for Expansion: Airlines can consider expanding services on similarly structured routes with high regional and intercity demand patterns."),
            ], style={'fontSize': '14px', 'lineHeight': '1.6'}),
        ])

        # Return the graph and context together
        return html.Div([
            dcc.Graph(figure=fig),
            context_info
        ])

    return html.Div("Content Not Available.")

# Section 2: Callback for filtered visualizations
@app.callback(
    Output('section2-tabs-content', 'children'),
    [Input('section2-tabs', 'value'), Input('airline-dropdown', 'value')]
)
def render_section2_content(tab, selected_airlines):
    if tab == 'tab7':  # Filtered Yearly Fare Trend
        filtered_data = df_airline[df_airline['carrier_full'].isin(selected_airlines)] if selected_airlines else df_airline
        yearly_filtered_data = filtered_data.groupby(['Year']).agg({'fare': 'mean'}).reset_index()
        fig = px.line(yearly_filtered_data, x='Year', y='fare', title='Filtered Average Fare Over Time (Yearly)',
                      labels={'fare': 'Average Fare ($)', 'Year': 'Year'},
                      color_discrete_map=global_color_map
                      )
        return html.Div([dcc.Graph(figure=fig)])

    elif tab == 'tab8':  # Average Fare Line Plot for Each Selected Airline
        # Filter data based on selected airlines
        filtered_data = df_airline[df_airline['carrier_full'].isin(selected_airlines)] if selected_airlines else df_airline
        yearly_filtered_data = filtered_data.groupby(['Year', 'carrier_full']).agg({'fare': 'mean'}).reset_index()

        # Create line plot for each selected airline
        fig = px.line(
            yearly_filtered_data,
            x='Year',
            y='fare',
            color='carrier_full',
            title='Average Fare by Airline (Separate Lines)',
            labels={'fare': 'Average Fare ($)', 'Year': 'Year', 'carrier_full': 'Airline'},
            color_discrete_map=global_color_map  # Apply consistent colors
        )

        # Update layout for clarity
        fig.update_layout(
            hovermode="x unified",  # Unified hover for better interaction
            title_x=0.5,  # Center the title
            legend_title="Airlines"
        )

        # Add contextual information as HTML
        context_info = html.Div([
            html.H5("Insights on Average Fare for Each Selected Airline:", style={'marginTop': '20px'}),
            html.Ul([
                html.Li("Separate Lines: Each line represents the average fare trend for a selected airline over time."),
                html.Li("Comparison: This visualization helps compare the pricing strategies of selected airlines."),
                html.Li("Insights: Identify consistent pricing patterns or unique fare fluctuations among airlines."),
            ], style={'fontSize': '14px', 'lineHeight': '1.6'}),
        ])

        return html.Div([
            dcc.Graph(figure=fig),
            context_info
        ])

    elif tab == 'tab9':  # Filtered Yearly Market Share
        filtered_data = market_data[market_data['carrier_full'].isin(selected_airlines)] if selected_airlines else market_data
        airline_order = (filtered_data.groupby('carrier_full')['large_ms'].sum().sort_values(ascending=False).index)
        fig = px.bar(filtered_data, x='Year', y='large_ms', color='carrier_full',
                     title='Filtered Yearly Market Share by Airline',
                     labels={'large_ms': 'Market Share (%)', 'Year': 'Year', 'carrier_full': 'Airline'},
                     color_discrete_map=global_color_map,
                     category_orders={'carrier_full': list(airline_order)})
        return html.Div([dcc.Graph(figure=fig)])

    return html.Div("Content Not Available.")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)



