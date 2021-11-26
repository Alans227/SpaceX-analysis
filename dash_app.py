# Import required libraries
import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['Count of fly'] = np.ones(len(spacex_df))

landing = []
for i in range(len(spacex_df)):
    if spacex_df['class'].iloc[i] == 1:
        landing.append('Success ')
    else:
        landing.append('Fail ')
spacex_df['Landing outcome'] = landing

max_payload = int(spacex_df['Payload Mass (kg)'].max() + 400)
min_payload = int(spacex_df['Payload Mass (kg)'].min())
launch_names = spacex_df.groupby(['Launch Site']).first().index


dropdown_launch_site = dcc.Dropdown(id='dropdown_ls',
                                    options=[
                                          {'label': launch_names[0], 'value': launch_names[0]},
                                          {'label': launch_names[1], 'value': launch_names[1]},
                                          {'label': launch_names[2], 'value': launch_names[2]},
                                          {'label': launch_names[3], 'value': launch_names[3]},
                                          {'label': 'ALL', 'value': 'ALL'}],
                                    value='ALL',
                                    clearable=False,
                                    searchable=False)

payload_slider_pl_mass = dcc.RangeSlider(id='payload-slider',
                                         min=min_payload,
                                         max=max_payload,
                                         step=100,
                                         marks={i: {'label': '{} kg'.format(i),
                                                    'style': {'width': '200px'}} for i in range(min_payload,
                                                                                                max_payload+1, 1000)},
                                         value=[min_payload, max_payload],
                                         allowCross=False,
                                         pushable=100
                                         )


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#0D1F2A', 'font-size': 40}),
                                html.Div('Launch Site:', style={'font-size': 20, 'margin': '0% 0% 0.2% 5%'}),
                                html.Div(dropdown_launch_site, style={'width': '16%', 'margin': '0% 0% 0% 5%'}),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart'), style={'width': '90%', 'margin': 'auto'}),
                                html.Div("Payload range:",
                                         style={'font-size': 20, 'textAlign': 'center', 'margin': '0% 5% 0.2% 5%'}),
                                html.Div(payload_slider_pl_mass, style={'width': '90%', 'margin': '0% 5% 0.2% 5%'}),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'),
                                         style={'width': '90%', 'margin': '0% 5% 0.2% 5%'}),
                                ]
                      )


#
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='dropdown_ls', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df.loc[spacex_df['Landing outcome'] == 'Success '],
                     names='Launch Site',
                     title='Total success launches by site')
    else:
        fig = px.pie(
            spacex_df.loc[spacex_df['Launch Site'] == entered_site],
            values='Count of fly',
            names='Landing outcome',
            title='Landing outcome of SpaceX',
            color_discrete_sequence=["#c716a9", "#24c0e3"]
        )
    return fig


@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(payload_range):
    scatter_data = spacex_df[(spacex_df['Payload Mass (kg)'] > payload_range[0]) &
                             (spacex_df['Payload Mass (kg)'] < payload_range[1])]
    fig = px.scatter(scatter_data, y="Landing outcome", x='Payload Mass (kg)',
                     title='Correlation between payload and landing outcome',
                     color="Booster Version Category")
    fig.update_traces(marker_size=7)
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
