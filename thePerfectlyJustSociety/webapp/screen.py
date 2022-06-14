import logging

import plotly.graph_objects as go
from dash import html
from dash.dependencies import Input, Output, State
from .style import Style
from .dropdownOption import DropdownOption

from thePerfectlyJustSociety.coinFlip.coinFlip import CoinFlipper


class Screen:
    def __init__(self, explanationSectionStyle, explanationStyle, explanationText, nextButtonStyle,
                 popSectionStyle, popText, wealthGraphHidden,
                 coinFlipSectionStyle, coinFlipHidden,
                 wealthDistributionText, wealthDistributionFig,
                 historyFig, coinFlipText, popParamsStyle, popButtonsStyle, paramSectionStyle, coinFlipParamsStyle,
                 coinFlipBottomSectionStyle, populationEditButtonStyle, coinFlipEditButtonStyle):

        self.explanationSectionStyle = explanationSectionStyle
        self.explanationStyle = explanationStyle
        self.explanationText = explanationText
        self.nextButtonStyle = nextButtonStyle
        self.popSectionStyle = popSectionStyle
        self.popText = popText
        self.popParamsStyle = popParamsStyle
        self.popButtonsStyle = popButtonsStyle
        self.coinFlipSectionStyle = coinFlipSectionStyle
        self.coinFlipHidden = coinFlipHidden
        self.coinFlipText = coinFlipText
        self.wealthGraphHidden = wealthGraphHidden
        self.wealthDistributionText = wealthDistributionText
        self.wealthDistributionFig = wealthDistributionFig
        self.historyFig = historyFig
        self.paramSectionStyle = paramSectionStyle
        self.coinFlipParamsStyle = coinFlipParamsStyle
        self.coinFlipBottomSectionStyle = coinFlipBottomSectionStyle or {}
        self.populationEditButtonStyle = populationEditButtonStyle
        self.coinFlipEditButtonStyle = coinFlipEditButtonStyle

        # TODO: The commented-out code works, but is it better to have explicitly set attributes like above?
        # kwargs = locals()
        # input_keys = list(locals().keys())
        # for key in self.stateMap('attr'):
        #     if key in input_keys:
        #         setattr(self, key, kwargs[key])
        #     else:
        #         raise TypeError(f"__init__() missing 1 required positional argument: '{key}'")

    @classmethod
    def stateMap(cls, get=None):
        states = [
            (('explanation_section', 'style'), 'explanationSectionStyle'),
            (('explanation', 'style'), 'explanationStyle'),
            (('explanation', 'children'), 'explanationText'),
            (('next_button', 'style'), 'nextButtonStyle'),
            (('population_section', 'style'), 'popSectionStyle'),
            (('population_section_text', 'children'), 'popText'),
            (('population_section_params', 'style'), 'popParamsStyle'),
            (('population_section_buttons', 'style'), 'popButtonsStyle'),
            (('population_section_edit_button', 'style'), 'populationEditButtonStyle'),
            (('coin_flip_section', 'style'), 'coinFlipSectionStyle'),
            (('coin_flip_section', 'hidden'), 'coinFlipHidden'),
            (('coin_flip_section_params', 'style'), 'coinFlipParamsStyle'),
            (('coin_flip_section_text', 'children'), 'coinFlipText'),
            (('wealth_distribution_section', 'hidden'), 'wealthGraphHidden'),
            (('wealth_distribution_text', 'children'), 'wealthDistributionText'),
            (('wealth_distribution_plot', 'figure'), 'wealthDistributionFig'),
            (('flip_history_plot', 'figure'), 'historyFig'),
            (('section_1', 'style'), 'paramSectionStyle'),
            (('coin_flip_section_bottom', 'style'), 'coinFlipBottomSectionStyle'),
            (('coin_flip_section_edit_button', 'style'), 'coinFlipEditButtonStyle'),
        ]
        if get is None:
            return states
        elif get == 'input':
            input_states = [State(*s[0]) for s in states]
            hard_coded_inputs = [
                Input('population_size_text_input', 'value'),
                Input('population_start_money_text_input', 'value'),
                Input('population_confirm_button', 'n_clicks'),
                Input('population_section_edit_button', 'n_clicks'),
                Input('wealth_distribution_dropdown', 'value'),
                Input('flip_history_dropdown', 'value'),
                Input('coin_flip_button', 'n_clicks'),
                Input('coin_flip_section_edit_button', 'n_clicks'),
                State('num_flips_text_input', 'value'),
                Input('reset_coin_flips_button', 'n_clicks'),
                State('dollars_per_flip_text_input', 'value'),
                Input('next_button', 'n_clicks'),
            ]
            return input_states + hard_coded_inputs
        elif get == 'output':
            return [Output(*s[0]) for s in states]
        elif get == 'attr':
            return [s[1] for s in states]

    def args(self):
        arg_strings = self.stateMap('attr')
        d = vars(self)
        args = [d[a] for a in arg_strings]
        return tuple(args)

    def setExplanation(self, idx):
        for i, txt in enumerate(self.explanationText):
            delay = '1s' if i else '0'
            if i == idx:
                self.explanationText[i]['props']['style'].update({'opacity': '1.0', 'height': '100%',
                                                                  'transition': f'opacity 1s linear {delay}'})
            else:
                self.explanationText[i]['props']['style'].update({'opacity': '0.0', 'height': '0px',
                                                                  'transition': 'opacity 1s'})
        self.nextButtonStyle.update(dict(opacity='1.0', transition='opacity 3s linear 5s'))

    def hideExplanations(self):
        self.nextButtonStyle.update(dict(opacity=0.0, transition='opacity 1s linear 0'))
        self.explanationSectionStyle.update(dict(opacity=0.0, height=0.0, transition='opacity 2s, height 1s linear 2s'))

    def updatePopulationText(self, flipper):
        if isinstance(flipper, str):
            text = flipper
        else:
            DEFAULT_TEXT = "Everyone should start with the same amount of wealth"
            text = f'Size: {int(len(flipper.population)):,} | ' \
                   f'Start Wealth: ${int(flipper.population[0].startMoney):,}' \
                if flipper.population else DEFAULT_TEXT
        logging.info(f'Update Population Text: {text}')
        self.popText = [html.P(txt, style=Style.text(margin='0')) for txt in text.split('\n')]

    @classmethod
    def _sanitizeTextForHTML(cls, text):
        sani_txt = [html.P(txt, style=Style.text(margin='0 auto 0 auto', flexBasis='100%')) for txt in text.split('\n')]
        return sani_txt

    def updateCoinFlipText(self, flipper=None):
        if isinstance(flipper, str):
            text = flipper
        else:
            DEFAULT_TEXT = 'An opportunity arises to accrue wealth.\n' \
                           'To decide who gets it, we will flip a coin!'
            text = f'A total of {len(flipper.flips):,} coins have been flipped!' \
                if flipper and flipper.flips else DEFAULT_TEXT
        logging.info(f'Update Coin Flip Text: {text}')
        self.coinFlipText = self._sanitizeTextForHTML(text)

    def minimizePopulationParams(self):
        logging.info('Minimize Population params')
        self.popSectionStyle.update(dict(height='75px', width='300px'))
        self.populationEditButtonStyle.update(dict(visibility='visible'))

    def maximizePopulationParams(self):
        logging.info('Maximize Population params')
        self.populationEditButtonStyle.update(dict(visibility='hidden'))
        self.popSectionStyle = Style.paramBox(height='220px', opacity='1.0')
        self.popText = "Everyone should start with the same amount of wealth"

    def minimizeCoinFlipParams(self):
        logging.info('Minimize Coin Flip params')
        self.coinFlipSectionStyle.update(dict(height='75px', width='300px'))
        self.coinFlipEditButtonStyle.update(dict(visibility='visible'))

    def maximizeCoinFlipParams(self):
        logging.info('Maximize Population params')
        self.coinFlipEditButtonStyle.update(dict(visibility='hidden'))
        self.coinFlipSectionStyle = Style.paramBox(height='300px', opacity='1.0')
        self.updateCoinFlipText()

    def hideCoinFlipSection(self, hidden=True):
        if hidden:
            self.coinFlipSectionStyle.update(dict(visibility='hidden', marginTop='1000px'))
        else:
            self.coinFlipSectionStyle.update(dict(visibility='visible', margin='10px auto 10px auto'))

    def showCoinFlipSection(self, show=True):
        self.hideCoinFlipSection(not show)

    def showWealthGraph(self, show=True):
        self.wealthGraphHidden = not show

    def hideWealthGraph(self, hidden=True):
        self.wealthGraphHidden = hidden

    def updateWealthDistributionGraph(self, dropdownVal, flipper: CoinFlipper):
        if flipper:
            top_1 = flipper.population.getWealthiestXPercent(topX=1).percentWealthOfParent
            text = f'Even though opportunities were given out at random, \n' \
                   f'after {len(flipper.flips)} flips, the top 1% wealthiest people have ' \
                   f'{round(top_1, 2):,}% of the total wealth.\n' \
                   f'Was our egalitarian society effective?\nWhat should we change?'
            self.wealthDistributionText = self._sanitizeTextForHTML(text)
        self.wealthDistributionFig = self.getUpdatedGraph(dropdownVal, flipper=flipper)

    def updateHistoryGraph(self, dropdownVal, flipper):
        if not self.wealthGraphHidden:
            self.historyFig = self.getUpdatedGraph(dropdownVal, flipper=flipper)
        else:
            # An empty figure
            self.historyFig = go.Figure([go.Scatter()])

    @classmethod
    def getUpdatedGraph(cls, dropdown_value, flipper):
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
