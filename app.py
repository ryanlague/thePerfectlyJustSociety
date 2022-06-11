# Built-In Python
import random
import shutil
import time
import uuid
from pathlib import Path
from datetime import datetime

# Third-Party
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.long_callback import DiskcacheLongCallbackManager
import plotly.graph_objects as go
import diskcache
from flask import request

# Custom
from coin_flip import CoinFlipper, Flips, Flip, History
from population import Population
from pollableThread import StoppableThread, PollableCoinFlipper
from impz_logger.decorators import profile

# Constants
INCLUDE_TOP_X = [0, 99]


class DropdownOption:
    def __init__(self, label, _id, xLabel='Number of Flips', xKey='numFlips', yLabel='Money', yKey=None,
                 title=None, graphFrom='wealth_distribution'):
        self.label = label
        self.id = _id
        self.xLabel = xLabel
        self.xKey = xKey
        self.yLabel = yLabel
        self.yKey = yKey or _id  # To avoid typing things twice, just set the id to what we want the yKey to be
        self.title = title
        self.graphFrom = graphFrom

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
            cls('Money Per Person', 'money', xLabel='People (sorted by wealth)', xKey='rank_by_money',
                yLabel='Money', yKey='money', graphFrom='individual_wealth'),
            cls('Money Per Percentile', 'percent_wealth', xLabel='Wealth Percentile', xKey='top_x_percent_low',
                yLabel='Percent of Total Wealth', yKey='percent_wealth', graphFrom='wealth_distribution'),
        ]

    @classmethod
    def getHistoryOptions(cls):
        kwargs = dict(graphFrom='flip_history')
        return [
            cls('Top 1%', 'top_0_to_1_percent_wealth', yLabel='Percent of Total Wealth', **kwargs),
            cls('Bottom 1%', 'top_99_to_100_percent_wealth', yLabel='Percent of Total Wealth', **kwargs),
            cls('Richest Person', 'max', **kwargs),
            cls('Poorest Person', 'min', **kwargs),
            cls('Total', 'total', **kwargs),
            cls('Average Person', 'mean', **kwargs),
        ]


class Flipper:
    @classmethod
    def getFilepath(cls, ip=None):
        ip = ip or request.remote_addr
        return Path(f'flipperCache/sessions/{ip}/currentFlipper.pickle')

    @classmethod
    def get(cls, filepath, popSize=None, startMoney=None, dollarsPerFlip=None):
        filepath = Path(filepath)
        if filepath.exists() and not any([popSize, startMoney, dollarsPerFlip]):
            print(f'Loading {filepath}')
            flipper = CoinFlipper.load(filepath)
            print(f'{filepath} has been loaded')
        else:
            population = Population()
            population.add(popSize, startMoney=startMoney)
            flipper = CoinFlipper(population, dollarsPerFlip=dollarsPerFlip, allowDebt=True, selectionStyle='random')
            flipper.save(filepath, includeTopX=INCLUDE_TOP_X)
        return flipper

    @classmethod
    def save(cls, coinFlipper, filepath):
        print(f'Saving {filepath}')
        filepath = filepath or coinFlipper.descriptiveFilepath(coinFlipper.cacheDir)
        coinFlipper.save(filepath)
        history = coinFlipper.history.getStatsOverTime(includeTopX=True)
        history.to_pickle(filepath.with_stem(f"{filepath.stem}_history"))
        print(f'{filepath} has been saved')


