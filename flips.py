from collections.abc import Sequence


class Flip:
    def __init__(self, winner, loser, bet: int):
        self.winner = winner
        self.loser = loser
        self.bet = int(bet)
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


class Flips(Sequence):
    def __init__(self, flips=None):
        self.flips = flips or []

    def __repr__(self):
        return f"<{self.__class__.__name__} | Num: {len(self)}>"

    def __len__(self):
        return len(self.flips)

    def __getitem__(self, item):
        return self.flips[item]

    def __iter__(self):
        return iter(self.flips)

    def append(self, val):
        self.flips.append(val)
