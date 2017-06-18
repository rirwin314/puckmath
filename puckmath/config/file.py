import yaml


class ConfigFile:
    FILE_PATH = '.puckmath.yaml'

    def __init__(self):
        raise AttributeError

    @classmethod
    def get_key(cls, group, key):
        with open(ConfigFile.FILE_PATH) as f:
            dat = yaml.load(f)
        return dat.get(group, {}).get(key)

    @classmethod
    def get_group(cls, group):
        with open(ConfigFile.FILE_PATH) as f:
            dat = yaml.load(f)
        return dat[group]

    @classmethod
    def put_key(cls, group, key, value):
        try:
            with open(ConfigFile.FILE_PATH) as f:
                dat = yaml.load(f)
            if group in dat:
                dat[group][key] = value
            else:
                dat[group] = {key: value}
        except FileNotFoundError:
            dat = {group: {key: value}}
        with open(ConfigFile.FILE_PATH, 'w') as f:
            yaml.dump(dat, f)
