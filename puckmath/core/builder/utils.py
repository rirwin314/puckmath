TEAMS_ABBREVIATIONS = {
    'ANAHEIM DUCKS': 'ANA',
    'ARIZONA COYOTES': 'ARI',
    'ATLANTA THRASHERS': 'ATL',
    'ATLANTA FLAMES': 'ATLF',
    'BOSTON BRUINS': 'BOS',
    'BROOKLYN AMERICANS': 'BRK',
    'BUFFALO SABRES': 'BUF',
    'CALIFORNIA GOLDEN SEALS': 'CAL',
    'CAROLINA HURRICANES': 'CAR',
    'CALGARY FLAMES': 'CGY',
    'CANADIENS MONTREAL': 'MTL',
    'CHICAGO BLACKHAWKS': 'CHI',
    'COLUMBUS BLUE JACKETS': 'CBJ',
    'CLEVELAND BARONS': 'CLE',
    'COLORADO AVALANCHE': 'COL',
    'COLORADO ROCKIES': 'COLR',
    'DALLAS STARS': 'DAL',
    'DETROIT RED WINGS': 'DET',
    'EDMONTON OILERS': 'EDM',
    'FLORIDA PANTHERS': 'FLA',
    'HAMILTON TIGERS': 'HAM',
    'HARTFORD WHALERS': 'HAR',
    'KANSAS CITY SCOUTS': 'KC',
    'LOS ANGELES KINGS': 'LAK',
    'MIGHTY DUCKS OF ANAHEIM': 'MDA',
    'MINNESOTA WILD': 'MIN',
    'MINNESOTA NORTH STARS': 'MNS',
    'MONTREAL CANADIENS': 'MTL',
    'MONTREAL MAROONS': 'MTLM',
    'MONTREAL WANDERERS': 'MTLW',
    'NASHVILLE PREDATORS': 'NSH',
    'NEW JERSEY DEVILS': 'NJD',
    'NEW YORK AMERICANS': 'NYA',
    'NEW YORK ISLANDERS': 'NYI',
    'NEW YORK RANGERS': 'NYR',
    'OAKLAND SEALS': 'OAK',
    'OTTAWA SENATORS': 'OTT',
    'OTTAWA SENATORS (ORIGINAL)': 'OTTO',
    'PHILADELPHIA FLYERS': 'PHI',
    'PHILADELPHIA QUAKERS': 'PHIQ',
    'PHOENIX COYOTES': 'PHX',
    'PITTSBURGH PENGUINS': 'PIT',
    'PITTSBURGH PIRATES': 'PITP',
    'QUEBEC NORDIQUES': 'QUE',
    'QUEBEC BULLDOGS': 'QUEB',
    'SAN JOSE SHARKS': 'SJS',
    'ST. LOUIS BLUES': 'STL',
    'ST LOUIS BLUES': 'STL',
    'ST. LOUIS EAGLES': 'STLE',
    'TAMPA BAY LIGHTNING': 'TBL',
    'TORONTO MAPLE LEAFS': 'TOR',
    'VANCOUVER CANUCKS': 'VAN',
    'WASHINGTON CAPITALS': 'WSH',
    'WINNIPEG JETS': 'WPG',
    'WINNIPEG JETS (ORIGINAL)': 'WPGO'
}


ALT_ABBRS = {
    'L.A': 'LAK'
}


GAME_TYPE = {
    1: 'Preseason',
    2: 'Regular',
    3: 'Playoffs'
}


def team_to_abbr(team_name):
    team_name = team_name.replace("b'", '')

    for _team_name in TEAMS_ABBREVIATIONS:
        if team_name.upper() == _team_name:
            return TEAMS_ABBREVIATIONS[_team_name]

    raise ValueError('Cannot match team name {0}'.format(team_name))


def format_team_abbr(team_abbr):
    team_abbr = team_abbr if team_abbr not in ALT_ABBRS else ALT_ABBRS[team_abbr]
    assert team_abbr in TEAMS_ABBREVIATIONS.values(), ValueError('{0} not in TEAMS_ABBREVIATIONS'.format(team_abbr))

    return team_abbr