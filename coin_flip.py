import random
import matplotlib.pyplot as plt
import numpy as np
import statistics


# from impz_logger.decorators import profile


class Person:
    def __init__(self, idNum, money):
        self.idNum = idNum
        self.money = money
        self.numWins = 0
        self.numLosses = 0

    def __repr__(self):
        return f"<{self.__class__.__name__} | ${self.money} | Flips: {self.numFlips} ({self.numWins} - {self.numLosses})>"

    @property
    def numFlips(self):
        return self.numWins + self.numLosses


class CoinFlipper:
    def __init__(self, people, dollarsPerFlip, allowDebt, activeStats=0, activePlots=0):
        self.people = people
        self.dollarsPerFlip = dollarsPerFlip
        self.allowDebt = allowDebt
        self.activeStats = activeStats
        self.activePlots = activePlots

        self.startMoney = self.people[0].money

        self.numFlips = 0
        self.stats = {'mean': [], 'median': [], 'mode': [], 'top': {}}

    @property
    def moneyPerPerson(self):
        return [p.money for p in self.people]

    def sorted(self):
        self.people = sorted(self.people, key=lambda x: x.money)
        return self.people

    def pickRandoms(self, numRandoms):
        return random.sample(self.people, numRandoms)

    def giveMoney(self, loser, winner):
        if loser.money > 0 or self.allowDebt:
            loser.money -= self.dollarsPerFlip
            loser.numLosses += self.dollarsPerFlip

            winner.money += self.dollarsPerFlip
            winner.numWins += self.dollarsPerFlip

    def flip(self):
        person1, person2 = self.pickRandoms(2)
        self.giveMoney(person1, person2)
        self.numFlips += 1

        if self.activeStats:
            if self.numFlips % self.activeStats == 0:
                self.getStats(printIt=True)

        if self.activePlots:
            if self.numFlips % self.activePlots == 0:
                self.plot(
                    t=0.1,
                    plotType='percentages',
                    title=f"Num People: {len(self.people):,}\nNum Flips: {self.numFlips:,}\nStart: ${self.startMoney}\n${self.dollarsPerFlip} per flip")

    def getStatsAboutTopX(self, topX):
        people = sorted(self.people, key=lambda p: p.money)
        total_money = sum([p.money for p in people])
        num_people_in_top_x = int(len(people) * (topX / 100))
        top_x_raw = people[len(people) - num_people_in_top_x:]
        if len(top_x_raw) > 0:
            top_x_total_money = sum([p.money for p in top_x_raw])
            top_x_total_percent = round(top_x_total_money / total_money * 100, 2)
        else:
            top_x_total_money = 'N/A'
            top_x_total_percent = 'N/A'

        return {'money': top_x_total_money, 'percent': top_x_total_percent}

    def plot(self, t=1, title='', plotType='hist'):
        self.getStats(printIt=False)

        x = [i for i in range(len(self.people))]
        y = [p.money for p in self.people]
        plt.clf()

        if plotType == 'scatter':
            plt.scatter(x, y)
        elif plotType == 'hist':
            plt.hist(y)
        elif plotType == 'stats':
            x = range(len(self.stats['mean']))

            for y in ['mean', 'median', 'mode']:
                plt.plot(x, self.stats[y], label=y)
                plt.legend(loc="upper left")
        elif plotType == 'percentages':
            x = range(len(self.stats['mean']))

            for y in [1]:
                plt.plot(x, self.stats['top'][y], label=f"Top {y}%")
                plt.legend(loc="upper left")

        plt.title(title)
        plt.xlabel('People')
        plt.ylabel('Money')
        plt.show(block=False)
        plt.pause(t)

    def getStats(self, printIt=False):

        stats = []

        total_money = sum([p.money for p in self.people])
        stats.append(f"Total Money: {total_money:,}")
        stats.append(f"Total People: {len(self.people):,}")

        mean, median, mode = statistics.mean(self.moneyPerPerson), statistics.median(
            self.moneyPerPerson), statistics.mode(self.moneyPerPerson)
        self.stats['mean'].append(mean)
        self.stats['median'].append(median)
        self.stats['mode'].append(mode)

        stats.append(f"Mean: {mean}")
        stats.append(f"Median: {median}")
        stats.append(f"Mode: {mode}")

        percentages = [1, 2, 3, 5, 10, 25, 50, 75, 90, 99]

        stats.append('\nTop:')
        for percentage in percentages:
            top_x_stats = self.getStatsAboutTopX(percentage)
            stats.append(f"\t{percentage}%: {top_x_stats['percent']}%")

            if percentage not in self.stats['top']:
                self.stats['top'][percentage] = []
            self.stats['top'][percentage].append(top_x_stats['percent'])

        stats_string = '\n'.join(stats)

        if printIt:
            print(f"\n{'-' * 10}STATS (after {self.numFlips:,} flips){'-' * 10}")
            print(f'\n{stats_string}')
        return stats_string

    def printStats(self, n):
        print(f"\n{'-' * 10}STATS (after {n:,} flips){'-' * 10}")
        print(f'\n{self.getStats()}')
        return


def buildPeople(n, startMoney):
    return [Person(i, startMoney) for i in range(n)]


def main(numFlips=100, numPeople=1000, startMoney=1000, dollarsPerFlip=100, activePlots=1_000, activeStats=100_000,
         endPlot=False, allowDebt=False, updateEvery=1):
    people = buildPeople(numPeople, startMoney)

    flipper = CoinFlipper(people, dollarsPerFlip, allowDebt, activeStats=activeStats, activePlots=activePlots)

    for n in range(numFlips):

        flipper.flip()

        if not activeStats:
            if n % updateEvery == 0:
                print(f"Completed: {n + 1:,} / {numFlips:,} flips", end='\r' if n < numFlips - 1 else '\n')

    flipper.getStats(printIt=True)
    if endPlot:
        if activePlots:
            plt.close()

        flipper.plot(t=10)
        plt.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-flips', type=int, default=1000, help='Number of flips')
    parser.add_argument('-people', type=int, default=1000, help='Number of people')
    parser.add_argument('-startMoney', type=int, default=10, help='Number of dollars each person starts with')
    parser.add_argument('-bet', type=int, default=1, help='Number of dollars to wager per flip')
    parser.add_argument('-activePlots', type=int, help='Plot results every X iterations')
    parser.add_argument('-activeStats', type=int, help='Print stats every X iterations')
    parser.add_argument('-plot', action='store_true', help='Use this flag to plot the results at the end')
    parser.add_argument('-allowDebt', action='store_true', help='Allow people to have less than $0')

    args = parser.parse_args()
    main(numFlips=args.flips, numPeople=args.people, startMoney=args.startMoney, dollarsPerFlip=args.bet,
         activePlots=args.activePlots, activeStats=args.activeStats, endPlot=args.plot, allowDebt=args.allowDebt)
