dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "base",
            "filename": "weather_log.log",
            "mode": "a"
        },
        # "file2": {
        #     "class": "logging.FileHandler",
        #     "level": "DEBUG",
        #     "formatter": "base",
        #     "filename": "weather_log_dct.log",
        #     "mode": "a"
        # }
    },
    "loggers": {
        "weather_logger": {
            "level": "DEBUG",
            "handlers": ["file"],
            # "propagate": False,
        },
        "main": {
            "level": "DEBUG",
            "handlers": ["file"],
            # "propagate": False,
        },
        "models": {
            "level": "DEBUG",
            "handlers": ["file"],
            # "propagate": False,
        },
        "get_weather": {
            "level": "DEBUG",
            "handlers": ["file"],
            # "propagate": False,
        }
    },

    # "filters": {},
    # "root": {} # == "": {}
}
