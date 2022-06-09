
# Third-Party
import random

import matplotlib.pyplot as plt
from tqdm import tqdm
from fire import Fire

# Custom
from population import Population


class Flip:
    def __init__(self, winner, loser, bet):
        self.winner = winner
        self.loser = loser
        self.bet = bet
        self.settled = False

    def __repr__(self):
        return f"<{self.__class__.__name__} +{self.winner} -{self.loser} (${self.bet:,})>"

    def settleBet(self):
        if not self.settled:
            self.loser.money -= self.bet
            self.loser.numLosses += 1

            self.winner.money += self.bet
            self.winner.numWins += 1

            self.settled = True
        else:
            raise Exception(f"Can not settle a bet twice")


class CoinFlipper:
    def __init__(self, population: Population, dollarsPerFlip: float, allowDebt: bool,
                 selectionStyle: str = 'sequential'):
        self.population = population
        self.dollarsPerFlip = dollarsPerFlip
        self.allowDebt = allowDebt
        self.selectionStyle = selectionStyle

        self.flips = []

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    def numFlips(self):
        return len(self.flips)

    def flip(self, num: int = 1, plotEvery=10_000):
        """Flip a coin some number of times and settle the bets"""
        for i in tqdm(range(num), total=num, unit='flips', desc='Flipping Coins'):
            self.flipOnce()
            if plotEvery and (i + 1) % plotEvery == 0:
                self.population.plot(t=0.1, title=f'Population after {i + 1:,} flips')

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


def main(numFlips=100_000_000, numPeople=1000, startMoney=100, dollarsPerFlip=1, allowDebt=True, plot=True):

    people = Population([])
    people.add(numPeople, startMoney)

    flipper = CoinFlipper(people, dollarsPerFlip, allowDebt)
    flipper.flip(numFlips)

    if plot:
        people.plot(t=10)
        plt.close()


if __name__ == '__main__':
    Fire(main)
