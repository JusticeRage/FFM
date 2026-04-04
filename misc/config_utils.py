TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off", ""}


def get_config_boolean(config, section, option, fallback=False):
    """
    Returns a boolean config value while tolerating direct bool assignments in tests.
    :param config: The ConfigParser-like object holding the configuration.
    :param section: The config section.
    :param option: The config option.
    :param fallback: The value to return if the option is missing.
    :return: The normalized boolean value.
    """
    try:
        value = config[section][option]
    except KeyError:
        return fallback

    if isinstance(value, bool):
        return value
    if value is None:
        return fallback

    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return bool(value)
