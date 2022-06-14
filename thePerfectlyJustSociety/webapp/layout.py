# Third-Party
from dash import html, dcc

# Custom
from .dropdownOption import DropdownOption
from .progress import make_progress_graph
from .style import Style
from .explanation import Explanation


class Layout:
    def __init__(self, title):
        self.title = title
        self.explanations = Explanation()

    def getLayout(self):
        # Layout
        layout = html.Div(
            id='parent',
            style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center',
                   'justify-content': 'center', 'width': '100%'},
            children=[
                # Main Title
                html.H1(id='H1', children=self.title,
                        style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 10}),

                # Explanation Section
                html.Div(
                    id='explanation_section',
                    style=Style.container(display='flex', flexDirection='column', width='40%', height='200px'),
                    children=[
                        html.Div(
                            id='explanation',
                            style=Style.section(flexDirection='row', alignItems='flex-start', marginBottom='20px',
                                                height='70%', overflow='hidden',
                                                textAlign='left', transitionDuration='5s'),
                            children=[html.Div(ex, style={'opacity': '0.0', 'transition': 'opacity 3s'})
                                      for ex in self.explanations]),
                        html.Button(
                            id='next_button',
                            n_clicks=0,
                            style=Style.icon(opacity='0', textAlign='center', margin='auto', marginBottom='0'),
                            children=[
                                html.Span('Next', style={'margin-right': '0.5em'}),
                                html.I(id='next_button_icon', n_clicks=0,
                                       className='fa fa-arrow-right')
                            ]
                        ),
                    ]
                ),
                # Parameter Sections
                html.Div(
                    id='section_1',
                    style=Style.section(),
                    children=[
                        # A Section for Building the Population
                        self._getPopulationSection(),

                        # A section for Flipping Coins
                        self._getCoinFlipSection(),
                    ]
                ),

                # Graphs
                html.Div(
                    id='graph_section',
                    style={'width': '50%'},
                    children=[
                        html.Div(
                            # Graph: Wealth Distribution
                            id='wealth_distribution_section',
                            hidden=True,
                            children=[
                                html.H2(id='wealth_distribution_title', children='Wealth Distribution',
                                        style={'textAlign': 'center', 'marginTop': 0, 'marginBottom': 0}),
                                html.Span(id='wealth_distribution_text', children=''),
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
        return layout

    @classmethod
    def _getParam(cls, _id, label, inputId, value, hidden=False):
        div = html.Div(
            id=_id,
            hidden=hidden,
            style=Style.inputWrapper(),
            children=[
                html.Label(label),
                dcc.Input(id=inputId, type='number', value=str(value), style={'text-align': 'center', 'width': '100%'})
            ],
        )
        return div

    @classmethod
    def _getEditButton(cls, _id, visibility='hidden'):
        btn = html.Button(
            id=_id,
            style=Style.icon(zIndex=1, visibility=visibility),
            children=[html.I(id=f'{_id}_icon', n_clicks=0,
                             className='fa fa-pencil-square-o')]
        )
        return btn

    @classmethod
    def _paramBox(cls, _id, h2, text, params, buttons, style=None):
        div = html.Div(
            id=_id,
            style=style or Style.paramBox(height='200px'),

            children=[
                html.Div(
                    id=f'{_id}_inner',
                    style=Style.container(),
                    children=[
                        cls._getEditButton(f'{_id}_edit_button', visibility='hidden'),
                        html.H2(h2, style=Style.text(marginTop='-40px', marginBottom='0px')),
                        html.Div(id=f'{_id}_text',
                                 children=[html.P(txt, style=Style.text(margin='0'))
                                           for txt in text.split('\n')],
                                 style=Style.text(margin='0 1em 10px 1em')),
                        html.Div(
                            id=f'{_id}_params',
                            style=Style.container(),
                            children=params
                        ),

                        # This Div functions like a line-break
                        html.Div(style={'flex-basis': '100%'}),
                        # Bottom Section
                        html.Div(
                            id=f'{_id}_bottom',
                            style=Style.container(),
                            children=[
                                # Buttons
                                html.Div(id=f'{_id}_buttons',
                                         style=Style.inputWrapper(),
                                         children=buttons
                                         )
                            ]
                        )
                    ]
                ),
            ])
        return div

    @classmethod
    def _getPopulationSection(cls):
        return cls._paramBox('population_section',
                             h2='Population',
                             text="",
                             params=[
                                # Population Size
                                cls._getParam('population_size_param', 'Pop. Size', 'population_size_text_input',
                                              '1000'),
                                # Start Money
                                cls._getParam('start_money_param', 'Wealth per Person',
                                              'population_start_money_text_input', '100')
                            ],
                             buttons=[
                                     html.Button('Confirm', id='population_confirm_button', n_clicks=0,
                                                 disabled=False,
                                                 style=Style.button2()),
                                     html.Button('Reset', id='reset_pop_button', n_clicks=0,
                                                 disabled=False,
                                                 style=Style.button2(visibility='hidden'))
                                 ],
                             style=Style.paramBox(margin='500px auto 10px auto', opacity='0.0'))

    @classmethod
    def _getCoinFlipSection(cls):
        div = cls._paramBox('coin_flip_section',
                            'Opportunities',
                            text="",
                            params=[
                                # Number of Coin Flips
                                cls._getParam('number_of_flips_param', 'Number of Coin Flips', 'num_flips_text_input',
                                              '1000'),
                                # Dollars per Flip
                                cls._getParam('dollars_per_flip_param', 'Wealth per Flip',
                                              'dollars_per_flip_text_input', '100')
                            ],
                            buttons=[
                                html.Div(id='coin_flip_buttons',
                                         style=Style.inputWrapper(),
                                         children=[
                                             html.Button('Flip', id='coin_flip_button', n_clicks=0, disabled=False,
                                                         style=Style.button()),
                                             html.Button('Reset', id='reset_coin_flips_button', n_clicks=0,
                                                         disabled=False,
                                                         style=Style.button(visibility='hidden'))
                                         ]
                                         ),
                                # Progress Bar
                                html.Div(id='progress_div',
                                         style=Style.progress(),
                                         children=[
                                             dcc.Graph(id="progress_bar",
                                                       figure=make_progress_graph(0, 100),
                                                       config=dict(displayModeBar=False)),
                                             html.Button(
                                                 id='cancel_button',
                                                 style=Style.cancel(),
                                                 children=[html.I(id='cancel_button_icon', n_clicks=0,
                                                                  className='fa fa-times')]
                                             )
                                         ]
                                         ),
                            ],
                            style=Style.paramBox(margin='300px auto 10px auto', visibility='hidden'))
        return div
