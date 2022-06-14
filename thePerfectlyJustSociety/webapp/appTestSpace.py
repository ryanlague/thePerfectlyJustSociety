
import shutil
from pathlib import Path
import uuid

from main import FlipperManager, getUpdatedGraph, INCLUDE_TOP_X
from thePerfectlyJustSociety.coinFlip.pollableThread import PollableCoinFlipper

FLIPPER_PATH = Path('flipperCache/session_xyz/THE_BEST_FLIPPER.pickle')


def update(set_progress, wealth_distribution_dropdown_value, history_dropdown_value, numCoinFlipClicks,
           num_flips, numResetClicks):

    # This is updated at an interval specified in PollableCoinFlipper(progressEvery=num_flips)
    def progress_callback(progressRatio):
        set_progress((str(int(progressRatio * 100)), str(100)))

    # Update the progress to 0
    progress_callback(0.0)
    # The most recent flipper
    flipper_path = FLIPPER_PATH
    flipper = FlipperManager.get(flipper_path)
    # In-Progress flips will be saved to this path, so if the process is cancelled,
    # the previous flipper is not corrupted
    in_progress_dir = FLIPPER_PATH.parent.joinpath('tmp')
    in_progress_path = in_progress_dir.joinpath(f'{FLIPPER_PATH.stem}_tmp_{uuid.uuid4()}{FLIPPER_PATH.suffix}')
    # A Pollable / Stoppable Thread
    save_every = (int(num_flips) // 4) or 1
    thread = PollableCoinFlipper(flipper=flipper, flipperPath=in_progress_path,
                                 numFlips=num_flips, progressEvery=1, saveEvery=save_every,
                                 saveTopX=INCLUDE_TOP_X)
    thread.start()
    # Regularly poll the thread and update the progress bar
    thread.pollEvery(0.5, progress_callback, pollAtStart=True)
    # The newly updated flipper
    flipper = FlipperManager.get(in_progress_path)
    # Overwrite the old flipper
    FlipperManager.save(flipper, FLIPPER_PATH)
    # Delete the in-progress file.
    # This method is cancellable with no cleanup method (Dash limitation)
    # So we delete the whole directory, which will also clean old, missed files
    shutil.rmtree(str(in_progress_dir), ignore_errors=True)

    # Message beneath the buttons
    message = f'A total of {len(flipper.flips)} coins have been flipped!' \
        if numCoinFlipClicks > 0 else ''

    # Whatever button was hit, we always update the graph
    population_fig = getUpdatedGraph(wealth_distribution_dropdown_value, flipper=flipper)
    history_fig = getUpdatedGraph(history_dropdown_value, flipper=flipper)

    return population_fig, history_fig, message


def main():
    update(set_progress=lambda x: True,
           wealth_distribution_dropdown_value='percent_wealth',
           history_dropdown_value='top_0_to_1_percent_wealth',
           numCoinFlipClicks=11,
           num_flips=1,
           numResetClicks=0)


if __name__ == '__main__':
    main()