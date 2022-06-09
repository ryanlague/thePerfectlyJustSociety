
from pathlib import Path

# Third-Party
import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import plotly.graph_objects as go
import pandas as pd

# Custom
from coin_flip import CoinFlipper, Flips, Flip, History

# Import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Coin Flip"

# Start Data
flipper_path = Path('saved_flippers/people_1000_start_100_bet_10_debt_True_flips_1000.pickle')
flipper = CoinFlipper.load(flipper_path)

df_cache = flipper_path.parent.joinpath(f'{flipper_path.stem}_history.pickle')
df = pd.read_pickle(df_cache)

# Layout
app.layout = html.Div(id='parent', children=[
    html.H1(id='H1', children='Coin Flip',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

    dcc.Dropdown(id='dropdown',
                 options=[
                     {'label': 'Richest Person', 'value': 'max'},
                     {'label': 'Poorest Person', 'value': 'min'},
                     {'label': 'Average Person', 'value': 'mean'},
                     {'label': 'Total', 'value': 'total'},
                 ],
                 value='total'),
    dcc.Graph(id='bar_plot')
])


@app.callback(Output(component_id='bar_plot', component_property='figure'),
              [Input(component_id='dropdown', component_property='value')])
def graph_update(dropdown_value):
    x_key = 'numFlips'
    y_key = f'{dropdown_value}'
    for key in [x_key, y_key]:
        if key not in df.columns:
            raise Exception(f"{key} is not in df.columns. Columns are: {', '.join(df.columns)}")

    fig = go.Figure([go.Scatter(x=df[x_key], y=df[y_key],
                                line=dict(color='firebrick', width=4))
                     ])

    fig.update_layout(title=f"Person {dropdown_value}'s Money over time",
                      xaxis_title='Number of Flips',
                      yaxis_title='Money'
                      )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