class Style:
    @classmethod
    def paramSection(cls, **kwargs):
        BASE_STYLE = {'height': '300px', 'width': '45%', 'margin': 'auto', 'border-style': 'solid',
                      'margin-bottom': '20px'}
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

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
    def inputWrapper(cls, textAlign='center',
                     marginTop='auto', marginRight='auto', marginLeft='auto', marginBottom='10px',
                     width='220px', flexBasis='40%', **kwargs):
        BASE_STYLE = {
            'text-align': textAlign,
            'margin-top': marginTop, 'margin-right': marginRight,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width, 'flex-basis': flexBasis
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
    def button2(cls, textAlign='center',
                marginTop='auto', marginRight='auto', marginLeft='auto', marginBottom='10px',
                width='220px', flexBasis='40%', **kwargs):
        BASE_STYLE = {
            'text-align': textAlign,
            'margin-top': marginTop, 'margin-right': marginRight,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width, 'flex-basis': flexBasis
        }
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def cancel(cls, **kwargs):
        BASE_STYLE = {'font-size': '18px', 'padding': '5px',
                      'margin': '0', 'margin-top': '-20px', 'margin-bot': '0', 'margin-left': '-80px',
                      'text-align': 'left',
                      'line-height': '100%', 'vertical-align': 'center', 'border': 'none'}
        style = BASE_STYLE.copy()
        style.update(kwargs)
        return style

    @classmethod
    def progress(cls, marginTop='10px', marginRight='auto', marginBottom='auto', marginLeft='auto',
                 height='40px', lineHeight='40px', display='flex', flexDirection='row',
                 alignItems='center', justifyContent='center',
                 **kwargs):
        BASE_STYLE = {'margin-top': marginTop, 'margin-right': marginRight,
                      'margin-bottom': marginBottom, 'margin-left': marginLeft,
                      'height': height, 'line-height': lineHeight, 'display': display,
                      'flex-direction': flexDirection,
                      'align-items': alignItems, 'justify-content': justifyContent}
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


def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])],
                  layout=dict(title='Progress', titlefont={'size': 8, 'family': 'PlayfairDisplay-Regular'}, title_y=0.68, title_x=0.07, height=75, width=600, margin=dict(t=20, b=40),
                              paper_bgcolor='rgba(255, 255, 255, 0.0)'))
            .update_xaxes(range=[0, total])
            .update_yaxes(
            showticklabels=False
        )
    )
    return progress_graph


# # # MAIN APP # # #


# Disk Cache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, long_callback_manager=long_callback_manager)
app.title = "The Perfectly Just Society"

