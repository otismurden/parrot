CONFIG = {"timeout": 30, "retries": 3, "region": "eu-west-2"}


def get_timeout():
    """Seconds before a request is abandoned.

    Read from the environment-backed CONFIG.
    """
    return CONFIG["timeout"]


def get_retries():
    """How many times a failed call is retried.

    Read from the environment-backed CONFIG.
    """
    return CONFIG["retries"]


def get_region():
    """Cloud region the shop is deployed to.

    Read from the environment-backed CONFIG.
    """
    return CONFIG["region"]
