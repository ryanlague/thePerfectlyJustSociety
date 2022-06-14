
# Built-In Python
import time
from pathlib import Path
import pickle
import random
import logging

# Third-Party
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from fire import Fire

# Custom
from .population import Population
from .flips import Flips, Flip


class History:
    def __init__(self):
        self.moneyStamps = []
        self.numFlips = []
        self.populationDfs = []

        self.stats = pd.DataFrame(columns=['numFlips', 'money', 'total', 'max', 'min', 'mean', 'median'])\
            .set_index('numFlips', drop=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} | Entries: {len(self)}>"

    def __len__(self):
        return len(self.moneyStamps)

    def add(self, population: Population, numFlips: int):
        self.moneyStamps.append(population.getMoneyStamp())
        self.numFlips.append(numFlips)
        self.populationDfs.append(population.toDf())

    def getStatsOverTime(self, includeTopX=True, logProgress=False):
        df = self.stats
        new_data = []
        if len(self):
            start_flip = len(df)
            for i in tqdm(range(start_flip, len(self)), desc=f'Converting History to df', disable=not logProgress):
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
                    use_indices = includeTopX if isinstance(includeTopX, list) else list(range(0, 100))
                    for idx, top_x_range in enumerate(_split):
                        if idx in use_indices:
                            row_data[f"top_{idx}_to_{idx+1}_percent_wealth"] = top_x_range.sum() / row.money.sum() * 100

                new_data.append(row_data)
            new_df = pd.DataFrame(new_data)
            df = pd.concat([self.stats, new_df])
            self.stats = df
        return self.stats

    def save(self, filepath, includeTopX=True):
        df = self.getStatsOverTime(includeTopX=includeTopX)
        df.to_pickle(str(filepath))


class CoinFlipper:
    def __init__(self, population: Population, dollarsPerFlip: int = 1, allowDebt: bool = False, brokeIsOut=True,
                 selectionStyle: str = 'random', cacheDir='flipperCache/cli'):
        self.population = population
        self.dollarsPerFlip = int(dollarsPerFlip)
        self.allowDebt = allowDebt
        self.brokeIsOut = brokeIsOut
        self.selectionStyle = selectionStyle

        self.cacheDir = Path(cacheDir)
        self.flips: Flips = Flips()
        self.history: History = History()
        self.history.add(self.population, numFlips=len(self.flips))

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def descriptiveFilepath(self, directory: Path = '.'):
        directory = Path(directory)
        return directory.joinpath(f'people_{len(self.population)}_start_{self.population[0].startMoney}_'
                                  f'bet_{self.dollarsPerFlip}_debt_{self.allowDebt}_'
                                  f'flips_{len(self.flips)}.pickle')

    @property
    def numFlips(self):
        return len(self.flips)

    def flip(self, num: int = 1, saveEvery=0, plotEvery=0, plotKind='topXPercentRanges', logProgress=False,
             saveHistory=True, closePlt=True):
        """Flip a coin some number of times and settle the bets"""
        for i in tqdm(range(num), total=num, unit='flips', desc='Flipping Coins', disable=not logProgress):
            self.flipOnce()

            if saveHistory:
                self.history.add(self.population, numFlips=len(self.flips))

            if saveEvery and len(self.flips) > 0 and len(self.flips) % saveEvery == 0:
                filepath = self.descriptiveFilepath(self.cacheDir)
                self.save(filepath, history=True)
            if plotEvery and len(self.flips) % plotEvery == 0:
                self.population.plot(t=0.1, keepAx=True, kind=plotKind,
                                     title=f'Population after {i + 1:,} flips (Total: ${self.population.totalMoney:,})')
        if closePlt:
            plt.close()

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
        pop = self.population.getPeopleWithMoreThan(0) if self.brokeIsOut else self.population
        if self.selectionStyle == 'random':
            return pop.pickRandoms(n)
        elif self.selectionStyle == 'sequential':
            if self.brokeIsOut:
                raise Exception(f'Can not use sequential selection when brokeIsOut is set to True.')
            nex = [pop.next(loop=True) for _ in range(n)]
            return nex
        else:
            raise Exception(f"Unknown selectionStyle: {self.selectionStyle}")

    def save(self, filepath, history=True, includeTopX=True):
        filepath = Path(filepath)
        if filepath.is_dir() or not filepath.suffix:
            filepath = self.descriptiveFilepath(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(str(filepath), 'wb') as pf:
            pickle.dump(self, pf)

        if history:
            self.history.save(filepath.with_stem(f"{filepath.stem}_history"), includeTopX=includeTopX)

    @classmethod
    def load(cls, filepath):
        filepath = Path(filepath)
        if filepath.exists():
            flipper: cls
            with open(str(filepath), 'rb') as pf:
                try:
                    flipper = pickle.load(pf)
                except (EOFError, pickle.UnpicklingError):
                    filepath.unlink(missing_ok=True)
                    raise EOFError(f"There was a problem loading {filepath}. It has been deleted.")

            if len(flipper.history) > 0 and flipper.history.stats.empty:
                # TODO: History cached stats do not seem to be loaded here...
                # This is a tmp solution until I can dig into the pickling / unpickling procedures
                history_path = filepath.with_stem(f'{filepath.stem}_history')
                if history_path.exists():
                    logging.debug(
                        'Warning: FlipperManager history stats were not loaded correctly. Manually loading now')
                    flipper.history.stats = pd.read_pickle(str(history_path))
            return flipper
        else:
            raise Exception(f"Filepath does not exist")


def flipCoins(numFlips=10_000, numPeople=1000, startMoney=100, dollarsPerFlip=1, allowDebt=False,
              plot=False, plotEvery=100, saveHistory=False, showResults=True, plotKind='topXPercentRanges',
              useCache=False):

    people = Population([])
    people.add(numPeople, startMoney)

    flipper = CoinFlipper(people, dollarsPerFlip, allowDebt)
    flipper.flip(numFlips, saveEvery=0, plotEvery=plotEvery if plot else 0, logProgress=True, saveHistory=saveHistory,
                 plotKind=plotKind, closePlt=False)

    if useCache:
        cache_dir = Path('flipperCache/cli')
        flipper_path = cache_dir.joinpath(
            f'people_{numPeople}_start_{startMoney}_bet_{dollarsPerFlip}_debt_{allowDebt}_'
            f'flips_{numFlips}.pickle')
        flipper.save(flipper_path)

    if showResults:
        print()
        print('Results:')
        print(flipper.population.getStatsByTopXRanges())

    print('Done flipping!')
    if plot:
        flipper.population.plot(kind=plotKind, keepAx=True,
                                title=f'Population after {len(flipper.flips):,} flips '
                                      f'(Total: ${flipper.population.totalMoney:,})')

    if len(flipper.history):
        flipper.history.getStatsOverTime()


if __name__ == '__main__':
    Fire(flipCoins)