# Layout
app.layout = html.Div(
    id='parent',
    children=[
        # Main Title
        html.H1(id='H1', children=app.title,
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),

        # Parameter Sections
        html.Div(
            id='param_sections',
            style={'display': 'flex', 'flex-direction': 'row'},
            children=[
                # A Section for Building the Population
                html.Div(
                    id='population_section',
                    style=Style.paramSection(display='flex', flexDirection='row', flexWrap='wrap', alignItems='center'),
                    children=[
                        html.H2('Population', style=Style.text(flexBasis='100%', margin='auto')),
                        html.Div(id='pop_confirmation_text',
                                 children="Build your society's population",
                                 style=Style.text(marginLeft='calc(50% - 250px)', width='500px', marginTop='0px')),
                        html.Div(
                            style=Style.inputWrapper(),
                            children=[
                                html.Label('Pop. Size'),
                                dcc.Input(id='population_size_text_input', type='number', value='1000',
                                          style={'text-align': 'center', 'width': '100%'}),
                            ],
                        ),
                        html.Div(
                            style=Style.inputWrapper(),
                            children=[
                                html.Label('Start Money'),
                                dcc.Input(id='start_money_text_input', type='number', value='100',
                                          style={'text-align': 'center', 'width': '100%'}),
                            ],
                        ),
                        html.Div(id='pop_buttons',
                                 style=Style.inputWrapper(),
                                 children=[
                                     html.Button('Confirm Population', id='confirm_pop_button', n_clicks=0,
                                                 disabled=False,
                                                 style=Style.button2()),
                                     html.Button('Reset', id='reset_pop_button', n_clicks=0,
                                                 disabled=False,
                                                 style=Style.button2()),
                                 ]
                                 ),
                    ]),

                # A section for Flipping Coins
                html.Div(
                    id='coin_flip_section',
                    hidden=True,
                    style=Style.paramSection(),
                    children=[
                        html.H2('Opportunities', style=Style.text(flexBasis='100%', margin='auto')),
                        html.Div(id='coin_flip_confirmation_text',
                                 children='Enter a number of flips and press "Flip"',
                                 style=Style.text(marginLeft='calc(50% - 250px)', width='500px', marginTop='0px')),
                        html.Label('Number of Coin Flips', style=Style.text(marginBottom='0px')),
                        html.Div(
                            dcc.Input(id='num_flips_text_input', type='number', value='1',
                                      style={'text-align': 'center'}),
                            style=Style.button()
                        ),
                        html.Div(id='coin_flip_buttons',
                                 children=[
                                     html.Button('Flip', id='coin_flip_button', n_clicks=0, disabled=False,
                                                 style=Style.button()),
                                     html.Button('Reset', id='reset_coin_flips_button', n_clicks=0, disabled=False,
                                                 style=Style.button()),
                                 ]
                                 ),
                        html.Div(id='progress_div',
                                 style=Style.progress(),
                                 hidden=True,
                                 children=[
                                     dcc.Graph(id="progress_bar", figure=make_progress_graph(0, 100),
                                               style={'flex-basis': '25%'}, config=dict(displayModeBar=False)),
                                     html.Button(
                                         id='cancel_button',
                                         style=Style.cancel(),
                                         children=[html.I(id='cancel_button_icon', n_clicks=0, className='fa fa-times')]
                                     )
                                 ]
                                 ),
                    ]
                ),
            ]
        ),

        # Graphs
        html.Div(
            id='graph_section',
            children=[
                html.Div(
                    # Graph: Wealth Distribution
                    id='wealth_distribution_section',
                    hidden=True,
                    children=[
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
                        )
                    ]
                ),
                html.Div(
                    # Graph: Flip History
                    hidden=True,
                    children=[
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
            ]
        )
    ]
)


@app.long_callback(
    inputs=[
        Input('population_size_text_input', 'value'),
        Input('start_money_text_input', 'value'),
        Input('confirm_pop_button', 'n_clicks'),
        State('wealth_distribution_section', 'hidden'),
        State('coin_flip_section', 'hidden'),
        State('coin_flip_confirmation_text', 'children'),
        Input('wealth_distribution_dropdown', 'value'),
        Input('flip_history_dropdown', 'value'),
        Input('coin_flip_button', 'n_clicks'),
        State('num_flips_text_input', 'value'),
        Input('reset_coin_flips_button', 'n_clicks')
    ],
    output=[
        Output('wealth_distribution_section', 'hidden'),
        Output('coin_flip_section', 'hidden'),
        Output('wealth_distribution_plot', 'figure'),
        Output('flip_history_plot', 'figure'),
        Output('coin_flip_confirmation_text', 'children')
    ],
    progress=Output("progress_bar", "figure"),
    progress_default=make_progress_graph(0, 100),
    interval=1000,
    running=[
        (Output("num_flips_text_input", "disabled"), True, False),
        (Output("coin_flip_button", "disabled"), True, False),
        (Output("reset_coin_flips_button", "disabled"), True, False),
        (Output("flip_history_dropdown", "disabled"), True, False),
        (Output("wealth_distribution_dropdown", "disabled"), True, False),
        (Output("cancel_button", "style"),
            Style.cancel(visibility='visible', transitionDelay='3s'),
            Style.cancel(visibility='hidden')
         ),
        # (Output("progress_bar", "style"), Style.progress(), Style.progress(visibility='hidden')),
    ],
    cancel=[Input("cancel_button", "n_clicks")],
    prevent_initial_call=True
)
@profile()
def update(set_progress, popSize, startMoney, numConfirmPopClicks, wealthGraphHidden, coinFlipHidden, coinFlipText,
           wealth_distribution_dropdown_value, history_dropdown_value, numCoinFlipClicks, num_flips, numResetClicks):
    """Update the screen"""

    flipper = None

    print(f'UPDATE: {datetime.now().strftime("%H:%M:%S")}: {ctx.triggered_id}')
    # The current status of elements
    wealth_graph_hidden = wealthGraphHidden
    coin_flip_hidden = coinFlipHidden
    coin_flip_text = coinFlipText

    if ctx.triggered_id == 'confirm_pop_button':
        # Once we have confirmed the population, un-hide the Wealth Distribution Graph
        wealth_graph_hidden = False
        # And the Coin Flip Section
        coin_flip_hidden = False

        # Create a new CoinFlipper
        # TODO: dollarsPerFlip should come from the Coin Flip Menu.
        #       Maybe default to 10 (or None / 0 / whatever) but on the first flips, reset it
        flipper_path = Flipper.getFilepath()
        flipper = Flipper.get(flipper_path)
        if flipper.population:
            if not all([len(flipper.population) == int(popSize),
                        flipper.population[0].startMoney == int(startMoney)]):
                print('WARNING: The old flipper does not seem to match the requested population properties. '
                      'Starting a new population.')
                flipper = Flipper.get(flipper_path, popSize=int(popSize), startMoney=int(startMoney), dollarsPerFlip=10)
                Flipper.save(flipper, flipper_path)

    elif ctx.triggered_id == 'coin_flip_button':  # Flip a coin some number of times
        # This is updated at an interval specified in PollableCoinFlipper(progressEvery=num_flips)
        # When Pollable CoinFlipper is not being used, the process will be fast so just do some dummy progress
        def progress_callback(progressRatio):
            # set_progress((str(int(progressRatio * 100)), str(100)))
            set_progress(make_progress_graph(int(progressRatio * 100), 100))
        # Update the progress to 0
        progress_callback(0.0)
        # The most recent flipper
        flipper_path = Flipper.getFilepath()
        flipper = Flipper.get(flipper_path)
        # In-Progress flips will be saved to this path, so if the process is cancelled,
        # the previous flipper is not corrupted
        in_progress_dir = flipper_path.parent.joinpath('tmp')
        in_progress_path = in_progress_dir.joinpath(f'{flipper_path.stem}_tmp_{uuid.uuid4()}{flipper_path.suffix}')
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
        Flipper.save(flipper, flipper_path)
        # Delete the in-progress file.
        # This method is cancellable with no cleanup method (Dash limitation)
        # So we delete the whole directory, which will also clean old, missed files
        shutil.rmtree(str(in_progress_dir), ignore_errors=True)
        # Message beneath the buttons
        coin_flip_text = f'A total of {len(flipper.flips)} coins have been flipped!' \
            if numCoinFlipClicks > 0 else ''
        # Set progress bar to 100%
        progress_callback(1.0)
        time.sleep(0.5)
    elif ctx.triggered_id == 'reset_coin_flips_button':
        # Delete the most recent flipper and init a new one
        flipper_path = Flipper.getFilepath()
        flipper_path.unlink(missing_ok=True)
        flipper = Flipper.get(flipper_path)

        # Message beneath the buttons
        coin_flip_text = f'A total of {len(flipper.flips)} coins have been flipped!' \
            if numCoinFlipClicks > 0 else ''

    # Whatever button was hit, we always update the graph
    population_fig = getUpdatedGraph(wealth_distribution_dropdown_value, flipper=flipper)
    history_fig = getUpdatedGraph(history_dropdown_value, flipper=flipper)

    return wealth_graph_hidden, coin_flip_hidden, population_fig, history_fig, coin_flip_text


def getUpdatedGraph(dropdown_value, flipper=None):
    """Get a Plotly figure for a graph
        Args:
            dropdown_value: The value from the dropdown menu (representing the id of a DropdownOption object)
            flipper: A CoinFlipper object to get info from for the graph (optional)
    """

    flipper = flipper or Flipper.get(Flipper.getFilepath())  # Flipper.get() is slow. Pass in a flipper to avoid it

    # A DropdownOption object containing info about the selected option
    selected_option = DropdownOption.getById(dropdown_value)

    if selected_option.graphFrom == 'wealth_distribution':
        df = flipper.population.getStatsByTopXRanges()
    elif selected_option.graphFrom == 'individual_wealth':
        df = flipper.population.toDf(sortBy='money')
    elif selected_option.graphFrom == 'flip_history':
        df = flipper.history.getStatsOverTime(includeTopX=True)
    else:
        raise Exception(f"Unknown graphFrom: {selected_option.graphFrom}")

    # Make sure the selection_option.xKey and .yKey exist
    for key in [selected_option.xKey, selected_option.yKey]:
        if key not in df.columns:
            print(f"ERROR: {key} is not in df.columns. Columns are: {', '.join(df.columns)}")
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
