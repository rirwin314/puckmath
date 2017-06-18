import getpass
from puckmath.config.file import ConfigFile


def build_db_route():
    user = ConfigFile.get_key('postgres', 'username')
    address = ConfigFile.get_key('postgres', 'uri')
    port = ConfigFile.get_key('postgres', 'port')
    db_name = ConfigFile.get_key('postgres', 'db_name')

    print(f'Postgres info: {address}:{port}/{db_name}')
    print(f'User: {user}')

    password = getpass.getpass('Postgres password:')

    return '{}:{}@{}:{}/{}'.format(user, password, address, port, db_name)
