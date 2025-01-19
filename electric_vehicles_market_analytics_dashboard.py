import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit

# Load the data
df = pd.read_csv('Electric_Vehicle_Population_Data.csv')
df.dropna(inplace=True)

# Data preparation
ev_adoption_by_year = df['Model Year'].value_counts().sort_index()
ev_type_distribution = df['Electric Vehicle Type'].value_counts()
ev_make_distribution = df['Make'].value_counts().head(10)

# Geographical distribution
ev_county_distribution = df['County'].value_counts()
top_counties = ev_county_distribution.head(3).index
top_counties_data = df[df['County'].isin(top_counties)]
ev_city_distribution_top_counties = top_counties_data.groupby(['County', 'City']).size().sort_values(ascending=False).reset_index(name='Number of Vehicles')

# Top manufacturers and popular models
top_3_makes = ev_make_distribution.head(3).index
top_makes_data = df[df['Make'].isin(top_3_makes)]
ev_model_distribution_top_makes = top_makes_data.groupby(['Make', 'Model']).size().sort_values(ascending=False).reset_index(name='Number of Vehicles')

# Electric range analysis
average_range_by_year = df.groupby('Model Year')['Electric Range'].mean().reset_index()
average_range_by_model = top_makes_data.groupby(['Make', 'Model'])['Electric Range'].mean().sort_values(ascending=False).reset_index()
top_range_models = average_range_by_model.head(10)

# Forecasting EV registrations
ev_registration_counts = df['Model Year'].value_counts().sort_index()
filtered_years = ev_registration_counts[ev_registration_counts.index <= 2023]

def exp_growth(x, a, b):
    return a * np.exp(b * x)

x_data = filtered_years.index - filtered_years.index.min()
y_data = filtered_years.values
params, _ = curve_fit(exp_growth, x_data, y_data)
forecast_years = np.arange(2024, 2024 + 6) - filtered_years.index.min()
forecasted_values = exp_growth(forecast_years, *params)
forecasted_evs = dict(zip(forecast_years + filtered_years.index.min(), forecasted_values))

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Electric Vehicles Market Size Analysis Dashboard", style={'textAlign': 'center'}),
    
    dcc.Tabs([
        dcc.Tab(label='EV Adoption Over Time', children=[
            dcc.Graph(
                figure=px.bar(x=ev_adoption_by_year.index, y=ev_adoption_by_year.values,
                              labels={'x': 'Model Year', 'y': 'Number of Vehicles'},
                              title='EV Adoption Over Time',
                              color=ev_adoption_by_year.values,  
                              color_continuous_scale='viridis'  
                              ).update_layout(coloraxis_showscale=False) 
            )
        ]),
        dcc.Tab(label='EV Type Distribution', children=[
            dcc.Graph(
                figure=px.bar(x=ev_type_distribution.values, y=ev_type_distribution.index,
                              orientation='h',
                              labels={'x': 'Number of Vehicles', 'y': 'Electric Vehicle Type'},
                              title='Distribution of Electric Vehicle Types',
                              color=ev_type_distribution.values,
                              color_continuous_scale='RdBu'  
                              ).update_layout(coloraxis_showscale=False)
            )
        ]),
        dcc.Tab(label='Top EV Manufacturers', children=[
            dcc.Graph(
                figure=px.bar(x=ev_make_distribution.values, 
                    y=ev_make_distribution.index,
                    orientation='h',
                    labels={'x': 'Number of Vehicles', 'y': 'Make'},
                    title='Top 10 Popular EV Makes',
                    color=ev_make_distribution.index,
                    color_discrete_sequence=px.colors.qualitative.Antique)
            )
        ]),
        dcc.Tab(label='Geographical Distribution', children=[
            dcc.Graph(
                figure=px.bar(ev_city_distribution_top_counties.head(10),
                              x='Number of Vehicles', y='City', color='County',
                              orientation='h',
                              title='Top Cities in Top Counties by EV Registrations',
                              labels={'City': 'City', 'Number of Vehicles': 'Number of Vehicles'},
                              color_discrete_sequence=px.colors.qualitative.Prism)
            )
        ]),
        dcc.Tab(label='Popular Models in Top Makes', children=[
            dcc.Graph(
                figure=px.bar(ev_model_distribution_top_makes.head(10),
                              x='Number of Vehicles', y='Model', color='Make',
                              orientation='h',
                              title='Top Models in Top 3 Makes by EV Registrations',
                              labels={'Model': 'Model', 'Number of Vehicles': 'Number of Vehicles'},
                              color_discrete_sequence=px.colors.qualitative.Set2)
            )
        ]),
        dcc.Tab(label='Electric Range Distribution', children=[
            dcc.Graph(
                figure=px.histogram(df, x='Electric Range', nbins=30,
                                    title='Distribution of Electric Vehicle Ranges',
                                    labels={'Electric Range': 'Electric Range (miles)', 'count': 'Number of Vehicles'})
                .add_vline(x=df['Electric Range'].mean(), line_dash="dash", line_color="red",
                           annotation_text=f"Mean: {df['Electric Range'].mean():.2f} miles")
            )
        ]),
        dcc.Tab(label='Top Models by Average Electric Range', children=[
            dcc.Graph(
                figure=px.bar(top_range_models,
                              x='Electric Range', y='Model', color='Make',
                              orientation='h',
                              title='Top 10 Models by Average Electric Range in Top Makes',
                              labels={'Electric Range': 'Average Electric Range (miles)', 'Model': 'Model'},
                              color_discrete_sequence=px.colors.qualitative.Vivid)
            )
        ]),
        dcc.Tab(label='Market Forecast', children=[
            dcc.Graph(
                figure=go.Figure()
                .add_trace(go.Scatter(x=filtered_years.index, y=filtered_years.values,
                                      mode='lines+markers', name='Actual'))
                .add_trace(go.Scatter(x=list(forecasted_evs.keys()), y=list(forecasted_evs.values()),
                                      mode='lines+markers', name='Forecasted'))
                .update_layout(title='EV Market Forecast',
                               xaxis_title='Year', yaxis_title='Number of Vehicles')
            )
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
