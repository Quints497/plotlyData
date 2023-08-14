from plotly.data import carshare
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

px.set_mapbox_access_token(open(".mapbox_token").read())
df = carshare()
externalStylesheet = [dbc.themes.CERULEAN]

# values
peakHourMin = df['peak_hour'].min()
peakHourMax = df['peak_hour'].max()

app = Dash(__name__, external_stylesheets=externalStylesheet)

app.layout = dbc.Container(
    [
        # Provide a title for the dashboard
        dbc.Row(children=
                [
                    html.H1(children="Car-sharing services in Montreal over a month-long period",
                            className='text-primary text-center')
                ], className='p-3'
        ),

        # Display a snippet of the data being used
        dbc.Row(children=
                [
                    dbc.Table.from_dataframe(df.head(5), index=True, hover=True, bordered=True, color='info')
                ], className='p-3'
        ),

        # Interactive slider to change the peak hours
        dcc.RangeSlider(min=peakHourMin,
                        max=peakHourMax,
                        step=1,
                        value=[peakHourMin, peakHourMax],
                        tooltip={'placement': 'bottom', 'always_visible': True},
                        id='slider'),

        # Display a graph of the geographical locations
        dbc.Row(children=
                [
                    dcc.Graph(figure={}, id='scatter'),
                    html.Div(id='shown-info', className='center')
                ],
        ),


    ], className='p-5'
)

@callback(
    Output(component_id='scatter', component_property='figure'),
    Output(component_id='shown-info', component_property='children'),
    Input(component_id='slider', component_property='value')
)
def update_colour(value):
    valueRange = [x for x in range(value[0], value[1]+1)]
    filteredDf = df[df['peak_hour'].isin(valueRange)]

    fig = px.scatter_mapbox(filteredDf,
                            lat='centroid_lat',
                            lon='centroid_lon',
                            color='peak_hour',
                            size='car_hours',
                            mapbox_style='dark',
                            color_continuous_scale=px.colors.sequential.Inferno_r,
                            size_max=13,
                            zoom=9.5
                            ).update_traces(
                                hoverlabel_bgcolor='blue'
                            ).update_layout(
                                title=f"Car sharing between the hours of {value[0]}:00 & {value[1]}:00",
                                title_x=0.5,
                           )

    carInfo = pd.DataFrame({
            "Metric": ["Number of Cars", "Total hours", "Average hours"],
            "Value": [len(filteredDf), filteredDf['car_hours'].sum(), filteredDf['car_hours'].mean()]
    })

    table = dbc.Table.from_dataframe(carInfo,
                                     striped=True,
                                     bordered=True,
                                     hover=True,
                                     style={'padding': '0.25rem', 'lineHeight': '1.1', 'text-align': 'center', 'vertical-align': 'center'})
    return fig, table

if __name__ == '__main__':
    app.run(debug=True)