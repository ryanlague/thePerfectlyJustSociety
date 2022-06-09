
# Built-In Python
import statistics
from pathlib import Path
import pickle
from collections.abc import Sequence
import random

# Third-Party
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from fire import Fire

# Custom
from population import Population
from flips import Flips, Flip
from impz_logger.decorators import profile


class History:
    def __init__(self):
        self.moneyStamps = []
        self.numFlips = []
        self.populations = []

    def __repr__(self):
        return f"<{self.__class__.__name__} | Entries: {len(self)}>"

    def __len__(self):
        return len(self.moneyStamps)

    def add(self, moneyStamp, numFlips, pop):
        self.moneyStamps.append(moneyStamp)
        self.numFlips.append(numFlips)
        self.populations.append(pop)

    def toDf(self, includeStats=True):
        data = []
        for i in tqdm(range(len(self)), desc=f'Converting {self} to df'):
            row = self.moneyStamps[i]
            row_data = {str(person_id): money for person_id, money in enumerate(row)}
            row_data.update({'numFlips': self.numFlips[i]})
            if includeStats:
                row_data.update({
                    'total': sum(row),
                    'max': max(row),
                    'min': min(row),
                    'mean': statistics.mean(row),
                    'median': statistics.median(row)
                })
            data.append(row_data)
        print('Initializing DF...')
        df = pd.DataFrame(data).set_index('numFlips', drop=False)
        print('Done!')
        return df


class CoinFlipper:
    def __init__(self, population: Population, dollarsPerFlip: float, allowDebt: bool,
                 selectionStyle: str = 'sequential'):
        self.population = population
        self.dollarsPerFlip = dollarsPerFlip
        self.allowDebt = allowDebt
        self.selectionStyle = selectionStyle

        self.flips: Flips = Flips()
        self.history: History = History()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def numFlips(self):
        return len(self.flips)

    def flip(self, num: int = 1, plotEvery=10_000, logHistory=True):
        """Flip a coin some number of times and settle the bets"""
        for i in tqdm(range(num), total=num, unit='flips', desc='Flipping Coins'):
            self.flipOnce()
            if logHistory:
                self.history.add(self.population.getMoneyStamp(), i + 1, self.population.toDf())
            if plotEvery and (i + 1) % plotEvery == 0:
                self.population.plot(t=0.1, title=f'Population after {i + 1:,} flips '
                                                  f'(Total: ${self.population.totalMoney:,})')

    def flipOnce(self):
        # Pick 2 random people from the group to "flip" against each other
        p1, p2 = self.getPeople(2)
        winner = random.choice([p1, p2])
        loser = p1 if winner == p2 else p2
        # Since both are random selections, we just assume the "first" one was the winner
        flip = Flip(winner=winner, loser=loser, bet=self.dollarsPerFlip)
        # Log the flip
        self.flips.append(flip)

        if loser.has(self.dollarsPerFlip) or self.allowDebt:
            flip.settleBet()

    def getPeople(self, n):
        if self.selectionStyle == 'random':
            return self.population.pickRandoms(n)
        elif self.selectionStyle == 'sequential':
            nex = [self.population.next(loop=True) for _ in range(n)]
            return nex
        else:
            raise Exception(f"Unknown selectionStyle: {self.selectionStyle}")

    def save(self, filepath):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(str(filepath), 'wb') as pf:
            pickle.dump(self, pf)
        print(f'Saved to {filepath}')

    @classmethod
    def load(cls, filepath):
        filepath = Path(filepath)
        if filepath.exists():
            flipper: cls
            with open(str(filepath), 'rb') as pf:
                flipper = pickle.load(pf)
            return flipper
        else:
            raise Exception(f"Filepath does not exist")


@profile()
def do_the_flips(flipper, numFlips, plotEvery=0):
    """This is just here for profiling"""
    flipper.flip(numFlips, plotEvery=plotEvery)
    return flipper


def main(numFlips=1_000_000, numPeople=1000, startMoney=100, dollarsPerFlip=10, allowDebt=True, plot=False, useCache=True):

    flipper_path = Path(f'saved_flippers/people_{numPeople}_start_{startMoney}_bet_{dollarsPerFlip}_debt_{allowDebt}_'
                        f'flips_{numFlips}.pickle')
    if useCache and flipper_path.exists():
        flipper = CoinFlipper.load(flipper_path)
    else:
        people = Population([])
        people.add(numPeople, startMoney)

        flipper = CoinFlipper(people, dollarsPerFlip, allowDebt)
        do_the_flips(flipper, numFlips=numFlips, plotEvery=10_000 if plot else 0)
        flipper.save(flipper_path)

    print('Done flipping!')
    if plot:
        flipper.population.plot()
        plt.close()

    flipper.history.toDf()


if __name__ == '__main__':
    Fire(main)
