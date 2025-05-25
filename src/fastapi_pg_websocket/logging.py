def config_logging(default_config_file: str = "logging.dev.yml"):
    # pylint: disable=import-outside-toplevel
    import logging.config
    import os

    import yaml

    config_path = os.getenv("LOGGING_CONFIG", default_config_file)
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
    logging.getLogger(__name__).info("Loaded test logging from %s", config_path)
