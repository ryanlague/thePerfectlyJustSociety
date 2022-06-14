
from thePerfectlyJustSociety import CoinFlipper, Population

# A Population of People
pop = Population()
# Add 1000 people to the population and give them each $100
pop.add(1000, 100)

# A Coin Flipper
flipper = CoinFlipper(pop)
# Flip a coin 1000 times to simulate "opportunities" and plot the results after every 10th flip
flipper.flip(1000, plotEvery=10)

# Plots
flipper.population.plot(
    kind='topXPercentRanges',
    title=f'Population after {len(flipper.flips):,} flips (Total: ${flipper.population.totalMoney:,})'
)
flipper.population.plot(
    kind='distribution',
    title=f'Wealth Distribution after {len(flipper.flips):,} flips (Total: ${flipper.population.totalMoney:,})'
)
