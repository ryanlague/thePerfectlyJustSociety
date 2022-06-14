
import logging
from fire import Fire
from webapp.main import app


def runServer(verbosity='INFO', debug=True, port='8050'):
    logging.getLogger().setLevel(verbosity)
    app.run(port=port, debug=debug)


if __name__ == '__main__':
    Fire(runServer)
