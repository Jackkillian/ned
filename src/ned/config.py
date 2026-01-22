from cfgsaver import cfgsaver

from ned.utils import ROOT_DIR


def save_config(config):
    cfgsaver.save("ned", config, ROOT_DIR)
    return config


def get_config():
    return cfgsaver.get("ned", ROOT_DIR)


def get_spotify_creds():
    config = get_config()
    if config is None:
        return None
    return config.get("id")


def get_device_name():
    return get_config().get("device_name", "Ned")


def get_cached_token():
    return get_config().get("token")


def save_cached_token(token):
    config = get_config()
    config["token"] = token
    save_config(config)


def setup_config():
    return save_config({"id": None, "token": None})
