
# Built-In Python
import threading
import time

# Third-Party
from tqdm import tqdm


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stop = threading.Event()

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def wait(self, pingEvery=0.1):
        while self.is_alive():
            time.sleep(pingEvery)


class PollableCoinFlipper(StoppableThread):
    def __init__(self, *args, flipper=None, flipperPath=None, numFlips=1, progressEvery=1, saveEvery=1, saveTopX=True,
                 logProgress=True, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.flipper = flipper
        self.flipperPath = flipperPath
        self.numFlips = numFlips
        self.progressEvery = progressEvery
        self.saveEvery = saveEvery
        self.saveTopX = saveTopX
        self.progress = 0
        self.logProgress = logProgress
        self.callback = None

    def run(self):
        try:
            self.numFlips = int(self.numFlips)
        except TypeError as e:
            self.stop()
            return f"That's not a number! Please enter a number of coins to flip"

        filepath = self.flipperPath
        for i in tqdm(range(0, self.numFlips, self.progressEvery), desc=f'Flipping {self.numFlips} coins',
                      disable=not self.logProgress):
            self.flipper.flip(self.progressEvery, logProgress=False)
            self.progress = i + self.progressEvery
            if i % self.saveEvery == 0:
                # Save to disk
                self.flipper.save(filepath, history=True, includeTopX=self.saveTopX)

        # Save at the end
        self.flipper.save(filepath, history=True)
        if self.callback:
            self.callback()

    def pollProgress(self):
        return self.progress / self.numFlips

    def pollEvery(self, t, callback, pollAtStart=False):
        if pollAtStart:
            callback(self.pollProgress())
        while self.is_alive():
            time.sleep(t)
            callback(self.pollProgress())
