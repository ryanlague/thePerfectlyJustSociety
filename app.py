
from pathlib import Path

# Third-Party
import dash
from dash.dependencies import Input, Output, State
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
flipper_path = Path('flipperCache/people_1000_start_100_bet_10_debt_True_flips_14000.pickle')
flipper = CoinFlipper.load(flipper_path)

df_cache = flipper_path.parent.joinpath(f'{flipper_path.stem}_history.pickle')
df: pd.DataFrame = pd.read_pickle(df_cache)


class DropdownOption:
    def __init__(self, label, value, yLabel='Money'):
        self.label = label
        self.value = value
        self.yLabel = yLabel

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.label}: {self.value}>"

    @property
    def dashDropdown(self):
        return {'label': self.label, 'value': self.value}


def getDropdownOptions():
    return [
        DropdownOption('Total', 'total'),
        DropdownOption('Richest Person', 'max'),
        DropdownOption('Top 1%', 'top_0_to_1_percent_wealth', 'Percent of Total Wealth'),
        DropdownOption('Bottom 1%', 'top_99_to_100_percent_wealth', 'Percent of Total Wealth'),
        DropdownOption('Average Person', 'mean'),
        DropdownOption('Poorest Person', 'min')
    ]


# Layout
app.layout = html.Div(id='parent', children=[
    html.H1(id='H1', children='Coin Flip',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

    html.Div(dcc.Input(id='input_on_submit', type='text', value='1'),
             style={'margin-bottom': '10px', 'margin-left': 'calc(50% - 110px)', 'width': '220px'}),
    html.Button('Flip A Coin', id='coin_flip_button', n_clicks=0,
                style={'margin-bottom': '10px', 'margin-left': 'calc(50% - 110px)', 'width': '220px'}),
    html.Div(id='coin_flip_confirmation',
             children='Enter a number of flips and press "Flip A Coin"',
             style={'margin-bottom': '10px', 'margin-left': 'calc(50% - 250px)', 'width': '500px', 'textAlign': 'center'}),
    dcc.Dropdown(id='dropdown',
                 options=[opt.dashDropdown for opt in getDropdownOptions()],
                 value='total'),
    dcc.Graph(id='bar_plot')
])


@app.callback(
    Output('coin_flip_confirmation', 'children'),
    Input('coin_flip_button', 'n_clicks'),
    State('input_on_submit', 'value')
)
def flipCoins(n_clicks, value):
    global df
    if n_clicks:
        try:
            val = int(value)
        except:
            return f'"{val} is not a number! Please enter a number of coins to flip"'

        # TODO: The flipper needs to happen on a cancellable thread
        print(f'NUMBER OF CLICKS: {n_clicks}')
        flipper.flip(val)
        df = flipper.history.getStatsOverTime(includeTopX=True)
        return f'Flipping {val} coins now...'


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
    selected_option = next((opt for opt in getDropdownOptions() if opt.value == dropdown_value))
    fig.update_layout(title=f"{selected_option.label}'s Money over time",
                      xaxis_title='Number of Flips',
                      yaxis_title=selected_option.yLabel
                      )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
