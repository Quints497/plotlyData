from plotly.data import election, election_geojson
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

px.set_mapbox_access_token(open(".mapbox_token").read())
df = election()
externalStylesheet = [dbc.themes.CERULEAN]

# info
names = df['winner'].unique()
totalVotes = df['total'].sum()
coderreTotal = df['Coderre'].sum()
bergeronTotal = df['Bergeron'].sum()
jolyTotal = df['Joly'].sum()
newDf = pd.melt(df, id_vars=['district_id'], value_vars=['Coderre', 'Bergeron', 'Joly'], var_name='Candidate', value_name='Votes')


totalDf = pd.DataFrame(data=[coderreTotal, bergeronTotal, jolyTotal], index=names, columns=['Votes'])

app = Dash(__name__, external_stylesheets=externalStylesheet)
app.layout = dbc.Container(
    [
        # Provide a title for the dashboard
        dbc.Row(children=
                [
                    html.H1(children="Voting results for an electoral district in Montreal 2013 mayoral election",
                            className='text-primary text-center')
                ], className='p-3'
        ),

        dbc.Row(children=
                [
                    dash_table.DataTable(data=df.to_dict('records'),
                                         page_size=10,
                                         id='data-table',
                                         row_selectable='single',
                                         selected_rows=[])
                ]
        ),


        dcc.Graph(figure={},
                  id='bar-graph',
                  config={'displayModeBar': False},
                  ),



        dbc.Row(children=
                [
                    dbc.RadioItems(options=[{'label': x, 'value': x} for x in names],
                                   value='Joly',
                                   inline=True,
                                   id='radio-buttons',
                                   className='text-secondary text-center'),

                    # select a name to get all their votes per district
                    dcc.Graph(figure={},
                              id='candidate-graph',
                              config={'displayModeBar': False}
                              ),
                ]),

        dcc.Graph(figure=px.pie(totalDf,
                                values='Votes',  # Use the index of the DataFrame
                                names=totalDf.index,  # Use the index values as names
                                hole=0.1,
                                # hover_name=totalDf.index,
                                # hover_data={'index': False,
                                #             'Votes': True}
                                ).update_traces(
                                    marker=dict(colors=px.colors.qualitative.Safe),
                                    pull=[0.05, 0, 0],
                                    textposition='inside',
                                    textinfo='label+percent',
                                    insidetextfont=dict(color='black'),
                                    hoverinfo='skip',
                                    hovertemplate='%{label}<br><br>Votes: %{value}',
                                    hoverlabel=dict(
                                        bgcolor='grey',
                                        font_size=16,
                                        font_family='Rockwell',
                                        font_color='white'
                                    )
                                ).update_layout(
                                ),
                  config={'displayModeBar': False}
                  ),
        dbc.Row(
            children=[
                dbc.RadioItems(
                    options=[
                        {'label': result, 'value': result} for result in df['result'].unique()
                    ],
                    value='plurality',
                    inline=True,
                    id='result-radio-buttons',
                    className='text-secondary text-center'
                )
            ],
            className='mx-auto'
        ),

        dcc.Graph(
            id='result-heatmap',  # Assign an ID to the graph
            config={'displayModeBar': False}
        ),

        dcc.Graph(
            figure=px.imshow(
                newDf.pivot_table(values='Votes', index='Candidate', columns=['district_id'], fill_value=None),
                color_continuous_scale='Viridis',  # Choose a color scale
                title='Votes Heatmap by Candidate and District ID',
            ).update_layout(
                coloraxis_colorbar=dict(title='Votes')
            ).update_traces(
                hovertemplate='Candidate: %{y}<br>District ID: %{x}<br>Votes: %{z}'
            ),
            config={'displayModeBar': False},
            className='mx-auto'
        ),

        dcc.Graph(figure=px.imshow(df.pivot_table(values='total', index='winner', columns='district_id'),
                                   color_continuous_scale='Viridis',
            ).update_layout(
                coloraxis_colorbar=dict(title='Total Votes'),
                title='Total Votes Heatmap by Winner',
                title_x=0.5,
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
            ).update_traces(
                hovertemplate='District ID: %{x}<br><br>Total Votes: %{z}'
            ),
            config={'displayModeBar': False},
            className='mx-auto'
        ),
    ]
)
@callback(
    Output('result-heatmap', 'figure'),  # Use the new graph ID as the Output
    [Input('result-radio-buttons', 'value')]  # Use radio button value as input
)
def update_result_heatmap(selected_result):
    filtered_df = df[df['result'] == selected_result]  # Filter DataFrame based on selected 'result'

    reshaped_df = pd.melt(filtered_df, id_vars=['district_id'], value_vars=['Coderre', 'Bergeron', 'Joly'],
                          var_name='Candidate', value_name='Votes')

    heatmap_fig = px.imshow(
        reshaped_df.pivot_table(values='Votes', index='Candidate', columns='district_id', fill_value=0),
        color_continuous_scale='Viridis',  # Choose a color scale
        title=f'Votes Heatmap by Candidate and District ID for Result: {selected_result}',
    ).update_layout(
        xaxis_title='District ID',  # Set x-axis title
        yaxis_title='Candidate',  # Set y-axis title
        coloraxis_colorbar=dict(title='Votes')
    ).update_traces(
        hovertemplate='Candidate: %{y}<br>District ID: %{x}<br>Votes: %{z}'
    )

    return heatmap_fig
@callback(
    Output('candidate-graph', 'figure'),
    Input('radio-buttons', 'value')
)
def update_candidate_graph(candidate):
    values = df[candidate]
    fig = px.bar(df, x='district_id', y=values, color='winner')

    return fig


@callback(
    Output('bar-graph', 'figure'),
    Input('data-table', 'selected_rows')
)
def update_bar_graph(selected_row_indices):
    if selected_row_indices:
        selected_district = df.iloc[selected_row_indices[0]]
        values = [selected_district[name] for name in names]

        bar_fig = px.bar(
            x=names,
            y=values,
            labels={'x': 'Candidates', 'y': 'Votes'},
            title='Votes for Candidates in Selected District',
        ).update_layout(
            xaxis=dict(showgrid=False),  # Hide x-axis grid
            yaxis=dict(showgrid=False),  # Hide y-axis grid
            title_x=0.5,
            title_y=0.95,
            bargap=0.30,
            margin=dict(autoexpand=True),  # Adjust margins
            template='plotly',  # Use the "plotly" template
            paper_bgcolor='rgba(0,0,0,0)',  # Make paper background transparent
        )

        return bar_fig
    else:
        return {'data': []}  # Return an empty graph if no row is selected

if __name__ == '__main__':
    app.run(debug=True)
