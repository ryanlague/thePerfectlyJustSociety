

class DropdownOption:
    def __init__(self, label, _id, xLabel='Number of Flips', xKey='numFlips', yLabel='Wealth', yKey=None,
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
            cls('Wealth Per Percentile', 'percent_wealth', xLabel='Wealth Percentile', xKey='top_x_percent_low',
                yLabel='Percent of Total Wealth', yKey='percent_wealth', graphFrom='wealth_distribution'),
            cls('Wealth Per Person', 'money', xLabel='People (sorted by wealth)', xKey='rank_by_money',
                yLabel='Money', yKey='money', graphFrom='individual_wealth'),
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
