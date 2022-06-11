# Built-In Python
import shutil
import uuid
from pathlib import Path

# Third-Party
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.long_callback import DiskcacheLongCallbackManager
import plotly.graph_objects as go
import diskcache

# Custom
from coin_flip import CoinFlipper, Flips, Flip, History
from population import Population
from pollableThread import StoppableThread, PollableCoinFlipper
from impz_logger.decorators import profile


# Global variable (fix this)
FLIPPER_PATH = Path('flipperCache/session_xyz/THE_BEST_FLIPPER.pickle')
INCLUDE_TOP_X = [0,  99]


class DropdownOption:
    def __init__(self, label, _id, xLabel='Number of Flips', xKey='numFlips', yLabel='Money', yKey=None,
                 title=None):
        self.label = label
        self.id = _id
        self.xLabel = xLabel
        self.xKey = xKey
        self.yLabel = yLabel
        self.yKey = yKey or _id  # To avoid typing things twice, just set the id to what we want the yKey to be
        self.title = title

    def __repr__(self):
        return f"<{self.__class__.__name__} | {self.label}: {self.id}>"

    @property
    def dashDropdown(self):
        return {'label': self.label, 'value': self.id}

    @classmethod
    def getById(cls, _id, opts=None):
        opts = opts or cls.getWealthDistributionOptions() + cls.getHistoryOptions()
        return next((opt for opt in opts if opt.id == _id))

    @classmethod
    def getWealthDistributionOptions(cls):
        return [
            cls('Money Per Percent', 'percent_wealth', xLabel='Wealth Percentile', xKey='top_x_percent_low',
                yLabel='Percent of Total Wealth', yKey='percent_wealth'),
            # cls('Money Per Person', 'money', xLabel='People (sorted by wealth)', xKey='rank_by_money',
            #     yLabel='Money', yKey='money'),
        ]

    @classmethod
    def getHistoryOptions(cls):
        return [
            cls('Top 1%', 'top_0_to_1_percent_wealth', yLabel='Percent of Total Wealth'),
            cls('Bottom 1%', 'top_99_to_100_percent_wealth', yLabel='Percent of Total Wealth'),
            cls('Richest Person', 'max'),
            cls('Poorest Person', 'min'),
            cls('Total', 'total'),
            cls('Average Person', 'mean'),
        ]


class Flipper:
    @classmethod
    def get(cls, filepath):
        filepath = Path(filepath)
        if filepath.exists():
            flipper = CoinFlipper.load(filepath)
        else:
            population = Population()
            population.add(1000, startMoney=100)
            flipper = CoinFlipper(population, dollarsPerFlip=10, allowDebt=True, selectionStyle='random')
            flipper.save(filepath, includeTopX=INCLUDE_TOP_X)
        return flipper

    @classmethod
    def save(cls, coinFlipper, filepath):
        filepath = filepath or coinFlipper.descriptiveFilepath(coinFlipper.cacheDir)
        coinFlipper.save(filepath)
        history = coinFlipper.history.getStatsOverTime(includeTopX=True)
        history.to_pickle(filepath.with_stem(f"{filepath.stem}_history"))


class Style:
    @classmethod
    def text(cls, textAlign='center', marginTop='0px', marginRight='0px', marginBottom='10px',
             marginLeft='calc(50% - 110px)', width='220px', **kwargs):
        BASE_STYLE = {
            'text-align': textAlign,
            'margin-top': marginTop, 'margin-right': marginRight,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width
        }
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def button(cls, textAlign='center', marginBottom='10px', marginLeft='calc(50% - 110px)', width='220px', **kwargs):
        BASE_STYLE = {
            'text-align': textAlign,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width
        }
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def cancel(cls, **kwargs):
        BASE_STYLE = {'font-size': '18px', 'padding': '5px', 'margin': '0', 'margin-bot': '10', 'text-align': 'left',
                      'line-height': '100%', 'vertical-align': 'center', 'border': 'none'}
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def dropdown(cls, **kwargs):
        BASE_STYLE = {'margin': 0, 'padding': 0}
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def graph(cls, **kwargs):
        BASE_STYLE = {'margin': 0, 'padding': 0, 'margin-top': '0px'}
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style


