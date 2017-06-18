import os
import puckmath.core.builder.build


if __name__ == '__main__':
    puckmath_url = os.environ['PUCKMATH_URL']
    puckmath_usr = os.environ['PUCKMATH_USR']
    puckmath_pwd = os.environ['PUCKMATH_PWD']
    puckmath.core.builder.build.create_tables('{}:{}@{}'.format(puckmath_usr, puckmath_pwd, puckmath_url))
    session, engine = puckmath.core.builder.build.make_session('{}:{}@{}/puckmath'.format(puckmath_usr, puckmath_pwd, puckmath_url))
    puckmath.core.builder.build.build_teams(session)
