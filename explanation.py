from dash import html, dcc


class Explanation:
    def __init__(self):
        self.content = self.getContent()

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return iter(self.content)

    @classmethod
    def getContent(cls):
        return [
            [
                html.Div("Equality", style={'font-size': '16px', 'font-weight': 'bold', 'margin-right': '0.5em',
                                            'margin-top': '1em'}),
                html.Div("(noun) e·qual·i·ty | /əˈkwälədē/", style={'font-size': '12px', 'font-style': 'italic'}),
                html.Div(style={'flex-basis': '100%'}),  # A line break
                html.P('The right of different groups of people to have a similar social position '
                       'and receive the same treatment'),
                html.P('Cambridge University Press. (n.d.). Equality. Cambridge Dictionary. Retrieved June 13, 2022, '
                       'from',
                       style={'font-size': '6px', 'font-style': 'italic', 'margin-bottom': '0'}),
                html.P('https://https://dictionary.cambridge.org/dictionary/english/equality',
                       style={'font-size': '6px', 'font-style': 'italic'})
            ],
            [
                html.Div("Equity", style={'font-size': '16px', 'font-weight': 'bold', 'margin-right': '0.5em',
                                          'margin-top': '1em'}),
                html.Div("(noun) eq·ui·ty | /ˈek.wə.t̬i/", style={'font-size': '12px', 'font-style': 'italic'}),
                html.Div(style={'flex-basis': '100%'}),  # A line break
                html.P('The situation in which everyone is treated fairly according to their needs '
                       'and no group of people is given special treatment'),
                html.P('Cambridge University Press. (n.d.). Equity. Cambridge Dictionary. Retrieved June 13, 2022, '
                       'from',
                       style={'font-size': '6px', 'font-style': 'italic', 'margin-bottom': '0'}),
                html.P('https://dictionary.cambridge.org/dictionary/english/equity',
                       style={'font-size': '6px', 'font-style': 'italic'})
            ],
            [
                html.Div("Let's build the perfectly just and equitable society!", style={'margin-top': '75px'})
            ]
        ]

    def getExplanation(self, idx=0):
        if idx < len(self):
            return self.content[idx]
        else:
            raise Exception(f'Can not get explanation {idx}. There are only {len(self)} explanations.')
