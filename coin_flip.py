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
        self.populationDfs = []

    def __repr__(self):
        return f"<{self.__class__.__name__} | Entries: {len(self)}>"

    def __len__(self):
        return len(self.moneyStamps)

    def add(self, population: Population, numFlips: int):
        self.moneyStamps.append(population.getMoneyStamp())
        self.numFlips.append(numFlips)
        self.populationDfs.append(population.toDf())

    def getStatsOverTime(self, includeTopX=True):
        # TODO: Don't recalculate every time.
        #       Keep a cache and just add new entries
        data = []
        if len(self):
            for i in tqdm(range(len(self)), desc=f'Converting History to df'):
                # A DataFrame representing the population after a given number of flips (self.numFlips[i])
                row = self.populationDfs[i]
                # Converting the df to a single row, so it can be a part of the full history df
                row_data = {
                    'numFlips': self.numFlips[i],
                    'money': row.money.values,  # This will be a numpy array, saved in a single cell of the df
                    'total': row.money.sum(),
                    'max': row.money.max(),
                    'min': row.money.min(),
                    'mean': row.money.mean(),
                    'median': row.money.median()
                }
                if includeTopX:
                    # Split the People into bins by
                    money: np.ndarray = row.money.values
                    money[::-1].sort()
                    num_per_percent = round(len(money) * 0.1)
                    _split = np.array_split(money, num_per_percent)
                    for idx, top_x_range in enumerate(_split):
                        row_data[f"top_{idx}_to_{idx+1}_percent_wealth"] = top_x_range.sum() / row.money.sum() * 100

                data.append(row_data)
            print('Initializing DF...')
            df = pd.DataFrame(data).set_index('numFlips', drop=False)
            print('Done!')
        else:
            df = pd.DataFrame()
        return df


class CoinFlipper:
    def __init__(self, population: Population, dollarsPerFlip: float, allowDebt: bool,
                 selectionStyle: str = 'sequential', cacheDir='flipperCache'):
        self.population = population
        self.dollarsPerFlip = dollarsPerFlip
        self.allowDebt = allowDebt
        self.selectionStyle = selectionStyle

        self.cacheDir = Path(cacheDir)
        self.flips: Flips = Flips()
        self.history: History = History()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def descriptiveFilepath(self, directory='.'):
        directory = Path(directory)
        return directory.joinpath(f'people_{len(self.population)}_start_{self.population[0].startMoney}_'
                                  f'bet_{self.dollarsPerFlip}_debt_{self.allowDebt}_'
                                  f'flips_{len(self.flips)}.pickle')

    @property
    def numFlips(self):
        return len(self.flips)

    @profile()
    def flip(self, num: int = 1, saveEvery=0, plotEvery=10_000, logHistory=True):
        """Flip a coin some number of times and settle the bets"""
        for i in tqdm(range(num), total=num, unit='flips', desc='Flipping Coins'):
            self.flipOnce()
            if logHistory:
                self.history.add(self.population, numFlips=len(self.flips))

            if saveEvery and len(self.flips) > 0 and len(self.flips) % saveEvery == 0:
                filepath = self.descriptiveFilepath(self.cacheDir)
                self.save(filepath)
                history = self.history.getStatsOverTime()
                history.to_pickle(filepath.with_stem(f"{filepath.stem}_history"))
            if plotEvery and len(self.flips) % plotEvery == 0:
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
        if filepath.is_dir() or not filepath.suffix:
            filepath = self.descriptiveFilepath(filepath)
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


def main(numFlips=1_000_000, numPeople=1000, startMoney=100, dollarsPerFlip=10, allowDebt=True, plot=False,
         useCache=True):
    flipper_path = Path(f'flipperCache/people_{numPeople}_start_{startMoney}_bet_{dollarsPerFlip}_debt_{allowDebt}_'
                        f'flips_{numFlips}.pickle')
    if useCache and flipper_path.exists():
        flipper = CoinFlipper.load(flipper_path)
    else:
        people = Population([])
        people.add(numPeople, startMoney)

        flipper = CoinFlipper(people, dollarsPerFlip, allowDebt)
        flipper.flip(numFlips, saveEvery=1_000, plotEvery=10_000 if plot else 0)
        flipper.save(flipper_path)

    print('Done flipping!')
    if plot:
        flipper.population.plot()
        plt.close()

    flipper.history.getStatsOverTime()


if __name__ == '__main__':
    Fire(main)
