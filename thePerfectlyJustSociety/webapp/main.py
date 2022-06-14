
# Built-In Python
import shutil
import time
import uuid
from datetime import datetime
import logging

# Third-Party
from dash import Dash, ctx
from dash.dependencies import Input, Output, State
from dash.long_callback import DiskcacheLongCallbackManager
import plotly.graph_objects as go
import diskcache

# Custom
from thePerfectlyJustSociety.coinFlip.pollableThread import PollableCoinFlipper
from thePerfectlyJustSociety.coinFlip.flipManager import FlipperManager
from .screen import Screen
from .layout import Layout
from .style import Style
from .dropdownOption import DropdownOption
from .progress import make_progress_graph
from .explanation import Explanation

# Constants
INCLUDE_TOP_X = [0, 99]

# Disk Cache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, long_callback_manager=long_callback_manager)
app.title = "The Perfectly Just Society."

# Get the layout
layout = Layout(app.title)
app.layout = layout.getLayout()


@app.long_callback(
    inputs=Screen.stateMap('input'),
    output=Screen.stateMap('output'),
    progress=Output("progress_bar", "figure"),
    progress_default=make_progress_graph(0, 100),
    interval=250,
    running=[
        (Output("num_flips_text_input", "disabled"), True, False),
        (Output("coin_flip_button", "disabled"), True, False),
        (Output("reset_coin_flips_button", "disabled"), True, False),
        (Output("flip_history_dropdown", "disabled"), True, False),
        (Output("wealth_distribution_dropdown", "disabled"), True, False),
        (Output("cancel_button", "style"),
         Style.cancel(visibility='visible', transitionDelay='3s'),
         Style.cancel(visibility='hidden')
         )
    ],
    cancel=[Input("cancel_button", "n_clicks")],
    prevent_initial_call=False
)
def update(set_progress, explanationSectionStyle, explanationStyle, explanationText, nextButtonStyle,
           popSectionStyle, popText, popParamsStyle,
           populationButtonsStyle, populationEditButtonStyle,
           coinFlipSectionStyle, coinFlipHidden, coinFlipParamsStyle, coinFlipText, wealthGraphHidden,
           wealthDistributionText,
           wealthDistributionFig, historyFig,
           paramSectionStyle, coinFlipBottomSectionStyle, coinFlipEditButtonStyle,
           popSize, startMoney, numConfirmPopClicks, editPopClicks, wealth_distribution_dropdown_value,
           history_dropdown_value,
           numCoinFlipClicks, coinFlipEditButtonClicks, numFlips, numResetClicks, dollarsPerFlip, nextButtonClicks):
    """Update the screen"""

    logging.info(f'Update: {datetime.now().strftime("%H:%M:%S")}: {ctx.triggered_id}')
    # The current status of elements
    screen = Screen(explanationSectionStyle=explanationSectionStyle, explanationStyle=explanationStyle,
                    explanationText=explanationText, nextButtonStyle=nextButtonStyle,
                    popSectionStyle=popSectionStyle, popText=popText, wealthGraphHidden=wealthGraphHidden,
                    coinFlipSectionStyle=coinFlipSectionStyle, coinFlipHidden=coinFlipHidden,
                    wealthDistributionText=wealthDistributionText,
                    wealthDistributionFig=wealthDistributionFig, historyFig=historyFig,
                    coinFlipText=coinFlipText,
                    popParamsStyle=popParamsStyle, popButtonsStyle=populationButtonsStyle,
                    paramSectionStyle=paramSectionStyle, coinFlipParamsStyle=coinFlipParamsStyle,
                    coinFlipBottomSectionStyle=coinFlipBottomSectionStyle,
                    populationEditButtonStyle=populationEditButtonStyle,
                    coinFlipEditButtonStyle=coinFlipEditButtonStyle)

    # Get the flipper
    flip_manager = FlipperManager(popSize=int(popSize), startMoney=int(startMoney), dollarsPerFlip=int(dollarsPerFlip),
                                  allowDebt=False, includeTopX=INCLUDE_TOP_X)

    if nextButtonClicks == 0:
        flip_manager.reset()

    # A first-time user who has not yet seen the explanations
    if not flip_manager.sessionInProgress:
        # Show Explanations
        explanations = Explanation()
        if nextButtonClicks < len(explanations):
            screen.setExplanation(nextButtonClicks)
        elif nextButtonClicks == len(explanations):
            screen.hideExplanations()
            screen.maximizePopulationParams()

    flipper = None

    if ctx.triggered_id:
        if ctx.triggered_id == 'population_confirm_button':
            # And the Coin Flip Section
            screen.showCoinFlipSection()

            # Create a new CoinFlipper
            flipper = flip_manager.new()
            if flipper.population:
                if not all([len(flipper.population) == int(popSize),
                            flipper.population[0].startMoney == int(startMoney)]):
                    logging.warning(
                        'WARNING: The old flipper does not seem to match the requested population properties. '
                        'Starting a new population.')
                    FlipperManager.save(flipper)

            # Update the text
            screen.updatePopulationText(flipper)
            screen.updateCoinFlipText(flipper)
            # Minimize the Population Box
            screen.minimizePopulationParams()
            screen.maximizeCoinFlipParams()

        elif ctx.triggered_id == 'coin_flip_button':  # Flip a coin some number of times
            # Show the Wealth Distribution Graph
            # TODO: It would be good if this could update dynamically as the coins are flipped
            screen.showWealthGraph()

            # This is updated at an interval specified in PollableCoinFlipper(progressEvery=numFlips)
            # When Pollable CoinFlipper is not being used, the process will be fast so just do some dummy progress
            def progress_callback(progressRatio):
                set_progress(make_progress_graph(int(progressRatio * 100), 100))

            # Update the progress to 0
            progress_callback(0.0)
            # The most recent flipper
            flipper_path = FlipperManager.getFilepath()
            flipper = flip_manager.get(flipper_path)
            # In-Progress flips will be saved to this path, so if the process is cancelled,
            # the previous flipper is not corrupted
            in_progress_dir = flipper_path.parent.joinpath('tmp')
            in_progress_path = in_progress_dir.joinpath(f'{flipper_path.stem}_tmp_{uuid.uuid4()}{flipper_path.suffix}')
            # A Pollable / Stoppable Thread
            save_every = (int(numFlips) // 10) or 1
            thread = PollableCoinFlipper(flipper=flipper, flipperPath=in_progress_path,
                                         numFlips=numFlips, progressEvery=1, saveEvery=save_every,
                                         saveTopX=flip_manager.includeTopX)
            thread.start()
            # Regularly poll the thread and update the progress bar
            # (The code blocks here, but the @long_callback decorator means the update function will still be called
            #  once per second)
            thread.pollEvery(0.5, progress_callback, pollAtStart=True)
            # The newly updated flipper
            flipper = flip_manager.get(in_progress_path)
            # Overwrite the old flipper
            FlipperManager.save(flipper, flipper_path)
            # Delete the in-progress file.
            # This method is cancellable with no cleanup method (Dash limitation)
            # So we delete the whole directory, which will also clean old, missed files
            shutil.rmtree(str(in_progress_dir), ignore_errors=True)
            # Message beneath the buttons
            screen.updateCoinFlipText(flipper)
            # Set progress bar to 100%
            progress_callback(1.0)
            # Sleep so Progress Bar still goes to 100% if the flips happen very quickly
            time.sleep(0.5)
            # Minimize the Coin Flip Box
            screen.minimizeCoinFlipParams()
        elif ctx.triggered_id == 'reset_coin_flips_button':
            # Delete the most recent flipper and init a new one
            flip_manager.reset()
            flipper = flip_manager.get()

            # Message beneath the buttons
            screen.coinFlipText = f'A total of {len(flipper.flips)} coins have been flipped!' \
                if numCoinFlipClicks > 0 else ''
        elif ctx.triggered_id == 'population_section_edit_button':
            # Maximize Population Parameter Box
            screen.maximizePopulationParams()
        elif ctx.triggered_id == 'coin_flip_section_edit_button':
            # Maximize Coin Flip Section
            screen.maximizeCoinFlipParams()
        elif '_long_callback_interval' in ctx.triggered_id:
            # Get the CoinFlipper
            flipper = flip_manager.get() if flip_manager.sessionInProgress else None
        else:
            logging.error(f'Uncaught triggered_id: {ctx.triggered_id}')

    # elif flip_manager.sessionInProgress and not nextButtonClicks:
    #     # Returning user (who has already seen the explanations)
    #     screen.hideExplanations()
    #     screen.maximizePopulationParams()
    #     flipper = flip_manager.get()

    # Whatever button was hit, we always update the graph
    screen.updateWealthDistributionGraph(wealth_distribution_dropdown_value, flipper=flipper)
    screen.updateHistoryGraph(history_dropdown_value, flipper=flipper)
    return screen.args()


def getUpdatedGraph(dropdown_value, flipper):
    """Get a Plotly figure for a graph
        Args:
            dropdown_value: The value from the dropdown menu (representing the id of a DropdownOption object)
            flipper: A CoinFlipper object to get info from for the graph
    """
    if not flipper:
        # If no flipper is passed, return an empty figure
        return go.Figure([go.Scatter()])
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
            logging.error(f"{key} is not in df.columns. Columns are: {', '.join(df.columns)}")
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
    logging.getLogger().setLevel('INFO')
    app.run_server(debug=True)
