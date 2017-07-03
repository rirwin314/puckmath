# puckmath

Puckmath is a toolset used to scrape NHL game reports and deposit the data in a PostgreSQL database using SQLAlchemy. This includes scraping NHL Play-by-Play reports from 2008, which gives analysts access to the most detailed, official NHL data available.

The workhorses of this repo are found in the following directories:
1. The ORM: [`puckmath/puckmath/core/schema/*.py`](https://github.com/rirwin314/puckmath/tree/master/puckmath/core/schema)
2. The HTML parser: [`puckmath/puckmath/tools/NHLParser/*.py`](https://github.com/rirwin314/puckmath/tree/master/puckmath/core/tools/NHLParser)
3. The parsed data to DB script: [`GameFactory.py`](https://github.com/rirwin314/puckmath/blob/master/puckmath/core/builder/GameFactory.py)

## Schema

![Database schema](https://github.com/rirwin314/puckmath/blob/master/schema.png?raw=true)

## Installing

Please contact the developer if you're interested in using this toolset (`rirwin314@gmail.com`)! It was originally written to support some research, and is not very user-friendly at the moment. However if there is some community interest, I'll be happy to clean up the scripts for downloading data and populating the database.

## Built With

* [SQLAlchmey](https://www.sqlalchemy.org/) - Python ORM
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing lib

## Authors

* **Rob Irwin**

## Acknowledgments

* Huge shoutout to `hockey-reference.com` for creating such a comprehensive database which this project leans on heavily.
* Inspiration from nhlscrapi `https://pypi.python.org/pypi/nhlscrapi/`.