# # # MAIN APP # # #


# Disk Cache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, long_callback_manager=long_callback_manager)
app.title = "Coin Flip"

# Layout
app.layout = html.Div(id='parent', children=[

    html.H1(id='H1', children='Coin Flip',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

    html.Div(
        id='parameter-section',
        style={'height': '225px'},
        children=[
            html.Div(
                dcc.Input(id='num_flips_text_input', type='number', value='1', style={'text-align': 'center'}),
                style=Style.button()
            ),
            html.Div(id='buttons',
                     children=[
                         html.Button('Flip A Coin', id='coin_flip_button', n_clicks=0, disabled=False,
                                     style=Style.button()),
                         html.Button('Reset', id='reset_button', n_clicks=0, disabled=False,
                                     style=Style.button()),
                     ]
                     ),
            html.Div(id='progress_div',
                     style={'height': '40px', 'line-height': '40px', 'display': 'flex', 'align-items': 'center'},
                     children=[
                         html.Progress(id="progress_bar", hidden=False,
                                       style=Style.button(marginBottom='auto', marginTop='auto')),
                         html.Button(
                             html.I(id='cancel_button_icon', n_clicks=0, className='fa fa-times'),
                             id='cancel_button',
                             style=Style.cancel(),
                         )
                         ,
                     ]),
            html.Div(id='coin_flip_confirmation_text', children='Enter a number of flips and press "Flip A Coin"',
                     style=Style.text(marginLeft='calc(50% - 250px)', width='500px', marginTop='-30px')),
        ]),
    html.Div(
        id='graph_section',
        children=[

            # Graph: Wealth Distribution
            html.H2(id='wealth_distribution_title', children='Wealth Distribution',
                    style={'textAlign': 'center', 'marginTop': 0, 'marginBottom': 0}),
            dcc.Dropdown(
                id='wealth_distribution_dropdown',
                options=[opt.dashDropdown for opt in DropdownOption.getWealthDistributionOptions()],
                value=DropdownOption.getWealthDistributionOptions()[0].id,
                style=Style.dropdown()
            ),
            dcc.Graph(
                id='wealth_distribution_plot',
                style=Style.graph()
            ),

            # GRAPH: Flip History
            html.H2(id='flip_history_title', children='Flip History',
                    style={'textAlign': 'center', 'marginTop': 0, 'marginBottom': 0}),
            dcc.Dropdown(
                id='flip_history_dropdown',
                options=[opt.dashDropdown for opt in DropdownOption.getHistoryOptions()],
                value=DropdownOption.getHistoryOptions()[0].id,
                style=Style.dropdown()
            ),
            dcc.Graph(
                id='flip_history_plot',
                style=Style.graph()
            )
        ]
    )
])


@app.long_callback(
    [
        Output(component_id='wealth_distribution_plot', component_property='figure'),
        Output(component_id='flip_history_plot', component_property='figure'),
        Output('coin_flip_confirmation_text', 'children')
    ],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    inputs=[
        Input(component_id='wealth_distribution_dropdown', component_property='value'),
        Input(component_id='flip_history_dropdown', component_property='value'),
        Input('coin_flip_button', 'n_clicks'),
        State('num_flips_text_input', 'value'),
        Input('reset_button', 'n_clicks'),
    ],
    running=[
        (Output("num_flips_text_input", "disabled"), True, False),
        (Output("coin_flip_button", "disabled"), True, False),
        (Output("reset_button", "disabled"), True, False),
        (Output("flip_history_dropdown", "disabled"), True, False),
        (Output("wealth_distribution_dropdown", "disabled"), True, False),
        (Output("cancel_button", "style"), Style.cancel(), Style.cancel(visibility='hidden')),
        (Output("coin_flip_confirmation_text", "hidden"), True, False),
        (Output("progress_bar", "hidden"), False, True),
    ],
    cancel=[Input("cancel_button", "n_clicks")]
)
@profile()
def update(set_progress, wealth_distribution_dropdown_value, history_dropdown_value, numCoinFlipClicks,
           num_flips, numResetClicks):

    flipper = None
    if ctx.triggered_id == 'coin_flip_button':  # Flip a coin some number of times
        # This is updated at an interval specified in PollableCoinFlipper(progressEvery=num_flips)
        def progress_callback(progressRatio):
            set_progress((str(int(progressRatio * 100)), str(100)))

        # Update the progress to 0
        progress_callback(0.0)
        # The most recent flipper
        flipper_path = FLIPPER_PATH
        flipper = Flipper.get(flipper_path)
        # In-Progress flips will be saved to this path, so if the process is cancelled,
        # the previous flipper is not corrupted
        in_progress_dir = FLIPPER_PATH.parent.joinpath('tmp')
        in_progress_path = in_progress_dir.joinpath(f'{FLIPPER_PATH.stem}_tmp_{uuid.uuid4()}{FLIPPER_PATH.suffix}')
        # A Pollable / Stoppable Thread
        save_every = (int(num_flips) // 10) or 1
        thread = PollableCoinFlipper(flipper=flipper, flipperPath=in_progress_path,
                                     numFlips=num_flips, progressEvery=1, saveEvery=save_every,
                                     saveTopX=INCLUDE_TOP_X)
        thread.start()
        # Regularly poll the thread and update the progress bar
        thread.pollEvery(0.5, progress_callback, pollAtStart=True)
        # The newly updated flipper
        flipper = Flipper.get(in_progress_path)
        # Overwrite the old flipper
        Flipper.save(flipper, FLIPPER_PATH)
        # Delete the in-progress file.
        # This method is cancellable with no cleanup method (Dash limitation)
        # So we delete the whole directory, which will also clean old, missed files
        shutil.rmtree(str(in_progress_dir), ignore_errors=True)
    elif ctx.triggered_id == 'reset_button':
        # Delete the most recent flipper and init a new one
        flipper_path = FLIPPER_PATH
        flipper_path.unlink(missing_ok=True)
        flipper = Flipper.get(flipper_path)

    # Message beneath the buttons
    message = f'A total of {len(flipper.flips)} coins have been flipped!' \
        if numCoinFlipClicks > 0 else ''

    # Whatever button was hit, we always update the graph
    population_fig = getUpdatedGraph(wealth_distribution_dropdown_value, 'wealth_distribution', flipper=flipper)
    history_fig = getUpdatedGraph(history_dropdown_value, 'flip_history', flipper=flipper)

    return population_fig, history_fig, message


def getUpdatedGraph(dropdown_value, graphFrom, flipper=None):
    """Get a Plotly figure for a graph
        Args:
            dropdown_value: The value from the dropdown menu (representing the id of a DropdownOption object)
            graphFrom: Where the values should come from.
                        options: 'wealth_distribution', 'flip_history'
            flipper: A CoinFlipper object to get info from for the graph
    """

    flipper = flipper or Flipper.get(FLIPPER_PATH)  # Flipper.get() is slow. Pass in a flipper to avoid it

    if graphFrom == 'wealth_distribution':
        df = flipper.population.getStatsByTopXRanges()
    elif graphFrom == 'flip_history':
        df = flipper.history.getStatsOverTime(includeTopX=True)
    else:
        raise Exception(f"Unknown graphFrom: {graphFrom}")

    # A DropdownOption object containing info about the selected option
    selected_option = DropdownOption.getById(dropdown_value)

    # Make sure the selection_option.xKey and .yKey exist
    for key in [selected_option.xKey, selected_option.yKey]:
        if key not in df.columns:
            print(f"{key} is not in df.columns. Columns are: {', '.join(df.columns)}")
            # If they don't, return an empty graph
            fig = go.Figure([go.Scatter()])
            break
    else:
        # If all is good, build the figure
        fig = go.Figure([go.Scatter(x=df[selected_option.xKey], y=df[selected_option.yKey],
                                    line=dict(color='firebrick', width=4))])
    # Styling
    fig.update_layout(title=selected_option.title,
                      xaxis_title=selected_option.xLabel,
                      yaxis_title=selected_option.yLabel,
                      paper_bgcolor='rgba(0, 0, 0, 0)',
                      plot_bgcolor='rgb(255, 255, 255)')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
