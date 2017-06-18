import urllib.request
import logging


def logger():
    return logging.getLogger('db_utils')


def download_html(url, dest_file):
    """

    :param url:
    :param dest_file:
    :return:
    """
    logger().debug('Requesting URL: {}'.format(url))
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
            'Connection': 'close'
        }
    )
    response = urllib.request.urlopen(req)
    html = response.read()

    logger().debug('Writing to {}'.format(dest_file))
    with open(dest_file, 'wb') as f:
        f.write(html)

    return response.geturl()
