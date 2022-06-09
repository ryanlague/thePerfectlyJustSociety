
# Built-In Python
import random
from collections.abc import Sequence
import statistics
import sys

# Third-Party
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm


class Person:
    def __init__(self, idNum, money: int, population):
        self.idNum = idNum
        self.money = int(money)
        self.startMoney = int(money)
        self.numWins = 0
        self.numLosses = 0
        self.population = population

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.idNum:,} | ${self.money:,} | Flips: {self.numFlips:,} " \
               f"({self.numWins:,} - {self.numLosses:,})>"

    def toDict(self):
        exclude = 'population'
        d = self.__dict__.copy()
        return {k: v for k, v in d.items() if k not in exclude}

    @property
    def numFlips(self):
        return self.numWins + self.numLosses

    def has(self, amount):
        return self.money >= amount


class Population(Sequence):
    def __init__(self, people=None, parent=None):
        self.people = people or []
        self._parent = parent
        self._iterator = None
        self._currentPlotAx = None

    def __repr__(self):
        return f"<{self.__class__.__name__} Num: {len(self.people)}>"

    def __len__(self):
        return len(self.people)

    def __iter__(self):
        return iter(self.people)

    def __getitem__(self, item):
        return self.people[item]

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_iterator'] = None
        return state

    def __setstate__(self, d):
        self.__dict__ = d

    def getMoneyStamp(self):
        return [p.money for p in self.people]

    def toDf(self):
        people = [p.toDict() for p in self.people]
        return pd.DataFrame(people)

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

            self._iterator = _iter()
        res = next(self._iterator, None)
        if res:
            return res
        elif loop:
            self._iterator = None
            return self.next(loop=loop, default=default)
        else:
            return default

    @property
    def moneyPerPerson(self):
        return [p.money for p in self.people]

    @property
    def totalMoney(self):
        return sum(self.moneyPerPerson)

    @property
    def percentPopulationOfParent(self):
        return len(self) / len(self.parent) * 100

    @property
    def percentWealthOfParent(self):
        return self.totalMoney / self.parent.totalMoney * 100

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
        self.people.extend([Person(i, startMoney, population=self) for i in tqdm(range(n),
                                                                                 desc='Adding people to population')])
        return self

    def addOne(self, startMoney):
        i = len(self)
        self.people.append(Person(i, startMoney, population=self))

    def sortedByWealth(self, ascending=False):
        return Population(sorted(self.people, key=lambda x: x.money, reverse=not ascending))

    def getWealthiest(self, n, least=False):
        """Get the people in the population with the most (or least) money
            Args:
                n: The number of people to get
                least: If True, get the least wealthy instead of the most wealthy
        """
        sorted_by_wealth = self.sortedByWealth(ascending=least)
        if n <= len(self):
            top = sorted_by_wealth[:] if n == len(self) else sorted_by_wealth[:n]
            return Population(top, parent=self)
        else:
            raise Exception(f"Can not get {n} wealthiest from {self}. It only has {len(self)} people")

    def getWealthiestXPercent(self, topX, least=False):
        pop = self.sortedByWealth(ascending=least)
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
            'total': self.totalMoney,
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
