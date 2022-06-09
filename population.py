
# Built-In Python
import random
from collections.abc import Sequence
import statistics

# Third-Party
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


class Person:
    def __init__(self, idNum, money):
        self.idNum = idNum
        self.money = money
        self.startMoney = money
        self.numWins = 0
        self.numLosses = 0

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.idNum:,} | ${self.money:,} | Flips: {self.numFlips:,} " \
               f"({self.numWins:,} - {self.numLosses:,})>"

    @property
    def numFlips(self):
        return self.numWins + self.numLosses

    def has(self, amount):
        return self.money >= amount


class Population(Sequence):
    def __init__(self, people, parent=None):
        self.people = people
        self._parent = parent
        self._currentPlotAx = None

        self._iterator = None

    def __repr__(self):
        return f"<{self.__class__.__name__} Num: {len(self.people)}>"

    def __len__(self):
        return len(self.people)

    def __iter__(self):
        return iter(self.people)

    def __getitem__(self, item):
        return self.people[item]

    @property
    def parent(self):
        if self._parent:
            return self._parent
        else:
            raise Exception(f"{self} is not a SubPopulation. It has no parent.")

    def next(self, loop=False, default=None):
        if not self._iterator:
            def _iter():
                for p in self:
                    yield p
                if loop:
                    yield from _iter()

            self._iterator = _iter()
        return next(self._iterator, default)

    @property
    def moneyPerPerson(self):
        return [p.money for p in self.people]

    @property
    def totalMoney(self):
        return sum(self.moneyPerPerson)

    @property
    def percentPopulationOfParent(self):
        return len(self) / len(self.parent)

    @property
    def percentWealthOfParent(self):
        return self.totalMoney / self.parent.totalMoney

    @property
    def meanWealth(self):
        return statistics.mean(self.moneyPerPerson)

    @property
    def medianWealth(self):
        return statistics.median(self.moneyPerPerson)

    @property
    def minWealth(self):
        return min(self.moneyPerPerson)

    @property
    def maxWealth(self):
        return max(self.moneyPerPerson)

    def add(self, n, startMoney):
        self.people.extend([Person(i, startMoney) for i in tqdm(range(n), desc='Adding people to population')])
        return self

    def sortedByWealth(self, ascending=False):
        return Population(sorted(self.people, key=lambda x: x.money, reverse=not ascending))

    def getWealthiest(self, n):
        sorted_by_wealth = self.sortedByWealth()
        if n <= len(self):
            top = sorted_by_wealth[:] if n == len(self) else sorted_by_wealth[:n]
            return Population(top, parent=self)
        else:
            raise Exception(f"Can not get {n} wealthiest from {self}. It only has {len(self)} people")

    def getWealthiestXPercent(self, topX):
        pop = self.sortedByWealth()
        num_people_in_top_x = round(len(pop) * (topX / 100))
        return self.getWealthiest(num_people_in_top_x)

    def getWealthRangeByPercent(self, lowPercent, highPercent):
        pop = self.sortedByWealth(ascending=False)
        this_range = pop[round(len(pop) * highPercent / 100): round(len(pop) * lowPercent / 100)]
        return Population(this_range, parent=self)


    def pickRandoms(self, numRandoms):
        return random.sample(self.people, numRandoms)

    def statsDict(self, **kwargs):
        return {
            'mean': self.meanWealth,
            'median': self.medianWealth,
            'min': self.minWealth,
            'max': self.maxWealth,
            'percent_population': self.percentPopulationOfParent,
            'percent_wealth': self.percentWealthOfParent,
            **kwargs
        }

    def getStatsByTopX(self, percentages=None):
        top_x_percentages = percentages or [1, 2, 3, 5, 10, 25, 50, 75, 90, 99, 100]
        stats = [self.getWealthiestXPercent(x).statsDict() for x in top_x_percentages]
        return pd.DataFrame(stats)

    def getStatsByTopXRanges(self, percentages=None):
        top_x_percentages = percentages or range(101)
        stats = [self.getWealthRangeByPercent(lowPercent=top_x_percentages[i + 1], highPercent=p)
                     .statsDict(top_x_percent_low=top_x_percentages[i + 1], top_x_percent_high=p)
                 for i, p in enumerate(top_x_percentages[:-1])]
        return pd.DataFrame(stats)

    def plot(self, t=0, title=''):
        # stats = self.getStatsByTopX()
        stats = self.getStatsByTopXRanges()

        df = stats.copy()
        df['percent_population'] = df['percent_population'].apply(lambda x: round(x * 100, 2))
        df['percent_wealth'] = df['percent_wealth'].apply(lambda x: round(x * 100, 2))

        if self._currentPlotAx:
            self._currentPlotAx.clear()

        self._currentPlotAx = df.plot(x='top_x_percent_low', y='percent_wealth', kind='line', ax=self._currentPlotAx)

        plt.title(title)
        plt.xlabel('Top X Percent of Population (1% buckets)')
        plt.ylabel('Percent of Total Money')
        if t:
            plt.show(block=False)
            plt.pause(t)
        else:
            plt.show(block=True)
