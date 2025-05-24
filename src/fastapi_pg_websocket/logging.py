import logging


def config_logging():
    logging.basicConfig(
        level=logging.INFO,  # or DEBUG
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],  # <== ensures output goes to stdout
    )
