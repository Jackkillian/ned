from cfgsaver import cfgsaver


def save_config(config):
    cfgsaver.save("ned", config)
    return config


def get_config():
    return cfgsaver.get("ned")


def get_spotify_creds():
    config = get_config()
    if config is None:
        return None
    return config.get("id"), config.get("secret")


def get_device_name():
    return get_config().get("device_name", "Ned")


def setup_config():
    return save_config({"id": None, "secret": None})
