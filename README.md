# The Perfectly Just Society

The Perfectly Just Society is an experiment in equality and equity. It aims to simulate an idealist society where everyone is treated equally to see how opportunities are given and wealth is dispersed.

## Installation

### PyPI (for use as a module)
```bash
    pip install thePerfectlyJustSociety
```
### GitHub
```bash
clone https://github.com/ryanlague/thePerfectlyJustSociety.git
cd thePerfectlyJustSociety
pip install .
```

## Usage

### Web App
![](https://github.com/ryanlague/thePerfectlyJustSociety/blob/main/thePerfectlyJustSociety/examples/tpjs_webapp_example.gif)
```bash
python3 server.py  # Dash is running on http://127.0.0.1:8050/
python3 server.py --port 8051  # Run on port 8051
python3 server.py --help  # A full list of parameters

```

### CLI
```bash
# Runs some coin flips and displays a Pandas DataFrame of the results
python3 cli.py

# Runs 1000 coin flips over a population of 1000 people starting with $100 each. 
# Each flip has a wager of $1 and we allow people to go into debt instead of stopping if they reach $0.
# A plot will be displayed after every 100 flips
python3 cli.py --numFlips=1000 --numPeople=1000 --startMoney=100 --dollarsPerFlip=1 --allowDebt --plot --plotEvery=100

# Show a complete list of a parameters and exit
python3 --help
```

### As a module

```python

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

```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
MIT License

Copyright (c) 2022 Ryan Lague

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.