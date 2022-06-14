
import logging
from pathlib import Path
from flask import request

from .coinFlip import CoinFlipper, Flips, Flip, History
from .population import Population


class FlipperManager:
    def __init__(self, popSize, startMoney, dollarsPerFlip, allowDebt, includeTopX):
        self.popSize = popSize
        self.startMoney = startMoney
        self.dollarsPerFlip = dollarsPerFlip
        self.allowDebt = allowDebt
        self.includeTopX = includeTopX

        self._cachedFlipper = None

    @property
    def sessionInProgress(self):
        return self.getFilepath().exists()

    @property
    def hasFlipped(self):
        return self.sessionInProgress and len(self.get().population.flips)

    @classmethod
    def getFilepath(cls, ip=None):
        ip = ip or request.remote_addr
        return Path(f'flipperCache/sessions/{ip}/currentFlipper.pickle')

    def reset(self):
        filepath = self.getFilepath()
        filepath.unlink(missing_ok=True)

    def new(self, filepath=None):
        filepath = Path(filepath or self.getFilepath())
        if filepath.exists():
            logging.warning(f'Overwriting {filepath} with a new flipper / population')

        logging.info(f'Starting a new Population with {self.popSize} people')
        population = Population()
        population.add(self.popSize, startMoney=self.startMoney)
        flipper = CoinFlipper(population, dollarsPerFlip=self.dollarsPerFlip, allowDebt=self.allowDebt,
                              selectionStyle='random')
        flipper.save(filepath, includeTopX=self.includeTopX)
        return flipper

    def get(self, filepath=None):
        if filepath or not self._cachedFlipper:
            filepath = Path(filepath or self.getFilepath())
            if filepath.exists():
                logging.info(f'Loading {filepath}')
                flipper = CoinFlipper.load(filepath)
                logging.info(f'{filepath} has been loaded')
                self._cachedFlipper = flipper
            else:
                raise Exception(f"No active CoinFlipper. Call {self}.new().")
            return flipper
        else:
            return self._cachedFlipper

    @classmethod
    def save(cls, coinFlipper, filepath):
        logging.info(f'Saving {filepath}')
        filepath = filepath or coinFlipper.descriptiveFilepath(coinFlipper.cacheDir)
        coinFlipper.save(filepath)
        history = coinFlipper.history.getStatsOverTime(includeTopX=True)
        history.to_pickle(filepath.with_stem(f"{filepath.stem}_history"))
        logging.info(f'{filepath} has been saved')

